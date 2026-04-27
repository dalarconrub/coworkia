# Playbook: crear protocolos para cualquier comando o funcion

## Proposito

Este playbook sirve para convertir una orden corta, comando, funcion, boton,
script o rutina repetida en un protocolo operativo reproducible.

El objetivo no es documentar "que hace" una funcion de forma superficial. El
objetivo es capturar como debe interpretarse, que contexto debe recuperarse
antes de ejecutarla, que validaciones exige, que artefactos deja y como se
cierra sin perder trazabilidad.

Ejemplos de comandos que merecen protocolo:

- `inicia sesion`, `sigue`, `cierra sesion`
- `deploy`, `release`, `sync`, `publish`
- `train model`, `evaluate`, `run benchmark`
- `migrate database`, `rollback`, `seed`
- `import dataset`, `refresh cache`, `generate report`
- cualquier boton critico en una herramienta interna

## Cuándo crear un protocolo

Crea un protocolo cuando se cumpla al menos una condicion:

- La orden se repite y cada ejecucion requiere recordar pasos implicitos.
- Un error de orden, contexto o validacion puede costar datos, dinero o tiempo.
- Varias personas o agentes ejecutan la misma funcion con criterios distintos.
- La funcion produce artefactos que deben quedar versionados, auditados o
  regenerables.
- El comando parece simple, pero en realidad implica preflight, decision,
  ejecucion, validacion y cierre.
- Ya hubo una confusion o incidente que el protocolo puede prevenir.

No crees un protocolo pesado para una accion trivial, local y reversible. En
ese caso basta una ayuda CLI, un comentario o una entrada breve en README.

## Principio base

Un protocolo bueno separa cinco cosas que suelen mezclarse:

1. **Intencion:** que quiere lograr el usuario al invocar la orden.
2. **Contexto:** que hay que leer o verificar antes de actuar.
3. **Ejecucion:** que pasos concretos se hacen, en que orden.
4. **Validacion:** como sabemos que salio bien o que debe detenerse.
5. **Cierre:** que se registra, publica, revierte o deja pendiente.

Si falta una de esas cinco capas, el protocolo todavia depende de memoria oral.

## Plantilla minima

Usa esta estructura como punto de partida:

```md
# Protocolo: <comando o funcion>

## Proposito

<Que resuelve y que no resuelve.>

## Disparadores

- `<orden exacta>` -> <interpretacion>
- `<alias>` -> <interpretacion>

## Precondiciones

- <estado esperado>
- <permisos o recursos necesarios>
- <fuentes de verdad que deben leerse>

## Flujo operativo

1. <paso 1>
2. <paso 2>
3. <paso 3>

## Validaciones

- <check automatico o manual>
- <criterio de exito>
- <criterio de bloqueo>

## Artefactos

| Artefacto | Se crea/actualiza | Para que sirve |
| --- | --- | --- |
| `<ruta>` | si/no/cuando | <uso> |

## Politica de Git / publicacion

- <commit, push, tag, release, no-op>

## Errores y recuperacion

| Fallo | Accion |
| --- | --- |
| <sintoma> | <respuesta segura> |

## Cierre

- <que registrar>
- <que responder al usuario>
- <que queda pendiente>
```

## Flujo para extraer el protocolo

### 1. Nombrar la orden

Especifica la interfaz exacta:

- texto natural: `cierra sesion`
- CLI: `python tools/session.py cierra`
- funcion: `close_session()`
- API: `POST /deployments`
- UI: boton "Publish"

Registra aliases aceptados y aliases prohibidos. Si dos palabras parecen
sinonimos pero no lo son, documentalo.

### 2. Definir la intencion real

Pregunta: "Cuando el usuario dice esto, que trabajo espera que quede hecho?"

Ejemplo:

- Malo: "`cierra sesion` corre `tools/session.py cierra`."
- Bueno: "`cierra sesion` deja la sesion reproducible: valida memoria,
  registra trazabilidad, prepara commit, hace push y deja pendientes claros."

La intencion manda sobre el mecanismo. Si el mecanismo cambia, el protocolo
sigue vivo.

### 3. Mapear fuentes de verdad

Antes de ejecutar, define que fuentes mandan:

| Tipo | Ejemplos |
| --- | --- |
| Instrucciones | `AGENTS.md`, `CLAUDE.md`, `README.md` |
| Memoria | `memory/*.md`, ADRs, changelog |
| Estado vivo | chat diario, devlog, issue, ticket |
| Estado tecnico | Git, DB migrations, manifests, env |
| Artefactos derivados | HTML generado, reports, snapshots |

La regla de precedencia debe quedar escrita. Sin precedencia, cada ejecucion
puede resolver conflictos de forma distinta.

### 4. Separar preflight de ejecucion

Todo comando con riesgo necesita preflight. El preflight responde:

- Estoy en la rama correcta?
- Hay cambios ajenos?
- Existen secretos o credenciales requeridos?
- El servicio esta vivo?
- El dataset/manifiesto coincide con la spec?
- La documentacion generada esta al dia?
- Hay locks, jobs activos o procesos que puedan interferir?

El preflight debe detener la ejecucion si una condicion hace inseguro seguir.

### 5. Especificar orden y atomicidad

El protocolo debe decir que pasos son:

- **secuenciales:** el paso B depende de A;
- **paralelizables:** pueden correrse a la vez;
- **atomicos:** si fallan, no debe quedar estado parcial;
- **idempotentes:** pueden repetirse sin dañar;
- **destructivos:** requieren confirmacion o alternativa segura.

Para comandos con varios outputs, documenta si se permite estado parcial y como
se recupera.

### 6. Definir validaciones

Cada protocolo debe tener checks proporcionales al riesgo:

| Riesgo | Validacion minima |
| --- | --- |
| Documentacion | build/validate del doc generado, links, tests estaticos |
| Codigo | tests tocados, lint/check relevante, smoke test |
| Datos | conteos, schema, manifest, checksum |
| Deploy | health check, rollback plan, logs |
| Git | `git diff --check`, status limpio, commit/push |
| Memoria | sync/check de memoria, devlog/chat |

No basta "parece bien". Debe haber una senal repetible.

### 7. Declarar artefactos

Lista que se crea o actualiza:

- archivos versionados;
- archivos ignorados regenerables;
- logs;
- snapshots;
- dashboards;
- releases;
- commits;
- tags;
- mensajes en sistemas externos.

Para cada artefacto, di si es fuente de verdad o derivado. Los derivados deben
tener comando de regeneracion o razon para versionarse.

### 8. Escribir politica de cierre

Todo protocolo necesita cierre:

- que se reporta al usuario;
- que se escribe en devlog/chat/issue;
- si hay commit;
- si hay push;
- si hay tag/release/deploy;
- que hacer si una validacion falla;
- que queda pendiente.

La ausencia de cierre crea sesiones largas con estado ambiguo.

### 9. Capturar errores conocidos

Incluye una tabla de fallos frecuentes:

| Sintoma | Causa probable | Respuesta segura |
| --- | --- | --- |
| lock de Git | proceso previo o permisos | verificar y reintentar sin borrar a ciegas |
| HTML desactualizado | no se corrio generador | regenerar y validar |
| memoria desfasada | TREE o snapshot viejo | correr snapshot/sync y repetir check |
| test lento timeout | suite larga | partir suite y registrar cobertura |
| push rechazado | remoto avanzo | fetch/rebase/merge segun politica |

El protocolo debe enseñar como fallar bien, no solo como pasar.

### 10. Enlazarlo donde se invoca

Un protocolo no sirve si nadie lo encuentra. Enlazalo desde:

- instrucciones de agentes;
- README;
- help del CLI;
- runbook;
- docs de usuario;
- indice `playbooks/README.md`;
- comentario cerca de la funcion si aplica.

## Criterios de calidad

Un protocolo esta listo cuando:

- un agente nuevo puede ejecutarlo sin contexto oral;
- distingue intencion de implementacion;
- contiene preflight, ejecucion, validacion y cierre;
- tiene criterios claros de stop/bloqueo;
- declara artefactos y fuentes de verdad;
- explica commit/push/publicacion si aplica;
- incluye al menos una ruta de recuperacion ante fallo;
- esta enlazado desde el lugar donde el usuario encontrara la orden;
- fue probado al menos una vez en una ejecucion real o simulada.

## Anti-patrones

- **Solo listar comandos.** Eso es un checklist, no un protocolo.
- **No definir stop conditions.** Sin stop, los agentes improvisan.
- **Ocultar decisiones en prosa.** Las decisiones deben estar en bullets o
  tablas claras.
- **No distinguir derivado vs fuente.** Lleva a editar HTML generado o snapshots
  como si fueran canónicos.
- **No registrar errores.** Si el protocolo solo cubre el camino feliz, fallara
  en la primera incidencia.
- **Versionar secretos.** Ningun protocolo debe normalizar tokens, tunnels o
  credenciales en Git.
- **Automatizar antes de entender.** Primero protocolo manual reproducible,
  luego script.

## Cuando convertirlo en script

Convierte el protocolo en herramienta si:

- se ejecuta a menudo;
- los pasos son deterministas;
- el coste de equivocarse es alto;
- las validaciones son automatizables;
- el resultado debe ser igual entre agentes.

Pero conserva el playbook. El script ejecuta; el playbook explica intencion,
politica, excepciones y recuperacion.

## Mini-ejemplo: comando `publish report`

```md
## Disparador

`publish report` -> regenerar informe, validar HTML/PDF, commit, tag y push.

## Preflight

- Git sin cambios ajenos.
- Datos fuente existen y manifest pasa schema.
- No hay secretos en `data_runtime/`.

## Flujo

1. Regenerar Markdown.
2. Renderizar HTML/PDF.
3. Validar links/tablas.
4. Ejecutar smoke tests.
5. Registrar devlog.
6. Commit.
7. Tag si es release.
8. Push.

## Stop

- Si falla schema, no renderizar.
- Si falla validacion HTML, no commit.
- Si push es rechazado, no forzar; resolver divergencia.
```

## Mantenimiento

Revisar el protocolo cuando:

- cambie el comando o funcion;
- aparezca un nuevo fallo recurrente;
- se automatice un paso manual;
- cambie la politica de Git/deploy;
- cambien fuentes de verdad o artefactos;
- una persona nueva no pueda ejecutarlo sin ayuda.

