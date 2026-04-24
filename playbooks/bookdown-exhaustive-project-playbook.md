# Playbook Para Crear Un Bookdown Exhaustivo De Un Proyecto

**Fecha:** 2026-04-24
**Fuente:** extraido del trabajo de ampliacion, auditoria y endurecimiento del bookdown de `ai-system-lab`.
**Proposito:** convertir lo aprendido en una metodologia reutilizable para documentar proyectos complejos mediante un manual bookdown navegable, exhaustivo y verificable.

---

## 0. Principio Central

Un bookdown exhaustivo no es una coleccion de capitulos bonitos. Es una capa operativa del proyecto.

Debe permitir que una persona nueva pueda:

- entender que hace el sistema;
- instalarlo;
- arrancarlo;
- ejecutar flujos representativos;
- saber que carpetas existen y para que sirven;
- distinguir demo, local, staging, produccion y pendiente;
- encontrar scripts, tests, evidencias y salidas;
- auditar contradicciones entre documentacion y codigo.

La regla practica es:

> Si el bookdown no ayuda a ejecutar, validar o navegar el proyecto, todavia no es exhaustivo.

---

## 1. Cuando Crear O Expandir El Bookdown

Conviene hacerlo cuando:

- el repo ya tiene multiples carpetas y entrypoints;
- hay usuarios nuevos que necesitan una ruta guiada;
- la documentacion esta repartida entre README, docs, scripts y tests;
- existen pipelines o casos de uso integrados;
- empiezan a aparecer claims de madurez que necesitan matices;
- el equipo necesita una "memoria navegable" del sistema.

No conviene hacerlo demasiado pronto si el proyecto cambia de forma cada dia. En esa fase basta con un README y notas de arquitectura. El bookdown empieza a pagar cuando el coste de orientarse en el repo ya es alto.

---

## 2. Fuentes Que Hay Que Minar

Antes de escribir capitulos, inventaria el proyecto.

Fuentes primarias:

| Fuente | Que extraer |
| --- | --- |
| `README.md` | comandos canonicos, promesa del proyecto, quickstart |
| arbol de carpetas | dominios reales del sistema |
| `examples/` | demos y scripts que un usuario puede ejecutar |
| `tests/` | comportamiento validado, suites importantes, coste de ejecucion |
| `ops/` | acceptance, release, deployment, runbooks, evidencias |
| `docs/` | guias previas, auditorias, planes, estado de produccion |
| codigo de API/dashboard/apps | entrypoints reales y rutas visibles |
| `data_runtime/` y `data/processed/` | tipos de evidencia que el sistema genera |

Fuentes secundarias:

| Fuente | Que extraer |
| --- | --- |
| historial de sprints | evolucion y prioridades |
| documentos de roadmap | que esta cerrado y que queda pendiente |
| errores de ejecucion | comandos que no arrancan, docs obsoletas |
| outputs de pruebas | coste real y confianza de cada suite |
| conversaciones de desarrollo | decisiones tacitas que aun no estan en docs |

---

## 3. Pipeline Recomendado

### Paso 1. Inventario De Superficie

Lista todos los elementos que el usuario podria necesitar:

- carpetas raiz;
- subcarpetas criticas;
- scripts ejecutables;
- tests;
- documentos;
- endpoints;
- outputs generados;
- pipelines;
- entidades de dominio;
- limites conocidos.

No escribas todavia. Primero calibra el tamano del sistema.

### Paso 2. Definir La Arquitectura Del Manual

Un bookdown exhaustivo debe tener al menos estas familias:

1. **Entrada y conceptos:** como leer el manual, vocabulario basico.
2. **Instalacion y primer arranque:** entorno, API, dashboard, app humana.
3. **Pipelines operativas:** recorridos end-to-end.
4. **Pipelines analiticas:** modelos, fitting, evaluacion, reporting.
5. **Estructura del repo:** mapa de carpetas y responsabilidades.
6. **Manual por procesos:** que hacer para lograr objetivos comunes.
7. **Catalogos:** scripts, tests, documentos, carpetas, outputs.
8. **Ops:** acceptance, deployment, production readiness, evidencias.
9. **Ecosistema avanzado:** memoria, sprints, orquestacion, portfolio, platform.
10. **FAQ/glosario:** dudas frecuentes y lectura final.

La estructura debe responder al usuario, no al autor. El orden ideal es: entender -> arrancar -> ejecutar -> interpretar -> operar -> auditar.

### Paso 3. Escribir Capitulos Por Bloques Cerrados

No intentes escribir todo linealmente. Cierra bloques:

- un bloque de instalacion;
- un bloque de pipelines;
- un bloque de carpetas;
- un bloque de modelos/fitting/evaluation;
- un bloque de tests;
- un bloque de ops;
- un bloque de navegacion maestra.

Cada bloque debe terminar con una tabla o resumen que permita usarlo sin releer todo.

### Paso 4. Convertir Conocimiento En Tablas Maestras

Las tablas maestras son el mecanismo que convierte documentacion larga en navegacion util.

Tablas recomendadas:

| Tabla | Columnas utiles |
| --- | --- |
| carpetas | carpeta -> para que sirve -> quien la usa -> ejemplos relacionados |
| modelos | archivo -> modelo -> tarea ideal -> salida principal |
| fitting | archivo -> funcion -> entrada -> salida -> cuando usarla |
| evaluation | funcion -> que valida -> interpretacion |
| funciones | funcion -> entrada -> salida -> caso de uso |
| tests | suite/test -> que valida -> cuando correrlo -> coste esperado |
| scripts | script -> objetivo -> entrada -> salida -> carpeta relacionada |
| documentos | documento -> objetivo -> cuando leerlo -> perfil |
| repo/documentacion | quiero hacer -> donde mirar -> documento -> comando |
| ecosistema operativo | capa -> documentos -> codigo -> evidencia -> usuario |
| ops | archivo -> objetivo -> evidencia generada -> cuando ejecutarlo -> salida esperada |

Regla: una tabla maestra debe servir para decidir el siguiente paso, no solo para enumerar.

### Paso 5. Anadir Diagramas Por Pipeline

Los diagramas funcionan cuando explican flujo, no decoracion.

Cada pipeline importante deberia tener:

- origen;
- transformaciones;
- validacion;
- artefactos;
- consumo posterior.

Formato recomendado:

```mermaid
flowchart LR
    A[Entrada] --> B[Proceso]
    B --> C[Validacion]
    C --> D[Evidencia]
    D --> E[Uso]
```

El diagrama debe complementar una tabla o pasos ejecutables. Si no conecta con comandos o salidas reales, sobra.

### Paso 6. Separar Capacidad Real De Aspiracion

Un bookdown exhaustivo debe ser honesto:

- `local`: funciona en la maquina del usuario;
- `demo`: ilustra un flujo con datos o servicios simulados;
- `staging simulado`: valida contratos sin proveedor externo real;
- `produccion real`: requiere endpoints, secretos, storage, cola, observabilidad y acceptance externo;
- `pendiente`: arquitectura o documentacion existe, pero falta activacion real.

La documentacion falla cuando dice "production-ready" sin explicar que evidencias lo prueban o que proveedores faltan.

---

## 4. Lecciones Aprendidas En Este Proyecto

### 4.1 La Fuente De Verdad Debe Ser Unica

Problema encontrado: el generador HTML tenia una lista manual de capitulos separada de `_bookdown.yml`.

Leccion:

- `_bookdown.yml` debe ser la fuente canonica del orden de capitulos;
- cualquier generador alternativo debe leer esa lista;
- duplicar listas crea divergencia silenciosa.

Regla:

> Si hay dos indices del libro, uno de los dos acabara mintiendo.

### 4.2 Las Tablas Son Contenido Critico, No Detalle De Render

Problema encontrado: el HTML estatico publicaba tablas Markdown como parrafos `| ... |`.

Impacto:

- las tablas maestras eran ilegibles;
- justo la parte mas util del manual perdia valor;
- el usuario veia texto plano en vez de una herramienta de navegacion.

Leccion:

- el render estatico debe soportar tablas;
- despues de crear tablas maestras hay que inspeccionar el HTML, no solo los `.Rmd`;
- debe existir un validador que falle si queda `<p>|...|</p>`.

### 4.3 Los Anchors Repetidos Rompen La Navegacion

Problema encontrado: muchos capitulos repiten titulos como `Alcance`, `Tabla Maestra` o `Que Debe Recordar Un Usuario`.

Leccion:

- un generador estatico debe crear IDs unicos;
- el indice debe apuntar a anchors existentes;
- hay que validar IDs duplicados y links internos rotos.

### 4.4 Los Enlaces Markdown Tambien Son Contrato

Problema encontrado: un enlace Markdown aparecia como texto literal en el HTML.

Leccion:

- el render debe convertir enlaces basicos;
- un validador debe buscar patrones crudos como `[texto](ruta)`;
- los enlaces a archivos locales son parte de la navegacion del manual.

### 4.5 La Documentacion De Estado Se Vuelve Obsoleta Rapido

Problema encontrado: `COORDINATION_STATUS.md` seguia describiendo como P0 un entrypoint antiguo, aunque el README y el bookdown ya usaban `ais_platform.api.main:app`.

Leccion:

- los documentos de coordinacion necesitan auditoria tras cada bloque grande;
- no basta con corregir el bookdown si otro documento lo contradice;
- la auditoria debe buscar comandos viejos, claims de madurez y diagnosticos superados.

### 4.6 El Bookdown Debe Tener Su Propia Suite De Validacion

Mejora introducida:

- `generate_static_html.py`;
- `validate_static_html.py`;
- tests dedicados para tablas, enlaces, anchors y lectura desde `_bookdown.yml`.

Leccion:

> Un manual grande sin tests se degrada igual que el codigo.

Validaciones minimas:

- generar HTML;
- validar HTML;
- comprobar que no hay tablas crudas;
- comprobar que no hay enlaces crudos;
- comprobar IDs duplicados;
- comprobar anchors rotos;
- correr smoke/readiness del proyecto;
- correr suite completa antes de release documental.

---

## 5. Estructura Recomendada De Archivos

```text
docs/bookdown/
  _bookdown.yml
  README.md
  index.Rmd
  01-...
  02-...
  ...
  render_book.R
  generate_static_html.py
  validate_static_html.py
  _book/
    index.html

tests/
  test_bookdown_static_html.py
```

Reglas:

- `_bookdown.yml` define el orden;
- `README.md` explica como renderizar y validar;
- `generate_static_html.py` permite publicar sin R;
- `validate_static_html.py` convierte problemas visuales en errores detectables;
- `tests/test_bookdown_static_html.py` protege el comportamiento del generador.

---

## 6. Checklist De Un Bookdown Exhaustivo

### Cobertura

- [ ] explica objetivo del proyecto;
- [ ] define conceptos basicos;
- [ ] instala desde cero;
- [ ] arranca servicios visibles;
- [ ] describe pipelines end-to-end;
- [ ] lista carpetas y responsabilidades;
- [ ] lista scripts ejecutables;
- [ ] lista tests y coste esperado;
- [ ] lista documentos y perfiles de lectura;
- [ ] explica outputs y evidencias;
- [ ] distingue local/demo/staging/prod;
- [ ] tiene FAQ y glosario.

### Navegacion

- [ ] tabla maestra de carpetas;
- [ ] tabla maestra de scripts;
- [ ] tabla maestra de tests;
- [ ] tabla maestra de documentos;
- [ ] tabla maestra de navegacion del repo;
- [ ] tabla maestra del ecosistema operativo;
- [ ] diagramas por pipeline;
- [ ] indice sin anchors rotos.

### Veracidad

- [ ] comandos documentados existen;
- [ ] entrypoints canonicos coinciden con README;
- [ ] claims de produccion tienen evidencias;
- [ ] stubs y simulaciones estan etiquetados;
- [ ] documentos de coordinacion no contradicen el manual;
- [ ] los tests citados pasan o se marca el fallo.

### Render

- [ ] HTML generado;
- [ ] tablas renderizadas como `<table>`;
- [ ] enlaces renderizados como `<a>`;
- [ ] IDs unicos;
- [ ] Mermaid visible o advertencia offline;
- [ ] validacion automatica del HTML.

---

## 7. Validador Minimo Recomendado

Un validador pragmatico debe comprobar:

1. todos los `.Rmd` de `_bookdown.yml` existen;
2. el HTML generado existe;
3. no hay parrafos que empiecen por `|`;
4. no quedan enlaces Markdown crudos;
5. no hay IDs duplicados;
6. los `href="#..."` apuntan a IDs existentes;
7. las tablas Markdown tienen columnas consistentes;
8. se emite warning si Mermaid depende de CDN.

Este tipo de validador no reemplaza una revision humana, pero evita regresiones tontas.

---

## 8. Antipatrones

### 8.1 Manual Como Vertedero

Sintoma: se agregan capitulos sin estructura ni tablas finales.

Correccion: cada bloque nuevo debe cerrar con una tabla maestra, checklist o mapa de decision.

### 8.2 Documentacion Aspiracional

Sintoma: el manual describe lo que se desea que el sistema haga, no lo que puede ejecutar.

Correccion: cada claim debe conectarse con comando, test, endpoint, output o evidencia.

### 8.3 Duplicar Indices

Sintoma: `_bookdown.yml`, scripts y README mantienen listas manuales distintas.

Correccion: una sola fuente de verdad, preferiblemente `_bookdown.yml`.

### 8.4 Publicar Sin Mirar El HTML

Sintoma: los `.Rmd` se ven correctos, pero el HTML rompe tablas, enlaces o diagramas.

Correccion: validar el artefacto publicado, no solo la fuente.

### 8.5 No Distinguir Usuarios

Sintoma: todos los capitulos hablan al mismo lector.

Correccion: crear rutas por perfil: usuario nuevo, investigador, operador, desarrollador, revisor, DevOps.

### 8.6 Confundir Exhaustivo Con Largo

Sintoma: muchas paginas, poca capacidad de decision.

Correccion: tablas maestras, comandos, salidas esperadas y rutas de lectura.

---

## 9. Plantilla De Capitulo

````markdown
# [Nombre Del Bloque]

## Para Que Sirve

[Explicacion breve y concreta.]

## Donde Vive

| Carpeta/archivo | Rol |
| --- | --- |

## Flujo Mental

```mermaid
flowchart LR
    A[Entrada] --> B[Proceso]
    B --> C[Salida]
```

## Como Usarlo

```bash
[comando]
```

## Salida Esperada

- [archivo]
- [endpoint]
- [evidencia]

## Tabla Maestra

| Elemento | Objetivo | Entrada | Salida | Cuando usarlo |
| --- | --- | --- | --- | --- |

## Errores Frecuentes

- [error] -> [interpretacion] -> [accion]

## Que Debe Recordar Un Usuario

- [3-5 ideas maximas]
````

---

## 10. Flujo Operativo Para Mantenerlo

Cada vez que se agregue una carpeta, script, test o pipeline:

1. actualizar el capitulo especifico;
2. actualizar la tabla maestra correspondiente;
3. actualizar la tabla de navegacion si cambia el recorrido del usuario;
4. actualizar `_bookdown.yml` si hay capitulo nuevo;
5. regenerar HTML;
6. validar HTML;
7. correr smoke/readiness;
8. si el cambio toca claims importantes, correr suite completa;
9. revisar documentos de estado que puedan quedar obsoletos.

Comandos recomendados:

```bash
python docs/bookdown/generate_static_html.py
python docs/bookdown/validate_static_html.py
python -m pytest tests/smoke tests/readiness -q
python -m pytest tests/test_bookdown_static_html.py -q
```

Antes de release documental:

```bash
python -m pytest -q
```

---

## 11. Criterios De Cierre

Un bookdown exhaustivo esta cerrado para una fase cuando:

- una persona nueva puede seguirlo sin abrir el codigo primero;
- cada carpeta importante tiene explicacion y ejemplos relacionados;
- cada pipeline tiene pasos, diagrama, validacion y salida esperada;
- los scripts principales aparecen en catalogo y tabla maestra;
- los tests principales indican que validan, cuando correrlos y coste;
- los documentos tienen objetivo, perfil y momento de lectura;
- el HTML generado es navegable y validado;
- las limitaciones reales estan marcadas sin maquillaje;
- la suite relevante pasa.

---

## 12. Mini-Workflow Si Solo Hay Tiempo Para Lo Esencial

Si no puedes construir el manual completo, haz esto:

1. `index.Rmd`: que es el proyecto y ruta de lectura.
2. instalacion + primer arranque.
3. estructura del repo con tabla maestra de carpetas.
4. pipelines principales con comandos y salidas.
5. tabla maestra de scripts.
6. tabla maestra de tests.
7. tabla maestra de documentacion.
8. generador HTML + validador minimo.

Eso no es perfecto, pero ya convierte el repo en algo navegable.

---

## 13. Provenance

Este playbook se extrajo aplicando la metodologia de `sprints/meta-methodology-extracting-playbooks-from-projects.md` al trabajo realizado sobre el bookdown de `ai-system-lab`.

Material fuente usado:

- ampliacion de capitulos `docs/bookdown/*.Rmd`;
- creacion de tablas maestras de carpetas, scripts, tests, docs, ops y navegacion;
- adicion de diagramas por pipeline;
- auditoria del HTML generado;
- correccion de tablas Markdown no renderizadas;
- eliminacion de lista duplicada de capitulos en el generador;
- anchors unicos;
- render de enlaces Markdown;
- creacion de `validate_static_html.py`;
- pruebas `tests/test_bookdown_static_html.py`;
- actualizacion de `docs/COORDINATION_STATUS.md`.

La leccion mas transferible es simple:

> Un bookdown exhaustivo debe tratarse como software: tiene arquitectura, fuente de verdad, validacion, regresiones y criterios de release.
