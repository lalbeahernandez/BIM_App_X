# Codex Execution Pack

Este directorio convierte el roadmap del harness en **140 tareas pequeñas, verificables y mergeables** para trabajar con Codex sin perder arquitectura.

## Cómo usarlo

1. Empieza por `AUD-001` y sigue `TASK_INDEX.md` respetando `depends_on`.
2. Crea una rama por task, por ejemplo `codex/BIM-007-ifc-element-index`.
3. Abre `tasks/BIM-007.md` y pega únicamente la sección **Prompt listo para Codex**.
4. No encadenes automáticamente una tarea si la anterior no está mergeada o su contrato no está estabilizado.
5. Usa un segundo turno/agente como reviewer antes del merge.
6. Actualiza `task-status.csv` (`TODO`, `DOING`, `REVIEW`, `DONE`, `BLOCKED`).

## Gates de release

- **MVP core**: AUD + FND + BIM + VWR + BOQ + SCH y D4 hasta una simulación integrada; algunas tareas marcadas Beta pueden posponerse.
- **Beta Project Controls**: PRG + COL y performance de viewer/ingest.
- **Post-Beta**: diff/lineage/clash/GIS/search/AI read-only.
- **Enterprise**: SSO, ABAC/RLS evaluado, security hardening, DR, webhooks/integrations, load certification y production readiness.

## Regla de tamaño

Si Codex estima que una task requiere más de ~1–2 días o toca >2 bounded contexts de forma profunda, divídela antes de implementar. Cada subtask debe conservar el ID padre, por ejemplo `BIM-007A`, `BIM-007B`, y no cambiar el criterio final del padre.

## Reviewer prompt

Usa `REVIEWER_PROMPT.md` después de cada task importante o antes del merge.

## Archivos

- `TASK_INDEX.md`: navegación humana.
- `tasks.yaml`: fuente estructurada para automatización.
- `task-status.csv`: tracker editable.
- `tasks/*.md`: prompt completo para cada task.
- `REVIEWER_PROMPT.md`: revisión independiente.
- `RELEASE_GATES.md`: hitos y criterios de salida.
