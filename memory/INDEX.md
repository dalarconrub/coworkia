# INDEX — Memoria del proyecto Coworkia

> **Punto de entrada único para cualquier agente IA que arranque sesión.**
> Este fichero apunta a todos los recursos MD y artefactos que definen el proyecto a día de hoy.
> Se lee **antes que el chat del día**: es el mapa del territorio.

---

## 0. Identidad y propósito

| Recurso                                              | Qué contiene                                              |
| ---------------------------------------------------- | --------------------------------------------------------- |
| [memory/PURPOSE.md](PURPOSE.md)                      | Qué es Coworkia, visión, funcionalidades, principios no negociables |
| [memory/STRUCTURE.md](STRUCTURE.md)                  | Mapa de carpetas, lógica de organización, árbol auto-generado |
| [memory/SNAPSHOT.md](SNAPSHOT.md)                    | Agregado auto-generado de `MEMORIA:` / `BLOQUEO:` / `SIGUIENTE:` de todos los chats (regenerado por `sync-chat-memory`) |
| [memory/ROSTER.md](ROSTER.md)                        | Directorio curado de subagentes activos (`Root/Sub`) y su foco |
| [README.md](../README.md)                            | Guía pública del proyecto                                 |

## 1. Protocolo de agentes (obligatorio leer según identidad)

| Agente     | Archivo principal                                                  | Rol                                   |
| ---------- | ------------------------------------------------------------------ | ------------------------------------- |
| Claude     | [CLAUDE.md](../CLAUDE.md)                                          | Análisis, revisión crítica            |
| Codex      | [AGENTS.md](../AGENTS.md)                                          | Implementación, código, tests         |
| Copilot    | [.github/copilot-instructions.md](../.github/copilot-instructions.md) | Orquestación, síntesis                |
| **Todos**  | [.claude/multiagent.md](../.claude/multiagent.md)                  | Protocolo compartido (append-only, formatos, marcadores, devlog) |

## 2. Conversación viva (hilo multiagente)

| Recurso                                          | Qué contiene                                     |
| ------------------------------------------------ | ------------------------------------------------ |
| [chats/](../chats/)                              | Histórico de chats diarios (`chat_YYYY-MM-DD.md`) |
| Chat activo del día                              | Resuelto por `python tools/init_chat.py`         |
| [multiagents/chat_template.md](../multiagents/chat_template.md) | Plantilla del chat diario              |

Regla: append-only, UTF-8 estricto. Leer completo antes de responder.

## 3. Decisiones y memoria multiagente (derivada)

Regenerable con `python agents/orchestrator_agent.py sync-chat-memory`.

| Recurso                                                                   | Qué contiene                                     |
| ------------------------------------------------------------------------- | ------------------------------------------------ |
| [artifacts/multiagent/chat_memory.md](../artifacts/multiagent/chat_memory.md)             | Snapshot legible de la memoria multiagente       |
| [artifacts/multiagent/decision_log.json](../artifacts/multiagent/decision_log.json)       | Log de decisiones (votos, evaluaciones, cierres) |
| [artifacts/multiagent/memory_records.json](../artifacts/multiagent/memory_records.json)   | Hechos marcados con `MEMORIA:`                   |
| [artifacts/multiagent/agent_state.json](../artifacts/multiagent/agent_state.json)         | Estado por agente (último mensaje, menciones)    |
| [artifacts/multiagent/conversation_records.jsonl](../artifacts/multiagent/conversation_records.jsonl) | Log estructurado mensaje a mensaje               |

## 4. Desarrollos del proyecto (feature-level)

| Recurso                                   | Qué contiene                                  |
| ----------------------------------------- | --------------------------------------------- |
| [devlog/DEVLOG.md](../devlog/DEVLOG.md)   | Log append-only de desarrollos por hito       |
| `python tools/devlog.py view --limit 20`  | Últimas 20 entradas desde CLI                 |

Obligatorio: entrada tras `✅ CERRADO`, `MEMORIA:` operativa, feature completada, `BLOQUEO:` / `UNBLOCKED`, o `REVERT`.

## 5. Artefactos operativos

| Recurso                                             | Qué contiene                                     |
| --------------------------------------------------- | ------------------------------------------------ |
| [artifacts/sprints/](../artifacts/sprints/)         | Planes y runtime de sprints multiagente          |
| [artifacts/inx/](../artifacts/inx/)                 | Logs diarios de sync INX-ENLACES                 |
| [artifacts/imports/](../artifacts/imports/)         | Staging local de importaciones manuales (p. ej. Google Keep Takeout) |
| [artifacts/daily/](../artifacts/daily/)             | Timeline agregada por día (regenerable con `python tools/timeline.py`) |
| [artifacts/ptn_log_state.json](../artifacts/ptn_log_state.json)         | Estado última sync PTN                           |
| [artifacts/obsidian_log_state.json](../artifacts/obsidian_log_state.json) | Estado última sync Obsidian                      |

**Vista temporal:** `python tools/timeline.py [--date YYYY-MM-DD | --from ... --to ... | --days N]` agrega chat + devlog + INX + sprints de un rango de fechas a `artifacts/daily/YYYY-MM-DD.md`. Solo lectura sobre las fuentes canónicas; no las modifica.

## 6. Documentación de usuario

| Recurso                                                           | Qué contiene                                |
| ----------------------------------------------------------------- | ------------------------------------------- |
| [docs/pipeline-atlas.md](../docs/pipeline-atlas.md)               | **Mapa completo del pipeline** (Mermaid por capa, links a casos) |
| [docs/guia-rapida.md](../docs/guia-rapida.md)                     | Quick start de todos los sistemas           |
| [docs/multiagent-system.md](../docs/multiagent-system.md)         | Arquitectura Scrum interna                  |
| [docs/abc-taxonomy.md](../docs/abc-taxonomy.md)                   | Taxonomía ABC de referencia                 |
| [docs/todoist-agent.md](../docs/todoist-agent.md)                 | MAR — guía del agente Todoist               |
| [docs/notion-ptn-agent.md](../docs/notion-ptn-agent.md)           | PTN — guía del agente Notion proyectos      |
| [docs/notion-kit-agent.md](../docs/notion-kit-agent.md)           | KIT — guía del catálogo de conocimiento     |
| [docs/inoreader-agent.md](../docs/inoreader-agent.md)             | Inoreader → KIT — fuente externa de Information (API + JSON feed) |
| [docs/git-agent.md](../docs/git-agent.md)                         | GIT — guía del agente GitHub                |
| [docs/bib-agent.md](../docs/bib-agent.md)                         | BIB — guía del agente bibliográfico         |
| [docs/obsidian-agent.md](../docs/obsidian-agent.md)               | ABGD — guía del agente Obsidian             |
| [docs/extract-portable-toolkit.md](../docs/extract-portable-toolkit.md) | Cómo exportar herramientas agnósticas      |
| [docs/casos-de-uso/](../docs/casos-de-uso/)                       | Workflows paso a paso                       |
| [bookdown/](../bookdown/)                                           | Manual navegable y validable del proyecto   |
| [playbooks/](../playbooks/)                                       | Metodologías reutilizables extraídas de trabajos cerrados |
| [playbooks/PROTOCOLO_INICIO_CIERRE_SESION.md](../playbooks/PROTOCOLO_INICIO_CIERRE_SESION.md) | Protocolo portable para inicio, continuación y cierre de sesión |

## 7. Arranque y entorno

| Recurso                                       | Qué contiene                                   |
| --------------------------------------------- | ---------------------------------------------- |
| [WINDOWS_START.md](../WINDOWS_START.md)       | Arranque en Windows                            |
| [INICIAR_COWORKIA.bat](../INICIAR_COWORKIA.bat) | Lanzador completo                              |
| [.env.example](../.env.example)               | Plantilla de credenciales (Todoist, Notion, GitHub, Paperpile, Obsidian) |

---

## Orden de lectura recomendado al arrancar un agente

1. **[memory/INDEX.md](INDEX.md)** — este fichero.
2. **[memory/PURPOSE.md](PURPOSE.md)** — qué hace Coworkia.
3. **[memory/STRUCTURE.md](STRUCTURE.md)** — cómo está organizado.
4. **[memory/ROSTER.md](ROSTER.md)** — subagentes activos (si los hay).
5. **Archivo de identidad** según agente: `CLAUDE.md` | `AGENTS.md` | `.github/copilot-instructions.md`.
6. **[.claude/multiagent.md](../.claude/multiagent.md)** — protocolo compartido.
7. **Chat del día** vía `python tools/init_chat.py` → leer completo.
8. **Últimas entradas del devlog** vía `python tools/devlog.py view --limit 20`.
9. Opcional si hay pregunta sobre decisiones previas: **[artifacts/multiagent/chat_memory.md](../artifacts/multiagent/chat_memory.md)**.

---

## Mantenimiento de este índice

- Se actualiza manualmente cuando:
  - Nace un recurso MD top-level nuevo.
  - Se crea un nuevo artefacto derivado.
  - Cambia la ruta o nombre de algo referenciado.
- Cada cambio a este fichero debe dejar entrada `[DOCS]` en el devlog.
- No se actualiza para ediciones internas de un recurso ya referenciado (esas viven en el devlog).
