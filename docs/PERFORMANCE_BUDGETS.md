# Performance budgets

Objetivos iniciales a validar con datasets reales:

- p95 API read no-BIM: < 300 ms.
- p95 selection resolver para <=10k links: < 500 ms.
- Work Area interactive shell: < 3 s en red corporativa razonable.
- Viewer: first meaningful geometry < 5 s para modelo optimizado; 30+ FPS en navegación objetivo.
- Modelo federado piloto: 5-20 M triangles visibles mediante streaming/LOD/instancing según motor.
- IFC ingest: asíncrono, progreso observable, sin bloquear HTTP; objetivo inicial 1 GB con timeout/job budget configurado.
- No enviar millones de elementos tabulares al browser: paginación/virtualización obligatoria.

Benchmarks deben registrar hardware, browser, modelo, element count, triangle count y memory peak.
