# Obsidian Agent — Guía de uso

Agente para el vault **ABGD** en Obsidian.

**Vault:** `G:/Mi unidad/ABGD/ABGD-25.09.05/1.ALPHA`

---

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
| A4-REF | Referencia |

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
python agents/obsidian_agent.py ver "G:/Mi unidad/ABGD/.../nota.md"

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
└── A4-REF/
    ├── B4X-LIB/
    ├── B4Y-MED/
    └── B4Z-APP/
```

---

## Configuración

- Vault path en `.env` → `OBSIDIAN_ALPHA_PATH`
- ABGD root en `.env` → `OBSIDIAN_ABGD_ROOT`
