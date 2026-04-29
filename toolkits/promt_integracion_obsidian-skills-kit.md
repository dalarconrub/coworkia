# Prompt: Integrar `obsidian-skills` (paquete completo) en un repo

Quiero que integres `obsidian-skills` como paquete portable dentro de este repositorio.

## 1. Objetivo

Dejar disponible el paquete completo para que los agentes puedan activar skills de:

- Markdown de Obsidian
- Wikilinks, embeds, callouts y properties/frontmatter
- Obsidian Bases (`.base`)
- JSON Canvas (`.canvas`)
- Vault/CLI y tareas relacionadas
- Defuddle (cuando aplique)

## 2. Regla principal (no negociable)

**No copies solo la subcarpeta `skills/`.**

Debe conservarse el paquete completo en una carpeta contenedora:

```text
.ai/skills/obsidian-skills/
```

Estructura mínima esperada:

```text
mi-repo/
├── .ai/
│   └── skills/
│       └── obsidian-skills/
│           ├── README.md
│           ├── LICENSE
│           ├── .claude-plugin/
│           └── skills/
│               ├── obsidian-markdown/
│               ├── obsidian-bases/
│               ├── json-canvas/
│               ├── obsidian-cli/
│               └── defuddle/
└── ...
```

Ruta clave:

```text
.ai/skills/obsidian-skills/skills/<nombre-skill>/SKILL.md
```

## 3. Instalación desde ZIP (robusta)

1. Descomprime el ZIP (p. ej. `obsidian-skills-main.zip`).
2. Si el ZIP trae carpeta raíz `obsidian-skills-main/`, muévela/renómbrala a:

```text
.ai/skills/obsidian-skills/
```

3. Verifica que existan al menos estas rutas:

```text
.ai/skills/obsidian-skills/skills/obsidian-markdown/SKILL.md
.ai/skills/obsidian-skills/skills/obsidian-bases/SKILL.md
.ai/skills/obsidian-skills/skills/json-canvas/SKILL.md
.ai/skills/obsidian-skills/skills/obsidian-cli/SKILL.md
.ai/skills/obsidian-skills/skills/defuddle/SKILL.md
```

4. Verifica que `.gitignore` no esté excluyendo `.ai/skills/`.

No hacer esto:

```text
.ai/skills/obsidian-markdown/
.ai/skills/obsidian-bases/
.ai/skills/json-canvas/
```

porque rompe la estructura portable del paquete.

## 4. Regla global para agentes

Añade/actualiza una regla de uso en los archivos de instrucciones del repo (por ejemplo `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursor/rules/*` si existe):

```md
## Uso de skills portables (`.ai/skills`)

Este repo incluye paquetes de skills bajo `.ai/skills/`. Cada paquete se conserva **completo** (no mover solo `skills/` al nivel superior).

Paquete `obsidian-skills`: `.ai/skills/obsidian-skills/`.
Cada skill en `.ai/skills/obsidian-skills/skills/<nombre>/SKILL.md`.

Rutas principales:

- `.ai/skills/obsidian-skills/skills/obsidian-markdown/SKILL.md`
- `.ai/skills/obsidian-skills/skills/obsidian-bases/SKILL.md`
- `.ai/skills/obsidian-skills/skills/json-canvas/SKILL.md`
- `.ai/skills/obsidian-skills/skills/obsidian-cli/SKILL.md`
- `.ai/skills/obsidian-skills/skills/defuddle/SKILL.md`

Cuando la tarea encaje con una skill, el agente debe leer ese `SKILL.md` antes de crear/modificar/revisar archivos.
Si no hay skill adecuada, seguir reglas generales del repo.
```

## 5. Activación recomendada por contexto

| Contexto | Skill |
|---|---|
| Notas markdown, wikilinks, embeds, callouts, properties | `obsidian-markdown` |
| Archivos `.base` | `obsidian-bases` |
| Archivos `.canvas` | `json-canvas` |
| Vault por CLI, plugins/temas (si aplica) | `obsidian-cli` |
| Flujo de lectura/limpieza HTML compatible | `defuddle` |

## 6. Integración opcional con comandos `/`

Si el repo usa `.ai/commands`, añade wrappers:

```text
.ai/commands/obsidian.md
.ai/commands/base.md
.ai/commands/canvas.md
.ai/commands/vault.md
```

y actualiza `.ai/COMMANDS.md` para incluirlos.

Cada wrapper debe forzar la carga previa de su `SKILL.md` correspondiente.

## 7. Documentación y memoria del repo (si aplica)

Si el proyecto mantiene documentación interna de estructura/memoria:

1. Añade referencia a `.ai/skills/obsidian-skills` en `README.md`.
2. Añade/actualiza entradas en índices de memoria (p. ej. `memory/INDEX.md`).
3. Si hay mapa de estructura con bloque TREE auto-generado, regénéralo.
4. Si el script de snapshot excluye carpetas ocultas (`.`), verifica que no oculte `.ai/`.
5. Registra el cambio en devlog/changelog del repo.

## 8. Criterio de aceptación (checklist)

- [ ] `obsidian-skills` existe en `.ai/skills/obsidian-skills/` como paquete completo.
- [ ] Están presentes `obsidian-markdown`, `obsidian-bases`, `json-canvas`, `obsidian-cli`, `defuddle`.
- [ ] Hay regla global de uso de skills en archivos de agentes del repo.
- [ ] (Si existe `.ai/commands`) wrappers creados y listados en `.ai/COMMANDS.md`.
- [ ] README/memory/estructura actualizados si el repo usa esos documentos.
- [ ] No se modificó código funcional innecesariamente.

## 9. Objetivo final

Que cualquier agente pueda detectar tareas relacionadas con Obsidian y activar automáticamente la skill correcta, manteniendo `obsidian-skills` portable y mantenible dentro del repo.

Referencia upstream: [kepano/obsidian-skills](https://github.com/kepano/obsidian-skills).
