# Inicio Rapido En Windows

## 1. Preparar el entorno virtual

Ejecuta:

[setup_venv.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/setup_venv.bat)

Esto:

- crea `.venv` si no existe
- actualiza `pip`
- instala las dependencias del proyecto

## 2. Iniciar Coworkia

Puedes arrancar el hub desde la raiz con:

[INICIAR_COWORKIA.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/INICIAR_COWORKIA.bat)

### (Opcional) Arranque automático con 1Password (sin .env)

Si quieres evitar tener tokens en texto plano en `.env` y no andar copiando/pegando entre máquinas, usa el **1Password CLI** (`op`) para inyectar variables de entorno al vuelo.

Flujo:

- Copia `config/env.1password.example` a `config/env.1password` y reemplaza cada valor por una referencia `op://...` a tu item/campos de 1Password.
- Inicia sesión en 1Password CLI (`op signin`) en esa máquina.
- Arranca Coworkia con `INICIAR_COWORKIA_1PASSWORD.bat` (en la raíz del repo).
- (Opcional) Usa wrappers dedicados para el protocolo multiagente:
  - `apps\abrir_sesion_1password.bat`
  - `apps\cerrar_sesion_1password.bat`

Notas:

- Este método **no escribe secretos en Git** y puede funcionar **sin `.env`**.
- Si mantienes `.env` por compatibilidad, recuerda que ya está ignorado por Git.

### (Alternativa) JSON desde 1Password -> generar `.env` automático

Si prefieres **no usar `op`** (1Password CLI), puedes guardar tus secretos en 1Password como un **JSON** descargable y generar `.env` automáticamente.

Recomendación para el ítem en 1Password:

- **Nombre**: `Coworkia — Secrets JSON (.env)`
- **Descripción**: JSON con todos los secretos y IDs de configuración de Coworkia (equivalente a `.env`: Todoist, Notion, GitHub, Paperpile, Obsidian, Inoreader). Se descarga como `config/secrets.1p.json` y se usa para regenerar `.env` automáticamente con `apps\generar_env_desde_json.bat`.

Flujo:

- Copia `config/secrets.1p.json.example` a `config/secrets.1p.json` (este fichero **NO se versiona**).
- Pega dentro el JSON descargado desde 1Password (formato recomendado: objeto plano con claves tipo `TODOIST_API_KEY`, `NOTION_TOKEN`, etc.).
- Ejecuta `apps\generar_env_desde_json.bat` para generar `.env` (sobrescribe y crea backup `.env.bak-YYYYMMDD-HHMMSS`).

O desde `apps/` con:

[project_hub_gui.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/project_hub_gui.bat)

La apertura recomendada ya corre `apps\abrir_sesion.bat` antes del GUI:

- resuelve o crea el chat del día
- imprime briefing con memoria + devlog reciente
- valida `memory/`

## 3. Si algo falla

- revisa que Python 3 este instalado
- vuelve a ejecutar `setup_venv.bat`
- comprueba que `.env` exista y tenga las credenciales necesarias
- ejecuta `apps\config_doctor.bat` para ver exactamente que variable o ruta falta
- ejecuta `apps\notion_doctor.bat` si el problema es Notion y necesitas localizar IDs o permisos
  - Si tarda demasiado, usa modo rápido: `set NOTION_DOCTOR_FAST=1` antes de ejecutar

## 4. Cerrar sesión correctamente

Al terminar, ejecuta:

`apps\cerrar_sesion.bat`

Si estás usando 1Password CLI para secretos (sin `.env`), usa:

`apps\cerrar_sesion_1password.bat`

Esto deja tres capas al día:

- `artifacts/multiagent/*` y `memory/SNAPSHOT.md` vía `sync-chat-memory`
- `artifacts/daily/YYYY-MM-DD.md` vía `tools/timeline.py`
- validación final de `memory/`

## Accesos principales

- Preparar entorno: [setup_venv.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/setup_venv.bat)
- Diagnostico de configuracion: [config_doctor.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/config_doctor.bat)
- Diagnostico de Notion: [notion_doctor.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/notion_doctor.bat)
- Iniciar desde raiz: [INICIAR_COWORKIA.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/INICIAR_COWORKIA.bat)
- Iniciar desde raiz (1Password): `INICIAR_COWORKIA_1PASSWORD.bat`
- Iniciar desde apps: [project_hub_gui.bat](/c:/Users/David/Desktop/MSI-20260321/03-GAMA/coworkia/apps/project_hub_gui.bat)
- Abrir sesión (1Password): `apps\abrir_sesion_1password.bat`
- Cerrar sesión (1Password): `apps\cerrar_sesion_1password.bat`

## Comandos útiles (B0A-INX / MAR)

- Sync Todoist → Notion: `apps\sync_todoist_to_notion.bat 200`
- Asegurar columnas TODOIST-TAREAS (una vez): `apps\ensure_todoist_tasks_schema.bat`
- Doctor MAR (checks opcionales): `apps\mar_doctor.bat`
- Check completo (sync + doctor): `apps\mar_check.bat 200 --no-pause`
- INX solo desde Todoist (`TODOIST-TAREAS` → `INX-ENLACES`): `apps\inx_sync_todoist.bat 200 --no-pause`
- Log PTN → `NOTION_DB`: `apps\log_ptn_changes.bat --no-pause`
- INX desde log PTN (`NOTION_DB` → `INX-ENLACES`): `apps\inx_sync_notion.bat 200 --no-pause`
- INX solo desde log Obsidian: `apps\inx_sync_obsidian.bat 200 --no-pause`
