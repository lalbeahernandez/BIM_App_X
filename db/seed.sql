-- Idempotent developer seed. The base seed is automatically applied on first DB creation.
\i /docker-entrypoint-initdb.d/020_seed.sql
