# Prompt: Integración y uso del starter kit `.ai/commands`

Quiero que revises e integres en este repo un starter kit portable de comandos para agentes IA. El contenido descomprimido debe quedar bajo:

```text
.ai/
├── README.md
├── COMMANDS.md
└── commands/
    └── *.md
```

---

## 1. Qué es el starter kit

El starter kit `.ai/commands` es una convención portable para definir comandos tipo `/` mediante archivos Markdown.

Cada archivo representa un comando reutilizable que encapsula un prompt estructurado.

Estructura mínima esperada (el ZIP puede traer **más** `.md`; ver sección 8):

```text
.ai/
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

La finalidad es que cualquier agente pueda interpretar comandos como:

```text
/plan implementar autenticación
/debug error en endpoint
/architecture rediseñar módulo
```

---

## 2. Cómo funcionan los comandos

Un comando `/` es una forma abreviada de cargar un prompt estructurado.

Ejemplo:

```text
/debug error al validar JWT
```

Debe procesarse así:

1. Detectar el comando: la **primera palabra** tras `/` (token), sin la barra. Ejemplos: `/plan …` → `plan`; `/deep-think …` → `deep-think`.
2. Resolver el fichero: **nombre del token + `.md`** en `.ai/commands/` → `.ai/commands/<token>.md` (respetar guiones y minúsculas como en el repo).
3. Leer sus instrucciones
4. Aplicarlas al resto del mensaje (todo lo que sigue al token)
5. Usar herramientas disponibles si existen
6. Generar la respuesta siguiendo el formato definido en el comando

Si el comando no existe:

* Informar al usuario
* Mostrar los comandos disponibles desde `.ai/COMMANDS.md` (no inventar listas desactualizadas)

---

## 3. Instalación desde ZIP en cualquier repo

1. Descomprimir el archivo ZIP.
2. Colocar la carpeta `.ai/` en la **raíz** del repositorio (mismo nivel que `README`, `src`, etc.).

Estructura final:

```text
mi-repo/
├── .ai/
│   ├── README.md
│   ├── COMMANDS.md
│   └── commands/
│       ├── think.md
│       ├── plan.md
│       ├── debug.md
│       └── ...
├── src/
├── tests/
└── ...
```

Importante:

* La carpeta `.ai/` debe estar en la raíz; no dentro de `src/`, `docs/` u otras subcarpetas salvo convención explícita del proyecto.
* Si el ZIP descomprime una carpeta intermedia (p. ej. `ai_commands_starter_kit/.ai/`), **subir** el contenido hasta que `.ai/` cuelgue de la raíz del repo.
* Comprobar que **`.gitignore` no excluya `.ai/`** (algunas plantillas ignoran `.ai` u ocultos genéricos).

### 3.1 Comandos que no estaban en la lista “canónica” del kit

Algunos ZIP añaden ficheros extra (p. ej. `deep-think.md`). En ese caso:

* Añadir o actualizar la entrada en **`.ai/COMMANDS.md`** para que el índice refleje el comando real (`/deep-think`, etc.).
* Actualizar la sección “Comandos disponibles” de **este** prompt de integración solo si mantienes una copia del listado en el repo; la fuente de verdad operativa es siempre `.ai/COMMANDS.md` + los ficheros presentes en `.ai/commands/`.

### 3.2 Windows y extracción

En PowerShell 5.1, rutas y codificación pueden dar problemas al listar o extraer ZIPs en una sola línea. Preferible:

* **Python** (`zipfile`) para listar y extraer de forma predecible y UTF-8, o
* Herramienta de archivo con “extraer aquí” revisando que el resultado sea `.ai/` en la raíz.

---

## 4. Integración en un sistema multiagente

Todos los agentes deben ser capaces de usar estos comandos de forma uniforme.

Añadir la siguiente regla global al sistema (adaptar rutas si tu proyecto usa otro nombre para “instrucciones de agente”):

```md
## Interpretación de comandos `/`

Cuando un mensaje comience por `/`, interpretar la primera palabra como un comando.

Ejemplo:

```text
/plan añadir sistema de login
```

Procedimiento:

1. Extraer el nombre del comando (`plan`)
2. Buscar el archivo:

```text
.ai/commands/plan.md
```

3. Leer su contenido
4. Aplicar sus instrucciones al resto del mensaje
5. Generar la respuesta según el formato del comando

Si el comando no existe:

* Informar al usuario
* Mostrar los comandos disponibles desde `.ai/COMMANDS.md`
```

Puntos de anclaje habituales (tocar los que existan en el repo):

* `AGENTS.md`, `CLAUDE.md` (o equivalentes)
* `.github/copilot-instructions.md` u otras reglas del IDE (p. ej. `.cursor/rules/`) si el proyecto las usa como fuente de verdad para agentes

---

## 5. Regla para cualquier agente

Todos los agentes deben seguir este flujo:

1. Si el mensaje empieza por `/`, activar modo comando
2. Cargar el archivo correspondiente bajo `.ai/commands/`
3. Aplicar las instrucciones del comando
4. Usar herramientas disponibles
5. No inventar archivos ni resultados
6. Declarar limitaciones si no puede completar alguna acción

---

## 6. Ejemplo de funcionamiento

Entrada:

```text
/debug El endpoint /api/login devuelve 500 cuando el token está caducado
```

Proceso:

```text
1. Detectar comando: debug
2. Leer .ai/commands/debug.md
3. Aplicar razonamiento de diagnóstico
4. Analizar posibles causas
5. Proponer verificación
6. Recomendar solución mínima
```

Salida esperada (orientativa; el formato exacto lo define cada `*.md`):

```md
## Síntoma

...

## Señales relevantes

...

## Hipótesis de causa raíz

| Rank | Hipótesis | Evidencia | Prueba |
|---|---|---|---|

## Cambio mínimo recomendado

...

## Verificación

...
```

---

## 7. Resultado esperado de la integración

Checklist mínima:

1. La carpeta `.ai/` está en la **raíz** y `.ai/commands/*.md` es coherente con `.ai/COMMANDS.md`.
2. Los agentes tienen la regla global de interpretación de `/` (copilot + otros canales que el repo mantenga).
3. **README** del repo: sección corta (convención `/<comando> …`, enlace a `.ai/COMMANDS.md`).
4. Si el proyecto mantiene **mapa de carpetas** o **índice de recursos** (p. ej. `memory/STRUCTURE.md`, `memory/INDEX.md`): añadir narrativa `.ai/` y referencia en el índice; **regenerar** cualquier bloque TREE u otro snapshot si existe script oficial para ello.
5. Si el script de árbol u otra herramienta **omite directorios ocultos** (nombre que empieza por `.`), comprobar que **`.ai/` no quede fuera del inventario**; si hace falta, añadir `.ai` a la allowlist junto a `.github` / `.claude` (ejemplo real: en repos con `tools/snapshot_structure.py` que filtre `p.name.startswith(".")`, incluir `".ai"` en las excepciones).
6. **Devlog o changelog** del proyecto: una entrada documentando la integración (área DOCS o la que corresponda).
7. No modificar código de producto salvo lo imprescindible (p. ej. allowlist del árbol, cierre de `.gitignore`).

---

## 8. Comandos disponibles (lista base del kit)

Comandos típicos del starter; **validar siempre** contra el ZIP y `.ai/COMMANDS.md`:

```text
/think
/plan
/debug
/architecture
/refactor
/review
/test
/docs
/security
/research
/decision
/handoff
```

---

## 9. Objetivo final

El objetivo es que cualquier agente del sistema multiagente pueda ejecutar:

```text
/<comando> <tarea>
```

y automáticamente:

* cargar el comando adecuado
* aplicar su lógica
* devolver una respuesta estructurada y consistente

Sin necesidad de escribir prompts complejos manualmente.
