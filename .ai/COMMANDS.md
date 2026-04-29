# Índice de comandos

| Comando | Archivo | Uso principal |
|---|---|---|
| `/think` | `commands/think.md` | Razonamiento profundo y análisis conceptual |
| `/deep-think` | `commands/deep-think.md` | Razonamiento profundo con checklist explícito |
| `/plan` | `commands/plan.md` | Plan incremental de implementación |
| `/debug` | `commands/debug.md` | Diagnóstico abductivo de fallos |
| `/architecture` | `commands/architecture.md` | Diseño técnico y trade-offs |
| `/refactor` | `commands/refactor.md` | Refactor seguro e incremental |
| `/review` | `commands/review.md` | Revisión crítica de código |
| `/test` | `commands/test.md` | Estrategia de pruebas |
| `/docs` | `commands/docs.md` | Documentación técnica |
| `/security` | `commands/security.md` | Revisión de seguridad |
| `/research` | `commands/research.md` | Investigación técnica o académica |
| `/decision` | `commands/decision.md` | Matriz de decisión |
| `/handoff` | `commands/handoff.md` | Resumen para continuar trabajo |
| `/obsidian` | `commands/obsidian.md` | Markdown Obsidian (wikilinks, embeds, callouts, properties) |
| `/base` | `commands/base.md` | Bases de Obsidian (`.base`) |
| `/canvas` | `commands/canvas.md` | JSON Canvas (`.canvas`) |
| `/vault` | `commands/vault.md` | CLI de Obsidian / plugins y temas (según skill) |

## Convención de invocación

```text
/<command> <objetivo o problema>
```

Ejemplo:

```text
/debug El endpoint /api/login devuelve 500 al validar JWT
```

## Regla general

Antes de modificar código:

1. Comprende el problema.
2. Localiza archivos relevantes.
3. Expón riesgos.
4. Propón plan.
5. Ejecuta cambios mínimos.
6. Verifica con tests o checks.
