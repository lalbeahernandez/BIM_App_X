# Security and compliance

## Baseline

- OIDC/OAuth2; MFA delegado al IdP.
- RBAC por organización/proyecto; ABAC para reglas finas.
- PostgreSQL RLS como defensa adicional en enterprise, no sustituto del service authorization.
- Encriptación TLS, storage encryption, key rotation.
- Secrets manager en cloud; `.env` sólo desarrollo.
- Audit append-only para writes sensibles.
- Antivirus/content scanning para uploads antes de procesar.
- Límites de tamaño, MIME sniffing y zip-bomb protection.
- SSRF/XXE/path traversal: parsing de formatos no confiables en workers aislados.
- SAST/SCA/container/IaC scanning en CI.

Threat models prioritarios: cross-tenant data access, malicious IFC/BCF archives, webhook forgery, viewer XSS via property text, authorization bypass en bulk APIs.
