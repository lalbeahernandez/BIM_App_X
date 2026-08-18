# Definition of Done

Una story está Done cuando:

- acceptance criteria demostrables pasan;
- autorización y aislamiento tenant están cubiertos;
- inputs y errores están validados;
- tests unit/integration/contract según riesgo existen;
- cambios UI críticos tienen E2E/visual cuando aplique;
- schema tiene migration forward y estrategia rollback;
- contrato OpenAPI/eventos se actualiza;
- auditoría/outbox se aplica a writes relevantes;
- logging no expone secretos/PII;
- performance budget no empeora sin ADR;
- docs/runbook/ADR se actualizan si procede;
- `lint + typecheck + test + smoke` pasan.
