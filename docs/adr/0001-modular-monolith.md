# ADR-0001: Start with modular monolith plus async BIM workers

Status: Accepted

## Decision

Mantener dominio/API en un deployment lógico inicialmente y separar workers BIM por aislamiento de CPU/memoria y naturaleza asíncrona.

## Consequences

Menor complejidad distribuida al inicio; boundaries siguen siendo explícitos para permitir extracción posterior.
