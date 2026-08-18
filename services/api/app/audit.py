import json
from uuid import uuid4

from sqlalchemy import text


def record_audit(
    conn,
    *,
    organization_id: str,
    project_id: str | None,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: str,
    before=None,
    after=None,
) -> None:
    conn.execute(text("""
      INSERT INTO audit_events(
        id, organization_id, project_id, actor, action, entity_type, entity_id, before_data, after_data
      )
      VALUES (
        :id, :org, :project, :actor, :action, :etype, :eid, CAST(:before AS jsonb), CAST(:after AS jsonb)
      )
    """), {
        'id': str(uuid4()),
        'org': organization_id,
        'project': project_id,
        'actor': actor,
        'action': action,
        'etype': entity_type,
        'eid': entity_id,
        'before': json.dumps(before) if before is not None else None,
        'after': json.dumps(after) if after is not None else None,
    })


def enqueue_outbox(
    conn,
    *,
    organization_id: str,
    project_id: str | None,
    event_type: str,
    payload: dict,
) -> str:
    event_id = str(uuid4())
    conn.execute(text("""
      INSERT INTO outbox_events(id, organization_id, project_id, event_type, payload)
      VALUES (:id, :org, :project, :type, CAST(:payload AS jsonb))
    """), {
        'id': event_id,
        'org': organization_id,
        'project': project_id,
        'type': event_type,
        'payload': json.dumps(payload),
    })
    return event_id
