# Prompt de reviewer independiente

```text
Actúa como reviewer senior de BIM Control X. No implementes features nuevas.

1. Lee `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/DOMAIN_MODEL.md` y el archivo de task que se está revisando bajo `codex/tasks/`.
2. Revisa el diff contra la rama base y ejecuta los tests relevantes.
3. Busca específicamente:
   - incumplimientos de tenant isolation/autorización;
   - pérdida de identidad `(revision_id, GlobalId)` o uso persistente de mesh/row indexes;
   - writes sin audit/outbox cuando aplique;
   - mutación destructiva de revisiones/progreso/baselines;
   - trabajo BIM pesado dentro del request HTTP;
   - races, retries no idempotentes, N+1, queries sin scope, memory leaks;
   - contract/schema drift, migrations inseguras y falta de rollback strategy;
   - vendor coupling dentro de domain/core;
   - tests insuficientes, tests eliminados o asserts débiles;
   - datos/secretos reales en fixtures;
   - regresiones de performance o observabilidad.
4. Clasifica hallazgos: BLOCKER / HIGH / MEDIUM / LOW.
5. Para cada hallazgo indica archivo, ubicación aproximada, causa, impacto y corrección propuesta.
6. Contrasta uno por uno los criterios de aceptación de la task y marca PASS/FAIL con evidencia.
7. No cambies código salvo que se te pida explícitamente después de la revisión.
```
