from pathlib import Path
import json, sys, zipfile

root = Path(__file__).resolve().parents[1]
required = [
 'README.md','AGENTS.md','docker-compose.yml','.env.example','Makefile',
 'docs/ARCHITECTURE.md','docs/DOMAIN_MODEL.md','docs/PROJECT_PLAN.md',
 'db/init/010_schema.sql','services/api/app/main.py','services/bim-worker/worker.py',
 'apps/web/app/page.tsx','specs/openapi.yaml','backlog/epics.yaml',
 'fixtures/ifc/tiny.ifc','fixtures/bcf/sample.bcfzip'
]
missing = [p for p in required if not (root/p).exists()]
if missing:
    print('HARNESS CHECK: FAIL missing:', *missing, sep='\n- ')
    sys.exit(1)
manifest = json.loads((root/'fixtures/golden/manifest.json').read_text())
assert manifest['datasets'], 'golden manifest empty'
with zipfile.ZipFile(root/'fixtures/bcf/sample.bcfzip') as z:
    assert 'bcf.version' in z.namelist()
print(f'HARNESS CHECK: OK ({sum(1 for p in root.rglob("*") if p.is_file())} files)')
