# Nueva Estructura de Beta - Sistema de Backups Flexible

**Fecha de Cambio:** 04 de febrero de 2026
**Modificación:** Sistema genérico de backups con carpeta molde DISK

---

## ¿Qué Cambió en Beta?

### Estructura Anterior ❌

```
Beta/
└── BACKS-2026/
    ├── GDRIVE-2026/       ← Orígenes específicos predefinidos
    │   └── .gitkeep
    ├── MSI-2026/
    │   └── .gitkeep
    ├── HP-2026/
    │   └── .gitkeep
    └── ONEDRIVE-2026/
        └── .gitkeep
```

**Limitaciones:**
- Orígenes fijos y predefinidos
- Poco flexible para nuevos orígenes
- No sigue el patrón de versionado por fecha

### Estructura Nueva ✅

```
Beta/
└── BACKS-2026/
    └── DISK-2026/              ← Carpeta molde genérica
        ├── DISK-2026.md        ← Guía de uso
        └── DISK-2026-02-04/    ← Snapshot con fecha de creación
            ├── DISK-2026-02-04.md
            └── .gitkeep
```

**Ventajas:**
- Sistema genérico y flexible
- Versionado por fecha consistente con el resto del sistema
- Fácil crear nuevos snapshots
- No necesitas predefinir orígenes

---

## Cómo Funciona el Nuevo Sistema

### Concepto: Carpeta Molde

**DISK-2026** es una "carpeta molde" que contiene snapshots de backup organizados por fecha.

Cada vez que haces un backup, creas una nueva carpeta dentro de `DISK-2026/` con el formato:
```
DISK-2026-MM-DD
```

### Estructura Completa

```
Beta/
├── README.md
└── BACKS-2026/
    ├── BACKS-2026.md
    └── DISK-2026/
        ├── DISK-2026.md                    ← Instrucciones
        ├── DISK-2026-01-15/                ← Backup del 15 enero
        │   ├── DISK-2026-01-15.md
        │   ├── Documentos/
        │   ├── Proyectos/
        │   └── Configuraciones/
        ├── DISK-2026-02-01/                ← Backup del 1 febrero
        │   ├── DISK-2026-02-01.md
        │   └── [contenido del backup]
        └── DISK-2026-02-04/                ← Backup del 4 febrero (ejemplo)
            ├── DISK-2026-02-04.md
            └── .gitkeep
```

---

## Uso Práctico

### Crear un Nuevo Backup

**Paso 1:** Navega a la carpeta DISK del año actual
```bash
cd Sistema_ABGD/ABGD-2026-02-04/Beta/BACKS-2026/DISK-2026/
```

**Paso 2:** Crea una carpeta con la fecha de hoy
```bash
# Formato: DISK-YYYY-MM-DD
mkdir DISK-2026-02-15
```

**Paso 3:** Copia el contenido a respaldar
```bash
# Desde Google Drive
cp -r ~/GoogleDrive/* DISK-2026-02-15/

# Desde un disco externo
cp -r /mnt/usb/* DISK-2026-02-15/

# Desde tu PC
cp -r ~/Documentos DISK-2026-02-15/
cp -r ~/Proyectos DISK-2026-02-15/
```

**Paso 4 (Opcional):** Crea un archivo .md descriptivo
```bash
# Copiar el template
cp DISK-2026-02-04/DISK-2026-02-04.md DISK-2026-02-15/DISK-2026-02-15.md

# Editar para añadir notas específicas del backup
```

### Ejemplo de Flujo de Trabajo Semanal

```bash
# Lunes 4 de febrero
mkdir DISK-2026/DISK-2026-02-04
cp -r ~/Trabajo/Proyectos/* DISK-2026/DISK-2026-02-04/

# Lunes 11 de febrero
mkdir DISK-2026/DISK-2026-02-11
cp -r ~/Trabajo/Proyectos/* DISK-2026/DISK-2026-02-11/

# Lunes 18 de febrero
mkdir DISK-2026/DISK-2026-02-18
cp -r ~/Trabajo/Proyectos/* DISK-2026/DISK-2026-02-18/
```

**Resultado:**
```
DISK-2026/
├── DISK-2026-02-04/
├── DISK-2026-02-11/
└── DISK-2026-02-18/
```

---

## Flexibilidad del Sistema

### Múltiples Orígenes en el Mismo Día

Puedes organizar por origen dentro de cada snapshot:

```
DISK-2026-02-04/
├── DISK-2026-02-04.md
├── GoogleDrive/
│   ├── Documentos/
│   └── Fotos/
├── OneDrive/
│   └── Trabajo/
├── PC-MSI/
│   └── Proyectos/
└── Disco-Externo/
    └── Backup-Completo/
```

### O Crear Snapshots Separados

```
DISK-2026/
├── DISK-2026-02-04-GoogleDrive/
├── DISK-2026-02-04-OneDrive/
├── DISK-2026-02-04-PC/
└── DISK-2026-02-05-DiscoExterno/
```

**Elige la organización que prefieras!**

---

## Archivo .md Descriptivo

Cada snapshot incluye (o debería incluir) un archivo `.md` con metadata:

```markdown
# DISK-2026-02-04

**Tipo:** SNAPSHOT DE BACKUP
**Fecha:** 2026-02-04

---

## Propósito

Backup semanal de proyectos activos y documentos de trabajo.

## Contenido

- Proyectos de investigación (A1-INV)
- Documentos universitarios (A2-UNI)
- Configuraciones de sistema

## Metadata del Backup

- **Fecha de creación:** 2026-02-04
- **Tipo de backup:** Completo
- **Origen:** PC MSI + Google Drive
- **Tamaño aproximado:** 15 GB
- **Notas:** Backup antes de actualización de sistema operativo

---
```

**Beneficio:** Sabes exactamente qué contiene cada backup sin tener que explorarlo.

---

## Gestión de Backups

### Limpieza de Backups Antiguos

```bash
# Listar todos los backups
ls -la DISK-2026/

# Ver cuántos backups tienes
ls -d DISK-2026/DISK-* | wc -l

# Eliminar backups específicos
rm -rf DISK-2026/DISK-2026-01-15

# Mantener solo los últimos 10 backups (ejemplo)
cd DISK-2026
ls -d DISK-* | sort | head -n -10 | xargs rm -rf
```

### Estrategia Recomendada

**Retención sugerida:**
- Última semana: Todos los backups diarios
- Último mes: Un backup por semana
- Último año: Un backup por mes
- Más de 1 año: Un backup por trimestre

**Ejemplo:**
```
DISK-2026/
├── DISK-2026-02-03/  ← Hace 1 día (mantener)
├── DISK-2026-02-04/  ← Hoy (mantener)
├── DISK-2026-01-27/  ← Hace 1 semana (mantener)
├── DISK-2026-01-01/  ← Hace 1 mes (mantener)
└── DISK-2025-10-01/  ← Hace 4 meses (mantener)

# Eliminar: backups intermedios > 1 semana
```

---

## Archivos Modificados

### Script Principal
- **[generar_estructura_abgd.py](generar_estructura_abgd.py)** (función `generate_beta()`)
  - Líneas 294-402: Generación de Beta completamente reescrita
  - Ahora crea: BACKS-YYYY → DISK-YYYY → DISK-YYYY-MM-DD
  - Incluye archivos .md descriptivos en cada nivel
  - Snapshot de ejemplo con fecha de generación

### Estructura Generada
- `Beta/BACKS-2026/DISK-2026/` - Carpeta molde
- `Beta/BACKS-2026/DISK-2026/DISK-2026-02-04/` - Snapshot de ejemplo
- Archivos .md descriptivos en cada carpeta

---

## Comparación de Conceptos

### Antes: Sistema de Orígenes Fijos

**Filosofía:** Organizar por origen del backup
- GDRIVE-2026 para Google Drive
- MSI-2026 para PC MSI
- etc.

**Dentro de cada origen:** Crear snapshots por fecha

**Limitación:** Necesitas saber de antemano todos los orígenes

### Ahora: Sistema de Molde Temporal

**Filosofía:** Organizar cronológicamente por fecha de backup
- DISK-2026 es el contenedor del año
- Dentro, snapshots por fecha: DISK-2026-MM-DD

**Dentro de cada snapshot:** Organiza como prefieras (por origen, por tipo, etc.)

**Ventaja:** Máxima flexibilidad, no necesitas predefinir nada

---

## Preguntas Frecuentes

### ¿Por qué "DISK" y no "BACKUP"?
→ DISK es más corto y consistente con el patrón de 4 letras del sistema (ABGD).

### ¿Puedo cambiar el nombre de DISK-2026?
→ Sí, pero mantén la consistencia. Si lo cambias, actualiza también el script.

### ¿Debo crear el archivo .md en cada snapshot?
→ Recomendado pero no obligatorio. Ayuda a documentar qué contiene cada backup.

### ¿Qué pasa si hago varios backups en el mismo día?
→ Opciones:
1. Usa sufijos: `DISK-2026-02-04-1`, `DISK-2026-02-04-2`
2. Organiza por origen dentro del snapshot
3. Añade timestamp: `DISK-2026-02-04-14h30`

### ¿Puedo usar otros años?
→ Sí, el script automáticamente usará el año actual al generar. Si necesitas crear manualmente otra carpeta de año: `mkdir BACKS-2027 && mkdir BACKS-2027/DISK-2027`

### ¿Cómo migro los backups del sistema anterior?
→ Si tienes backups en el sistema anterior:
```bash
# Ejemplo: Migrar GDRIVE-2026
mkdir DISK-2026/DISK-2026-02-04-GoogleDrive
cp -r GDRIVE-2026/* DISK-2026/DISK-2026-02-04-GoogleDrive/
```

---

## Ventajas Técnicas

1. **Consistencia con el Sistema General**
   - Sigue el mismo patrón de versionado por fecha que `ABGD-YYYY-MM-DD`
   - Nomenclatura uniforme en todo el sistema

2. **Escalabilidad**
   - Fácil añadir nuevos backups sin modificar estructura
   - No hay límite de orígenes predefinidos

3. **Simplicidad**
   - Un solo patrón: DISK-YYYY-MM-DD
   - Fácil de entender y usar

4. **Flexibilidad**
   - Organiza el contenido dentro como prefieras
   - Adapta a tu flujo de trabajo

---

## Próximos Pasos

1. **Explora la estructura generada:**
   ```bash
   cd Sistema_ABGD/ABGD-2026-02-04/Beta/BACKS-2026/DISK-2026/
   ls -la
   ```

2. **Lee los archivos .md:**
   - [Beta/README.md](Sistema_ABGD/ABGD-2026-02-04/Beta/README.md)
   - [Beta/BACKS-2026/DISK-2026/DISK-2026.md](Sistema_ABGD/ABGD-2026-02-04/Beta/BACKS-2026/DISK-2026/DISK-2026.md)

3. **Crea tu primer backup real:**
   ```bash
   mkdir DISK-2026/DISK-2026-02-05
   cp -r /tu/contenido/* DISK-2026/DISK-2026-02-05/
   ```

4. **Configura backups automáticos (opcional):**
   ```bash
   # Crear script de backup automático
   # Ver sección "Automatización" más abajo
   ```

---

## Automatización (Bonus)

### Script de Backup Automático

Crea un archivo `backup_automatico.sh`:

```bash
#!/bin/bash

# Configuración
FECHA=$(date +%Y-%m-%d)
BACKUP_DIR="Sistema_ABGD/ABGD-2026-02-04/Beta/BACKS-2026/DISK-2026"
ORIGEN="$HOME/Documentos"

# Crear carpeta de backup
mkdir -p "$BACKUP_DIR/DISK-$FECHA"

# Copiar contenido
cp -r "$ORIGEN"/* "$BACKUP_DIR/DISK-$FECHA/"

# Crear archivo .md descriptivo
cat > "$BACKUP_DIR/DISK-$FECHA/DISK-$FECHA.md" <<EOF
# DISK-$FECHA

**Tipo:** SNAPSHOT DE BACKUP
**Fecha:** $FECHA

---

## Contenido

Backup automático de Documentos

## Metadata del Backup

- **Fecha de creación:** $FECHA
- **Tipo de backup:** Automático
- **Origen:** ~/Documentos
- **Script:** backup_automatico.sh

---
EOF

echo "✓ Backup completado: DISK-$FECHA"
```

### Programar con Cron (Linux/Mac)

```bash
# Editar crontab
crontab -e

# Backup semanal (cada lunes a las 9 AM)
0 9 * * 1 /ruta/a/backup_automatico.sh

# Backup diario (cada día a las 23:00)
0 23 * * * /ruta/a/backup_automatico.sh
```

### Programar con Task Scheduler (Windows)

1. Abre "Programador de tareas"
2. Crear tarea básica
3. Selecciona el script .bat o PowerShell
4. Define frecuencia (diaria, semanal, etc.)

---

**Sistema actualizado por:** Claude Code
**Implementado por:** David
**Fecha:** 2026-02-04
**Versión:** ABGD v1.2 (Beta con sistema de molde DISK)
