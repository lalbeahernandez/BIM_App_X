from pathlib import Path
import json
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
ignored_dirs = {
    '.git', 'node_modules', '.next', '__pycache__', '.pytest_cache', '.mypy_cache',
    '.ruff_cache', 'dist', 'build', 'coverage', 'playwright-report', 'test-results',
    '.data', 'uploads',
}
ignored_file_names = {'next-env.d.ts', 'tsconfig.tsbuildinfo'}
ignored_relative_prefixes = {('codex', 'responses')}
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
file_count = 0
for p in root.rglob('*'):
    if not p.is_file():
        continue
    relative_parts = p.relative_to(root).parts
    if any(part in ignored_dirs for part in relative_parts):
        continue
    if p.name in ignored_file_names:
        continue
    if any(relative_parts[:len(prefix)] == prefix for prefix in ignored_relative_prefixes):
        continue
    file_count += 1
print(f'HARNESS CHECK: OK ({file_count} files)')
