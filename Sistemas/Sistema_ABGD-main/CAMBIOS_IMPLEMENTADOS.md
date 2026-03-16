# Cambios Implementados - Sistema de Versionado

**Fecha:** 04 de febrero de 2026
**Modificación:** Sistema de versionado automático por fecha

---

## ¿Qué Cambió?

### Antes

```
ABGD/
└── Sistema_ABGD/
    ├── Alpha/
    ├── Beta/
    ├── Delta/
    └── Gamma/
```

Cada vez que se ejecutaba el script, se sobrescribía la estructura existente.

### Ahora

```
ABGD/
└── Sistema_ABGD/
    ├── README.md
    ├── ABGD-2026-02-04/    ← Versión de hoy
    │   ├── Alpha/
    │   ├── Beta/
    │   ├── Delta/
    │   └── Gamma/
    ├── ABGD-2026-03-01/    ← Si regeneras en marzo
    │   ├── Alpha/
    │   ├── Beta/
    │   ├── Delta/
    │   └── Gamma/
    └── ABGD-2026-06-15/    ← Si regeneras en junio
        └── ...
```

Cada ejecución crea una carpeta nueva con la fecha: `ABGD-YYYY-MM-DD/`

---

## Ventajas del Sistema de Versionado

### 1. Historial de Cambios
- Mantén múltiples versiones de tu estructura
- Compara cómo ha evolucionado el sistema
- No pierdes configuraciones anteriores

### 2. Seguridad
- No se sobrescribe nada
- Cada versión es independiente
- Fácil recuperación de versiones anteriores

### 3. Experimentación
- Prueba cambios en el Excel sin miedo
- Genera nuevas versiones sin afectar las actuales
- Compara resultados fácilmente

### 4. Backup Implícito
- Cada generación es un snapshot de la configuración
- Puedes eliminar versiones antiguas cuando quieras
- Preserva el histórico de tu sistema

---

## Modificaciones Técnicas

### En el Script Python

**Cambio 1: Constructor de la clase**
```python
# Ahora calcula la fecha y crea la ruta con fecha
self.current_date = now.strftime('%Y-%m-%d')
self.container_dir = Path(root_dir)
self.dated_folder = f"ABGD-{self.current_date}"
self.root_dir = self.container_dir / self.dated_folder
```

**Cambio 2: Creación de directorios**
```python
# Crea primero el contenedor, luego la carpeta con fecha
self.create_directory(self.container_dir)
self.create_directory(self.root_dir)
```

**Cambio 3: Logging mejorado**
```python
logger.info(f"Directorio contenedor: {self.container_dir}")
logger.info(f"Carpeta con fecha: {self.dated_folder}")
logger.info(f"Ruta completa: {self.root_dir}")
```

**Cambio 4: Argumentos actualizados**
```python
# Default cambió de ./ABGD_Sistema a ./Sistema_ABGD
--root-dir default: './Sistema_ABGD'
# Ahora crea: ./Sistema_ABGD/ABGD-YYYY-MM-DD/
```

---

## Uso del Nuevo Sistema

### Generar Primera Versión

```bash
python generar_estructura_abgd.py
```

**Resultado:**
```
Sistema_ABGD/
└── ABGD-2026-02-04/
    ├── Alpha/
    ├── Beta/
    ├── Delta/
    └── Gamma/
```

### Generar Segunda Versión (Otro Día)

```bash
# El 1 de marzo
python generar_estructura_abgd.py
```

**Resultado:**
```
Sistema_ABGD/
├── ABGD-2026-02-04/  ← Primera versión (preservada)
└── ABGD-2026-03-01/  ← Nueva versión
```

### Verificar Versiones Disponibles

```bash
ls Sistema_ABGD/
```

**Salida:**
```
ABGD-2026-02-04
ABGD-2026-03-01
ABGD-2026-06-15
README.md
```

---

## Flujo de Trabajo Recomendado

### Cuándo Generar Nueva Versión

**Genera nueva versión cuando:**
1. Actualizas el Excel con nuevas áreas/bloques/contextos
2. Cambias la estructura del sistema
3. Inicio de cada trimestre (backup de la configuración)
4. Antes de hacer cambios significativos

**NO es necesario generar nueva versión:**
- Cuando trabajas en tus notas de Obsidian
- Cuando añades contenido a Delta/Gamma
- En el uso diario del sistema

### Gestión de Versiones

**Mantener:**
- Última versión (actual)
- Versión de inicio de año
- Versiones de cambios importantes

**Eliminar:**
- Versiones intermedias sin cambios significativos
- Versiones de prueba que no se usaron
- Versiones >1 año sin uso

### Ejemplo de Gestión

```bash
# Enero 2026: Versión inicial
python generar_estructura_abgd.py
# Crea: ABGD-2026-01-01/

# Febrero: Pruebas
python generar_estructura_abgd.py
# Crea: ABGD-2026-02-04/

# Abril: Cambio en estructura (añadiste nuevos contextos)
python generar_estructura_abgd.py
# Crea: ABGD-2026-04-01/

# Julio: Nueva versión trimestral
python generar_estructura_abgd.py
# Crea: ABGD-2026-07-01/

# Mantener: 2026-01-01, 2026-04-01, 2026-07-01 (última)
# Eliminar: 2026-02-04 (fue solo prueba)
```

---

## Integración con Obsidian

### Trabajar con Versión Específica

**Opción 1: Última versión siempre**
1. Abre Obsidian
2. Selecciona la carpeta de la versión más reciente
3. Ejemplo: `Sistema_ABGD/ABGD-2026-02-04/Alpha/`

**Opción 2: Crear enlace simbólico (avanzado)**
```bash
# Crear enlace a la versión actual
ln -s Sistema_ABGD/ABGD-2026-02-04/Alpha Sistema_ABGD/Alpha_Actual

# Obsidian siempre apunta a Alpha_Actual
# Actualiza el enlace cuando generes nueva versión
```

### Migrar Contenido Entre Versiones

Si generas una nueva versión y quieres migrar tu trabajo:

```bash
# Copiar notas de Alpha de versión anterior a nueva
cp -r Sistema_ABGD/ABGD-2026-02-04/Alpha/* \
      Sistema_ABGD/ABGD-2026-03-01/Alpha/

# O copiar selectivamente carpetas específicas
cp -r Sistema_ABGD/ABGD-2026-02-04/Alpha/A1-INV/ \
      Sistema_ABGD/ABGD-2026-03-01/Alpha/
```

**Nota:** Normalmente NO necesitas migrar entre versiones. Solo generas nueva versión si cambia la ESTRUCTURA, no si cambias el contenido.

---

## Comparación de Versiones

### Ver Diferencias en Estructura

```bash
# Listar áreas en cada versión
ls Sistema_ABGD/ABGD-2026-02-04/Alpha/
ls Sistema_ABGD/ABGD-2026-03-01/Alpha/

# Comparar cantidad de contextos
find Sistema_ABGD/ABGD-2026-02-04 -name "C*" -type d | wc -l
find Sistema_ABGD/ABGD-2026-03-01 -name "C*" -type d | wc -l

# Usar diff para comparar
diff -r Sistema_ABGD/ABGD-2026-02-04/Alpha/ \
        Sistema_ABGD/ABGD-2026-03-01/Alpha/
```

---

## Preguntas Frecuentes

### ¿Qué versión debo usar en Obsidian?
→ Siempre la más reciente. Cambia a nueva versión solo si cambió la estructura.

### ¿Puedo eliminar versiones antiguas?
→ Sí, cada versión es independiente. Elimina las que no necesites.

### ¿Se duplica todo el contenido en cada versión?
→ Solo se duplica la ESTRUCTURA (carpetas y .md descriptivos). Tu contenido real (notas, archivos) va en una sola versión.

### ¿Cuántas versiones debo mantener?
→ Recomendado: Última + versiones de cambios importantes. Típicamente 2-3 versiones.

### ¿Ocupa mucho espacio tener varias versiones?
→ No mucho. Cada versión son ~130 archivos .md pequeños (~242 KB total). 10 versiones = ~2.4 MB.

### Si actualizo el Excel, ¿debo regenerar?
→ Sí. Genera nueva versión para reflejar los cambios del Excel.

### ¿Puedo usar diferentes Excels para diferentes versiones?
→ Sí:
```bash
python generar_estructura_abgd.py --excel-path ./config_v1.xlsx
python generar_estructura_abgd.py --excel-path ./config_v2.xlsx
```

---

## Archivos Modificados

### Script Principal
- [generar_estructura_abgd.py](generar_estructura_abgd.py)
  - Líneas 23-36: Constructor modificado
  - Líneas 605-611: Generación con contenedor y fecha
  - Líneas 620-624: Argumentos actualizados
  - Líneas 629-641: Documentación actualizada

### Nuevos Archivos
- [Sistema_ABGD/README.md](Sistema_ABGD/README.md) - Guía de versiones
- [CAMBIOS_IMPLEMENTADOS.md](CAMBIOS_IMPLEMENTADOS.md) - Este archivo

---

## Estadísticas

**Estructura por versión:**
- Directorios: 112 (1 contenedor + 111 de estructura)
- Archivos: 131 (110 .md + 21 .gitkeep)
- Tamaño aproximado: ~242 KB por versión

**Tiempo de generación:**
- < 1 segundo por versión completa

---

## Próximos Pasos

1. **Usa la versión generada:** [Sistema_ABGD/ABGD-2026-02-04/](Sistema_ABGD/ABGD-2026-02-04/)

2. **Configura Obsidian:** Apunta a [Sistema_ABGD/ABGD-2026-02-04/Alpha/](Sistema_ABGD/ABGD-2026-02-04/Alpha/)

3. **Actualiza cuando necesites:** Si cambias el Excel, genera nueva versión

4. **Mantén limpio:** Elimina versiones antiguas periódicamente

---

**Sistema actualizado por:** Claude Code
**Implementado por:** David
**Fecha:** 2026-02-04
**Versión del sistema:** ABGD v1.1 (con versionado automático)
