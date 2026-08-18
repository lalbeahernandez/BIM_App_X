import json
import urllib.request

for url in ['http://localhost:8000/health', 'http://localhost:8000/v1/projects']:
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode()
        print(url, response.status, body[:300])
print('SMOKE: OK')
