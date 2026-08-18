# Runbooks

## IFC job stuck

1. Revisar `model_revisions.status/error_message`.
2. Correlacionar `job_id` en logs.
3. Validar espacio en storage y memoria worker.
4. Reintentar sólo si el job es idempotente.
5. Si el archivo es malicioso/corrupto, aislarlo y marcar `FAILED`.

## DB recovery

Usar backups PITR en producción. Probar restore trimestralmente. Docker local no es estrategia DR.
