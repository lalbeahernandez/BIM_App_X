# Prompt templates

## Implement feature

> Implementa `<story-id>`. Lee AGENTS.md, los ADR y el spec relacionado. No inventes APIs externas; si una integración no está documentada, crea/usa un adapter. Mantén la identidad BIM, tenant isolation y append-only progress. Añade tests. Ejecuta verify/lint/typecheck/test/smoke. Entrega un resumen de contratos, migraciones, riesgos y validaciones.

## Review

> Revisa este cambio contra AGENTS.md y Definition of Done. Busca: fugas cross-tenant, ruptura de GlobalId/revision identity, queries N+1, jobs pesados en HTTP, pérdida de audit/outbox, contratos divergentes, errores de unidades/currency/timezone y regresiones de performance.

## BIM golden test

> Añade un golden test con fixture sintético. Registra hash, expected element count, IFC schema, expected GlobalIds y QTOs relevantes. El test debe fallar ante cambios no aprobados en ingestión.
