# Prompt de integración del `inoreader-mcp-kit`

Integra en el repo el contenido útil de `inoreader-mcp-kit.zip` y deja al desarrollador con el MCP de **Inoreader** funcional en **Cursor** y/o **Claude Code** sin que las credenciales terminen en Git.

> ⚠️ Este kit toca archivos **fuera del repo del usuario** (en `$HOME`): `~/.cursor/mcp.json` y `~/.claude.json`. Nunca lo hagas sin autorización explícita.
>
> El kit en sí es portable y se copia al repo destino bajo una carpeta dedicada (por defecto `tools/inoreader-mcp-kit/`). No fusiona ni reescribe nada del repo destino — sólo añade carpeta y documentación.

## Árbol real del toolkit

```text
inoreader-mcp-kit/
├── README.md
├── CHANGELOG.md
├── LICENSE.thirdparty.txt
├── .gitignore
├── docs/
│   ├── BACKGROUND.md
│   └── TROUBLESHOOTING.md
├── server/
│   ├── main.py
│   ├── config.py
│   ├── inoreader_client.py
│   ├── tools.py
│   ├── utils.py
│   ├── requirements.txt
│   └── .env.example
├── templates/
│   ├── cursor-mcp.json
│   └── claude-code-mcp.json
├── install/
│   ├── install.sh
│   ├── install.ps1
│   ├── uninstall.sh
│   └── uninstall.ps1
└── tools/
    ├── check_mcp.sh
    ├── check_mcp.ps1
    └── merge_mcp_config.py
```

## Archivos que NO deben integrarse

```text
.git/
__pycache__/
*.pyc
.env
**/*.bak.*
~/.cursor/mcp.json         (config personal del usuario)
~/.claude.json             (config personal del usuario)
```

## Objetivo

Añadir al repo principal una **carpeta autocontenida** con:

- Servidor MCP de Inoreader en Python (`server/`).
- Plantillas JSON para configurar el MCP en Cursor / Claude Code (`templates/`).
- Instaladores idempotentes que hacen backup y merge no destructivo (`install/`).
- Diagnóstico (`tools/check_mcp.*`) y merge JSON (`tools/merge_mcp_config.py`).

El kit funciona en cualquier proyecto. No depende de otros toolkits.

## Regla principal

**No sobrescribir ningún archivo existente del repo destino.** El kit se instala como **carpeta nueva**, no fusiona contenido del repo.

Si la ruta de destino propuesta (`tools/inoreader-mcp-kit/`) ya existe:

1. Detectar el conflicto.
2. Mostrar informe.
3. Consultarme antes de modificarla.
4. Si autorizo, proponer ruta alternativa o renombrar la previa con sufijo `.bak.YYYYMMDD`.

Para los archivos que el kit toca **fuera del repo** (en `$HOME`):

- El instalador hace backup automático con sufijo `.bak.YYYYMMDD_HHMMSS`.
- El instalador hace **merge JSON no destructivo**: añade `mcpServers.inoreader-mcp` sin tocar otras entradas existentes.
- Nunca borra ni renombra archivos sin pedir confirmación.

## Informe de conflictos

Usar esta tabla:

| Archivo existente | Archivo del toolkit | Tipo de conflicto | Acción propuesta |
| ----------------- | ------------------- | ----------------- | ---------------- |

Tipos posibles:

- Carpeta de destino ya existe.
- `~/.cursor/mcp.json` con bloque `inoreader-mcp` previo.
- `~/.claude.json` con bloque `inoreader-mcp` previo.
- Falta Python / pip en la máquina del usuario.

## Archivos sensibles

Revisar especialmente:

```text
~/.cursor/mcp.json  (config personal del usuario, fuera del repo)
~/.claude.json      (config personal del usuario, fuera del repo)
<repo>/.gitignore   (evitar comitear .env / backups si aparecen en workspace)
<repo>/tools/inoreader-mcp-kit/
```

## Estrategia de integración

1. **Inspeccionar la raíz actual del repo destino**.
2. **Decidir ruta de destino** (por defecto `tools/inoreader-mcp-kit/`).
3. **Descomprimir `inoreader-mcp-kit.zip`** dentro de la ruta elegida.
4. **Verificar permisos de ejecución** de los `.sh` (si aplica).
5. **NO ejecutar el instalador automáticamente**. Mostrar al usuario el comando exacto y pedir confirmación antes de modificar archivos en `$HOME`.
6. **Añadir al README del repo** (si lo tiene) un párrafo apuntando a `tools/inoreader-mcp-kit/README.md`.
7. **Validar la integración** con los smoke-tests del kit.

## Validación

Antes de ejecutar el instalador:

```bash
cd tools/inoreader-mcp-kit
python -m py_compile server/*.py
python -c "import json; json.load(open('templates/cursor-mcp.json','r',encoding='utf-8'))"
```

Después de ejecutar el instalador (con autorización) y reiniciar el cliente:

```bash
bash tools/inoreader-mcp-kit/tools/check_mcp.sh
```

```powershell
powershell -ExecutionPolicy Bypass -File tools\inoreader-mcp-kit\tools\check_mcp.ps1
```

## Comandos de uso diario (para incluir en el README del repo destino)

```bash
# instalar (una vez por máquina)
bash tools/inoreader-mcp-kit/install/install.sh
powershell -ExecutionPolicy Bypass -File tools\inoreader-mcp-kit/install/install.ps1

# diagnóstico
bash tools/inoreader-mcp-kit/tools/check_mcp.sh

# desinstalar
bash tools/inoreader-mcp-kit/install/uninstall.sh
```

## Restricción absoluta

Ante cualquier conflicto, ya sea en el repo o en archivos personales del usuario en `$HOME`:

```text
DETENER → INFORMAR → CONSULTAR → ESPERAR RESPUESTA
```

