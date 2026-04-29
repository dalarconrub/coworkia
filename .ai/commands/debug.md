# /debug

## Propósito

Diagnosticar fallos usando razonamiento abductivo: síntomas → hipótesis → verificación.

## Entrada esperada

Error, stack trace, comportamiento inesperado, test fallido o logs.

## Instrucciones

Si está disponible `deep-thinker`, usa estrategia `abductive` y después `evaluate`.

No edites código hasta tener una hipótesis principal y una prueba mínima.

## Procedimiento

1. Resume el síntoma.
2. Extrae señales del error, logs o test.
3. Genera hipótesis de causa raíz.
4. Ordena hipótesis por probabilidad e impacto.
5. Propón pruebas mínimas para confirmar o descartar.
6. Recomienda el cambio mínimo.

## Salida

```markdown
## Síntoma

## Señales relevantes

## Hipótesis de causa raíz

| Rank | Hipótesis | Evidencia a favor | Evidencia en contra | Prueba mínima |
|---|---|---|---|---|

## Hipótesis más probable

## Cambio mínimo recomendado

## Verificación
```
