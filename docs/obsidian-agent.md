# Obsidian Agent — Guía de uso

Agente para el vault **ABGD** en Obsidian.

**Vault activo:** definido por `.env` en `OBSIDIAN_ABGD_ROOT`.

Política vigente desde 2026-05-09: el vault primario debe estar en disco local del PC. Google Drive, otros servicios de nube y discos externos se usan como réplicas/backups sincronizados, no como ruta operativa principal.

Referencia actual validada en la sesión 2026-05-09:

```text
OBSIDIAN_ABGD_ROOT=C:/Users/David/Documents/ABGD/ABGD-260509
OBSIDIAN_ALPHA_PATH=C:/Users/David/Documents/ABGD/ABGD-260509/1.ALPHA
```

Convención vigente: Obsidian Desktop abre `OBSIDIAN_ABGD_ROOT` (el vault real). Las herramientas de Coworkia que operan sobre conocimiento vivo usan `OBSIDIAN_ALPHA_PATH`, que apunta a la subcarpeta `1.ALPHA`.

Si se rota el vault con `tools/reset_obsidian.py rotate`, estas rutas deben actualizarse en `.env`; la guía no debe apuntar a rutas históricas como fuente de verdad.

Ruta local propuesta para la siguiente rotación:

```text
C:/Users/David/Documents/ABGD/ABGD-260509
```

---

## Capas internas del vault

```text
ABGD-260509/
├── .obsidian/
├── 1.ALPHA/
├── 2.BETA/
├── 3.GAMMA/
├── 4.DELTA/
└── 5.EPSILON/
```

| Carpeta | Rol | Regla operativa |
| --- | --- | --- |
| `1.ALPHA` | Trabajo vivo | Notas, proyectos, tareas intelectuales, journals, fichas trabajadas, MOCs y material enlazable/promovible. Coworkia la indexa por defecto. |
| `2.BETA` | Staging / inbox | Importaciones, capturas brutas, notas sueltas y material pendiente de clasificar. No debe ser almacenamiento permanente. |
| `3.GAMMA` | Productos generados | Informes, HTML, PDF, presentaciones, exports limpios y artefactos para entregar. |
| `4.DELTA` | Archivos y media | PDFs, datasets, imágenes, audios, vídeos, adjuntos y documentos externos pesados. |
| `5.EPSILON` | Histórico frío | Legacy, snapshots, material cerrado o congelado que se conserva pero no se opera. |

Regla: las integraciones automáticas de Coworkia deben operar sobre `1.ALPHA` salvo que un flujo especifique explícitamente otra capa.

## Jerarquía ABGD

```
Área (A) → Bloque (B) → Contexto (C) → Proyecto (P) → Tarea (T) → Nota (N)
```

### Áreas

| Código | Nombre |
|--------|--------|
| A0-GTD | Getting Things Done |
| A1-INV | Investigación |
| A2-UNI | Universidad |
| A3-VIT | Vital |
| A4-ARX | Archivo |

### Nomenclatura de archivos

| Nivel | Formato | Ejemplo |
|-------|---------|---------|
| Nota | `N[YYMMDD]-Descripción.md` | `N260316-Reunión con Enrique.md` |
| Tarea | `T[BXXX.NN]-Nombre/` | `T12601.03-Datos Estudio 3/` |
| Proyecto | `P[BXXX.NN]-Nombre/` | `P126.01-Tesis Fran/` |

---

## Comandos

### Explorar estructura

```bash
# Mapa completo del vault (Área → Bloque → Contexto)
python agents/obsidian_agent.py mapa

# Estadísticas del vault
python agents/obsidian_agent.py estado

# Listar contenido de cualquier nivel por código
python agents/obsidian_agent.py listar A1-INV        # bloques de Investigación
python agents/obsidian_agent.py listar B12-LAB        # contextos de Laboratorio
python agents/obsidian_agent.py listar C125-DAT       # proyectos de Datos
python agents/obsidian_agent.py listar C126-DIR       # proyectos de Dirección tesis
```

### Notas

```bash
# Últimas N notas del vault
python agents/obsidian_agent.py ultimas
python agents/obsidian_agent.py ultimas --n 20
python agents/obsidian_agent.py ultimas --n 5 --area A1-INV

# Ver contenido de una nota (por nombre o path)
python agents/obsidian_agent.py ver "N260316-Reunión con Enrique"
python agents/obsidian_agent.py ver "C:/Users/David/Documents/ABGD/ABGD-260509/1.ALPHA/.../nota.md"

# Buscar texto en las notas
python agents/obsidian_agent.py buscar "análisis GLM"
python agents/obsidian_agent.py buscar "Tesis Fran" --area A1-INV
```

### Crear notas

```bash
# Nota en un contexto (nivel más común)
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C125-DAT "Resultados preliminares"

# Con contenido y fecha
python agents/obsidian_agent.py nueva-nota A1-INV B13-PUB C137-ART "Revisión Paper Human Communication" \
  --contenido "## Puntos clave\n- ..." \
  --fecha 2026-03-16

# En un proyecto específico
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C126-DIR "Sesión de trabajo" \
  --proyecto "P126.01-Tesis Fran" \
  --fecha 2026-03-16

# En una tarea específica
python agents/obsidian_agent.py nueva-nota A1-INV B12-LAB C126-DIR "Análisis datos" \
  --proyecto "P126.01-Tesis Fran" \
  --tarea "T12601.03-Datos Estudio 3"
```

---

## Estructura real del vault

```
1.ALPHA/
├── A0-GTD/
│   ├── B0A-INX/
│   ├── B0B-ABC/
│   └── B0C-PLA/
│       └── C0C9-Notas/
├── A1-INV/
│   ├── B11-CVT/  (C111-REP, C112-SOL, C113-CAT)
│   ├── B12-LAB/  (C124-PRO, C125-DAT, C126-DIR)
│   └── B13-PUB/  (C137-ART, C138-COM, C139-REV)
├── A2-UNI/
│   ├── B24-DOC/  (C241-GRA, C242-MAS, C243-POS)
│   ├── B25-FOR/  (C254-EST, C255-PDI, C256-MOC)
│   └── B26-GES/  (C267-UPO, C268-UNED, C269-MIN)
├── A3-VIT/
│   ├── B37-ORG/  (C371-ADM, C372-PER, C373-SOC)
│   ├── B38-TEC/  (C384-INF, C385-STA, C386-IAA)
│   └── B39-DES/  (C397-FIS, C398-MEN, C399-MUS)
└── A4-ARX/
    ├── B4X-BIB/
    ├── B4Y-KIT/
    └── B4Z-GIT/
```

---

## Configuración

- Vault Obsidian real en `.env` → `OBSIDIAN_ABGD_ROOT`
- Carpeta viva de notas ABPC en `.env` → `OBSIDIAN_ALPHA_PATH`
- Ruta primaria recomendada: local (`C:/Users/David/Documents/ABGD/...` o equivalente).
