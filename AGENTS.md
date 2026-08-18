# AGENTS.md — reglas obligatorias para humanos y agentes IA

## Antes de cambiar código

1. Leer `README.md`.
2. Leer `docs/ARCHITECTURE.md` y `docs/DOMAIN_MODEL.md`.
3. Leer el spec de la feature en `specs/features/`.
4. Si la decisión cambia un boundary arquitectónico, crear/actualizar un ADR.
5. No inventar APIs de librerías: verificar documentación o aislar la incertidumbre tras un adapter.

## Invariantes de dominio

- La identidad de un objeto BIM no es un mesh index. La identidad primaria es `revision_id + GlobalId` y, cuando sea posible, se mantiene una identidad lógica entre revisiones mediante `element_lineage`.
- IFC original es inmutable. Toda revisión se almacena como artefacto nuevo.
- BOQ, Gantt y Viewer NO son silos: todas las selecciones se resuelven por relaciones persistentes.
- El histórico de progreso es append-only; no sustituirlo por un único `%complete` mutable.
- Jobs BIM pesados jamás se ejecutan en el request HTTP sincrónico.
- Todos los writes relevantes generan auditoría y, cuando corresponda, evento outbox.
- Domain/core no depende del vendor del viewer, storage, scheduler, ERP o CDE.
- Toda feature multi-tenant debe filtrar por organización/proyecto en servidor; nunca confiar en el filtro del cliente.

## Flujo de trabajo

`SPEC -> failing test -> domain/data -> API contract -> implementation -> tests -> docs/ADR -> validation`.

## Comandos obligatorios antes de entregar

```bash
python scripts/verify_harness.py
make lint
make typecheck
make test
make smoke
```

Si un comando no puede ejecutarse por falta de Docker/dependencia, documentar exactamente cuál, por qué y qué se ejecutó en su lugar.

## Definition of Done resumida

No se considera terminada una story porque “se vea en UI”. Debe tener: acceptance criteria, autorización, validación, tests, manejo de errores, logging/audit, contratos actualizados, migración reversible o estrategia de rollback, y documentación mínima.

## Límites para agentes IA

- No hacer refactors masivos no solicitados.
- Cambios pequeños y verificables; preferir un PR por story.
- No eliminar tests para que CI pase.
- No bajar thresholds de calidad sin ADR.
- No cambiar schema o contrato público sin migration/versioning.
- No introducir secretos, tokens o datos reales en fixtures.
- Marcar claramente `TODO(PROD)` sólo cuando el harness define un punto de extensión intencionado.


## Ejecución con Codex

Para implementar el roadmap por tareas, usar `codex/TASK_INDEX.md` y un único archivo `codex/tasks/<TASK-ID>.md` por PR. No ejecutar una task cuyas dependencias no estén completadas. Validar el grafo con `python scripts/validate_codex_tasks.py`.
