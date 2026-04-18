# ROSTER — Subagentes del sistema multiagente

> Directorio curado de **subagentes** activos. Los subagentes son variantes especializadas de un agente raíz (Claude / Copilot / Codex) que heredan su protocolo pero se centran en un dominio o tarea concreta.
>
> - Raíces (siempre presentes): `Claude`, `Copilot`, `Codex`.
> - Subagentes: notación `Root/Sub` (ej. `Claude/KIT`, `Codex/INX`).
> - `Sub`: letras, dígitos, `_`, `-`. Sin espacios.
> - `Root` fija el protocolo de respuesta y la especialidad base; `Sub` delimita el foco.
>
> Regla: un subagente solo aparece aquí cuando David lo activa en un chat o cuando una raíz lo propone y queda confirmado con `✅ CERRADO`. Este fichero **no se autogenera**.

## Cómo se invoca un subagente

En el chat del día:

```md
**David [@Claude/KIT]:** revisa si KIT necesita nueva area.
**Claude/KIT:** ...
```

O mediante mención lateral:

```md
**Copilot:** @Codex/INX ¿tienes el último estado de sync?
```

`tools/init_chat.py`, `multiagents/chat_memory.py` y `tools/devlog.py` aceptan `Root/Sub` como identidad de primera clase (mismo `MENTION_RE`, mismo `VALID_AGENTS`).

## Directorio activo

| Subagente | Raíz | Dominio / foco | Cuándo invocar | Activado en |
| --------- | ---- | -------------- | -------------- | ----------- |
| _ninguno_ |      |                |                |             |

> Añadir una fila cuando David confirme la activación (o tras `✅ CERRADO` que lo cree). Incluir el chat del día donde se activó (`chat_YYYY-MM-DD.md`).

### Plantilla de fila

```md
| Claude/KIT | Claude | curaduría del catálogo KIT (Notion) | auditorías de taxonomía, dedupe de entradas, revisión de relaciones | chat_YYYY-MM-DD.md |
```

## Reglas operativas

1. **Herencia de protocolo**: un subagente sigue el protocolo de su raíz (`CLAUDE.md` / `AGENTS.md` / `.github/copilot-instructions.md`) y `.claude/multiagent.md`. No redefine reglas base.
2. **Foco declarado**: cada subagente tiene un dominio o tarea explícita en la tabla. Si la conversación se sale de su foco, hace handoff a la raíz o a otro subagente con `SIGUIENTE: @Root`.
3. **No duplica a la raíz**: si una pregunta cabe en la raíz, la raíz responde directamente. Los subagentes son para cuando el foco es lo suficientemente nítido como para beneficiarse de contexto especializado.
4. **Memoria y devlog**: `MEMORIA:`, `BLOQUEO:`, `SIGUIENTE:` funcionan igual. En `devlog.py`, usar `--agent Claude/KIT` para atribuir correctamente.
5. **Retirada**: si un subagente deja de tener uso, se mueve a la sección "Archivados" con la fecha de cese. No se borra la fila.

## Archivados

| Subagente | Raíz | Dominio / foco | Activado en | Archivado en | Razón |
| --------- | ---- | -------------- | ----------- | ------------ | ----- |
| _ninguno_ |      |                |             |              |       |

## Mantenimiento

- Edición manual. Este fichero es curado, no derivado.
- Cada alta/baja deja entrada `[DOCS]` en `devlog/DEVLOG.md` en el mismo turno.
- Si nace un subagente nuevo, `memory/INDEX.md` ya apunta aquí: no hace falta tocarlo salvo que cambie la ruta.
