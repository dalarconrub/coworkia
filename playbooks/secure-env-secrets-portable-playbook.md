# Playbook portable — Gestión segura de secretos `.env` (tokens / API keys)

**Fecha:** 2026-04-27  
**Propósito:** definir un método **reutilizable** para almacenar, transportar y cargar **secretos de configuración** (tokens, API keys, credenciales) de forma segura en cualquier proyecto, sin depender del tipo de secreto ni del stack (Python/Node/etc.).  
**Aplicabilidad:** cualquier repo con `.env` o variables de entorno; personal o equipo.

---

## 0) Principios (lo mínimo que no se negocia)

1. **Los secretos no van a Git.** Ni en `.env`, ni en JSON, ni “temporalmente”.
2. **Los secretos tienen ciclo de vida:** creación → uso → rotación → revocación.
3. **El repo solo guarda *plantillas* y *mecanismos*, no valores.**
4. **Separar “config pública” de “secreto”**: IDs no sensibles pueden vivir en `.env.example`, tokens no.
5. **Automatiza la carga de secretos** para eliminar copy/paste (que es una fuente de fugas).

---

## 1) Modelo de amenazas (elige tu nivel)

Antes de decidir un método, responde:

- **¿Riesgo principal?**
  - **Filtración del repo** (GitHub público, fork accidental, ZIP compartido).
  - **Exfiltración local** (malware, backups, logs, historial de shell).
  - **Robo de portátil** (disco, perfil de usuario).
  - **Errores humanos** (pegar tokens en chat/issues).
- **¿Necesitas multi-máquina?** (sí/no)
- **¿Necesitas multi-usuario?** (sí/no)
- **¿Necesitas CI/CD?** (sí/no)
- **¿Puedes usar herramientas externas?** (gestor de contraseñas / vault / KMS)

Esto determina si te conviene “gestor de contraseñas”, “cifrado en repo”, “keychain local”, o “vault central”.

---

## 2) Arquitectura canónica (independiente del proyecto)

En el repo deben existir (como mínimo):

1. **`.env.example`** (sin secretos)
2. **`.gitignore`** que ignore `.env` y cualquier archivo local de secretos
3. **Un “loader”** que convierta secretos en variables de entorno para el proceso (o que genere `.env`)
4. **Una receta de arranque** (script/bat/make/npm) que ejecute el loader + la app

Plantillas típicas:

- `.env` (local, secreto, gitignored)
- `config/secrets.<source>.json` (local, secreto, gitignored)
- `config/secrets.<source>.json.example` (plantilla, versionada)

---

## 3) Opciones de almacenamiento seguro (elige 1 como “fuente”)

### Opción A — Gestor de contraseñas (recomendado para personal + multi-máquina)

**Ejemplos:** 1Password, Bitwarden, KeePass (local).  
**Idea:** los secretos viven en el gestor. El repo solo sabe **cómo** cargarlos.

Dos variantes:

1) **CLI del gestor** (inyección de env vars sin archivo `.env`)  
2) **Export/Download a JSON** + **script** que genera `.env` (sin copy/paste manual repetido)

**Pros:** multi-máquina, auditoría, rotación, UX buena.  
**Contras:** dependencia del gestor / CLI / política de export.

### Opción B — Cifrado en el repo (cuando necesitas que “viaje” con el repo)

**Ejemplos:** `sops+age`, `git-crypt`.  
**Idea:** se versiona `secrets.enc` cifrado; el secreto real se descifra localmente.

**Pros:** portable con el repo; reproducible.  
**Contras:** gestión de claves (age/GPG), rotación, onboarding más complejo.

### Opción C — Keychain / Secret store del SO (buena para local-only)

**Ejemplos:** Windows Credential Manager (DPAPI), macOS Keychain, Linux Secret Service.  
**Pros:** seguro, sin dependencias externas.  
**Contras:** menos portable; por máquina/usuario.

### Opción D — Secret manager para equipos/CI

**Ejemplos:** GitHub Actions Secrets, Vault, Doppler, Infisical, AWS/GCP secrets.  
**Pros:** ideal para CI/CD y equipos.  
**Contras:** requiere adopción y permisos.

---

## 4) “Fuente → Inyección” (patrón operativo)

Independientemente de la opción, la carga debe terminar en **una de dos salidas**:

- **Salida 1: variables de entorno del proceso** (preferida)  
  - Pros: no escribes `.env` a disco
  - Contras: si la app/herramientas esperan `.env`, necesitas adaptarlas

- **Salida 2: generar `.env` local** (compatible con casi todo)  
  - Pros: funciona con stacks existentes
  - Contras: secreto en disco (aunque esté gitignored). Mitiga con backups/ACLs/rotación.

---

## 5) Implementación recomendada (portable)

### 5.1 Plantilla de secretos

Versiona un ejemplo:

- `config/secrets.json.example` (sin secretos)

Y mantén ignorado:

- `config/secrets.json` (con secretos reales)

### 5.2 Script “secrets → .env”

Requisitos:

- **No imprime secretos**
- **Sobrescribe con backup**
- **Mantiene el orden de `.env.example`** para legibilidad
- **Reporta qué claves faltan** (sin mostrar valores)

### 5.3 Script de arranque

Un comando que haga:

1) generar/injectar secretos  
2) arrancar la app / scripts del repo

---

## 6) Checklist de seguridad (antes de darlo por cerrado)

- **Git**
  - `.env` ignorado
  - `config/secrets*.json` ignorado (si aplica)
- **DX / automatización**
  - “un comando” para arrancar sin copy/paste
  - “un comando” para rotar (o al menos para reemplazar el secreto)
- **Auditoría**
  - no hay tokens en `README`, `docs/`, `chats/`, `devlog/`
  - no hay secretos en tests/fixtures
- **Rotación**
  - procedimiento escrito: “si se filtra X → revocar X → regenerar → re-sync”

---

## 7) Antipatrones (lo que NO hacer)

- **Subir `.env` por error** “solo una vez”.
- **Guardar secretos en `.env.example`** (o en docs).
- **Copiar tokens por chat/email** sin cifrado.
- **Depender de que la terminal tenga una sesión exportada** como única estrategia.
- **Logs con valores**: imprimir `os.environ` o volcar config completa.

---

## 8) Plantillas (copy/paste)

### 8.1 `.gitignore` mínimo

```gitignore
.env
*.env
.env.*
!.env.example
config/secrets*.json
```

### 8.2 Estructura de repo sugerida

```text
config/
  secrets.json.example
  secrets.json            (gitignored)
tools/
  generate_env_from_json.py
apps/ (o scripts/)
  generar_env_desde_json.bat
.env.example
```

---

## 9) Criterios de cierre (Definition of Done)

✅ CERRADO cuando:

- Hay **un método seleccionado** (A/B/C/D) y documentado en el README/guía de arranque.
- Existe `.env.example` y `.gitignore` correcto.
- Existe **automatización** (loader + arranque) sin copy/paste.
- Existe procedimiento de **rotación** y **revocación** (aunque sea breve).

---

## Provenance

- Extraído y universalizado a partir de un caso real en Coworkia (2026-04-27) donde se implementaron dos rutas: 1Password (`op run`) y JSON descargable → generación automática de `.env`.
