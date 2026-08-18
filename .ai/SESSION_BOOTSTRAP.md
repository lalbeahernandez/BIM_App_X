# Session bootstrap

Cada sesión de implementación debe comenzar con este orden:

1. `git status` y rama actual.
2. Leer `AGENTS.md`.
3. Identificar story en `backlog/epics.yaml` y feature spec.
4. Leer ADRs relacionados.
5. Ejecutar baseline: `python scripts/verify_harness.py` y tests relevantes.
6. Escribir plan de máximo 5-8 pasos verificables.
7. Implementar el cambio más pequeño que satisface aceptación.
8. Ejecutar validaciones obligatorias.
9. Resumir archivos cambiados, contratos/migrations, riesgos y próximos pasos.
