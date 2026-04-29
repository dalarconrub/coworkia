# /review

## Propósito

Revisar código, PRs o cambios con criterios técnicos explícitos.

## Entrada esperada

Diff, archivos modificados o descripción de PR.

## Instrucciones

Sé crítico pero constructivo. Prioriza problemas reales sobre preferencias estilísticas. Clasifica por severidad.

## Criterios

- Correctitud.
- Seguridad.
- Rendimiento.
- Mantenibilidad.
- Tests.
- Compatibilidad.
- Claridad.

## Salida

```markdown
## Resumen de revisión

## Hallazgos

| Severidad | Archivo/zona | Problema | Recomendación |
|---|---|---|---|

## Bloqueantes

## Mejoras no bloqueantes

## Tests faltantes

## Veredicto
```

Usa severidades: `blocker`, `major`, `minor`, `nit`.
