# Portable AI Commands Starter Kit

Este kit define comandos `/` portables mediante archivos Markdown en `.ai/commands`.

No depende de un framework concreto. Funciona como convención para Claude Code, Cursor, Codex, agentes personalizados, ECC u otros entornos que permitan cargar prompts desde archivos.

## Uso básico

Copia la carpeta `.ai/` en la raíz de cualquier repo.

```text
your-repo/
└── .ai/
    ├── README.md
    ├── COMMANDS.md
    └── commands/
        ├── think.md
        ├── plan.md
        ├── debug.md
        ├── architecture.md
        ├── refactor.md
        ├── review.md
        ├── test.md
        ├── docs.md
        ├── security.md
        ├── research.md
        ├── decision.md
        └── handoff.md
```

Después usa los comandos como prompts:

```text
/think Analiza esta decisión técnica...
/debug Este test falla con este error...
/architecture Diseña la arquitectura del módulo...
```

Si el cliente no soporta comandos `/`, copia el contenido del archivo correspondiente y úsalo como prompt.

## Integración opcional con MCP

Los comandos están escritos para poder usar herramientas MCP cuando existan, especialmente:

- `deep-thinker`, para razonamiento estructurado.
- herramientas de búsqueda de código.
- herramientas de lectura de ficheros.
- herramientas de ejecución de tests.

Si una herramienta no está disponible, el agente debe continuar con razonamiento textual y declarar la limitación.
