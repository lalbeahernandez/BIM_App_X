# Workflow para agentes

## Feature slice recomendado

1. Spec y acceptance test.
2. Cambio mínimo de schema/domain.
3. Endpoint/command/query.
4. Adapter/worker si aplica.
5. UI thin slice.
6. Observabilidad/audit.
7. Tests y documentación.

Evitar construir “todo el módulo” en una sola tarea. Ejemplos de slices válidos: “crear ActivityRelation FS con lag”, “resolver selección BOQ -> elementos”, “persistir un ProgressRecord de cantidad”, “comparar GlobalIds entre revisiones”.
