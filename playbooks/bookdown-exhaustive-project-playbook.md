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
bookdown/
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
python bookdown/generate_static_html.py
python bookdown/validate_static_html.py
python -m pytest tests/smoke tests/readiness -q
python -m pytest tests/test_bookdown_static_html.py -q
```

Antes de release documental:

```bash
python -m pytest -q
```

---

## 10.1 Patron Incremental Usado En Este Repo

La practica que mejor funciono en `ai-system-lab` fue tratar cada avance del sistema como una unidad documental cerrada. Cuando se anadio un caso de uso, una fase operativa o una funcionalidad transversal, no se espero a una "fase de documentacion" posterior: se actualizo el bookdown en el mismo bloque de trabajo.

La secuencia reusable fue:

1. implementar o consolidar el cambio en codigo, scripts, tests y artefactos;
2. identificar que capitulo explica el flujo principal;
3. actualizar las tablas maestras afectadas;
4. actualizar los catalogos de scripts, tests, docs y ops;
5. regenerar el HTML estatico;
6. validar el HTML y correr los tests relevantes;
7. revisar documentos de estado para evitar contradicciones.

Esta regla evita que el manual sea una fotografia antigua del repo. El bookdown debe cambiar al mismo ritmo que los entrypoints reales.

### 10.1.1 Cuando Hay Un Nuevo Caso De Uso

Un caso de uso nuevo no debe quedar solo en `examples/`, `ops/` o `data_runtime/`. Debe entrar en el manual como recorrido completo.

En este repo, el caso Centaur/Psych-101 acabo documentado como capitulo propio porque tenia:

- dataset y fuente externa;
- endpoint real o wrapper local;
- comandos de diagnostico;
- fases de ejecucion;
- scoring;
- acceptance;
- evidencias runtime;
- paper report;
- publication package;
- decisiones de escalado.

Criterio practico:

| Senal | Accion en bookdown |
| --- | --- |
| El caso tiene mas de un comando | crear seccion de flujo o capitulo propio |
| Genera evidencias en `data_runtime/` | documentar rutas de salida |
| Tiene tests dedicados | anadirlo a la tabla maestra de tests |
| Tiene scripts en `ops/` o `examples/` | anadirlos a la tabla maestra de scripts |
| Cambia claims del proyecto | actualizar estado, limitaciones y README/bookdown |
| Requiere credenciales o endpoint externo | separar local/demo/staging/real y anadir stop conditions |

Plantilla minima para un caso de uso:

````markdown
# Caso: [nombre]

## Objetivo

## Entradas

| Entrada | Ruta | Estado |
| --- | --- | --- |

## Comandos

```bash
[comando de diagnostico]
[comando de ejecucion]
[comando de validacion]
```

## Evidencias

| Artefacto | Ruta | Uso |
| --- | --- | --- |

## Acceptance

## Limitaciones Y Stop Conditions

## Siguiente Decision
````

### 10.1.2 Cuando Se Anade Una Funcionalidad Transversal

Las funcionalidades transversales suelen tocar varias zonas: API, dashboard, ops, docs, tests y runtime. Si solo se documentan en un capitulo, el usuario no las encontrara desde otros recorridos.

Patron usado:

| Cambio | Donde actualizar |
| --- | --- |
| Nuevo endpoint o API | capitulo de plataforma/API, tabla de scripts si hay cliente, tabla de tests |
| Nuevo dashboard o vista | capitulo dashboard/UX, screenshots o descripcion de flujo, tests relacionados |
| Nueva herramienta CLI | catalogo de scripts, tabla ops, README si es comando canonico |
| Nueva fase de acceptance | capitulo ops, tabla de acceptance, guia de produccion si aplica |
| Nuevo modelo/fitting/evaluation | capitulo del bloque, tabla maestra especifica, tests |
| Nueva memoria/orquestacion/programa | ecosistema avanzado, tabla de sistema operativo, docs relacionados |

Regla:

> Una funcionalidad transversal necesita al menos una explicacion narrativa y una entrada de tabla maestra.

### 10.1.3 Cuando Se Anade Un Script

Cada script nuevo debe responder a cinco preguntas en el manual:

1. para que sirve;
2. que entrada espera;
3. que salida genera;
4. cuando se ejecuta;
5. que test lo cubre o que validacion lo sustituye.

En este repo se volvio critico mantener `15a-catalogo-completo-de-ejemplos-y-scripts.Rmd`, `15b-tabla-maestra-de-scripts.Rmd` y `22-tabla-maestra-ops-y-publicacion-resultados.Rmd` sincronizados. La buena practica es no crear scripts "invisibles".

Checklist para script nuevo:

- [ ] aparece en el capitulo de su carpeta;
- [ ] aparece en la tabla maestra de scripts;
- [ ] declara entradas y salidas;
- [ ] enlaza evidencia si escribe en `data_runtime/`;
- [ ] tiene test o smoke asociado;
- [ ] el comando esta escrito con rutas reales;
- [ ] si consume secretos, no imprime ni documenta valores reales.

### 10.1.4 Cuando Se Anade Un Test

Los tests son documentacion ejecutable. Si una suite nueva valida una capacidad importante, debe aparecer en el bookdown.

Practica usada:

| Tipo de test | Como documentarlo |
| --- | --- |
| smoke/readiness | capitulo de instalacion, ops y tabla de tests |
| test de script `ops/` | tabla de scripts y tabla de tests |
| test de caso real | capitulo del caso y acceptance |
| test de render bookdown | README de bookdown y seccion de validacion |
| test de produccion/staging | guias de activacion y tabla ops |

Cada entrada util de test debe incluir:

- que valida;
- cuando correrlo;
- coste esperado;
- que fallo indica;
- que archivo o artefacto protege.

### 10.1.5 Cuando Se Anaden Evidencias Runtime

`data_runtime/` crece rapido. No conviene listar todo, pero si explicar las familias de evidencia que un operador debe mirar.

Patron usado:

- el capitulo del caso explica las rutas concretas;
- las tablas maestras de ops enlazan validadores, acceptance y publication package;
- el README/bookdown solo menciona los artefactos canonicos;
- los detalles exhaustivos viven en tablas o capitulos especializados.

Buena practica:

| Evidencia | Debe aparecer en |
| --- | --- |
| run archivado | capitulo del caso, tabla ops, publication/report |
| acceptance report | capitulo ops, criterios de cierre |
| readiness/status | capitulo operativo del caso |
| handoff/resume packet | capitulo del caso y stop conditions |
| publication package | capitulo publication, tabla ops, README si es entrega principal |
| validation report | seccion de validacion y tests |

### 10.1.6 Cuando Cambia El Estado Del Proyecto

Una de las mejores practicas fue auditar los documentos de estado despues de cambios grandes. Si el bookdown dice que algo esta completo, pero `COORDINATION_STATUS.md`, README o una guia de produccion dicen otra cosa, el repo queda incoherente.

Despues de cada bloque grande:

```bash
rg -n "pendiente|blocked|TODO|production-ready|staging|demo|simulado|phase-|endpoint|next_action" README.md docs sprints
```

Busca:

- entrypoints antiguos;
- fases ya completadas que siguen como pendientes;
- comandos sustituidos por otros;
- claims de produccion sin evidencia;
- nombres de runs o fases obsoletos;
- rutas `data_runtime/` que cambiaron;
- instrucciones de endpoint que ya no son seguras.

### 10.1.7 Como Decidir Si Crear Capitulo Nuevo O Ampliar Uno Existente

No todo cambio merece capitulo propio. El criterio es de navegacion, no de importancia interna.

| Situacion | Decision |
| --- | --- |
| Es un flujo end-to-end con entradas, comandos, evidencias y acceptance | capitulo propio |
| Es una tabla de referencia grande | capitulo-tabla propio |
| Es una funcion dentro de un bloque ya explicado | ampliar capitulo existente |
| Es una variacion de un pipeline ya documentado | subseccion dentro del pipeline |
| Es una fase operativa con stop conditions | capitulo o seccion ops dedicada |
| Es una mejora interna sin superficie de usuario | mencionar solo si afecta tests/scripts/limitaciones |

Regla practica:

> Si una persona preguntaria "donde esta todo lo de X?", X probablemente necesita capitulo o tabla propia.

### 10.1.8 Mantener `_bookdown.yml` Como Contrato

Cada capitulo nuevo debe agregarse a `_bookdown.yml` en el mismo cambio. La posicion importa:

- conceptos antes de comandos;
- instalacion antes de operacion;
- pipelines antes de catalogos;
- carpetas antes de tablas maestras;
- ops antes de casos reales complejos;
- FAQ/glosario al final.

Despues de tocar `_bookdown.yml`:

```bash
python bookdown/generate_static_html.py
python bookdown/validate_static_html.py
python -m pytest -q tests/test_bookdown_static_html.py
```

### 10.1.9 Actualizacion En Cascada

Cada cambio documental debe revisar esta cascada:

| Cambio | Cascada minima |
| --- | --- |
| nuevo caso de uso | capitulo caso -> scripts -> tests -> ops -> navegacion -> README si es canonico |
| nuevo script | tabla scripts -> capitulo carpeta -> tests -> ops si escribe evidencias |
| nuevo test | capitulo tests -> tabla relacionada -> README si entra en quickstart |
| nuevo artefacto runtime | capitulo caso/ops -> publication/report si aplica |
| nuevo capitulo | `_bookdown.yml` -> README bookdown -> validacion HTML |
| cambio de estado | capitulo afectado -> docs de coordinacion -> changelog/release si aplica |

Esta cascada evita que el bookdown crezca por acumulacion desordenada.

### 10.1.10 DevLog Documental Recomendado

Cuando el cambio documental sea grande, deja una nota de cierre en el sistema de memoria o devlog si existe. En este repo, tras integrar el toolkit multiagente, esto deberia registrar:

- que se anadio o actualizo;
- que comandos de validacion pasaron;
- que limitaciones quedan;
- donde esta la siguiente decision.

El objetivo no es burocracia. Es que la siguiente sesion sepa que el bookdown ya fue actualizado junto con el codigo.

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

- ampliacion de capitulos `bookdown/*.Rmd`;
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

