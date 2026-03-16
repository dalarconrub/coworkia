# Sistema ABGD - Directorio de Versiones

Este directorio contiene las diferentes versiones de la estructura ABGD generadas a lo largo del tiempo.

---

## Estructura de Versiones

Cada vez que ejecutas el script `generar_estructura_abgd.py`, se crea una nueva carpeta con la fecha de generación:

```
Sistema_ABGD/
├── README.md (este archivo)
├── ABGD-2026-02-04/    ← Primera generación (hoy)
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

---

## ¿Por Qué Varias Versiones?

Este sistema de versionado te permite:

1. **Mantener histórico de cambios**
   - Si actualizas el Excel con nuevas áreas/bloques/contextos
   - Si quieres probar diferentes configuraciones
   - Si necesitas recuperar una versión anterior

2. **Comparar evoluciones**
   - Ver cómo ha crecido tu sistema
   - Comparar estructuras de diferentes momentos

3. **Backup de la estructura misma**
   - Cada carpeta es independiente
   - Puedes eliminar versiones antiguas sin afectar las actuales

---

## Versión Activa

**Versión actual:** `ABGD-2026-02-04/`

Para usar esta versión en Obsidian:
1. Abre Obsidian
2. Selecciona "Abrir carpeta como vault"
3. Navega a `Sistema_ABGD/ABGD-2026-02-04/Alpha/`

---

## Gestión de Versiones

### Mantener Solo la Última Versión

Si solo quieres trabajar con la versión más reciente:
```bash
# Eliminar versiones antiguas (ejemplo)
rm -rf Sistema_ABGD/ABGD-2026-01-15/
rm -rf Sistema_ABGD/ABGD-2026-02-01/
```

### Mantener Versiones Específicas

Recomendación: Mantener versiones de:
- Última generación (actual)
- Inicio de cada trimestre
- Cambios significativos en la estructura

### Comparar Versiones

```bash
# Ver diferencias en cantidad de archivos
find ABGD-2026-02-04 -type f | wc -l
find ABGD-2026-03-01 -type f | wc -l

# Ver estructura de cada versión
ls -R ABGD-2026-02-04/
ls -R ABGD-2026-03-01/
```

---

## Generar Nueva Versión

Para generar una nueva versión con la fecha actual:

```bash
# Desde el directorio ABGD/
python generar_estructura_abgd.py
```

Esto creará automáticamente `Sistema_ABGD/ABGD-YYYY-MM-DD/` con la fecha de hoy.

### Con Opciones

```bash
# Modo simulación (no crea archivos)
python generar_estructura_abgd.py --dry-run

# Con Excel personalizado
python generar_estructura_abgd.py --excel-path ./mi_excel.xlsx

# En otro directorio
python generar_estructura_abgd.py --root-dir ./Otro_Sistema_ABGD
```

---

## Historial de Versiones

| Fecha | Versión | Notas |
|-------|---------|-------|
| 2026-02-04 | ABGD-2026-02-04 | Versión inicial del sistema ABGD |

**Actualiza esta tabla** cada vez que generes una nueva versión anotando cambios importantes.

---

## Archivos del Sistema

En el directorio padre (`ABGD/`) encontrarás:

- **[generar_estructura_abgd.py](../generar_estructura_abgd.py)** - Script de generación
- **[Sistema_ABC_Completo_Final.xlsx](../Sistema_ABC_Completo_Final.xlsx)** - Base de datos fuente
- **[Sistema_ABGD_Documentacion_Completa.md](../Sistema_ABGD_Documentacion_Completa.md)** - Documentación completa
- **[GUIA_RAPIDA_INICIO.md](../GUIA_RAPIDA_INICIO.md)** - Guía de inicio rápido
- **[requirements.txt](../requirements.txt)** - Dependencias Python

---

## Limpieza de Versiones Antiguas

### Script de Limpieza (Ejemplo)

Puedes crear un script para mantener solo las últimas N versiones:

```bash
#!/bin/bash
# mantener_ultimas_versiones.sh

# Mantener solo las últimas 3 versiones
cd Sistema_ABGD
ls -d ABGD-* | sort -r | tail -n +4 | xargs rm -rf
```

**Usa con precaución:** Siempre verifica antes de eliminar versiones.

---

**Generado:** 2026-02-04
**Sistema:** ABGD v1.0 con versionado automático
