# /test

## Propósito

Diseñar una estrategia de pruebas para una funcionalidad, bugfix o módulo.

## Entrada esperada

Descripción del cambio, módulo o bug.

## Instrucciones

Prioriza pruebas que reduzcan incertidumbre. Incluye unitarias, integración y regresión cuando corresponda.

## Procedimiento

1. Identifica comportamiento esperado.
2. Identifica casos borde.
3. Identifica invariantes.
4. Propón tests mínimos.
5. Señala mocks, fixtures y datos necesarios.

## Salida

```markdown
## Comportamiento a verificar

## Casos principales

## Casos borde

## Tests propuestos

| Tipo | Nombre sugerido | Qué verifica | Datos/fixtures |
|---|---|---|---|

## Tests mínimos antes de merge

## Riesgo cubierto por cada test
```
