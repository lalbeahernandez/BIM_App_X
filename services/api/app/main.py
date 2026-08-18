import hashlib
import json
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from sqlalchemy import text

from app.audit import enqueue_outbox, record_audit
from app.config import settings
from app.db import connection
from app.schemas import (
    ModelCreate,
    ModelOut,
    ProjectCreate,
    ProjectOut,
    RevisionOut,
    SelectionResolveIn,
    SelectionResolveOut,
    WorkAreaOut,
)

app = FastAPI(title='BIM Control X API', version='0.1.0')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


@app.get('/health')
def health() -> dict:
    return {'status': 'ok', 'service': 'api'}


@app.get('/v1/projects', response_model=list[ProjectOut])
def list_projects():
    with connection() as conn:
        rows = conn.execute(text("""
          SELECT id, organization_id, code, name, timezone, currency, created_at
          FROM projects WHERE organization_id=:org ORDER BY created_at
        """), {'org': settings.default_org_id}).mappings().all()
    return [dict(r) for r in rows]


@app.post('/v1/projects', response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate):
    project_id = str(uuid4())
    with connection() as conn:
        row = conn.execute(text("""
          INSERT INTO projects(id, organization_id, code, name, timezone, currency)
          VALUES (:id,:org,:code,:name,:tz,:currency)
          RETURNING id, organization_id, code, name, timezone, currency, created_at
        """), {
            'id': project_id,
            'org': settings.default_org_id,
            'code': payload.code,
            'name': payload.name,
            'tz': payload.timezone,
            'currency': payload.currency.upper(),
        }).mappings().one()
        record_audit(
            conn,
            organization_id=settings.default_org_id,
            project_id=project_id,
            actor='dev-user',
            action='project.created',
            entity_type='project',
            entity_id=project_id,
            after=dict(row),
        )
    return dict(row)


@app.post('/v1/projects/{project_id}/models', response_model=ModelOut, status_code=status.HTTP_201_CREATED)
def create_model(project_id: UUID, payload: ModelCreate):
    model_id = str(uuid4())
    with connection() as conn:
        exists = conn.execute(
            text('SELECT 1 FROM projects WHERE id=:id AND organization_id=:org'),
            {'id': str(project_id), 'org': settings.default_org_id},
        ).first()
        if not exists:
            raise HTTPException(404, 'Project not found')
        row = conn.execute(text("""
          INSERT INTO models(id, project_id, discipline, name)
          VALUES (:id,:project,:discipline,:name)
          RETURNING id, project_id, discipline, name, created_at
        """), {
            'id': model_id,
            'project': str(project_id),
            'discipline': payload.discipline,
            'name': payload.name,
        }).mappings().one()
        record_audit(
            conn,
            organization_id=settings.default_org_id,
            project_id=str(project_id),
            actor='dev-user',
            action='model.created',
            entity_type='model',
            entity_id=model_id,
            after=dict(row),
        )
    return dict(row)


@app.post('/v1/models/{model_id}/revisions', response_model=RevisionOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_revision(model_id: UUID, file: Annotated[UploadFile, File(...)]):
    if not file.filename or not file.filename.lower().endswith('.ifc'):
        raise HTTPException(422, 'Only .ifc files are accepted by this MVP endpoint')
    data = await file.read()
    if len(data) > 1024 * 1024 * 1024:
        raise HTTPException(413, 'File exceeds 1 GiB development limit')
    sha256 = hashlib.sha256(data).hexdigest()
    revision_id = str(uuid4())
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f'{revision_id}.ifc'
    file_path.write_bytes(data)

    with connection() as conn:
        model = conn.execute(text("""
          SELECT m.id, m.project_id FROM models m JOIN projects p ON p.id=m.project_id
          WHERE m.id=:id AND p.organization_id=:org
        """), {'id': str(model_id), 'org': settings.default_org_id}).mappings().first()
        if not model:
            file_path.unlink(missing_ok=True)
            raise HTTPException(404, 'Model not found')
        revision_no = conn.execute(
            text('SELECT COALESCE(MAX(revision_no),0)+1 FROM model_revisions WHERE model_id=:id'),
            {'id': str(model_id)},
        ).scalar_one()
        row = conn.execute(text("""
          INSERT INTO model_revisions(id, model_id, revision_no, file_name, file_sha256, status)
          VALUES (:id,:model,:no,:name,:sha,'QUEUED')
          RETURNING id, model_id, revision_no, file_name, status, ifc_schema, error_message
        """), {
            'id': revision_id,
            'model': str(model_id),
            'no': revision_no,
            'name': file.filename,
            'sha': sha256,
        }).mappings().one()
        event_id = enqueue_outbox(
            conn,
            organization_id=settings.default_org_id,
            project_id=str(model['project_id']),
            event_type='model.revision.ingest_requested.v1',
            payload={
                'revision_id': revision_id,
                'model_id': str(model_id),
                'file_path': str(file_path),
            },
        )
        record_audit(
            conn,
            organization_id=settings.default_org_id,
            project_id=str(model['project_id']),
            actor='dev-user',
            action='model.revision_uploaded',
            entity_type='model_revision',
            entity_id=revision_id,
            after={'file_name': file.filename, 'sha256': sha256},
        )
    redis_client.lpush(
        'bim:ingest',
        json.dumps({'job_id': event_id, 'revision_id': revision_id, 'file_path': str(file_path)}),
    )
    return dict(row)


@app.get('/v1/projects/{project_id}/work-area', response_model=WorkAreaOut)
def work_area(project_id: UUID):
    pid = str(project_id)
    with connection() as conn:
        project_ok = conn.execute(
            text('SELECT 1 FROM projects WHERE id=:id AND organization_id=:org'),
            {'id': pid, 'org': settings.default_org_id},
        ).first()
        if not project_ok:
            raise HTTPException(404, 'Project not found')
        boq = conn.execute(text("""
          SELECT id, code, description, unit, quantity::float8 AS quantity, rate::float8 AS rate,
                 (quantity*rate)::float8 AS amount
          FROM boq_items WHERE project_id=:p ORDER BY code LIMIT 100
        """), {'p': pid}).mappings().all()
        activities = conn.execute(text("""
          SELECT
            id, external_id, name, planned_start, planned_finish, percent_complete::float8 AS percent_complete
          FROM activities WHERE project_id=:p ORDER BY planned_start NULLS LAST LIMIT 200
        """), {'p': pid}).mappings().all()
        revisions = conn.execute(text("""
          SELECT r.id, r.model_id, r.revision_no, r.file_name, r.status, r.ifc_schema, r.error_message
          FROM model_revisions r JOIN models m ON m.id=r.model_id WHERE m.project_id=:p
          ORDER BY r.created_at DESC LIMIT 20
        """), {'p': pid}).mappings().all()
    return {
        'boq': [dict(r) for r in boq],
        'activities': [dict(r) for r in activities],
        'revisions': [dict(r) for r in revisions],
    }


@app.post('/v1/selection/resolve', response_model=SelectionResolveOut)
def resolve_selection(payload: SelectionResolveIn):
    ids = [str(i) for i in payload.ids]
    with connection() as conn:
        element_ids: set[str] = set()
        boq_ids: set[str] = set()
        activity_ids: set[str] = set()
        if payload.source_type == 'element':
            element_ids.update(ids)
            rows = conn.execute(
                text('SELECT element_id, boq_item_id FROM element_boq_links WHERE element_id = ANY(:ids)'),
                {'ids': ids},
            ).all()
            boq_ids.update(str(r.boq_item_id) for r in rows)
            rows = conn.execute(
                text("""
                  SELECT element_id, activity_id FROM element_activity_links WHERE element_id = ANY(:ids)
                """),
                {'ids': ids},
            ).all()
            activity_ids.update(str(r.activity_id) for r in rows)
        elif payload.source_type == 'boq':
            boq_ids.update(ids)
            rows = conn.execute(
                text('SELECT element_id, boq_item_id FROM element_boq_links WHERE boq_item_id = ANY(:ids)'),
                {'ids': ids},
            ).all()
            element_ids.update(str(r.element_id) for r in rows)
            if element_ids:
                rows = conn.execute(
                    text('SELECT activity_id FROM element_activity_links WHERE element_id = ANY(:ids)'),
                    {'ids': list(element_ids)},
                ).all()
                activity_ids.update(str(r.activity_id) for r in rows)
        else:
            activity_ids.update(ids)
            rows = conn.execute(
                text("""
                  SELECT element_id, activity_id FROM element_activity_links WHERE activity_id = ANY(:ids)
                """),
                {'ids': ids},
            ).all()
            element_ids.update(str(r.element_id) for r in rows)
            if element_ids:
                rows = conn.execute(
                    text('SELECT boq_item_id FROM element_boq_links WHERE element_id = ANY(:ids)'),
                    {'ids': list(element_ids)},
                ).all()
                boq_ids.update(str(r.boq_item_id) for r in rows)
    return {
        'element_ids': sorted(element_ids),
        'boq_item_ids': sorted(boq_ids),
        'activity_ids': sorted(activity_ids),
    }
