# /deep-think

## Propósito

Usar explícitamente un servidor MCP de razonamiento avanzado, como `deep-thinker`, cuando esté disponible.

## Entrada esperada

Problema complejo, decisión, arquitectura, investigación, bug difícil o hipótesis.

## Instrucciones

Intenta usar herramientas MCP en este orden si están disponibles:

1. `deep-thinker.think`
2. `deep-thinker.evaluate`
3. `deep-thinker.metacog`
4. `deep-thinker.prune`
5. `deep-thinker.graph`

Si esas herramientas no están disponibles, simula el mismo procedimiento de forma textual y declara que no se pudo invocar MCP.

## Estrategias

Usa una combinación según el caso:

- `first_principles` para fundamentos.
- `systems_thinking` para arquitectura e interdependencias.
- `counterfactual` para escenarios alternativos.
- `abductive` para debugging.
- `mcts` para exploración de decisiones con muchas ramas.

## Salida

```markdown
## Estrategias usadas

## Grafo conceptual del razonamiento

## Ramas principales

## Evaluación

| Rama | Confianza | Evidencia | Riesgos |
|---|---:|---|---|

## Ramas descartadas

## Conclusión

## Siguiente paso verificable
```
