# Playbook portable para crear un indice `playbooks/README.md`

Este playbook reproduce el patron de `playbooks/README.md` de Coworkia en una
version aplicable a cualquier repositorio. Sirve para crear una carpeta de
metodologias reutilizables sin confundirla con memoria canonica, documentacion
de usuario o historial del proyecto.

## Objetivo

Crear un `playbooks/README.md` que responda rapido a tres preguntas:

1. Que es un playbook en este repo.
2. Que playbooks existen y para que sirven.
3. Que criterios debe cumplir un nuevo playbook antes de entrar.

El indice debe ser corto, estable y mantenible. No debe convertirse en una
cronica ni en un manual completo.

## Cuando usarlo

Usalo cuando un repo tenga o vaya a tener una carpeta `playbooks/` con guias
transferibles, por ejemplo:

- protocolos de sesion;
- metodos de documentacion;
- flujos de release;
- auditorias repetibles;
- plantillas de migracion;
- procedimientos operativos que pueden moverse a otro repo.

No lo uses para sustituir:

- `README.md`, que explica el proyecto;
- `memory/`, que define memoria canonica del repo;
- `docs/`, que documenta el uso del sistema;
- `devlog/`, que registra hitos cerrados;
- `CHANGELOG.md`, que registra versiones publicas.

## Estructura recomendada

Un indice portable debe tener cuatro bloques:

```md
# Playbooks

Descripcion breve de que es esta carpeta y que no es.

## Disponibles

| Playbook | Para que sirve |
| --- | --- |
| [nombre-del-playbook.md](nombre-del-playbook.md) | Uso en una frase. |

## Criterios

- Debe declarar proposito, fuentes, flujo operativo y criterios de cierre.
- Debe distinguir capacidad real, limitaciones y aspiraciones.
- Debe contener pasos reutilizables, no solo una cronica del trabajo original.

## Mantenimiento

- Anadir una fila cuando nace un playbook.
- Actualizar la descripcion si cambia el alcance real.
- Eliminar o marcar como obsoleto lo que ya no sea fiable.
```

El bloque `Mantenimiento` es opcional si el repo ya tiene reglas equivalentes
en `AGENTS.md`, `CLAUDE.md`, `memory/STRUCTURE.md` o docs internas.

## Semantica de la carpeta

Define la carpeta con una frase parecida a esta:

```md
Metodologias reutilizables extraidas de trabajos ya ejecutados. Un playbook no
es memoria canonica del proyecto ni documentacion de usuario de un sistema
concreto: es un patron transferible para aplicar en otros proyectos o frentes.
```

Adaptala al repo, pero conserva la distincion:

- **Playbook**: metodo reusable.
- **Docs**: explicacion del producto o sistema.
- **Memory**: verdad canonica del repo.
- **Devlog/changelog**: historico de cambios.

## Tabla de playbooks

La tabla debe ser pequena y escaneable.

Formato recomendado:

```md
| Playbook | Para que sirve |
| --- | --- |
| [session-protocol.md](session-protocol.md) | Interpretar `inicia sesion`, `sigue` y `cierra sesion`. |
| [release-checklist.md](release-checklist.md) | Cerrar una release con validaciones, evidencias y rollback. |
```

Reglas:

- Una fila por archivo.
- Nombre enlazado relativo a `playbooks/`.
- Descripcion de una frase, no parrafo.
- Sin estado emocional ni marketing.
- Sin duplicar el contenido del playbook.

## Criterios de entrada

Un nuevo playbook entra si cumple:

- Tiene proposito explicito.
- Declara de que fuentes parte.
- Tiene flujo operativo reproducible.
- Incluye criterios de cierre o Definition of Done.
- Distingue lo probado de lo aspiracional.
- Es portable: otra persona puede aplicarlo fuera del repo original.
- No depende de secretos, rutas locales privadas ni memoria no versionada.

Si no cumple esos criterios, todavia es una nota, borrador o cronica; no un
playbook.

## Criterios de salida u obsolescencia

Marca o retira un playbook si:

- apunta a rutas que ya no existen;
- recomienda comandos peligrosos o obsoletos;
- contradice instrucciones del repo;
- mezcla demasiados casos y ya no es aplicable;
- depende de herramientas retiradas.

Opciones:

- actualizarlo;
- moverlo a `archive/`;
- marcarlo con una seccion `Estado: obsoleto`;
- reemplazarlo por otro playbook y enlazar el nuevo.

## Integracion con repos multiagente

Si el repo usa `memory/`, `chats/`, `devlog/` o agentes coordinados:

1. Referencia `playbooks/` en `memory/INDEX.md`.
2. Explica la carpeta en `memory/STRUCTURE.md`.
3. Regenera el arbol de estructura si existe uno.
4. Anade entrada en `devlog/DEVLOG.md` cuando nazca o cambie la familia.
5. Si el cambio deja memoria operativa, escribe `MEMORIA:` en el chat diario.

El indice de playbooks no sustituye a esos sistemas. Solo facilita descubrir
metodos reutilizables.

## Integracion en repos simples

Si el repo no tiene sistema multiagente, basta con:

1. Crear `playbooks/`.
2. Crear `playbooks/README.md`.
3. Enlazarlo desde el `README.md` principal.
4. Mantener la tabla a mano.

Opcionalmente anade esta regla al `README.md` o a las instrucciones del agente:

```md
Los playbooks viven en `playbooks/`. Cada nuevo playbook debe aparecer en
`playbooks/README.md` con una descripcion de una frase.
```

## Plantilla minima

```md
# Playbooks

Metodologias reutilizables del repo. Un playbook no es memoria canonica ni
documentacion completa: es un patron transferible para repetir un trabajo.

## Disponibles

| Playbook | Para que sirve |
| --- | --- |
| [example-playbook.md](example-playbook.md) | Describe el metodo reusable en una frase. |

## Criterios

- Debe declarar proposito, fuentes, flujo operativo y criterios de cierre.
- Debe distinguir capacidad real, limitaciones y aspiraciones.
- Debe contener pasos reutilizables, no solo una cronica del trabajo original.
```

## Checklist de implementacion

- [ ] Crear `playbooks/README.md`.
- [ ] Definir que es y que no es un playbook.
- [ ] Anadir tabla `Disponibles`.
- [ ] Registrar todos los playbooks existentes.
- [ ] Anadir criterios de entrada.
- [ ] Enlazar desde `README.md` o memoria del repo.
- [ ] Validar que todos los enlaces relativos existen.
- [ ] Registrar el cambio en devlog/changelog si el repo lo usa.

## Antipatrones

- Convertir el indice en una pagina larga de documentacion.
- Listar documentos que no son playbooks.
- No enlazar los archivos.
- Usar descripciones vagas como "varias cosas utiles".
- Mantener filas para playbooks borrados.
- Meter decisiones historicas que deberian ir a devlog o ADR.

## Definition of Done

El indice esta listo cuando:

- una persona nueva entiende que es `playbooks/` en menos de un minuto;
- todos los playbooks tienen enlace relativo valido;
- cada descripcion cabe en una frase;
- los criterios de entrada evitan que la carpeta se llene de notas sueltas;
- el README principal o la memoria del repo apuntan a `playbooks/` si procede.

