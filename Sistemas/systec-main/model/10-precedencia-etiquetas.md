# MAR — Precedencia explícita de etiquetas de tipo

---

## 1. Problema que se resuelve

MAR clasifica las acciones de forma **automática** usando filtros temporales  
(fecha, hora, recurrencia y deadline).

Sin embargo, existen situaciones en las que el usuario **necesita forzar** el tipo
de una acción, independientemente de sus propiedades temporales.

Para ello, MAR introduce una **regla formal de precedencia**:
las **etiquetas de tipo** anulan cualquier inferencia automática.

---

## 2. Principio de precedencia

> **Si una acción tiene una etiqueta de tipo,  
> esa etiqueta tiene prioridad absoluta sobre los filtros temporales.**

La inferencia automática **solo se aplica cuando no hay decisión explícita**.

---

## 3. Etiquetas de tipo en MAR

Las etiquetas de tipo son:

- `@idea`
- `@meta`
- `@tarea`
- `@habito`
- `@evento`

Estas etiquetas:

- ❌ No son obligatorias  
- ❌ No se usan por defecto  
- ✅ Se usan **solo como excepción consciente**

---

## 4. Caso canónico: IDEA

La clasificación **IDEA** se define mediante la siguiente expresión lógica:

```text
((no date & no deadline) | (@idea & !@tarea & !@meta & !@habito & !@evento))
````

---

## 5. Lectura formal de la expresión

Una acción es **IDEA** si se cumple **al menos una** de las siguientes condiciones:

### 5.1 Inferencia automática

```text
(no date & no deadline)
```

* No tiene fecha de inicio
* No tiene fecha límite
* No existe decisión temporal
* Es una idea en estado puro

---

### 5.2 Decisión explícita (precedente)

```text
(@idea & !@tarea & !@meta & !@habito & !@evento)
```

* El usuario ha decidido conscientemente que es una idea
* No existe ambigüedad con otros tipos
* La etiqueta **anula cualquier inferencia temporal**

---

## 6. Qué garantiza esta estructura

Esta formulación asegura que:

* La etiqueta `@idea` **gana siempre** si está presente
* La inferencia temporal **solo actúa en ausencia de etiquetas de tipo**
* Nunca puede haber **doble clasificación**
* El filtro es **atemporal y estable**
* El sistema es **auditable y lógico**

---

## 7. Regla general MAR (formalizada)

Para cualquier tipo `X`:

> **X = (Etiqueta X explícita) OR (Inferencia temporal X)**
> **siempre excluyendo el resto de etiquetas de tipo**

Esta es la base de todos los filtros con precedencia.

---

## 8. Cuándo usar etiquetas de tipo

Usa una etiqueta de tipo **solo cuando**:

* la inferencia automática no refleja tu intención real
* quieres una excepción estable en el tiempo
* el caso no encaja limpiamente en el árbol de decisión

No las uses como norma general.

---

## 9. Regla de coherencia MAR

> **Si al eliminar todas las etiquetas
> el tipo deja de estar claro,
> el sistema está mal modelado.**

Las etiquetas corrigen casos límite,
los filtros sostienen el sistema.

---

## 10. Cierre

La precedencia explícita permite a MAR combinar:

* **automatización robusta**
* **control humano consciente**

sin mezclar planos ni romper la coherencia temporal del sistema.
