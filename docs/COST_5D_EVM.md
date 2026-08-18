# BOQ / 5D / EVM

BOQ jerárquico con revisiones. Quantity conserva `value, unit, source, rule_id, revision_id`.

Costes: rates por effective date/currency/source; commitments, actuals y forecast separados. No mezclar presupuesto aprobado con forecast actual.

EVM:

- PV = budgeted cost of scheduled work.
- EV = budgeted cost of performed work.
- AC = actual cost.
- SPI = EV/PV; CPI = EV/AC.
- EAC/ETC/VAC con método configurable y documentado.

Curvas S deben indicar data date, baseline/cost revision y moneda.
