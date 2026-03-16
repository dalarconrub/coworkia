# Beta - Backups Cronológicos

**Tipo:** BACKUPS ESTRUCTURADOS
**Organización:** Cronológica por año y fecha

---

## Propósito

Beta contiene copias de seguridad periódicas organizadas cronológicamente por año y fecha.

## Estructura

- **BACKS-YYYY/**: Backups del año
  - **DISK-YYYY/**: Carpeta molde para backups
    - **DISK-YYYY-MM-DD/**: Snapshots por fecha

## Uso

Cada vez que realices un backup, crea una carpeta con la fecha dentro de DISK-YYYY:

```bash
# Ejemplo
mkdir Beta/BACKS-2026/DISK-2026/DISK-2026-02-04
# Copia tus archivos dentro
```

---

*Generado automáticamente por el script de estructura ABGD*
