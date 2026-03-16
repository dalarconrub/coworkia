# 📤 Actualizar GitHub - Guía de Uso

Scripts para subir cambios a GitHub automáticamente sin escribir comandos git.

## 🚀 Uso Rápido

### Opción 1: Script Batch (`.bat`)
**Más fácil - Solo doble clic:**

1. Haz doble clic en `actualizar_github.bat`
2. El script automáticamente:
   - Agrega todos los cambios
   - Crea un commit con fecha y hora
   - Sube todo a GitHub
3. Presiona cualquier tecla para cerrar

### Opción 2: Script PowerShell (`.ps1`)
**Más flexible - Permite mensajes personalizados:**

```powershell
# Con mensaje automático (fecha/hora)
.\actualizar_github.ps1

# Con tu propio mensaje
.\actualizar_github.ps1 "Agregado nuevo módulo de exportación"
```

## 📋 ¿Qué hace el script?

```
git add .                              # Agrega todos los cambios
git commit -m "mensaje"                # Crea commit
git push                               # Sube a GitHub
```

## ✅ Ventajas

- **Sin comandos**: No necesitas recordar comandos git
- **Rápido**: Un solo clic o comando
- **Automático**: Detecta cambios y los sube
- **Seguro**: Solo sube si hay cambios

## ⚠️ Nota Importante

Estos scripts suben **todos** los cambios en tu carpeta. Si quieres más control sobre qué archivos subir, usa los comandos git manualmente.

## 🔧 Solución de Problemas

**"Permission denied"**: Usa el script `.bat` en lugar del `.ps1`

**"Not a git repository"**: Asegúrate de estar en la carpeta del proyecto

**"Nothing to commit"**: No hay cambios para subir

## 📚 Comandos Git Manuales

Si prefieres control total:

```bash
git add .                              # Agregar cambios
git status                             # Ver estado
git commit -m "tu mensaje"            # Crear commit
git push                               # Subir a GitHub
```
