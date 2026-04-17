# Playbook: extraer un toolkit portable desde un proyecto

> Método reproducible para convertir funcionalidad que nació en un
> proyecto concreto en un paquete portable que se pueda incorporar a otros.
>
> Caso de referencia: extracción del sistema multiagente de Coworkia
> como [`multiagent-kit/`](../multiagent-kit/).

## 1. Decidir si vale la pena extraer

Antes de abstraer, pregúntate:

- **¿La funcionalidad es útil fuera del proyecto origen?** Si solo sirve aquí, no la conviertas en kit — añade fricción sin retorno.
- **¿Hay al menos 2 proyectos donde se usaría?** Uno actual + uno previsto. Abstraer para un único usuario es especulación.
- **¿La parte genérica se puede separar limpiamente del dominio?** Si el acoplamiento es alto (nombres de tablas, APIs internas, reglas de negocio entremezcladas), el coste de extracción supera el beneficio.
- **¿Es estable?** Un módulo que todavía cambia todas las semanas no debería congelarse en un kit.

Si alguna respuesta es "no clara", mejor esperar y copiar/pegar la próxima vez. Un kit prematuro es deuda.

## 2. Inventariar y clasificar

Lista todos los ficheros implicados en la funcionalidad. Clasifícalos en tres cubos:

| Cubo | Qué contiene | Qué hacer |
| --- | --- | --- |
| **Núcleo genérico** | No depende del dominio. Reutilizable tal cual. | Copiar al kit. |
| **Híbrido** | Código genérico pegado a identificadores de dominio (nombres de proyecto, rutas canónicas, paths hard-coded). | Copiar al kit **extrayendo lo específico**. |
| **Específico de dominio** | Reglas de negocio, agentes de integración con APIs concretas. | Se queda en el proyecto origen. |

**Ejemplo** (caso multiagent-kit):

| Fichero | Cubo | Acción |
| --- | --- | --- |
| `tools/init_chat.py` | Núcleo | Copiado intacto. |
| `tools/fix_chat_mojibake.py` | Núcleo | Copiado intacto. |
| `multiagents/chat_memory.py` | Núcleo | Copiado (parser UTF-8 estricto). |
| `multiagents/chat_template.md` | Híbrido | Se copia sin referencias a Coworkia. |
| `.claude/multiagent.md` | Híbrido | Se copia reemplazando `David` por "director". |
| `AGENTS.md` / `CLAUDE.md` / `copilot-instructions.md` | Híbrido | Se copian generalizando identidad y ejemplos. |
| `agents/orchestrator_agent.py` | Específico (Scrum Coworkia) | Se queda. Se extrae solo `sync-chat-memory` como CLI autónomo. |
| `multiagents/registry.py`, `planner.py`, `artifacts.py` | Específico | Se quedan. |

## 3. Generalizar los híbridos

Reglas al portar un fichero híbrido:

- **Sustituye nombres propios por placeholders o descripciones genéricas.**
  `**David** — director` → `**David** — director (rol fijo)` + nota de que cualquier IA puede cumplir las demás funciones.
- **Marca huecos con `TODO` o `{{PLACEHOLDER}}`** donde el proyecto destino deba rellenar:

  ```md
  ## Contexto del proyecto
  <!-- TODO: describe aquí dominios, reglas canónicas. -->
  ```

- **Elimina ejemplos con datos reales** (tablas, IDs, nombres de bases de datos). Sustitúyelos por ejemplos neutros.
- **Respeta el tono y estructura originales** para que el usuario del proyecto origen reconozca el kit y no tenga que aprenderlo de nuevo.

## 4. Romper dependencias con el proyecto origen

Un kit portable no puede depender de que exista un orquestador, una configuración o una convención de rutas del proyecto madre.

Patrones útiles:

- **Entry point autónomo** — si una función se invocaba como subcomando del orquestador (`python agents/orchestrator_agent.py sync-chat-memory`), crea un CLI directo dentro del kit (`python tools/sync_chat_memory.py`).
- **Imports locales solamente** — cada script resuelve rutas relativas a sí mismo:

  ```python
  _ROOT = Path(__file__).resolve().parent.parent
  sys.path.insert(0, str(_ROOT))
  ```

- **Evita imports circulares** — si `chat_memory.py` necesita `init_chat.py`, haz el import **lazy** dentro de la función, no al top-level.
- **Nada de variables de entorno del proyecto madre** salvo las explícitamente documentadas en el README del kit.

## 5. Estructura canónica del kit

```
<kit-name>/
├── README.md              <- instalación, uso, extensión
├── <dotfiles y convenciones del protocolo>
├── <subcarpetas de datos vacías con .gitkeep>
├── <módulo Python núcleo>/
│   ├── __init__.py
│   └── <core>.py
└── tools/
    ├── <entry-point>.py
    └── <utility>.py
```

Principios:

- Raíz plana — todo lo que se copia va a la raíz del proyecto destino; las subcarpetas reflejan esa raíz.
- `README.md` siempre, aunque sea breve.
- `.gitkeep` en carpetas de datos vacías (chats, artifacts, etc.) para que el `git clone` las preserve.

## 6. README mínimo del kit

Incluye, en este orden:

1. **Qué resuelve** (1–2 párrafos).
2. **Estructura** (árbol de ficheros con una línea de descripción por cada uno).
3. **Instalación en otro proyecto** (comando de copia en bash y PowerShell).
4. **Uso diario** (los 2–3 comandos que el usuario va a ejecutar más).
5. **Reglas operativas clave** (invariantes que el kit asume).
6. **Extender el kit** (cómo añadir piezas sin romperlo).

No hace falta más. Si el lector necesita leer 10 páginas para usarlo, el kit está mal.

## 7. Smoke-test desde cero

Antes de declarar el kit terminado, **pruébalo como si fueras un usuario nuevo**:

```bash
rm -rf /tmp/kit-smoke && mkdir -p /tmp/kit-smoke
cp -r <ruta>/<kit-name>/. /tmp/kit-smoke/
cd /tmp/kit-smoke
python tools/<entry-point>.py       # comando principal
python tools/<utility>.py            # alguna utilidad
ls <carpetas de datos generadas>     # verificar que se crearon
```

Si falla, itera. El smoke-test en un directorio virgen detecta:

- paths hard-coded al proyecto origen
- imports fantasma a módulos que solo existen en el origen
- supuestos sobre configuración previa
- ficheros olvidados

## 8. Lista de verificación final

- [ ] Núcleo genérico copiado sin referencias al dominio origen
- [ ] Placeholders (`TODO`, `{{...}}`) donde el usuario rellena
- [ ] Entry point CLI autónomo (no depende de orquestadores externos)
- [ ] Imports resuelven rutas relativas al propio kit
- [ ] README cubre: qué, estructura, instalar, uso diario, reglas
- [ ] Carpetas de datos vacías con `.gitkeep`
- [ ] UTF-8 estricto en lectura y escritura de todos los ficheros
- [ ] Smoke-test desde directorio virgen pasa
- [ ] Versión endurecida del núcleo también se aplica de vuelta al proyecto origen (si se corrigió algún bug durante la extracción)

## 9. Anti-patrones

- **Abstraer antes de tiempo.** Regla de tres: extrae solo cuando la tercera copia dolería. Dos copias puntuales son más baratas que una abstracción prematura.
- **Kits con configuración propia** (ficheros `.config`, variables de entorno propias). Un kit bien diseñado se instala copiando la carpeta, punto.
- **Incluir el historial del proyecto origen.** Si copias ejemplos reales del origen, contaminas el kit. Ejemplos siempre neutros.
- **Olvidar que el kit es público.** Si hay secretos, rutas internas, datos sensibles — auditar antes de extraer.
- **No revalidar el proyecto origen.** Durante la extracción probablemente refactorizas el núcleo. Asegúrate de aplicar ese refactor también al origen (p.ej. si arreglas un bug del parser, ambos lados se benefician).

## 10. Cuando el kit madura

Si pasa a usarse en varios proyectos:

- Versiona explícitamente (`CHANGELOG.md`, semver).
- Considera publicarlo como repositorio independiente.
- Considera empaquetarlo (`pyproject.toml` + instalación vía `pip install -e`) para evitar copias divergentes.

Mientras sea un kit de 1–3 proyectos, **copia directa es suficiente**. No sobreingenierices el empaquetado antes de tiempo.
