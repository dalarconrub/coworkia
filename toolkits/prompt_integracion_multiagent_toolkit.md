# Prompt de integración del `multiagent-toolkit`

Integra en la raíz del repo el contenido útil de `multiagent-toolkit.zip`.

## Árbol real del toolkit

```text
multiagent-toolkit/
├── .claude/
│   └── multiagent.md
├── .github/
│   └── copilot-instructions.md
├── .gitignore
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── artifacts/
│   ├── daily/
│   │   └── .gitkeep
│   ├── multiagent/
│   │   └── .gitkeep
│   └── sprints/
│       └── .gitkeep
├── chats/
│   └── .gitkeep
├── devlog/
│   └── DEVLOG.md
├── memory/
│   ├── INDEX.md
│   ├── PURPOSE.md
│   ├── ROSTER.md
│   ├── SNAPSHOT.md
│   └── STRUCTURE.md
├── multiagents/
│   ├── __init__.py
│   ├── artifacts.py
│   ├── chat_memory.py
│   ├── chat_template.md
│   ├── models.py
│   ├── planner.py
│   └── registry.py
└── tools/
    ├── devlog.py
    ├── fix_chat_mojibake.py
    ├── init_chat.py
    ├── memory_check.py
    ├── session.py
    ├── snapshot_structure.py
    ├── sprint.py
    ├── sync_chat_memory.py
    └── timeline.py
```

## Archivos que NO deben integrarse

```text
.git/
__pycache__/
*.pyc
```

## Objetivo

Añadir al repo principal la funcionalidad del toolkit:

- Sistema de comunicación multiagente.
- Chat diario en `chats/`.
- Memoria estructurada en `memory/`.
- DevLog en `devlog/`.
- Herramientas CLI en `tools/`.
- Módulo Python `multiagents/`.
- Artefactos derivados en `artifacts/`.
- Instrucciones para Claude, Codex y Copilot.

## Regla principal

No sobrescribir ningún archivo existente.

Si un archivo ya existe, se debe:

1. Detectar el conflicto.
2. Mostrar informe.
3. Consultarme antes de modificarlo.
4. Si autorizo la fusión, añadir el contenido nuevo al final del archivo existente.

Separador obligatorio para fusiones:

```text
--- MULTIAGENT TOOLKIT ADDITION ---
```

## Informe de conflictos

Usar esta tabla:

| Archivo existente | Archivo del toolkit | Tipo de conflicto | Acción propuesta |
| ----------------- | ------------------- | ----------------- | ---------------- |

Tipos posibles:

- Mismo nombre.
- Misma función.
- Documentación duplicada.
- Configuración de agente existente.
- Dependencia incompatible.

## Archivos sensibles

Revisar especialmente:

```text
README.md
AGENTS.md
CLAUDE.md
.gitignore
.github/copilot-instructions.md
.claude/multiagent.md
memory/
tools/
devlog/
artifacts/
chats/
multiagents/
```

## Estrategia de integración

1. Inspeccionar la raíz actual del repo.
2. Comparar la estructura existente con el árbol del toolkit.
3. Copiar los archivos nuevos que no entren en conflicto.
4. Detectar conflictos antes de tocar archivos existentes.
5. Consultarme antes de cualquier fusión.
6. Si autorizo, fusionar añadiendo el contenido nuevo al final.
7. Ajustar imports y rutas si es necesario.
8. Validar que el sistema funciona.

## Validación

Ejecutar:

```bash
python tools/memory_check.py
python tools/init_chat.py
python tools/devlog.py view --limit 20
python tools/sprint.py --help
python tools/timeline.py --help
python -c "import multiagents; print('multiagents OK')"
```

## Entregables

Al terminar, entregar:

1. Estructura final del repo.
2. Archivos añadidos.
3. Archivos fusionados.
4. Archivos ignorados.
5. Conflictos detectados.
6. Cambios en imports o rutas.
7. Comandos de prueba.
8. Estado final:

   - integrado,
   - parcialmente integrado,
   - bloqueado por conflictos.

## Restricción absoluta

Ante cualquier conflicto:

```text
DETENER → INFORMAR → CONSULTAR → ESPERAR RESPUESTA
```

## 💡 Principio clave

No se trata de copiar archivos, sino de:

> Integrar funcionalidad respetando el estado actual del sistema
