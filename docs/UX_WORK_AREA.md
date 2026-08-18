# UX — Work Area

Layout principal: Viewer + panel tabular contextual + timeline/Gantt. Todo filtro/selección emite un `SelectionIntent` y el backend/selector resuelve entidades relacionadas.

Flujos esenciales:

- click elemento -> propiedades + BOQ + actividades + issues + QA;
- click BOQ -> elementos + coste + actividades;
- click activity -> elementos + progress + cost impact;
- scrub data date -> estado 4D + planned/actual/forecast;
- compare revision -> added/removed/changed con vínculos remapeados.

Evitar colores como única señal; incluir leyenda, patrones/labels y accesibilidad de teclado.
