# OpenBIM standards strategy

- IFC2x3/IFC4/IFC4.3: ingest; canonical internal model no replica todo IFC.
- BCF: issue exchange + viewpoints; conservar referencias a components/GlobalIds.
- IDS: requirements validation; resultados por requirement + entity + revision.
- bSDD: adapter de diccionario para clasificación/propiedades; cachear referencias, no copiar semántica sin provenance.
- openCDE APIs: considerar para interoperabilidad de documentos/issues.

## Georeferencing

Persistir CRS del proyecto, mapa de conversión desde coordenadas IFC, origen local y precisión. Nunca “hornear” una transformación irreversible en la identidad geométrica.
