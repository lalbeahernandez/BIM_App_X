# API guidelines

- REST v1 para CRUD/commands claros; endpoints bulk explícitos.
- OpenAPI es contrato versionado.
- Idempotency-Key para comandos externos/reintentables.
- Cursor pagination para colecciones grandes.
- `409` para conflictos de versión/invariantes; `422` para validación semántica.
- ETag/version columns para optimistic concurrency en edición crítica.
- Webhooks salen desde outbox, firmados y reintentables.
- Para analytics complejos considerar query service/GraphQL sólo cuando exista un caso real; no introducirlo por moda.
