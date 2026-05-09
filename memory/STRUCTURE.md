# STRUCTURE — Coworkia

> Mapa de carpetas y lógica de organización. **Documento híbrido**:
> - Secciones narrativas: curadas a mano (qué vive en cada carpeta y por qué).
> - Bloque TREE al final: regenerado por `python tools/snapshot_structure.py`.
>
> Regla: si añades o renombras una carpeta top-level, actualiza la narrativa y regenera el TREE en el mismo commit. Deja entrada `[DOCS]` en el devlog.

## Principio de organización

Coworkia separa por **responsabilidad operativa**, no por tecnología:

- **Lo vivo** (hilos, logs, memoria operativa) → `chats/`, `devlog/`, `artifacts/`.
- **Lo curado** (identidad, propósito, estructura) → `memory/`, raíz (`README.md`, `CLAUDE.md`, `AGENTS.md`).
- **Lo ejecutable** (lógica del sistema) → `agents/`, `tools/`, `apps/`, `multiagents/`.
- **La documentación de uso** (guías para humanos) → `docs/`, `bookdown/`, `playbooks/`.
- **Kits portables** (artefactos listos para copiar a otros repos) → `toolkits/`.
- **Prompts y skills portables para agentes** (comandos `/` y paquetes bajo `.ai/skills/`) → `.ai/`.

## Carpetas top-level

### `agents/` — orquestación por dominio
Un módulo Python por sistema (`MAR`/`PTN`/`KIT`/`GIT`/`BIB`/`ABGD`) más el orquestador multiagente. Son las **entradas principales por dominio**: cada fichero expone un CLI (`python agents/<x>.py <cmd>`). Dependen de `tools/` para llamadas API de bajo nivel.

- `todoist_agent.py` — MAR (ejecutar).
- `notion_agent.py` — PTN (dirigir).
- `kit_agent.py` — KIT (catalogar conocimiento).
- `github_agent.py` — GIT (catalogar repos). Antes REP, alias retenido en devlog.
- `bib_agent.py` — BIB (catalogar bibliografía).
- `obsidian_agent.py` — ABGD (almacenar notas).
- `inoreader_agent.py` — fuente externa que alimenta KIT (no catálogo separado): articulos con tag `kit-import` → `NOTION_DB_KIT`. Ver `docs/inoreader-agent.md`.
- `orchestrator_agent.py` — multiagente, sprints, INX sync, memoria.

### `tools/` — wrappers de APIs y utilidades
Biblioteca de funciones reutilizables: wrappers de API por sistema (`todoist_tools.py`, `notion_tools.py`, `github_tools.py`, `paperpile_tools.py`, `obsidian_tools.py`), scripts de sync (`sync_todoist_to_notion.py`, `sync_inx_links.py`), scripts de auditoría (`log_ptn_changes.py`, `log_obsidian_changes.py`), utilidades de repo (`init_chat.py`, `devlog.py`, `snapshot_structure.py`, `fix_chat_mojibake.py`), y scripts de migración/schema (`migrate_ptn.py`, etc.).

Regla: si algo se usa desde más de un agente, va aquí. Si es de un solo dominio, vive junto a su agente.

### `apps/` — interfaces de usuario
GUIs Tkinter, dashboards interactivos, doctores de diagnóstico y lanzadores `.bat` para Windows. Consumen `agents/` y `tools/` pero no son invocadas por ellos (capa superior).

Ejemplos: `dashboard.py` (MAR diario), `project_hub_gui.*` (PTN), `github_gui.py` (GIT), `bib_gui.py` (BIB), `inx_daily.*`, `config_doctor.py`, `notion_doctor.py`, `inx_doctor.py`.

### `multiagents/` — capa de orquestación IA
Paquete Python que modela Scrum sobre el proyecto:

- `registry.py` — `SCRUM_ROLES` y `DOMAIN_AGENTS` con capacidades.
- `planner.py` — planificación de sprints.
- `models.py` — `SprintRun`, `TaskExecution`, `AgentSpec`, etc.
- `chat_memory.py` — parseo de `MEMORIA:`, `BLOQUEO:`, `SIGUIENTE:` desde chats.
- `artifacts.py` — serializa sprints y memoria a JSON/MD.
- `chat_template.md` — plantilla del chat diario.

### `chats/` — hilo compartido diario
Un fichero por día (`chat_YYYY-MM-DD.md`). Append-only, UTF-8 estricto. Fuente de verdad de la conversación multiagente. Generado/resuelto por `tools/init_chat.py`.

### `devlog/` — log feature-level append-only
`DEVLOG.md` narrativo con entradas por hito (no por commit). Escrito vía `tools/devlog.py`. Obligatorio para todo agente cuando cierra decisión, completa feature, marca bloqueo, etc. Ver `.claude/multiagent.md` sección "DevLog obligatorio".

### `memory/` — memoria curada del proyecto
Esta carpeta. Contiene los MDs de alto nivel que definen al proyecto frente a cualquier agente nuevo:

- `PURPOSE.md` — qué es y qué hace (curado).
- `STRUCTURE.md` — este mapa (híbrido).
- `INDEX.md` — meta-índice de todos los recursos (curado, se actualiza cuando nace un recurso nuevo).
- `ROSTER.md` — directorio curado de subagentes (`Root/Sub`) activos y su foco. Se edita a mano cuando David activa o retira un subagente; cada cambio deja entrada `[DOCS]` en el devlog.
- `SNAPSHOT.md` — agregado auto-generado de `MEMORIA:` / `BLOQUEO:` / `SIGUIENTE:` (no editar).

### `artifacts/` — salidas operativas (regenerables)
Todo lo derivado que se regenera desde fuentes:

- `artifacts/multiagent/` — memoria multiagente derivada (`conversation_records.jsonl`, `decision_log.json`, `agent_state.json`, `memory_records.json`, `chat_memory.md`). Regenerable con `python agents/orchestrator_agent.py sync-chat-memory`.
- `artifacts/inx/` — logs diarios de INX-ENLACES (`inx-daily-YYYYMMDD-HHMMSS.md`).
- `artifacts/imports/` — staging local para importaciones manuales hacia el sistema (por ahora Google Keep Takeout para poblar KIT). No es fuente de verdad; solo input operativo local.
- `artifacts/sprints/` — planes y runtime de sprints (`sprint-*.md`, `sprint-*-runtime.json`, `sprint-*-sync.json`).
- `artifacts/ptn_log_state.json`, `artifacts/obsidian_log_state.json` — estados de última sync para detección de cambios.

### `docs/` — documentación de usuario
Guías para humanos. No es memoria del sistema.

- `guia-rapida.md` — quick start.
- `todoist-agent.md`, `notion-ptn-agent.md`, `notion-kit-agent.md`, `git-agent.md`, `bib-agent.md`, `obsidian-agent.md` — una guía por agente.
- `multiagent-system.md` — arquitectura Scrum interna.
- `abc-taxonomy.md` — referencia de la taxonomía ABC.
- `extract-portable-toolkit.md` — exportar herramientas agnósticas.
- `casos-de-uso/` — workflows paso a paso.

### `bookdown/` — manual navegable y validable
Manual operativo del proyecto en formato bookdown ligero. Usa `_bookdown.yml` como fuente canónica del orden de capítulos, `.Rmd` como fuentes del manual y `generate_static_html.py` / `validate_static_html.py` para generar y auditar el HTML local en `bookdown/_book/index.html`.

Regla: si cambia un flujo, script, carpeta o test relevante, actualizar el capítulo y la tabla maestra correspondiente en el mismo bloque de trabajo.

### `playbooks/` — metodologías reutilizables
Guías operativas extraídas de trabajos ya ejecutados en otros proyectos o frentes. No son memoria canónica de Coworkia ni documentación de usuario por sistema; son patrones transferibles que pueden aplicarse a proyectos futuros.

- `bookdown-exhaustive-project-playbook.md` — método para crear un bookdown exhaustivo, navegable y validable de un proyecto complejo.
- `PROTOCOLO_INICIO_CIERRE_SESION.md` — protocolo portable para interpretar `inicia sesión`, `sigue` y `cierra sesión`; en Coworkia se adapta con `tools/session_protocol.py` respetando memoria, chat y devlog.
- `playbooks-readme-portable-playbook.md` — método para crear y mantener un índice `playbooks/README.md` portable en cualquier repo.

### `toolkits/` — kits portables (ZIP + prompts)
Artefactos empaquetados para **reutilizar en otros proyectos** sin acoplarlos al núcleo de Coworkia: ZIPs de kits (MCP, multiagente, comandos, etc.) y prompts de integración en markdown. No son código ejecutado por el repo salvo que los copies explícitamente a otro sitio.

### `.ai/` — comandos `/` y skills portables para agentes
- **Comandos**: Markdown bajo `.ai/commands/` e invocaciones tipo `/<comando> ...`; índice en `.ai/COMMANDS.md`. Debe mantenerse en la **raíz** del repo (no dentro de `src/` u otras carpetas).
- **Skills**: paquetes completos bajo `.ai/skills/` (p. ej. `.ai/skills/obsidian-skills/` con su carpeta interna `skills/<nombre>/SKILL.md`). No aplastar la estructura del paquete copiando solo los `SKILL.md` sueltos a `.ai/skills/`.

### `.claude/`, `.cursor/`, `.github/`
Protocolo y configuración de agentes:

- `.claude/multiagent.md` — protocolo compartido (append-only, formatos, marcadores, devlog obligatorio).
- `.claude/hooks/`, `.claude/settings.local.json` — config local de Claude Code.
- `.cursor/rules/` — reglas persistentes de Cursor para complementar (sin contradecir) la memoria versionada y los archivos de identidad.
- `.github/copilot-instructions.md` — identidad/protocolo para Copilot.

### Raíz
- `README.md` — guía pública del proyecto.
- `CLAUDE.md` — identidad y rol para Claude.
- `AGENTS.md` — identidad y rol para Codex.
- `WINDOWS_START.md`, `INICIAR_COWORKIA.bat` — arranque en Windows.
- `.env.example` — plantilla de credenciales.

### `Sistemas/`
Documentación de referencia y repositorios externos no-ejecutables (material de apoyo).

## Reglas de crecimiento

1. **Nuevo agente de dominio** → fichero en `agents/`, wrapper API en `tools/`, guía en `docs/<agente>.md`, referencia en `memory/PURPOSE.md` y `memory/INDEX.md`, regenerar `STRUCTURE.md` TREE.
2. **Nueva utilidad transversal** → en `tools/`, sin GUI salvo que realmente la requiera.
3. **Nueva GUI** → en `apps/`, consumiendo `agents/`+`tools/`.
4. **Nuevo MD top-level en raíz** → actualizar `memory/INDEX.md` y `memory/STRUCTURE.md`.
5. **Nuevo tipo de artefacto derivado** → bajo `artifacts/<nombre>/`, documentar qué script lo regenera.
6. **Nuevo playbook reutilizable** → bajo `playbooks/`, con propósito, fuentes, criterios de cierre y referencia en `memory/INDEX.md` si inaugura una nueva familia.
7. **Nuevo capítulo bookdown** → añadir `.Rmd`, actualizar `bookdown/_bookdown.yml`, regenerar HTML y validar con `bookdown/validate_static_html.py`.

## Árbol actual

<!-- TREE:START -->

_Auto-generado por `tools/snapshot_structure.py` @ 2026-05-09T16:33Z. No editar a mano dentro de este bloque._

```
- .ai/
  - commands/
    - architecture.md
    - base.md
    - canvas.md
    - debug.md
    - decision.md
    - deep-think.md
    - docs.md
    - handoff.md
    - obsidian.md
    - plan.md
    - refactor.md
    - research.md
    - review.md
    - security.md
    - test.md
    - think.md
    - vault.md
  - skills/
    - obsidian-skills/
  - COMMANDS.md
  - README.md
- .claude/
  - multiagent.md
  - settings.local.json
- .cursor/
  - rules/
    - 00-priority.mdc
    - 10-ai-commands-skills.mdc
    - 20-docs-memory-devlog.mdc
    - 30-strict-quality-gates.mdc
- .github/
  - copilot-instructions.md
- agents/
  - bib_agent.py
  - github_agent.py
  - inoreader_agent.py
  - kit_agent.py
  - notion_agent.py
  - obsidian_agent.py
  - orchestrator_agent.py
  - todoist_agent.py
- apps/
  - abrir_sesion.bat
  - abrir_sesion_1password.bat
  - backs_notion.py
  - backs_obsidian.py
  - backs_todoist.py
  - bib_gui.py
  - catalogar_repos.py
  - cerrar_sesion.bat
  - cerrar_sesion_1password.bat
  - close_obsidian_checkboxes_to_todoist.bat
  - config_doctor.bat
  - config_doctor.py
  - dashboard.bat
  - dashboard.py
  - ensure_todoist_tasks_schema.bat
  - export_zinbox.py
  - generar_env_desde_json.bat
  - github_gui.py
  - inx_daily.bat
  - inx_daily.py
  - inx_doctor.bat
  - inx_doctor.py
  - inx_sync_notion.bat
  - inx_sync_obsidian.bat
  - inx_sync_todoist.bat
  - log_ptn_changes.bat
  - mar_check.bat
  - mar_doctor.bat
  - mar_doctor.py
  - notion_doctor.bat
  - notion_doctor.py
  - pipeline_gui.bat
  - pipeline_gui.py
  - project_hub_gui.bat
  - project_hub_gui.py
  - promote_bib_to_obsidian.bat
  - promote_notas_checkboxes_to_todoist.bat
  - promote_obsidian_to_ptn.bat
  - reset_all.bat
  - reset_mar.bat
  - ... (15 mas)
- artifacts/
  - daily/
    - 2026-04-17.md
    - 2026-04-18.md
    - 2026-04-19.md
    - 2026-05-09.md
  - imports/
    - google_keep/
    - README.md
  - inx/
    - inx-daily-20260417-072710.md
  - multiagent/
    - agent_state.json
    - chat_memory.md
    - chat_memory_snapshot.json
    - conversation_records.jsonl
    - decision_log.json
    - memory_records.json
  - resets/
    - 2026-04-19/
    - 2026-05-09/
  - sprints/
    - sprint-multiagent-1.md
    - sprint-multiagent-2.json
    - sprint-multiagent-2.md
    - sprint-multiagent-runtime.json
    - sprint-multiagent-runtime.md
    - sprint-multiagent-sync.json
    - sprint-multiagent-sync.md
  - obsidian_log_state.json
  - ptn_log_state.json
- bookdown/
  - 01-instalacion-y-arranque.Rmd
  - 02-arquitectura-operativa.Rmd
  - 03-pipelines-principales.Rmd
  - 04-catalogos-maestros.Rmd
  - 05-operacion-validacion-y-mantenimiento.Rmd
  - 06-faq-y-glosario.Rmd
  - 07-sistemas-y-agentes.Rmd
  - 08-tabla-maestra-scripts.Rmd
  - 09-casos-de-uso.Rmd
  - 10-validacion-y-acceptance.Rmd
  - 11-inx-arquitectura.Rmd
  - 12-notion-abc-fuentes-de-verdad.Rmd
  - 13-coordinacion-multiagente.Rmd
  - 14-operacion-windows-resets-backups.Rmd
  - 15-catalogo-documentacion.Rmd
  - 16-roadmap-limitaciones.Rmd
  - 17-matriz-cobertura-release.Rmd
  - _bookdown.yml
  - generate_static_html.py
  - index.Rmd
  - README.md
  - validate_static_html.py
- chats/
  - chat_2026-04-17.md
  - chat_2026-04-18.md
  - chat_2026-04-19.md
  - chat_2026-04-21.md
  - chat_2026-04-22.md
  - chat_2026-04-23.md
  - chat_2026-04-24.md
  - chat_2026-04-25.md
  - chat_2026-04-26.md
  - chat_2026-04-27.md
  - chat_2026-04-29.md
  - chat_2026-05-05.md
  - chat_2026-05-06.md
  - chat_2026-05-09.md
  - chat_archive_2026-04-17.md
- config/
  - env.1password.example
  - secrets.1p.json
  - secrets.1p.json.example
- devlog/
  - DEVLOG.md
- docs/
  - casos-de-uso/
    - 00-template.md
    - 01-captura-todoist-zinbox.md
    - 02-tarea-a-proyecto-ptn-con-inx.md
    - 03-nota-obsidian-desde-ptn.md
    - 04-sync-diario-inx.md
    - 05-git-enlazado-a-ptn.md
    - 06-paperpile-bib-enlazado.md
    - 07-promocion-obsidian-a-ptn.md
    - 08-kit-en-inx.md
    - 09-bib-a-obsidian.md
    - 10-checkboxes-obsidian-a-todoist.md
    - 11-journal-diario-en-timeline.md
    - 12-backfill-inx-historico.md
    - 13-wikilinks-cross-system.md
    - 14-reset-sistema.md
    - 15-inoreader-a-kit.md
    - index.md
  - abc-taxonomy.md
  - bib-agent.md
  - extract-portable-toolkit.md
  - git-agent.md
  - guia-rapida.md
  - inoreader-agent.md
  - multiagent-system.md
  - notion-kit-agent.md
  - notion-ptn-agent.md
  - obsidian-agent.md
  - pipeline-atlas.md
  - todoist-agent.md
- memory/
  - INDEX.md
  - PURPOSE.md
  - ROSTER.md
  - SNAPSHOT.md
  - STRUCTURE.md
- multiagents/
  - __init__.py
  - artifacts.py
  - chat_memory.py
  - chat_template.md
  - models.py
  - multiagent-system.md
  - planner.py
  - registry.py
- playbooks/
  - bookdown-exhaustive-project-playbook.md
  - cursor-global-rules-portable-playbook.md
  - extract-portable-toolkit.md
  - iterative-multi-agent-review-playbook.md
  - meta-methodology-extracting-playbooks-from-projects.md
  - methodology-systematic-research-with-AI-agents.md
  - playbooks-readme-portable-playbook.md
  - protocol-playbook-for-any-command.md
  - PROTOCOLO_INICIO_CIERRE_SESION.md
  - README.md
  - secure-env-secrets-portable-playbook.md
- Sistemas/
  - ABC/
    - ABC 2a5622cf315b8044a83feb2033f661d1_ABC-AREA 2a5622cf315b813faa22000be68a3416.csv
    - ABC 2a5622cf315b8044a83feb2033f661d1_ABC-AREA 2a5622cf315b813faa22000be68a3416_all.csv
    - ABC 2a5622cf315b8044a83feb2033f661d1_ABC-BLOQUE 2a5622cf315b803ca9f0000bd4fbd157_all.csv
    - ABC 2a5622cf315b8044a83feb2033f661d1_ABC-CONTEXTO 2a5622cf315b8018919f000bbe9adc05_all.csv
    - B0B-ABC 117622cf315b80229da5c5ac1de348b4.md
  - DMS-main/
    - config/
    - docs/
    - ejemplos/
    - src/
    - templates/
    - demo-doc.md
    - README.md
    - requirements.txt
  - Sistema_ABGD-main/
    - .claude/
    - Sistema_ABGD/
    - actualizar_github.bat
    - actualizar_github.ps1
    - BETA_NUEVA_ESTRUCTURA.md
    - beta_test.txt
    - CAMBIOS_IMPLEMENTADOS.md
    - DELTA_FINAL_4x4.md
    - DELTA_NUEVA_ESTRUCTURA.md
    - generar_estructura_abgd.py
    - GUIA_ACTUALIZAR_GITHUB.md
    - GUIA_RAPIDA_INICIO.md
    - Instrucciones_Claude_Code_ABGD.md
    - requirements.txt
    - RESULTADO_GENERACION.md
    - Sistema_ABC_Completo_Final.xlsx
    - Sistema_ABGD_Documentacion_Completa.md
  - systec-main/
    - .github/
    - docs/
    - MAR_EXPORTS/
    - model/
    - DEPLOY.md
    - LICENSE
    - mkdocs.yml
    - netlify.toml
    - PUBLICAR.md
    - README.md
    - requirements.txt
    - vercel.json
- tests/
  - test_bookdown_static_html.py
  - test_session_protocol.py
  - test_todoist_tools.py
- toolkits/
  - ai_commands_starter_kit.zip
  - consensus-mcp-kit.zip
  - inoreader-mcp-kit.zip
  - multiagent-toolkit.zip
  - obsidian-skills-main.zip
  - prompt_integracion_consensus_mcp_kit.md
  - prompt_integracion_inoreader_mcp_kit.md
  - prompt_integracion_multiagent_toolkit.md
  - promt_integracion_obsidian-skills-kit.md
  - promt_integration_commands-kit.md
- tools/
  - backfill_obsidian_to_inx.py
  - cleanup_notas_legacy_props.py
  - close_obsidian_checkboxes_to_todoist.py
  - create_abc_taxonomy_dbs.py
  - create_inx_links_db.py
  - dedupe_abc_taxonomy.py
  - dedupe_notion_db.py
  - devlog.py
  - enable_ptn_relations.py
  - ensure_archivo_field.py
  - ensure_inx_completed_status.py
  - ensure_inx_paperpile_citekey_field.py
  - ensure_kit_cross_fields.py
  - ensure_kit_external_fields.py
  - ensure_todoist_tasks_schema.py
  - env_utils.py
  - find_notion_page.py
  - fix_chat_mojibake.py
  - generate_env_from_json.py
  - github_tools.py
  - google_keep_tools.py
  - import_abc_taxonomy.py
  - import_inoreader_articles.py
  - import_keep_remaining.py
  - init_chat.py
  - inoreader_oauth.py
  - inoreader_tools.py
  - list_notion_children.py
  - log_obsidian_changes.py
  - log_ptn_changes.py
  - memory_check.py
  - migrate_database.py
  - migrate_notas_ptn_relations.py
  - migrate_notas_ruta_obsidian.py
  - migrate_ptn.py
  - notion_tools.py
  - obsidian_tools.py
  - obsidian_wikilinks.py
  - paperpile_tools.py
  - promote_bib_to_obsidian.py
  - ... (30 mas)
- .env.example
- AGENTS.md
- CLAUDE.md
- INICIAR_COWORKIA.bat
- INICIAR_COWORKIA_1PASSWORD.bat
- Notion
- README.md
- requirements.txt
- WINDOWS_START.md
```

<!-- TREE:END -->
