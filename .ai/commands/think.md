# /think

## Propósito

Realizar razonamiento profundo sobre un problema antes de actuar.

## Entrada esperada

Un problema, hipótesis, decisión o pregunta compleja.

## Instrucciones

Actúa como analista técnico y cognitivo. Si está disponible una herramienta MCP de razonamiento como `deep-thinker`, úsala para estructurar el análisis.

Estrategias preferidas:

1. `first_principles`: reduce el problema a supuestos básicos.
2. `systems_thinking`: identifica componentes, interacciones y efectos secundarios.
3. `counterfactual`: analiza qué pasaría si las hipótesis principales fueran falsas.
4. `abductive`: genera explicaciones plausibles si hay síntomas o fallos.

## Procedimiento

1. Reformula el problema.
2. Identifica supuestos explícitos e implícitos.
3. Genera entre 3 y 5 hipótesis o alternativas.
4. Evalúa cada alternativa por plausibilidad, coste, riesgo y verificabilidad.
5. Señala incertidumbres.
6. Propón el siguiente paso mínimo.

## Salida

Devuelve:

```markdown
## Problema reformulado

## Supuestos

## Hipótesis / alternativas

| Alternativa | Ventajas | Riesgos | Cómo verificar |
|---|---|---|---|

## Incertidumbres

## Recomendación

## Siguiente paso mínimo
```
