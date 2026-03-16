# Script para actualizar GitHub automáticamente
# Uso: .\actualizar_github.ps1 ["mensaje opcional"]

param(
    [string]$mensaje = ""
)

Write-Host "🔄 Actualizando GitHub..." -ForegroundColor Cyan

# Agregar todos los cambios
Write-Host "`n📦 Agregando cambios..." -ForegroundColor Yellow
git add .

# Verificar si hay cambios
$status = git status --porcelain
if ([string]::IsNullOrEmpty($status)) {
    Write-Host "✅ No hay cambios para subir" -ForegroundColor Green
    exit 0
}

# Crear mensaje de commit
if ([string]::IsNullOrEmpty($mensaje)) {
    $fecha = Get-Date -Format "yyyy-MM-dd HH:mm"
    $mensaje = "Actualización automática - $fecha"
}

# Hacer commit
Write-Host "`n💾 Creando commit..." -ForegroundColor Yellow
git commit -m $mensaje

# Subir a GitHub
Write-Host "`n⬆️  Subiendo a GitHub..." -ForegroundColor Yellow
git push

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ ¡GitHub actualizado exitosamente!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Error al actualizar GitHub" -ForegroundColor Red
    exit 1
}
