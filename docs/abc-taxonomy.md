# ABC Taxonomy

Taxonomía estructural maestra de Coworkia en Notion.

Jerarquía:

```text
Área -> Bloque -> Contexto
```

## A0-GTD

- `B00-GTD`: ejecución (`MAR`)
  - `C000-GTD`
- `B0A-INX`: integración y trazabilidad entre sistemas
- `B0A-INX` (contextos):
  - `C0A1-TODOIST` → base `TODOIST-TAREAS` (relación PTN + ABC)
  - `C0A2-NOTION` → base `NOTION` (histórico PTN + ABC)
  - `C0A3-OBSIDIAN` → base `OBSIDIAN` (histórico Obsidian + PTN + ABC)
  - Relaciones cruzadas:
    - `TODOIST-TAREAS` → `NOTION`
    - `NOTION` → `OBSIDIAN`
    - `OBSIDIAN` → `NOTION` (retorno)
- `B0B-ABC`: taxonomía del sistema
- `B0B-ABC` (contextos):
  - `C0B4-AREA` → base `ABC-Areas`
  - `C0B5-BLOQUE` → base `ABC-Bloques`
  - `C0B6-CONTEXTO` → base `ABC-Contextos`
- `B0C-PLA`: planificación y dirección (`PTN`)
  - `C0C7-PROYECTOS`
  - `C0C8-TAREAS`
  - `C0C9-NOTAS`

## A1-INV

- `B11-CVT`
  - `C110-CVT`
  - `C111-ANE`
  - `C112-ACA`
  - `C113-ACR`
- `B12-LAB`
  - `C120-LAB`
  - `C124-PRY`
  - `C125-DAT`
  - `C126-DIR`
- `B13-PUB`
  - `C130-PUB`
  - `C137-ART`
  - `C138-CON`
  - `C139-MAN`

## A2-UNI

- `B24-DOC`
  - `C240-DOC`
  - `C241-GRA`
  - `C242-MAS`
  - `C243-POS`
- `B25-FOR`
  - `C250-FOR`
  - `C254-PDI`
  - `C255-EST`
  - `C256-CUR`
- `B26-GES`
  - `C260-GES`
  - `C267-UPO`
  - `C268-MIN`
  - `C269-EVA`

## A3-VIT

- `B37-ORG`
  - `C370-ORG`
  - `C371-ADM`
  - `C372-PER`
  - `C373-SOC`
- `B38-TEC`
  - `C380-TEC`
  - `C384-INF`
  - `C386-STA`
  - `C387-IAA`
- `B39-DES`
  - `C390-DES`
  - `C397-FIS`
  - `C398-MEN`
  - `C399-MUS`

## A4-ARX

- `B40-REF`
  - `C400-REF`
    - `KIT` (catálogo maestro)
- `B4X-LIB`
  - `C4x0-LIB`
  - `C4x1-FIC`
  - `C4x2-SCI`
  - `C4x3-ENS`
  - `BIB` (catálogo bibliográfico)
- `B4Y-MED`
  - `C4y0-MED`
  - `C4y4-VID`
  - `C4y5-AUD`
  - `C4y6-MP3`
- `B4Z-APP`
  - `C4z0-APP`
  - `C4z7-MOC`
  - `C4z8-WEB`
  - `C4z9-SOF`
  - `REP` (catálogo de repositorios)

## Fuente

- Export CSV legado en [Sistemas/ABC](/abs/path/not-applicable)
- Regla de reconstrucción: si hay redefiniciones, la última fila del CSV es la válida

## Relaciones y rollups ABC

En las bases `ABC`:

- `ABC-Bloques`:
  - `Area Rel` → relación con `ABC-Areas`
  - `Area (nombre)` → rollup del nombre del área
- `ABC-Contextos`:
  - `Bloque Rel` → relación con `ABC-Bloques`
  - `Bloque (nombre)` → rollup del nombre del bloque
  - `Area (via Bloque)` → rollup del área derivada
