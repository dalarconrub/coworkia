# 🖼️ Exportables finales

## Sistema **MAR – Meta · Acción · Resultado**

---

## 1. Principios generales de exportación

Todos los exportables deben cumplir:

* Correspondencia cromática MAR **estricta**
* Proporciones fijas (no estirar / no comprimir)
* Misma jerarquía visual definida en el manual
* Fondo transparente cuando sea posible

---

## 2. Paquete principal de exportables

### 📦 Carpeta recomendada

```text
MAR_EXPORTS/
├─ SVG/
├─ PNG/
├─ MONO/
├─ ICONS/
└─ README.md
```

---

## 3. Exportables en SVG (maestro)

📁 `SVG/`

El **SVG es el archivo fuente maestro**.  
Todo lo demás debe derivar de él.

### 3.1 Logo completo (oficial)

**Nombre**

```
MAR_logo_full.svg
```

**Incluye**

* Símbolo (triángulo + espiral)
* Texto ES:

  ```
  META  ACCIÓN
  RESULTADO
  ```
* Línea separadora dorada
* Texto EN:

  ```
  GOAL • ACTION • OUTCOME
  ```

**Uso**

* Documentos académicos
* Web
* Portadas
* Presentaciones

---

### 3.2 Logo sin texto

```
MAR_symbol.svg
```

**Incluye**

* Solo triángulo + espiral
* Sin ningún texto

**Uso**

* Icono grande
* Marca de agua
* Cabeceras limpias

---

## 4. Exportables en PNG

📁 `PNG/`

Todos los PNG deben exportarse desde el SVG, con **fondo transparente**, salvo indicación contraria.

### 4.1 Logo completo

```
MAR_logo_full_3000px.png
MAR_logo_full_1500px.png
MAR_logo_full_800px.png
```

**Resolución**

* 300 dpi (impresión)
* 144 dpi (digital)

---

### 4.2 Logo sobre fondo oscuro

```
MAR_logo_darkbg.png
```

* Fondo: `#0B1220`
* Uso: presentaciones, PDFs, portadas

---

### 4.3 Logo reducido

```
MAR_logo_compact.png
```

* Símbolo + texto español
* Sin inglés
* Uso: encabezados, pies de página

---

## 5. Versiones monocromas

📁 `MONO/`

### 5.1 Negro

```
MAR_logo_black.svg
MAR_logo_black.png
```

Uso:

* Documentos impresos
* Escalas de grises
* Sellos

---

### 5.2 Blanco

```
MAR_logo_white.svg
MAR_logo_white.png
```

Uso:

* Fondos oscuros
* Diapositivas
* Portadas

⚠️ En versión monocroma:

* No hay color semántico
* Se mantiene jerarquía, no color

---

## 6. Iconos (uso operativo)

📁 `ICONS/`

### 6.1 Icono principal MAR

```
MAR_icon.svg
MAR_icon_256.png
MAR_icon_128.png
MAR_icon_64.png
```

**Incluye**

* Solo triángulo + espiral
* Sin texto

**Uso**

* Favicon
* App
* Obsidian / Notion
* Marcadores

---

### 6.2 Iconos semánticos (opcional, muy potente)

```
MAR_icon_meta.svg
MAR_icon_accion.svg
MAR_icon_resultado.svg
```

* 🟠 Meta → triángulo resaltando lado naranja
* 🔵 Acción → triángulo resaltando lado azul
* ⚪ Resultado → triángulo resaltando lado plateado

Uso:

* Dashboards
* Plantillas
* Señalización visual interna

---

## 7. Tamaños y márgenes

### 7.1 Tamaños mínimos

| Uso           | Tamaño mínimo |
| ------------- | ------------- |
| Logo completo | 1200 px ancho |
| Símbolo       | 256 px        |
| Icono         | 64 px         |

---

### 7.2 Área de seguridad

Regla:

> El espacio libre mínimo alrededor del logo es la **altura de la letra "M" de META**.

Ningún texto ni elemento puede invadir ese espacio.

---

## 8. README del paquete

📄 `README.md`

Contenido mínimo:

```md
# MAR – Exportables oficiales

Este paquete contiene los exportables oficiales del sistema
Meta–Acción–Resultado (MAR).

El archivo maestro es:
- SVG/MAR_logo_full.svg

Todas las demás versiones derivan de él.
No modificar colores ni proporciones.
```

---

## 9. Checklist final (validación)

Antes de considerar cerrado el paquete:

* [ ] SVG maestro correcto
* [ ] Colores HEX exactos
* [ ] Texto ES + EN correcto
* [ ] Versiones monocromas legibles
* [ ] Iconos visibles a 64 px
* [ ] Fondo oscuro probado

---

## 10. Cierre conceptual

> **El manual define.  
> Las plantillas obligan.  
> Los exportables hacen visible el sistema.**

Con esto, el sistema MAR **ya es una identidad completa**, no solo un método.

---

## 11. Próximos pasos (opcionales)

Si quieres ir a nivel "sistema total":

* 🧠 **Dashboard MAR semanal**
* ⚙️ **Automatización (KPIs, conteo de bloques)**
* 📘 **Plantillas LaTeX / Beamer / Quarto**

Tú decides hasta dónde llevarlo.
