import json
import os
import time
from pathlib import Path
from uuid import uuid4

import psycopg
from redis import Redis

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
DATABASE_DSN = os.getenv('DATABASE_DSN', 'postgresql://bim:bim@db:5432/bim')
QUEUE = 'bim:ingest'


def safe_attr(obj, name):
    try:
        value = getattr(obj, name, None)
        return str(value) if value is not None else None
    except Exception:
        return None


def process(job: dict) -> None:
    revision_id = job['revision_id']
    file_path = Path(job['file_path'])
    with psycopg.connect(DATABASE_DSN) as conn:
        conn.execute("UPDATE model_revisions SET status='PROCESSING', error_message=NULL WHERE id=%s", (revision_id,))
        conn.commit()
        try:
            import ifcopenshell
            model = ifcopenshell.open(str(file_path))
            schema = getattr(model, 'schema', None)
            count = 0
            for element in model.by_type('IfcProduct'):
                global_id = safe_attr(element, 'GlobalId')
                if not global_id:
                    continue
                info = {
                    'step_id': element.id(),
                    'tag': safe_attr(element, 'Tag'),
                    'description': safe_attr(element, 'Description'),
                }
                conn.execute('''
                    INSERT INTO bim_elements(id, revision_id, global_id, ifc_class, name, object_type, properties)
                    VALUES (%s,%s,%s,%s,%s,%s,%s::jsonb)
                    ON CONFLICT (revision_id, global_id) DO UPDATE SET
                      ifc_class=EXCLUDED.ifc_class, name=EXCLUDED.name,
                      object_type=EXCLUDED.object_type, properties=EXCLUDED.properties
                ''', (str(uuid4()), revision_id, global_id, element.is_a(), safe_attr(element, 'Name'),
                      safe_attr(element, 'ObjectType'), json.dumps(info)))
                count += 1
                if count % 1000 == 0:
                    conn.commit()
            conn.execute("UPDATE model_revisions SET status='READY', ifc_schema=%s WHERE id=%s", (schema, revision_id))
            conn.commit()
            print(json.dumps({'event':'ifc_ingest_complete','revision_id':revision_id,'elements':count,'schema':schema}))
        except Exception as exc:
            conn.rollback()
            with psycopg.connect(DATABASE_DSN) as error_conn:
                error_conn.execute("UPDATE model_revisions SET status='FAILED', error_message=%s WHERE id=%s",
                                   (str(exc)[:4000], revision_id))
                error_conn.commit()
            print(json.dumps({'event':'ifc_ingest_failed','revision_id':revision_id,'error':str(exc)}))


def main() -> None:
    redis = Redis.from_url(REDIS_URL, decode_responses=True)
    print(json.dumps({'event':'worker_started','queue':QUEUE}))
    while True:
        item = redis.brpop(QUEUE, timeout=5)
        if not item:
            time.sleep(0.2)
            continue
        _, raw = item
        process(json.loads(raw))

if __name__ == '__main__':
    main()
