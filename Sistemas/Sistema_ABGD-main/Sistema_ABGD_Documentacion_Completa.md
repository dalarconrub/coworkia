# Sistema de Gestión Documental ABGD
## Documentación Completa

**Versión:** 1.0 Definitiva  
**Fecha:** 04 de febrero de 2026  
**Autor:** David

---

## Tabla de Contenidos

1. [Visión General del Sistema](#visión-general-del-sistema)
2. [Estructura de Primer Nivel: Alpha-Beta-Delta-Gamma](#estructura-de-primer-nivel)
3. [Alpha: Sistema Johnny Decimal](#alpha-sistema-johnny-decimal)
4. [Beta: Backups Cronológicos](#beta-backups-cronológicos)
5. [Delta: Archivo Clasificado](#delta-archivo-clasificado)
6. [Gamma: Almacenamiento Temporal](#gamma-almacenamiento-temporal)
7. [Tablas de Referencia Completas](#tablas-de-referencia-completas)
8. [Flujos de Trabajo](#flujos-de-trabajo)
9. [Mantenimiento del Sistema](#mantenimiento-del-sistema)

---

## Visión General del Sistema

### Filosofía ABGD

El sistema ABGD es un método de organización documental jerárquico que separa claramente cuatro contextos fundamentales de gestión de información:

- **Alpha (A)**: Núcleo de trabajo activo (Vault de Obsidian)
- **Beta (B)**: Backups cronológicos estructurados
- **Delta (Δ)**: Archivo clasificado semánticamente
- **Gamma (Γ)**: Almacenamiento temporal

### Principios Fundamentales

1. **Separación de contextos**: Cada carpeta tiene propósito y ciclo de vida distintos
2. **Nomenclatura consistente**: Prefijos heredados en todos los niveles
3. **Progresión natural**: Los archivos fluyen de indefinido (Gamma) a estructurado (Delta/Alpha)
4. **Núcleo activo limpio**: Alpha solo contiene trabajo en curso
5. **Backups no intrusivos**: Beta preserva sin reorganizar
6. **Archivo semántico**: Delta organiza por significado, no por fecha

---

## Estructura de Primer Nivel

```
Sistema_ABGD/
├── Alpha/          # Vault de Obsidian - Trabajo activo
├── Beta/           # Backups cronológicos
├── Delta/          # Archivo clasificado por tipo
└── Gamma/          # Almacenamiento temporal cronológico
```

---

## Alpha: Sistema Johnny Decimal

### Visión General

Alpha es el vault principal de Obsidian organizado con un **sistema Johnny Decimal adaptado** de tres niveles jerárquicos:

**ÁREA (A) → BLOQUE (B) → CONTEXTO (C)**

### Nivel 1: ÁREAS (A)

Las áreas representan las grandes divisiones de vida y trabajo.

```
Alpha/
├── A0-GTD/          # Getting Things Done - Sistema operativo
├── A1-INV/          # Investigación académica
├── A2-UNI/          # Universidad y docencia
├── A3-VIT/          # Vital - Información personal
└── A4-ARC/          # Archivo - Conocimiento consolidado
```

#### Tabla de Áreas

| Código | Nombre | Descripción | Estado |
|--------|--------|-------------|--------|
| A0-GTD | Getting Things Done | Sistema operativo diario - GTD | Activo |
| A1-INV | Investigación | Investigación académica y proyectos | Activo |
| A2-UNI | Universidad | Contenido universitario y docencia | Activo |
| A3-VIT | Vital | Información personal y vida | Activo |
| A4-ARC | Archivo | Archivo de conocimiento consolidado | Activo |

---

### Nivel 2: BLOQUES (B)

Los bloques son agrupaciones temáticas dentro de cada área.

**Nomenclatura:**
- Para A0: `B0[A-Z]-[CÓDIGO]` (usa letras)
- Para A1-A9: `B[Área][0-9]-[CÓDIGO]` (usa números)

#### A0-GTD: Getting Things Done

```
A0-GTD/
├── B0A-RED/         # Recursos y documentos
├── B0B-ABC/         # Sistema ABC (Meta-documentación)
└── B0C-PLA/         # Planificación
```

#### A1-INV: Investigación

```
A1-INV/
├── B11-CVT/         # Curriculum Vitae
├── B12-LAB/         # Laboratorio
└── B13-PUB/         # Publicaciones
```

#### A2-UNI: Universidad

```
A2-UNI/
├── B24-DOC/         # Docencia
├── B25-FOR/         # Formación
└── B26-GES/         # Gestión
```

#### A3-VIT: Vital

```
A3-VIT/
├── B37-ORG/         # Organización personal
├── B38-TEC/         # Tecnología personal
└── B39-DES/         # Desarrollo personal
```

#### A4-ARC: Archivo

```
A4-ARC/
├── B4X-LIB/         # Libros/Biblioteca
├── B4Y-MED/         # Media/Medios
└── B4Z-APP/         # Aplicaciones
```

#### Tabla Completa de Bloques

| Código | Nombre | Área | Descripción |
|--------|--------|------|-------------|
| B0A-RED | Recursos y documentos | A0-GTD | Recursos y documentos |
| B0B-ABC | Sistema ABC | A0-GTD | Meta-sistema de documentación |
| B0C-PLA | Planificación | A0-GTD | Sistema de planificación |
| B11-CVT | Curriculum Vitae | A1-INV | Curriculum Vitae |
| B12-LAB | Laboratorio | A1-INV | Trabajo de laboratorio |
| B13-PUB | Publicaciones | A1-INV | Gestión de publicaciones |
| B24-DOC | Docencia | A2-UNI | Docencia |
| B25-FOR | Formación | A2-UNI | Cursos y formación |
| B26-GES | Gestión | A2-UNI | Gestión administrativa |
| B37-ORG | Organización | A3-VIT | Organización personal |
| B38-TEC | Tecnología | A3-VIT | Tecnología personal |
| B39-DES | Desarrollo | A3-VIT | Desarrollo personal |
| B4X-LIB | Libros/Biblioteca | A4-ARC | Biblioteca |
| B4Y-MED | Media/Medios | A4-ARC | Contenido multimedia |
| B4Z-APP | Aplicaciones | A4-ARC | Apps y Recursos online |

---

### Nivel 3: CONTEXTOS (C)

Los contextos son las carpetas específicas donde residen las notas.

**Nomenclatura:** `C[Prefijo del bloque][0-9]-[CÓDIGO]`

**Patrón especial:**
- Contextos base: `C[Prefijo]0` (sin código de 3 letras)
- Contextos específicos: Números no consecutivos para permitir expansión

#### Tabla Completa de Contextos

##### A0-GTD: Getting Things Done

| Contexto | Nombre | Bloque | Descripción |
|----------|--------|--------|-------------|
| C0A0 | Base recursos | B0A-RED | Contexto base del bloque recursos |
| C0A1-REF | Referencias | B0A-RED | Referencias y recursos generales |
| C0A2-ENL | Enlaces | B0A-RED | Gestión de enlaces |
| C0A3-DIR | Directorio | B0A-RED | Directorio de recursos |
| C0B0 | Base ABC | B0B-ABC | Contexto base del bloque ABC |
| C0B4-ARE | Doc. nivel ÁREA | B0B-ABC | Documentación del sistema de áreas |
| C0B5-BLQ | Doc. nivel BLOQUE | B0B-ABC | Documentación del sistema de bloques |
| C0B6-CTX | Doc. nivel CONTEXTO | B0B-ABC | Documentación del sistema de contextos |
| C0C0 | Base planificación | B0C-PLA | Contexto base del bloque planificación |
| C0C7-PRY | Proyectos | B0C-PLA | Gestión de proyectos |
| C0C8-TAR | Tareas | B0C-PLA | Gestión de tareas |
| C0C9-NOT | Notas | B0C-PLA | Notas generales |

##### A1-INV: Investigación

| Contexto | Nombre | Bloque | Descripción |
|----------|--------|--------|-------------|
| C110 | Base cuantitativo | B11-CVT | Contexto base del bloque |
| C111-REP | Repositorios | B11-CVT | Reportes de investigación |
| C112-ACR | Acreditaciones | B11-CVT | Acrónimos y acreditaciones |
| C113-CAT | Catedra | B11-CVT | Catálogo y categorías |
| C120 | Base laboratorio | B12-LAB | Contexto base del bloque |
| C124-PRY | Proyectos | B12-LAB | Proyectos de laboratorio |
| C125-EXP | Experimentos | B12-LAB | Experimentos |
| C126-DIR | Direccion | B12-LAB | Direccion tesis tfg tfm |
| C130 | Base publicaciones | B13-PUB | Contexto base del bloque |
| C137-ART | Artículos | B13-PUB | Artículos científicos |
| C138-CON | Congresos/Conferencias | B13-PUB | Congresos y conferencias |
| C139-EVA | Evaluación | B13-PUB | Revisiones y evaluacion de proyectos |

##### A2-UNI: Universidad

| Contexto | Nombre | Bloque | Descripción |
|----------|--------|--------|-------------|
| C240 | Base docencia | B24-DOC | Contexto base del bloque |
| C241-GRA | Grado | B24-DOC | Docencia de grado |
| C242-MAS | Máster | B24-DOC | Docencia de máster |
| C243-POS | Posgrado | B24-DOC | Docencia de posgrado |
| C250 | Base formación | B25-FOR | Contexto base del bloque |
| C254-PDI | Personal Docente Investigador | B25-FOR | Formación para PDI |
| C255-EST | Estudios personales | B25-FOR | Formación personal |
| C256-MOC | MOOCs | B25-FOR | Cursos masivos online |
| C260 | Base gestión | B26-GES | Contexto base del bloque |
| C267-UPO | Universidad Pablo de Olavide | B26-GES | Gestión UPO |
| C268-UNED | UNED | B26-GES | Gestión UNED |
| C269-MIN | Ministerio | B26-GES | Gestión ministerio |

##### A3-VIT: Vital

| Contexto | Nombre | Bloque | Descripción |
|----------|--------|--------|-------------|
| C370 | Base organización | B37-ORG | Contexto base del bloque organización |
| C371-ADM | Administración | B37-ORG | Administración y gestión personal |
| C372-PER | Personal | B37-ORG | Asuntos personales |
| C373-SOC | Social | B37-ORG | Social y relaciones |
| C380 | Base tecnología | B38-TEC | Contexto base del bloque tecnología |
| C386-IAA | Inteligencia Artificial Aplicada | B38-TEC | Inteligencia Artificial aplicada |
| C384-INF | Informática | B38-TEC | Informática general |
| C385-STA | Estadistica | B38-TEC | Estadistica |
| C390 | Base desarrollo | B39-DES | Contexto base del bloque desarrollo |
| C397-FIS | Físico | B39-DES | Desarrollo físico y ejercicio |
| C398-MEN | Mental | B39-DES | Desarrollo mental y psicológico |
| C399-MUS | Música | B39-DES | Música y práctica musical |

##### A4-ARC: Archivo

| Contexto | Nombre | Bloque | Descripción |
|----------|--------|--------|-------------|
| C4X0-LIB | Base libros | B4X-LIB | Contexto base del bloque libros |
| C4X1-FIC | Ficción | B4X-LIB | Libros de ficción |
| C4X2-SCI | Ciencia/Técnico | B4X-LIB | Libros científicos y técnicos |
| C4X3-ENS | Ensayo | B4X-LIB | Ensayos |
| C4Y0-MED | Base media | B4Y-MED | Contexto base del bloque media |
| C4Y4-VID | Vídeos | B4Y-MED | Contenido en vídeo |
| C4Y5-AUD | Audio | B4Y-MED | Contenido de audio |
| C4Y6-MP3 | MP3/Música | B4Y-MED | Música MP3 |
| C4Z0-APP | Base aplicaciones | B4Z-APP | Contexto base del bloque aplicaciones |
| C4Z7-MOC | MOCs | B4Z-APP | Maps of Content |
| C4Z8-WEB | Web/Enlaces | B4Z-APP | Enlaces web y recursos online |
| C4Z9-SOF | Software | B4Z-APP | Software y aplicaciones |

---

### Sistema B0B-ABC: El Meta-Sistema

**Ubicación:** `A0-GTD/B0B-ABC/`

Este bloque especial contiene la **documentación completa del sistema de organización** - el "meta-nivel" que explica cómo funciona toda la estructura.

#### Estructura de B0B-ABC:

```
A0-GTD/B0B-ABC/
├── C0B4-ARE/
│   └── [Documentación del nivel ÁREA]
│
├── C0B5-BLQ/
│   └── [Documentación del nivel BLOQUE]
│
├── C0B6-CTX/
│   └── [Documentación del nivel CONTEXTO]
│
└── [Base de datos ABC en Notion]/
    ├── Vista BLOQUES
    │   └── Correspondencia BLOQUE → ÁREA
    │
    └── Vista CONTEXTOS
        └── Correspondencia CONTEXTO → BLOQUE → ÁREA
```

#### Propósito del Sistema ABC:

1. **Documentación centralizada**: Información sobre cómo funciona el sistema
2. **Índice maestro**: Base de datos completa de áreas, bloques y contextos
3. **Guía de referencia**: Explicaciones de cada nivel jerárquico
4. **Control de expansión**: Seguimiento de qué códigos están en uso
5. **Onboarding**: Punto de entrada para entender el sistema

---

### Reglas del Sistema Johnny Decimal

#### Nivel ÁREA (A):
- Formato: `A[0-9]-[CÓDIGO]`
- Ejemplo: `A1-INV`, `A2-UNI`
- Máximo: 10 áreas (A0-A9)

#### Nivel BLOQUE (B):
- Para A0: `B0[A-Z]-[CÓDIGO]` (26 bloques máximo)
- Para A1-A9: `B[Área][0-9]-[CÓDIGO]` (10 bloques por área)
- Ejemplo: `B0A-RED`, `B11-CVT`, `B24-DOC`
- No consecutivos: Rangos temáticos permiten expansión

#### Nivel CONTEXTO (C):
- Formato: `C[Prefijo bloque][0-9]-[CÓDIGO]`
- Contexto base: `C[Prefijo]0` (sin código de 3 letras)
- Contextos específicos: Números no consecutivos
- Ejemplos:
  - Bloque B11 → C110 (base), C111, C112, C113
  - Bloque B24 → C240 (base), C241, C242, C243

#### Códigos de 3 Letras:

Abreviaciones mnemotécnicas en español, mayúsculas:

**A0-GTD:**
- RED - Recursos/Redacción
- ABC - Sistema ABC
- PLA - Planificación
- REF - Referencias
- ENL - Enlaces
- DIR - Directorio
- ARE - Áreas
- BLQ - Bloques
- CTX - Contextos
- PRY - Proyectos
- TAR - Tareas
- NOT - Notas

**A1-INV:**
- CVT - Curriculum Vitae
- LAB - Laboratorio
- PUB - Publicaciones
- REP - Repositorios
- ACR - Acreditaciones
- CAT - Catedra
- PRY - Proyectos
- EXP - Experimentos
- DIR - Direccion
- ART - Artículos
- CON - Congresos
- EVA - Evaluación

**A2-UNI:**
- DOC - Docencia
- FOR - Formación
- GES - Gestión
- GRA - Grado
- MAS - Máster
- POS - Posgrado
- PDI - Personal Docente Investigador
- EST - Estudios
- MOC - MOOCs
- UPO - Universidad Pablo de Olavide
- MIN - Ministerio

**A3-VIT:**
- ORG - Organización
- TEC - Tecnología
- DES - Desarrollo
- ADM - Administración
- PER - Personal
- SOC - Social
- IAA - Inteligencia Artificial Aplicada
- INF - Informática
- STA - Estadistica
- FIS - Físico
- MEN - Mental
- MUS - Música

**A4-ARC:**
- LIB - Libros
- MED - Media
- APP - Aplicaciones
- FIC - Ficción
- SCI - Ciencia
- ENS - Ensayo
- VID - Vídeos
- AUD - Audio
- MP3 - MP3/Música
- MOC - Maps of Content
- WEB - Web
- SOF - Software

---

### Metadata Recomendado en Notas

```markdown
---
# Identificación Johnny Decimal
ubicacion: A1-INV/B11-CVT/C111-REP
area: A1-INV
bloque: B11-CVT
contexto: C111-REP

# Estado y clasificación
estado: activo|pausado|archivado
tipo: proyecto|nota|recurso|índice
tags: [investigación, repositorios, cv]

# Relaciones
relacionado:
  - "[[A4-ARC/B4X-LIB/C4X2-SCI/Paper importante]]"
  - "[[A2-UNI/B24-DOC/C241-GRA/Curso]]"
  - "[[A0-GTD/B0B-ABC/C0B6-CTX/Guía]]"

# Recursos externos
recursos_delta:
  - Delta/DOC/Académico/paper.pdf
  - Delta/LIB/Técnico/libro.pdf
recursos_gamma:
  - Gamma/Gamma-2026/Gamma-2026-02-04/ideas/

# Backups
backup_origen: GDRIVE-2026
ultimo_backup: GDRIVE-2026-02-04
ruta_backup: Beta/BACKS-2026/GDRIVE-2026/GDRIVE-2026-02-04/

# Fechas
created: 2026-02-04
modified: 2026-02-04
---
```

---

## Beta: Backups Cronológicos

### Visión General

Beta contiene copias de seguridad periódicas organizadas cronológicamente por **año** y por **origen** del backup (nube o dispositivo).

### Estructura Jerárquica

```
Beta/
├── BACKS-2026/
│   ├── GDRIVE-2026/
│   │   ├── GDRIVE-2026-02-04/
│   │   │   ├── Descargas/
│   │   │   ├── Escritorio/
│   │   │   ├── Documentos/
│   │   │   ├── Imágenes/
│   │   │   └── Vídeos/
│   │   └── GDRIVE-2026-03-15/
│   │       └── [misma estructura]
│   │
│   ├── MSI-2026/
│   │   ├── MSI-2026-01-15/
│   │   └── MSI-2026-02-01/
│   │
│   ├── HP-2026/
│   │   ├── HP-2026-01-10/
│   │   └── HP-2026-02-07/
│   │
│   └── ONEDRIVE-2026/
│       ├── ONEDRIVE-2026-02-01/
│       └── ONEDRIVE-2026-03-01/
│
├── BACKS-2025/
│   ├── GDRIVE-2025/
│   ├── MSI-2025/
│   ├── HP-2025/
│   └── ONEDRIVE-2025/
│
└── BACKS-2024/
    └── [misma estructura]
```

### Nomenclatura de Carpetas

**Nivel 1 - Año:** `BACKS-YYYY`

**Nivel 2 - Origen:** `[ORIGEN]-YYYY`
- `GDRIVE-YYYY` - Google Drive
- `ONEDRIVE-YYYY` - OneDrive
- `MSI-YYYY` - PC MSI
- `HP-YYYY` - Portátil HP

**Nivel 3 - Snapshot:** `[ORIGEN]-YYYY-MM-DD` (hereda prefijo)
- `GDRIVE-2026-02-04` - Backup de Google Drive del 4 de febrero
- `MSI-2026-01-15` - Backup del PC MSI del 15 de enero

### Ventajas del Sistema de Prefijo Heredado

1. **Identificación única**: Cada snapshot se identifica completamente por su nombre
2. **Portabilidad**: Las carpetas pueden moverse sin perder contexto
3. **Búsqueda eficiente**: Filtrar por origen sin navegar por jerarquía
4. **Claridad visual**: El nombre completo indica año, origen y fecha
5. **Trazabilidad**: Historial completo visible desde el nombre

### Principios de Uso

- Crear `BACKS-YYYY` al inicio de cada año
- Dentro, crear carpetas por origen: `[ORIGEN]-YYYY`
- Cada backup en subcarpeta: `[ORIGEN]-YYYY-MM-DD`
- Mantener estructura original del sistema dentro del snapshot
- Backups programados según origen:
  - Nube (GDRIVE, ONEDRIVE): Semanal
  - PCs (MSI, HP): Quincenal
- Mantener 1-2 años de histórico completo
- Comprimir o eliminar backups >3 años

### Ejemplos de Rutas Completas

```
Beta/BACKS-2026/GDRIVE-2026/GDRIVE-2026-02-04/Documentos/Proyectos/
Beta/BACKS-2026/MSI-2026/MSI-2026-01-15/Escritorio/Capturas/
Beta/BACKS-2025/HP-2025/HP-2025-12-20/Descargas/Instaladores/
Beta/BACKS-2026/ONEDRIVE-2026/ONEDRIVE-2026-03-01/Imágenes/
```

---

## Delta: Archivo Clasificado

### Visión General

Delta es la biblioteca permanente de archivos organizados por **categoría de contenido** de manera semántica.

### Estructura de Carpetas

```
Delta/
├── DOC/  (Documentos)
│   ├── Académico/
│   ├── Personal/
│   ├── Profesional/
│   └── Referencia/
│
├── LIB/  (Libros)
│   ├── Ficción/
│   ├── No-ficción/
│   ├── Técnico/
│   └── Académico/
│
├── MED/  (Media)
│   ├── Audio/
│   ├── Video/
│   ├── Imágenes/
│   └── Presentaciones/
│
└── SOF/  (Software)
    ├── Instaladores/
    ├── Portable/
    ├── Scripts/
    └── Configuraciones/
```

### Características

- **Clasificación semántica**: Por tipo de contenido, no por fecha
- **Estructura permanente**: Estable y predecible
- **Fácil localización**: Por categoría conocida
- **Suborganización temática**: Dentro de cada tipo

### Principios de Uso

- Archivo definitivo de recursos valiosos
- Naming consistente dentro de cada categoría
- Metadatos en nombres de archivo cuando sea relevante
- Revisión y limpieza periódica (anual)
- Solo contenido curado y de valor permanente

---

## Gamma: Almacenamiento Temporal

### Visión General

Gamma es el espacio para archivos que requieren conservación pero cuya clasificación no está clara o es temporal. Organizado cronológicamente siguiendo el mismo sistema de prefijos que Beta.

### Estructura Cronológica

```
Gamma/
├── Gamma-2026/
│   ├── Gamma-2026-01-15/
│   ├── Gamma-2026-02-04/
│   ├── Gamma-2026-02-28/
│   └── Gamma-2026-03-10/
│
├── Gamma-2025/
│   ├── Gamma-2025-01-20/
│   ├── Gamma-2025-03-14/
│   └── Gamma-2025-12-15/
│
└── Gamma-2024/
    └── [carpetas por fecha]
```

### Nomenclatura

**Nivel 1 - Año:** `Gamma-YYYY`

**Nivel 2 - Fecha específica:** `Gamma-YYYY-MM-DD` (hereda prefijo)

### Características

- Organización puramente cronológica
- Sin clasificación temática previa
- Prefijo heredado para identificación completa
- Cada carpeta representa un "momento de llegada"
- Estructura libre dentro de cada carpeta

### Principios de Uso

- Crear `Gamma-YYYY` al inicio de cada año
- Para contenido sin clasificar, crear `Gamma-YYYY-MM-DD` del día
- Depositar archivos directamente o en subcarpetas ad-hoc
- **Revisión trimestral obligatoria**
- Tres destinos en la revisión:
  1. **Delta**: Clasificación clara
  2. **Alpha**: Se convierte en proyecto activo
  3. **Eliminar**: Perdió relevancia

### Ejemplo de Uso

```
Gamma/Gamma-2026/Gamma-2026-02-04/
├── papers_interesantes/
│   ├── articulo1.pdf
│   └── articulo2.pdf
├── capturas_pantalla/
│   └── screenshot_bug.png
└── notas_reunión.txt
```

### Flujo de Revisión

1. Cada 3 meses, ordenar carpetas por fecha
2. Para cada carpeta antigua:
   - Revisar contenido
   - Decidir destino
   - Mover o eliminar
   - Borrar carpeta vacía
3. Mantener solo últimos 3-6 meses sin revisar

### Criterios de Revisión

- **Más de 3 meses**: Revisar obligatoriamente
- **6-12 meses**: Si no se movió, probablemente eliminar
- **Más de 1 año**: Eliminar directamente

---

## Tablas de Referencia Completas

### Resumen del Sistema

| Nivel | Total | Descripción |
|-------|-------|-------------|
| Áreas | 5 | A0-GTD, A1-INV, A2-UNI, A3-VIT, A4-ARC |
| Bloques | 15 | Agrupaciones temáticas |
| Contextos | 60 | Carpetas específicas de trabajo |

### Capacidad del Sistema

**Con numeración flexible:**
- A0: 26 bloques × ~4 contextos = ~104 contextos
- A1-A9: 9 áreas × 10 bloques × ~4 contextos = ~360 contextos
- **Capacidad teórica total: ~464 contextos**

**Capacidad real utilizada:** 60 contextos (12.9% de capacidad)

### Distribución por Área

| Área | Bloques | Contextos | Uso |
|------|---------|-----------|-----|
| A0-GTD | 3 | 12 | Sistema operativo |
| A1-INV | 3 | 12 | Investigación |
| A2-UNI | 3 | 12 | Universidad |
| A3-VIT | 3 | 12 | Vida personal |
| A4-ARC | 3 | 12 | Archivo |

---

## Flujos de Trabajo

### Ciclo de Vida de un Archivo

```
┌─────────────────────────────────────────────────────────┐
│                    ENTRADA AL SISTEMA                    │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
          ¿Clasificación clara?    ¿Trabajo activo?
                │                       │
        ┌───────┴───────┐               │
        │               │               │
       SÍ              NO              SÍ
        │               │               │
        ▼               ▼               ▼
    ┌───────┐      ┌────────┐      ┌───────┐
    │ DELTA │      │ GAMMA  │      │ ALPHA │
    └───────┘      └────────┘      └───────┘
                        │               │
                        │               │
                   Revisión       Proyecto
                   trimestral     completado
                        │               │
                        ▼               ▼
                   ┌────────────────────┐
                   │ DELTA o ELIMINAR   │
                   └────────────────────┘
```

### Flujo de Trabajo Diario

**Captura rápida:**
1. Idea/archivo llega → `A0-GTD/B0C-PLA/C0C9-NOTAS/` (inbox)
2. Procesamiento diario
3. Clasificación a carpetas correspondientes

**Desarrollo de proyectos:**
1. Proyectos activos en contextos apropiados
2. Referencias desde `A4-ARC`
3. Recursos externos desde `Delta`

**Consolidación de conocimiento:**
1. Notas de trabajo en contextos específicos
2. Destilación de conceptos clave
3. Creación de notas permanentes en `A4-ARC`
4. Archivo de proyectos completados

### Estrategia de Backups en Beta

**Planificación anual:**
- Al inicio de año, crear `BACKS-YYYY`
- Crear subcarpetas para cada origen activo

**Ejecución de backup:**
1. Identificar origen (GDRIVE, MSI, HP, ONEDRIVE)
2. Navegar a `Beta/BACKS-YYYY/[ORIGEN]-YYYY/`
3. Crear carpeta: `[ORIGEN]-YYYY-MM-DD`
4. Copiar estructura completa del origen
5. Verificar integridad

**Recuperación de archivos:**
- Por año → `BACKS-YYYY`
- Por origen → `[ORIGEN]-YYYY`
- Por fecha → `[ORIGEN]-YYYY-MM-DD`
- Buscar en estructura original

### Integración entre Sistemas

**Alpha ↔ Delta:**
```markdown
# En nota de Alpha
recursos_delta:
  - Delta/DOC/Académico/paper.pdf
  - Delta/LIB/Técnico/libro.pdf
```

**Alpha ↔ Beta:**
```
Beta/BACKS-2026/GDRIVE-2026/GDRIVE-2026-02-04/Alpha/
└── [Estructura Johnny Decimal respaldada]
```

**Alpha ↔ Gamma:**
```
Gamma/Gamma-2026/Gamma-2026-01-15/ideas_proyecto/
→ Se clasifica y mueve a →
Alpha/A1-INV/B12-LAB/C124-PRY/nueva_nota.md
```

---

## Mantenimiento del Sistema

### Calendario de Mantenimiento

| Frecuencia | Tarea | Carpetas Afectadas |
|------------|-------|-------------------|
| **Diario** | Trabajo en proyectos activos | Alpha |
| **Diario** | Depositar archivos sin clasificar | Gamma/Gamma-YYYY |
| **Semanal** | Backup de nube (GDRIVE, ONEDRIVE) | Beta/BACKS-YYYY |
| **Quincenal** | Backup de PCs (MSI, HP) | Beta/BACKS-YYYY |
| **Mensual** | Archivar proyectos completados | Alpha → Delta |
| **Trimestral** | **Reclasificar o eliminar** | **Gamma → Delta/Alpha** |
| **Anual** | Crear nueva estructura de año | Beta, Gamma |
| **Anual** | Comprimir/eliminar backups >3 años | Beta |
| **Anual** | Eliminar Gamma >1 año sin procesar | Gamma |
| **Anual** | Auditoría completa | Todas |

### Checklist de Mantenimiento Trimestral

**Gamma (Obligatorio):**
- [ ] Listar carpetas de Gamma ordenadas por fecha
- [ ] Revisar carpetas >3 meses
- [ ] Para cada carpeta antigua:
  - [ ] ¿Va a Alpha como proyecto? → Mover
  - [ ] ¿Va a Delta clasificado? → Mover
  - [ ] ¿Ya no es relevante? → Eliminar
- [ ] Eliminar carpetas vacías
- [ ] Documentar decisiones

**Alpha:**
- [ ] Revisar proyectos pausados >3 meses
- [ ] Archivar proyectos completados a Delta
- [ ] Actualizar base de datos ABC si hay cambios
- [ ] Verificar integridad de enlaces

**Beta:**
- [ ] Verificar que backups se ejecutaron correctamente
- [ ] Probar recuperación de un archivo aleatorio
- [ ] Documentar cualquier fallo

**Delta:**
- [ ] Verificar que archivos movidos desde Gamma están clasificados
- [ ] Eliminar duplicados
- [ ] Actualizar índices si existen

### Checklist de Mantenimiento Anual

**Estructura de año nuevo:**
- [ ] Crear `Beta/BACKS-YYYY/`
- [ ] Crear subcarpetas de origen: `[ORIGEN]-YYYY`
- [ ] Crear `Gamma/Gamma-YYYY/`
- [ ] Actualizar scripts de backup con nuevo año

**Limpieza de Beta:**
- [ ] Identificar carpetas `BACKS-` con >3 años
- [ ] Evaluar si comprimir o eliminar
- [ ] Mantener al menos 1 backup del año más antiguo
- [ ] Documentar eliminaciones

**Limpieza de Gamma:**
- [ ] Eliminar directamente carpetas >1 año sin revisar
- [ ] Documentar qué se eliminó

**Auditoría de Alpha:**
- [ ] Revisar todos los contextos "base" (C[X]0)
- [ ] ¿Están siendo utilizados?
- [ ] Actualizar descripciones si es necesario
- [ ] Verificar que base de datos ABC está actualizada

**Auditoría de Delta:**
- [ ] Revisar cada subcategoría
- [ ] Eliminar archivos obsoletos
- [ ] Reorganizar si hay crecimiento excesivo
- [ ] Documentar cambios estructurales

---

## Ventajas del Sistema ABGD

### Claridad Mental
- Cada cosa tiene su lugar y propósito
- Separación clara de contextos
- Fácil saber dónde buscar

### Recuperabilidad
- Backups históricos por año y origen
- Trazabilidad completa
- Independencia contextual de las carpetas

### Escalabilidad
- Estructura simple que crece orgánicamente
- Nomenclatura consistente
- Espacio para expansión sin reorganización

### Flexibilidad
- Gamma absorbe incertidumbre
- Alpha permite trabajo multifacético
- Delta adaptable a nuevas categorías

### Enfoque
- Alpha mantiene solo lo relevante
- Sin distracción de archivos antiguos
- Proyectos activos claramente identificados

### Preservación
- Delta asegura acceso a largo plazo
- Beta protege contra pérdida de datos
- Múltiples capas de respaldo

---

## Notas Finales

### Integración Notion + Obsidian

El sistema utiliza:
- **Notion**: Base de datos maestra (B0B-ABC) con vistas relacionales
- **Obsidian**: Editor de notas, enlaces bidireccionales, búsqueda
- **Sincronización**: Mantiene ambos sistemas actualizados

### Personalización

Este sistema es adaptable. Puede:
- Añadir nuevas áreas (A5, A6, A7...)
- Crear nuevos bloques según necesidad
- Expandir contextos sin límite
- Adaptar nomenclatura a preferencias personales

### Mejores Prácticas

1. **Ser consistente**: Seguir siempre la nomenclatura
2. **Revisar regularmente**: No dejar Gamma sin revisar >3 meses
3. **Documentar cambios**: Actualizar base de datos ABC
4. **Hacer backups**: No depender solo de un sistema
5. **Mantener Alpha limpio**: Archivar proyectos completados
6. **Curar Delta**: Solo contenido de valor permanente

---

**Fin de la documentación**

Sistema ABGD v1.0 - Febrero 2026
