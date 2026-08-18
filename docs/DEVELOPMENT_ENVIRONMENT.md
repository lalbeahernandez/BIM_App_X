# Development Environment

This repository supports a small, explicit toolchain for local development, Docker and CI.

## Supported Toolchain

| Tool | Supported version | Source of truth |
|---|---|---|
| Python | 3.11.x | `.python-version`, Python Dockerfiles, CI setup-python |
| Node.js | 22.x LTS | `.nvmrc`, web Dockerfile, CI setup-node |
| npm | npm bundled with supported Node 22, lockfile v3 | `apps/web/package-lock.json` |
| Git | 2.x | local/CI |
| Docker | Docker Engine/Desktop with Compose v2+ | local stack |
| Docker Compose | v2+ or Docker Compose plugin | `docker-compose.yml` |

Local newer runtimes may work, but CI and Docker define the supported baseline.

## Bootstrap

From a clean checkout:

```bash
cp .env.example .env
python -m pip install -r services/api/requirements.txt
cd apps/web
npm ci
cd ../..
python scripts/dev.py verify
python scripts/dev.py lint
python scripts/dev.py typecheck
python scripts/dev.py test
```

`npm ci` is preferred because the project versions frontend dependencies through
`apps/web/package-lock.json`.

## Quality Gates

Canonical cross-platform commands:

```bash
python scripts/dev.py verify
python scripts/dev.py codex-tasks
python scripts/dev.py lint
python scripts/dev.py typecheck
python scripts/dev.py test
python scripts/dev.py smoke
python scripts/dev.py all
```

Granular commands exist for CI:

```bash
python scripts/dev.py lint-api
python scripts/dev.py lint-web
python scripts/dev.py typecheck-api
python scripts/dev.py typecheck-web
```

GNU Make remains supported where available:

```bash
make lint
make typecheck
make test
make smoke
make verify
```

On Windows, GNU Make is optional; use `python scripts/dev.py ...`.

## Windows

Use PowerShell or another shell with Python, Node/npm, Git and Docker on `PATH`.

Known observations from AUD-003:

- Python, pip, Node, npm, Git, Docker CLI and Docker Compose CLI were available.
- GNU Make was not available.
- Docker daemon was unavailable because Docker Desktop's Linux engine pipe was missing.
- Port 8000 may be occupied by a non-project Windows service.

Do not disable TLS validation to work around corporate proxies. Configure the corporate CA,
proxy and tool certificate stores instead.

## Linux/macOS

The same `python scripts/dev.py ...` commands are supported. If GNU Make is installed,
Makefile targets wrap the same runner rather than reimplementing the gates.

## Docker

Start the full stack:

```bash
docker compose up --build
```

Check service state:

```bash
docker compose ps
```

Cleanup after a stack you started:

```bash
docker compose down
```

Avoid `docker compose down -v` unless you intentionally want to remove local volumes.

If Docker CLI exists but the daemon is unavailable, this is an external environment issue.
Start Docker Desktop or fix the user's Docker context/engine outside the repository.

## Ports And Smoke

Default ports are defined in `.env.example`:

```text
API_PORT=8000
WEB_PORT=3000
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`scripts/smoke_http.py` reads `API_BASE_URL` first. If it is not set, it derives
`http://localhost:<API_PORT>`.

If port 8000 is occupied, set another value in `.env`:

```text
API_PORT=8010
API_BASE_URL=http://localhost:8010
NEXT_PUBLIC_API_URL=http://localhost:8010
```

Then start the stack with Docker Compose and run:

```bash
python scripts/dev.py smoke
```

## TLS And Corporate Proxy

Persistent insecure settings are not allowed:

- no `trusted-host` in project pip config;
- no `strict-ssl=false` in project npm config;
- no `NODE_TLS_REJECT_UNAUTHORIZED=0`;
- no Python `verify=False`.

Use supported CA/proxy configuration for pip, npm, Git and Docker. Keep any corporate
certificate material outside this repository.

## Dependency Management

Python currently uses service-level `requirements.txt` files with bounded ranges. This is
simple but not fully locked; a future AUD/FND task may introduce compiled lock files or a
constraints strategy if reproducibility requires it.

Frontend dependencies use npm and `apps/web/package-lock.json`. Use:

```bash
cd apps/web
npm ci
```

Do not run `npm audit fix --force` without explicit approval.

## Troubleshooting

| Symptom | Meaning | Action |
|---|---|---|
| `make` is not recognized | GNU Make is absent on Windows | Use `python scripts/dev.py ...` |
| Docker CLI works but `docker info` fails | Docker daemon/Desktop is not running or current context is unavailable | Start/fix Docker Desktop manually |
| Smoke test times out on port 8000 | API is not running or another local process owns the port | Set `API_BASE_URL`/`API_PORT` to a free port and restart the stack |
| `npm audit` requires a lockfile | Frontend lockfile is missing | Regenerate with `npm install --package-lock-only`, then use `npm ci` |
