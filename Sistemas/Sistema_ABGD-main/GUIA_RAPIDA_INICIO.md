# Guía Rápida de Inicio - Sistema ABGD

**¡Felicidades!** Tu estructura ABGD ha sido generada exitosamente.

---

## ¿Qué hacer ahora?

### 1. Inicializa Obsidian con Alpha

**Paso 1:** Abre Obsidian

**Paso 2:** Crea un nuevo vault
- Selecciona "Abrir carpeta como vault"
- Navega a `Sistema_ABGD/Alpha/`
- Confirma

**Paso 3:** Explora la estructura
- Verás las 5 áreas principales (A0-GTD, A1-INV, A2-UNI, A3-VIT, A4-ARC)
- Cada área contiene sus bloques
- Cada bloque contiene sus contextos
- Cada carpeta tiene su archivo .md descriptivo

---

## 2. Comprende las 4 Carpetas Principales

### Alpha (Núcleo Activo)
**¿Qué va aquí?**
- Notas de trabajo actual
- Proyectos en curso
- Documentación activa

**Ubicación:** `Sistema_ABGD/Alpha/`

**Ejemplo:**
```
A0-GTD/B0C-PLA/C0C7-PRY/proyecto_actual.md
A1-INV/B12-LAB/C124-PRY/experimento_actual.md
```

### Beta (Backups)
**¿Qué va aquí?**
- Copias de seguridad cronológicas
- Snapshots de diferentes orígenes
- Historial preservado

**Ubicación:** `Sistema_ABGD/Beta/`

**Ejemplo:**
```
Beta/BACKS-2026/GDRIVE-2026/GDRIVE-2026-02-04/
Beta/BACKS-2026/MSI-2026/MSI-2026-01-15/
```

### Delta (Archivo Clasificado)
**¿Qué va aquí?**
- Documentos finalizados
- Libros y recursos permanentes
- Media clasificada
- Software y configuraciones

**Ubicación:** `Sistema_ABGD/Delta/`

**Ejemplo:**
```
Delta/DOC/Académico/paper_publicado.pdf
Delta/LIB/Técnico/manual_python.pdf
Delta/MED/Imágenes/diagrama_sistema.png
```

### Gamma (Temporal)
**¿Qué va aquí?**
- Archivos sin clasificar
- Descargas recientes
- Ideas sin procesar
- Contenido pendiente de revisar

**Ubicación:** `Sistema_ABGD/Gamma/`

**Ejemplo:**
```
Gamma/Gamma-2026/Gamma-2026-02-04/
├── capturas_pantalla/
├── papers_revisar/
└── ideas_proyecto/
```

---

## 3. Flujo de Trabajo Básico

### Llegada de Nuevo Contenido

```
¿Nuevo archivo/idea/documento?
            │
            ▼
    ¿Sé dónde va exactamente?
            │
    ┌───────┴───────┐
   SÍ               NO
    │                │
    ▼                ▼
¿Es trabajo      GAMMA
 activo?       (temporal)
    │
┌───┴───┐
│       │
SÍ      NO
│       │
▼       ▼
ALPHA  DELTA
```

### Ejemplo Práctico

**Escenario 1:** Recibes un PDF de un paper interesante
- **Destino:** `Gamma/Gamma-2026/Gamma-2026-02-04/papers_revisar/`
- **Después de revisar:** Muévelo a `Delta/DOC/Académico/` o a Alpha si vas a trabajar con él

**Escenario 2:** Inicias un nuevo proyecto de investigación
- **Destino:** `Alpha/A1-INV/B12-LAB/C124-PRY/nuevo_proyecto.md`
- **Cuando termines:** Archiva el resultado en Delta

**Escenario 3:** Descargas una captura de pantalla
- **Destino:** `Gamma/Gamma-2026/Gamma-2026-02-04/capturas/`
- **Después de usar:** Elimina o mueve a Delta/MED/Imágenes/

---

## 4. Tareas del Primer Día

### ☐ Tarea 1: Explora Alpha en Obsidian
- Abre cada área y lee su archivo .md
- Familiarízate con los bloques y contextos
- Identifica dónde crearás tus primeras notas

### ☐ Tarea 2: Crea una carpeta de hoy en Gamma
```bash
mkdir "Gamma/Gamma-2026/Gamma-2026-02-04"
```
- Esta será tu "bandeja de entrada" temporal

### ☐ Tarea 3: Mueve archivos existentes
- Archivos de trabajo activo → Alpha (según contexto)
- Recursos valiosos clasificados → Delta (según tipo)
- Todo lo demás sin clasificar → Gamma

### ☐ Tarea 4: Crea tu primera nota en Alpha
Ejemplo en `Alpha/A0-GTD/B0C-PLA/C0C9-NOT/`:
```markdown
---
created: 2026-02-04
tags: [inicio, sistema-abgd]
---

# Inicio del Sistema ABGD

Hoy he iniciado el sistema ABGD. Mis primeros pasos son:
- Familiarizarme con la estructura
- Mover archivos existentes
- Definir mi flujo de trabajo
```

---

## 5. Calendario de Mantenimiento

### Diario
- Trabaja en tus notas de Alpha
- Guarda archivos sin clasificar en Gamma/Gamma-YYYY/Gamma-YYYY-MM-DD/

### Semanal (Lunes)
- **Backup de GDRIVE**
  ```bash
  # Crear carpeta
  mkdir "Beta/BACKS-2026/GDRIVE-2026/GDRIVE-2026-MM-DD"
  # Copiar contenido
  ```
- **Backup de ONEDRIVE**
  ```bash
  mkdir "Beta/BACKS-2026/ONEDRIVE-2026/ONEDRIVE-2026-MM-DD"
  ```

### Quincenal (1 y 15)
- **Backup de MSI**
  ```bash
  mkdir "Beta/BACKS-2026/MSI-2026/MSI-2026-MM-DD"
  ```
- **Backup de HP**
  ```bash
  mkdir "Beta/BACKS-2026/HP-2026/HP-2026-MM-DD"
  ```

### Mensual
- Archivar proyectos completados de Alpha a Delta
- Revisar carpetas de Gamma del mes anterior

### Trimestral (Crítico)
- **Revisión obligatoria de Gamma**
  - Para cada carpeta >3 meses:
    - ¿Va a Alpha como proyecto? → Mueve
    - ¿Va a Delta clasificado? → Mueve
    - ¿Ya no es relevante? → Elimina
  - Elimina carpetas vacías

### Anual (Enero)
- Crear `Beta/BACKS-YYYY/`
- Crear subcarpetas de origen: `GDRIVE-YYYY/`, etc.
- Crear `Gamma/Gamma-YYYY/`
- Auditar y limpiar Gamma >1 año
- Comprimir o eliminar Beta >3 años

---

## 6. Atajos y Tips

### Búsquedas Rápidas en Obsidian

**Buscar en un área específica:**
```
path:A1-INV [tu búsqueda]
```

**Buscar en un bloque:**
```
path:B12-LAB [tu búsqueda]
```

**Buscar por tags:**
```
tag:#investigación
```

### Nomenclatura de Notas

**Recomendación:** Usa nombres descriptivos en español
```
✓ Bueno: experimento_celulas_2026-02-04.md
✗ Evita: exp1.md, nota.md, temp.md
```

### Referencias entre Carpetas

**En una nota de Alpha, referencia a Delta:**
```markdown
## Recursos
- [Paper importante](../../../Delta/DOC/Académico/paper.pdf)
- [Manual técnico](../../../Delta/LIB/Técnico/manual.pdf)
```

**Referencia a Gamma:**
```markdown
## Archivos temporales
Ver: Gamma/Gamma-2026/Gamma-2026-02-04/ideas/
```

---

## 7. Preguntas Frecuentes

### ¿Dónde van mis proyectos de investigación?
→ `Alpha/A1-INV/B12-LAB/C124-PRY/`

### ¿Dónde van mis notas de clase?
→ `Alpha/A2-UNI/B24-DOC/C241-GRA/` (para Grado)
→ `Alpha/A2-UNI/B24-DOC/C242-MAS/` (para Máster)

### ¿Dónde guardo PDFs de papers importantes?
- Si estás trabajando con ellos: Referencias en Alpha
- Si son para archivo: `Delta/DOC/Académico/`
- Si no estás seguro: `Gamma/Gamma-YYYY/Gamma-YYYY-MM-DD/papers/`

### ¿Qué hago si no sé dónde clasificar algo?
→ ¡Pon lo en Gamma! Es exactamente para eso.
→ En la revisión trimestral decidirás dónde va.

### ¿Puedo cambiar la estructura?
→ Sí, pero mantén la consistencia.
→ Si añades áreas/bloques/contextos, actualiza el Excel y regenera si es necesario.

### ¿Cómo uso el sistema B0B-ABC?
→ `Alpha/A0-GTD/B0B-ABC/` es tu meta-documentación.
→ Ahí puedes poner guías de uso, índices, documentación del sistema.

---

## 8. Primeros Comandos Útiles

### Crear carpeta de hoy en Gamma
```bash
# Windows
mkdir "Sistema_ABGD\Gamma\Gamma-2026\Gamma-2026-02-04"

# Linux/Mac
mkdir -p "Sistema_ABGD/Gamma/Gamma-2026/Gamma-2026-$(date +%m-%d)"
```

### Ver estructura de Alpha
```bash
# Windows
dir /s /b Sistema_ABGD\Alpha

# Linux/Mac
find Sistema_ABGD/Alpha -type d
```

### Buscar un archivo
```bash
# Windows
dir /s /b Sistema_ABGD\*.pdf

# Linux/Mac
find Sistema_ABGD -name "*.pdf"
```

---

## 9. Recursos Adicionales

### Documentación
- [Sistema_ABGD_Documentacion_Completa.md](Sistema_ABGD_Documentacion_Completa.md) - Documentación exhaustiva
- [RESULTADO_GENERACION.md](RESULTADO_GENERACION.md) - Detalles técnicos de la generación

### Script de Generación
- [generar_estructura_abgd.py](generar_estructura_abgd.py) - Script Python
- Puedes regenerar la estructura si añades más áreas/bloques/contextos al Excel

### Sistema Johnny Decimal
- La estructura de Alpha sigue el sistema Johnny Decimal adaptado
- Tres niveles: ÁREA → BLOQUE → CONTEXTO
- Nomenclatura consistente y escalable

---

## 10. ¡Empieza Ahora!

### Checklist de Primer Día

- [ ] ✅ Abrir Obsidian con Alpha como vault
- [ ] ✅ Explorar las 5 áreas principales
- [ ] ✅ Crear carpeta de hoy en Gamma
- [ ] ✅ Crear primera nota en Alpha
- [ ] ✅ Mover 3-5 archivos existentes a su lugar correcto
- [ ] ✅ Configurar backup semanal (opcional pero recomendado)
- [ ] ✅ Añadir recordatorio trimestral para revisar Gamma

---

## ¡Disfruta de tu sistema ABGD!

Este sistema crecerá contigo. Al principio puede parecer complejo, pero en pocos días será natural saber dónde va cada cosa.

**Recuerda:**
- Alpha = Trabajo activo
- Beta = Backups cronológicos
- Delta = Archivo clasificado permanente
- Gamma = Temporal sin clasificar

**La clave del éxito:** Revisar Gamma cada 3 meses. Todo lo demás fluirá naturalmente.

---

**Generado:** 2026-02-04
**Versión del Sistema:** ABGD v1.0
**Por:** Claude Code & David
