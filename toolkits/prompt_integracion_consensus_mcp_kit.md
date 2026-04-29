# Prompt de integración del `consensus-mcp-kit`

Integra en el repo el contenido útil de `consensus-mcp-kit.zip` y deja al desarrollador con el MCP de **Consensus** funcional en Cursor y/o VSCode (Claude Code) sin pelearse con OAuth, planes free vs Pro, ni conflictos de puerto.

> ⚠️ Este kit toca **dos archivos fuera del repo del usuario** (en `$HOME`): `~/.cursor/mcp.json` y `~/.claude.json`. Nunca lo hagas sin autorización explícita.
>
> El kit en sí es portable y se copia al repo destino bajo una carpeta dedicada (por defecto `tools/consensus-mcp-kit/` o ruta equivalente). No fusiona ni reescribe nada del repo destino — sólo añade carpeta y documentación.

## Árbol real del toolkit

```text
consensus-mcp-kit/
├── README.md
├── CHANGELOG.md
├── docs/
│   ├── BACKGROUND.md
│   └── TROUBLESHOOTING.md
├── templates/
│   ├── README.md
│   ├── cursor-mcp.json
│   ├── claude-code-mcp.json
│   ├── claude-code-mcp.direct.json
│   └── vscode-mcp.json
├── install/
│   ├── install.sh
│   ├── install.ps1
│   ├── uninstall.sh
│   └── uninstall.ps1
└── tools/
    ├── check_mcp.sh
    ├── check_mcp.ps1
    ├── reset_oauth.sh
    ├── reset_oauth.ps1
    ├── free_oauth_port.sh
    └── free_oauth_port.ps1
```

## Archivos que NO deben integrarse

```text
.git/
__pycache__/
*.pyc
*.bak.*
~/.mcp-auth/        (tokens OAuth del usuario, jamás)
~/.claude.json.bak* (backups personales del usuario)
~/.cursor/mcp.json.bak*
```

## Objetivo

Añadir al repo principal una **carpeta autocontenida** con todo lo necesario para que cualquier integrante del equipo conecte el MCP oficial de Consensus a su cliente IA local:

- Plantillas JSON de configuración para Cursor (`~/.cursor/mcp.json`), Claude Code (`~/.claude.json`) y VSCode (extensiones MCP).
- Instaladores idempotentes en bash + PowerShell que hacen backup automático y merge no destructivo.
- Diagnóstico (`check_mcp`), purga OAuth (`reset_oauth`), liberación de puerto callback (`free_oauth_port`).
- Documentación que explica las **3 variantes** de conexión (legacy claude.ai con cuota mensual, HTTP directo anónimo, mcp-remote con OAuth Pro) y los 10 errores operativos más frecuentes.

El kit funciona en cualquier proyecto. No depende de `memory/`, `devlog/`, ni de ningún otro toolkit del repo destino.

## Regla principal

**No sobrescribir ningún archivo existente del repo destino.** El kit se instala como **carpeta nueva**, no fusiona contenido del repo.

Si la ruta de destino propuesta (por ejemplo `tools/consensus-mcp-kit/` o `toolkits/consensus-mcp-kit/`) ya existe:

1. Detectar el conflicto.
2. Mostrar informe.
3. Consultarme antes de modificarla.
4. Si autorizo, proponer ruta alternativa o renombrar la previa con sufijo `.bak.YYYYMMDD`.

Para los archivos que el kit toca **fuera del repo** (en `$HOME`):

- El instalador hace backup automático con sufijo `.bak.YYYYMMDD_HHMMSS`.
- El instalador hace **merge JSON no destructivo**: añade la entrada `mcpServers.consensus` sin tocar otras entradas existentes.
- Nunca borra ni renombra archivos sin pedir confirmación.

## Informe de conflictos

Usar esta tabla:

| Archivo existente | Archivo del toolkit | Tipo de conflicto | Acción propuesta |
| ----------------- | ------------------- | ----------------- | ---------------- |

Tipos posibles:

- Carpeta de destino ya existe.
- `~/.cursor/mcp.json` con bloque `consensus` previo (de otra config).
- `~/.claude.json` con bloque `consensus` previo.
- Conector legacy "claude.ai Consensus" activo en paralelo.
- `~/.mcp-auth/mcp-remote-*/` con tokens previos no válidos (cuenta diferente).
- Puerto OAuth (`6761`) ocupado por proceso ajeno (no node).

## Archivos sensibles

Revisar especialmente:

```text
~/.claude.json                                      (config personal del usuario, fuera del repo)
~/.cursor/mcp.json                                  (config personal del usuario, fuera del repo)
~/.mcp-auth/mcp-remote-*/*tokens.json               (tokens OAuth — JAMÁS commitear)
<repo>/.gitignore                                   (asegurar que excluye lo anterior)
<repo>/<ruta-destino>/                              (donde se aloja el kit en el repo)
```

Si el repo destino tiene un `.gitignore`, **verificar que excluye** explícitamente:

```text
# secretos de cliente IA
~/.claude.json
~/.cursor/mcp.json
.mcp-auth/
**/*.bak.*
```

(Aunque en general el `~/` sólo afecta a backups en home; lo que importa de cara al repo es asegurarse de que no se cuelan tokens si el kit se ejecuta dentro del workspace).

## Estrategia de integración

1. **Inspeccionar la raíz actual del repo destino**.
2. **Decidir ruta de destino** (sugerencia por defecto: `tools/consensus-mcp-kit/`; alternativa: `toolkits/consensus-mcp-kit/` o `vendor/consensus-mcp-kit/`). Consultarme si hay duda.
3. **Descomprimir `consensus-mcp-kit.zip`** dentro de la ruta elegida.
4. **Verificar permisos de ejecución** de los `.sh`:
   ```bash
   chmod +x <ruta-destino>/install/*.sh <ruta-destino>/tools/*.sh
   ```
5. **Detectar el cliente IA del usuario** (Cursor, VSCode con Claude Code, o ambos). Inspeccionar:
   - Cursor: `~/.cursor/` existe.
   - Claude Code: `~/.claude.json` existe (o el comando `claude` está en PATH).
6. **NO ejecutar el instalador automáticamente**. Mostrar al usuario el comando exacto y pedir confirmación antes de modificar archivos en `$HOME`.
7. **Añadir al README del repo** (si lo tiene) un párrafo apuntando a `<ruta-destino>/README.md` para que cualquiera del equipo encuentre el kit.
8. **Validar la integración** con los smoke-tests del kit.

## Validación

Tras descomprimir y antes de ejecutar el instalador:

```bash
cd <ruta-destino>

# Validar plantillas JSON
for f in templates/*.json; do
  node -e "JSON.parse(require('fs').readFileSync('$f','utf8'))" && echo "[ok] $f"
done

# Validar sintaxis de scripts bash
for s in install/*.sh tools/*.sh; do
  bash -n "$s" && echo "[ok] $s"
done

# Validar que Node es >= 18 (requisito de mcp-remote)
node --version
```

Tras ejecutar el instalador (con autorización del usuario) y reiniciar el cliente:

```bash
# bash / Git Bash
bash <ruta-destino>/tools/check_mcp.sh

# PowerShell
powershell -ExecutionPolicy Bypass -File <ruta-destino>\tools\check_mcp.ps1
```

`check_mcp` debería reportar:

- Node >= 18: ok.
- `~/.cursor/mcp.json` y/o `~/.claude.json` con `mcpServers.consensus`: ok.
- Tokens OAuth presentes con `scope=search type=Bearer refresh=yes`: ok (después de completar OAuth en navegador).
- Puerto 6761: libre o en uso por mcp-remote del cliente activo.

## Comandos de uso diario (para incluir en el README del repo destino)

```bash
# instalar (una vez por máquina)
bash <ruta-destino>/install/install.sh                     # Linux/macOS/Git Bash
powershell -ExecutionPolicy Bypass -File <ruta-destino>\install\install.ps1   # Windows

# diagnóstico cuando algo falle
bash <ruta-destino>/tools/check_mcp.sh

# si el OAuth quedó en cuenta free y queremos relogin con Pro
bash <ruta-destino>/tools/reset_oauth.sh

# si el puerto 6761 está ocupado por un node huérfano
bash <ruta-destino>/tools/free_oauth_port.sh

# desinstalar
bash <ruta-destino>/install/uninstall.sh
```

## Variantes de instalación

El instalador acepta flags opcionales:

| Flag | Efecto | Cuándo usarlo |
| --- | --- | --- |
| (sin flags) | Instala con `mcp-remote` (OAuth completo) en Cursor + Claude Code | Caso por defecto, recomendado |
| `--direct` (bash) / `-Direct` (ps) | Instala con HTTP directo (modo anónimo, top 3) sin Node ni OAuth | Sólo si OAuth falla repetidamente |
| `--port N` / `-Port N` | Pasa `--auth-server-port=N` a mcp-remote | Cuando el puerto 6761 choca sistemáticamente |
| `--cursor-only` / `-CursorOnly` | Sólo modifica `~/.cursor/mcp.json` | Si el equipo sólo usa Cursor |
| `--claude-only` / `-ClaudeOnly` | Sólo modifica `~/.claude.json` | Si el equipo sólo usa Claude Code |

## Entregables

Al terminar, entregar:

1. Ruta final del kit en el repo destino.
2. Lista de archivos añadidos al repo.
3. Conflictos detectados (si los hubo) y resolución acordada.
4. Cambios en `.gitignore` si fueron necesarios.
5. Comandos exactos que el usuario debe ejecutar para instalar localmente (con su SO).
6. Resultado de los smoke-tests pre-instalación.
7. Estado final:
   - integrado, listo para que cada miembro instale localmente,
   - parcialmente integrado (kit en repo, pendiente de docs/.gitignore),
   - bloqueado por conflictos (esperando autorización).

## Restricción absoluta

Ante cualquier conflicto, ya sea en el repo o en archivos personales del usuario en `$HOME`:

```text
DETENER → INFORMAR → CONSULTAR → ESPERAR RESPUESTA
```

Nunca:

- Modificar `~/.claude.json` o `~/.cursor/mcp.json` sin que el usuario lo haya autorizado en este turno.
- Borrar `~/.mcp-auth/` sin backup.
- Matar procesos node sin verificar primero qué son.
- Commitear ficheros que contengan tokens, refresh_tokens, client_secret o backups personales.

## 💡 Principio clave

No se trata de configurar el MCP por el usuario, sino de:

> Dejarle un kit autosuficiente y un instalador idempotente que pueda ejecutar en su máquina cuando quiera, con docs y diagnóstico para resolver los problemas más frecuentes sin pedir ayuda.
