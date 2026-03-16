# Checklist de validación de exportables MAR

Antes de considerar cerrado el paquete, verificar:

## Archivos maestros (SVG)

- [ ] `SVG/MAR_logo_full.svg` - Logo completo oficial
  - [ ] Triángulo con 3 segmentos (naranja, azul, plateado)
  - [ ] Espiral áurea dorada
  - [ ] Texto ES: "META ACCIÓN RESULTADO" con colores correctos
  - [ ] Línea separadora dorada
  - [ ] Texto EN: "GOAL • ACTION • OUTCOME" con colores correctos

- [ ] `SVG/MAR_symbol.svg` - Solo símbolo (sin texto)

## Versiones PNG

- [ ] `PNG/MAR_logo_full_3000px.png` - Alta resolución (300 dpi)
- [ ] `PNG/MAR_logo_full_1500px.png` - Resolución media
- [ ] `PNG/MAR_logo_full_800px.png` - Resolución web
- [ ] `PNG/MAR_logo_darkbg.png` - Con fondo oscuro (#0B1220)
- [ ] `PNG/MAR_logo_compact.png` - Versión compacta (símbolo + ES, sin EN)

## Versiones monocromas

- [ ] `MONO/MAR_logo_black.svg` - Versión negra (SVG)
- [ ] `MONO/MAR_logo_black.png` - Versión negra (PNG)
- [ ] `MONO/MAR_logo_white.svg` - Versión blanca (SVG)
- [ ] `MONO/MAR_logo_white.png` - Versión blanca (PNG)

## Iconos

- [ ] `ICONS/MAR_icon.svg` - Icono principal (solo símbolo)
- [ ] `ICONS/MAR_icon_256.png` - Icono 256px
- [ ] `ICONS/MAR_icon_128.png` - Icono 128px
- [ ] `ICONS/MAR_icon_64.png` - Icono 64px (mínimo visible)

### Iconos semánticos (opcionales)

- [ ] `ICONS/MAR_icon_meta.svg` - Icono resaltando lado naranja
- [ ] `ICONS/MAR_icon_accion.svg` - Icono resaltando lado azul
- [ ] `ICONS/MAR_icon_resultado.svg` - Icono resaltando lado plateado

## Validación técnica

- [ ] Colores HEX exactos según manual
- [ ] Texto ES + EN correcto
- [ ] Versiones monocromas legibles
- [ ] Iconos visibles a 64 px
- [ ] Fondo oscuro probado
- [ ] Área de seguridad respetada
- [ ] Proporciones no distorsionadas

## Notas

Todos los archivos PNG deben tener fondo transparente (salvo `MAR_logo_darkbg.png`).

Todos los archivos deben derivar del SVG maestro para mantener consistencia.
