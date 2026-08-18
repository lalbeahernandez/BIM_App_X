# Integrations

Adapters previstos:

- Scheduling: Primavera P6 (XER/XML/API según disponibilidad), Microsoft Project.
- Cost/ERP: CSV/XLSX primero; conectores ERP por cliente.
- CDE: ACC/Autodesk, openCDE/BCF endpoints donde aplique.
- Identity: OIDC primero; SAML vía IdP/enterprise gateway.
- BI: export/query views y eventos; evitar acceso directo indiscriminado al OLTP.

Todo con mapping explícito, external_id, sync cursor, idempotencia, retries y dead-letter handling.
