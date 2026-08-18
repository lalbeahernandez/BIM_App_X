import os
from pathlib import Path
import urllib.request


def read_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding='utf-8').splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


root = Path(__file__).resolve().parents[1]
defaults = read_env_file(root / '.env.example')
local = read_env_file(root / '.env')

api_base_url = os.getenv('API_BASE_URL') or local.get('API_BASE_URL')
if not api_base_url:
    configured_port = os.getenv('API_PORT') or local.get('API_PORT')
    if configured_port:
        api_base_url = f'http://localhost:{configured_port}'
    else:
        api_base_url = defaults.get('API_BASE_URL') or f"http://localhost:{defaults.get('API_PORT') or '8000'}"
api_base_url = api_base_url.rstrip('/')

for path in ['/health', '/v1/projects']:
    url = f'{api_base_url}{path}'
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode()
        print(url, response.status, body[:300])
print('SMOKE: OK')
