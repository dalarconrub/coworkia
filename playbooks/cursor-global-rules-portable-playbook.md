# Playbook portable — Reglas globales de Cursor para cualquier repo

**Fecha:** 2026-04-29  
**Propósito:** definir un método reusable para crear, validar e integrar reglas globales de Cursor (`.cursor/rules/*.mdc`) en cualquier ordenador y cualquier repositorio, sin acoplarse a una base de código específica.  
**Aplicabilidad:** proyectos personales, equipos pequeños, repos mono-repo o multi-repo, con o sin sistema multiagente.

---

## 0. Por qué existe este playbook

Las reglas globales de Cursor evitan repetir instrucciones operativas en cada chat y reducen desviaciones de estilo/proceso.  
El problema habitual no es "crear una regla", sino mantener una configuración que:

- sea portable entre máquinas;
- no contradiga la gobernanza existente (`AGENTS.md`, `CLAUDE.md`, etc.);
- siga siendo mantenible cuando el repo evoluciona.

Este playbook resuelve ese problema con un pipeline estándar.

---

## 1. Cuándo usarlo

### 1.1 Triggers correctos

Usa este playbook cuando:

1. Arrancas un repo nuevo y quieres una base de comportamiento consistente en Cursor.
2. Detectas instrucciones repetidas en chats (síntoma de falta de reglas persistentes).
3. Integras sistemas portables (`.ai/commands`, `.ai/skills`) y necesitas activación consistente.
4. Quieres homogeneizar comportamiento entre varios ordenadores.

### 1.2 Cuándo NO usarlo

- Si el repo aún no tiene convenciones mínimas definidas.
- Si buscas resolver un bug puntual (no mezclar con diseño de reglas).
- Si no puedes versionar cambios de documentación/memoria.

---

## 2. Prerrequisitos

Antes de crear reglas:

1. Identifica las fuentes de verdad del repo (por ejemplo: `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `memory/*`).
2. Verifica si `.cursor/rules/` ya existe.
3. Define alcance: reglas globales (`alwaysApply: true`) o por patrones (`globs`).
4. Acordar precedencia para evitar conflictos.

Regla clave: **las reglas de Cursor complementan, no sustituyen, la gobernanza versionada del repo**.

---

## 3. Unidad de trabajo y estructura recomendada

Usa varias reglas pequeñas en lugar de una regla gigante:

```text
.cursor/rules/
  00-priority.mdc
  10-ai-commands-skills.mdc
  20-docs-memory-devlog.mdc
  30-strict-quality-gates.mdc
```

Convención:

- `00-*`: precedencia y límites.
- `10-*`: flujo operativo principal (commands, skills, herramientas).
- `20-*`: higiene documental (README/memory/devlog/tests si aplica).
- `30-*`: gates de calidad y cierre estricto (validación + trazabilidad).

---

## 4. Formato estándar de regla `.mdc`

Cada archivo debe incluir frontmatter YAML:

```md
---
description: Qué hace esta regla
alwaysApply: true
---
```

Para reglas no globales:

```md
---
description: Convenciones para Python
globs: **/*.py
alwaysApply: false
---
```

Buenas prácticas:

- una regla = una responsabilidad;
- texto corto, accionable y verificable;
- evitar duplicar párrafos completos de otros archivos de identidad.

---

## 5. Pipeline de implementación (7 pasos)

### Paso 1 — Inventario de gobernanza actual

Lista archivos que ya dictan comportamiento de agentes y documentación viva.

### Paso 2 — Diseñar mapa de reglas mínimas

Define 2-4 reglas con roles claros (precedencia, operación, higiene).

### Paso 3 — Crear `.cursor/rules/*.mdc`

Escribe reglas con frontmatter válido y lenguaje operativo.

### Paso 4 — Integración con convenciones portables

Si existe `.ai/commands` y/o `.ai/skills`, añade reglas explícitas de activación y fallback.

### Paso 5 — Sincronizar documentación del repo

Si el repositorio mantiene índice/estructura:

- actualizar `playbooks/README.md` si nace un nuevo playbook;
- actualizar memoria estructural cuando proceda;
- regenerar snapshots de árbol si aplica.

### Paso 6 — Verificar consistencia

Checklist rápida:

- no contradicción con archivos de identidad;
- rutas existentes;
- nomenclatura consistente;
- sin reglas redundantes.

### Paso 7 — Registrar trazabilidad

Añade entrada al devlog/changelog con alcance y decisión operativa.

---

## 6. Plantillas copy-paste

### 6.1 Regla de precedencia

```md
---
description: Precedencia de fuentes y alcance
alwaysApply: true
---

# Precedencia

- Complementar archivos de identidad; no contradecirlos.
- Ante conflicto, prevalece la memoria versionada y la gobernanza principal.
```

### 6.2 Regla de commands/skills

```md
---
description: Activación de /commands y skills
alwaysApply: true
---

# Commands y skills

- Si mensaje inicia con `/`, resolver `.ai/commands/<comando>.md`.
- Si no existe, listar desde `.ai/COMMANDS.md`.
- Para tareas de dominio con skills, leer `SKILL.md` antes de editar.
```

### 6.3 Regla de higiene documental

```md
---
description: Coherencia docs/memory/devlog
alwaysApply: true
---

# Coherencia

- Al cambiar estructura o protocolo, actualizar índice/estructura del repo si existen.
- Regenerar snapshot de árbol cuando exista script oficial.
- Registrar cambio en devlog/changelog.
```

### 6.4 Regla de quality gates estrictos

```md
---
description: Gates estrictos de calidad para commits/docs/tests
alwaysApply: true
---

# Strict quality gates

- No cerrar cambios de código sin validación relevante o explicación explícita de limitación.
- Reportar qué se verificó y qué riesgo residual queda.
- No hacer commit/push sin petición explícita del usuario.
- Si hay cambios estructurales/protocolares, actualizar documentación correspondiente.
```

---

## 7. Integración portable en cualquier ordenador

Para mover esta configuración entre máquinas:

1. Versiona `.cursor/rules/` dentro del repo.
2. Mantén rutas relativas (no absolutas del sistema operativo).
3. Evita dependencias a rutas locales de usuario.
4. Documenta prerequisitos mínimos de Cursor en `README` o en este playbook.

Si hay diferencias OS:

- usa comandos equivalentes por plataforma en ejemplos;
- evita sintaxis shell no portable dentro de las reglas.

---

## 8. Anti-patrones

1. **Regla monolítica** de cientos de líneas con temas mezclados.
2. **Contradicción directa** con `AGENTS.md`/`CLAUDE.md`.
3. **Copiar-pegar literal** toda la gobernanza dentro de `.cursor/rules/`.
4. **Reglas sin trazabilidad** (sin actualizar docs ni devlog).
5. **Acoplamiento local** (rutas de usuario o supuestos de una máquina).
6. **Falso cierre**: declarar "hecho" sin checks ni riesgos residuales.

---

## 9. Criterios de cierre (Definition of Done)

- `.cursor/rules/` existe y contiene reglas enfocadas.
- Todas las reglas tienen frontmatter válido (`description`, `alwaysApply`/`globs`).
- No hay conflicto con la gobernanza existente.
- Documentación de playbooks/memoria actualizada si aplica.
- Cambio registrado en devlog/changelog.
- Para cambios de código, hay evidencia de validación o limitación declarada.

---

## 10. Mantenimiento evolutivo

Versionado recomendado:

- v1.0: baseline global;
- v1.1+: ajustes de redacción/alcance;
- v2.0: rediseño estructural (nuevas áreas o integración multi-repo).

Revisión sugerida:

- mensual en repos activos;
- tras cada cambio relevante de protocolo de agentes.

Deprecaciones:

- no borrar reglas sin contexto;
- marcar reemplazo y motivo en commit + devlog.

---

## 11. Receta rápida (comandos)

```bash
# 1) Crear carpeta de reglas
mkdir -p .cursor/rules

# 2) Crear archivos base
# 00-priority.mdc
# 10-ai-commands-skills.mdc
# 20-docs-memory-devlog.mdc
# 30-strict-quality-gates.mdc

# 3) Validar coherencia manual con archivos de identidad del repo

# 4) Actualizar playbooks/README.md si creaste un playbook nuevo

# 5) Registrar en devlog/changelog
```

---

## 12. Principio final

> Reglas globales eficaces no son "más texto": son una capa mínima, portable y coherente que reduce fricción y preserva decisiones operativas entre sesiones, máquinas y repositorios.

---

## Provenance

- Integración real en Coworkia de `.cursor/rules` con reglas globales (precedencia, commands/skills, docs/devlog).
- Patrón estructural basado en `playbooks/meta-methodology-extracting-playbooks-from-projects.md`.
