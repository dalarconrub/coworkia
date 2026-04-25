# Protocolo portable de inicio, continuacion y cierre de sesion

Version 2. Este playbook define como interpretar tres ordenes cortas del
usuario en repositorios asistidos por agentes:

- `inicia sesion`
- `sigue` / `continua`
- `cierra sesion`

El objetivo es que cualquier agente recupere el estado real del repositorio,
respete el trabajo vivo y deje una huella util para la siguiente sesion. El
protocolo funciona en repositorios genericos, pero esta version incorpora las
adaptaciones aprendidas al integrarlo con un sistema multiagente con `memory/`,
`chats/`, `devlog/`, `artifacts/multiagent/` y playbooks versionados.

## Principio base

La sesion no empieza en blanco. Antes de decidir o editar, el agente debe
reconstruir el contexto desde fuentes locales versionadas y desde Git. Si el
repo tiene sistema multiagente, el chat diario y el devlog son fuentes vivas; si
no lo tiene, se aplican los mismos pasos con las memorias, logs y documentos que
existan.

Orden de autoridad recomendado:

1. Instrucciones del repo (`AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, etc.).
2. Memoria curada (`memory/*.md`) si existe.
3. Chat diario append-only (`chats/chat_YYYY-MM-DD.md`) si existe.
4. Devlog o historial de hitos (`devlog/DEVLOG.md`, changelog, ADRs).
5. Estado Git real.
6. Documentacion de usuario (`README.md`, `docs/`, `bookdown/`, `playbooks/`).

## Instalacion en otro repositorio

Minimo recomendado:

1. Copiar este archivo a una ruta estable:
   - `playbooks/PROTOCOLO_INICIO_CIERRE_SESION.md`
   - `docs/PROTOCOLO_INICIO_CIERRE_SESION.md`
   - `AGENT_SESSION_PROTOCOL.md`
2. Enlazarlo desde las instrucciones de agentes:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `.github/copilot-instructions.md`
   - `README.md`
3. Definir que `inicia sesion`, `sigue` y `cierra sesion` activan este flujo.
4. Si el repo usa multiagentes, anadir o adaptar las piezas de la seccion
   "Contrato multiagente portable".

## Contrato multiagente portable

Un repo con el sistema completo deberia declarar estas rutas y reglas:

| Recurso | Funcion |
| --- | --- |
| `memory/INDEX.md` | Mapa de recursos y orden de lectura |
| `memory/PURPOSE.md` | Que es el proyecto y que no es |
| `memory/STRUCTURE.md` | Organizacion real del repo |
| `memory/SNAPSHOT.md` | Memoria derivada de chats, si existe |
| `memory/ROSTER.md` | Subagentes y focos, si existen |
| `chats/chat_YYYY-MM-DD.md` | Hilo vivo del dia, append-only |
| `multiagents/chat_template.md` | Plantilla de chat diario |
| `devlog/DEVLOG.md` | Log feature-level append-only |
| `artifacts/multiagent/` | Memoria estructurada derivada |
| `artifacts/daily/` | Timelines diarios derivados, si existen |
| `artifacts/sprints/` | Planes o ejecuciones multiagente, si existen |
| `tools/init_chat.py` | Resuelve o crea el chat activo |
| `tools/devlog.py` | Consulta y escribe devlog |
| `tools/memory_check.py` | Valida memoria/documentacion critica |
| `tools/snapshot_structure.py` | Regenera o valida el arbol de estructura |
| `tools/fix_chat_mojibake.py` | Repara mojibake en chats, si aplica |
| `tools/timeline.py` | Agrega chat/devlog/artifacts por dia, si aplica |
| `agents/orchestrator_agent.py sync-chat-memory` | Regenera memoria multiagente derivada, si aplica |

Reglas obligatorias para repos con este contrato:

- `chats/` y `devlog/` son append-only.
- Todo script que lea o escriba chats/devlog usa UTF-8 explicito.
- No se reescriben mensajes anteriores del chat.
- Los marcadores `MEMORIA:`, `BLOQUEO:` y `SIGUIENTE:` deben ir en mensajes
  nuevos, no enterrados en texto viejo.
- Una decision cerrada, feature completada, bloqueo abierto/cerrado, revert o
  memoria operativa deja entrada en `devlog/DEVLOG.md`.
- Los artefactos derivados (`artifacts/multiagent/`, timelines, builds de
  manuales) deben ser regenerables o estar justificados como estado versionado.

## Prompt operativo

Cuando el usuario diga `inicia sesion`, interpreta:

> Recupera el estado completo antes de actuar: instrucciones locales, memoria,
> chat del dia, devlog, sprints/backlog si existen, estado Git, diff y cambios
> pendientes. Deduce donde se dejo el trabajo y resume el siguiente paso
> razonable.

Cuando el usuario diga `sigue` o `continua`, interpreta:

> Haz una recuperacion ligera del estado vivo y continua la tarea pendiente mas
> probable. No reinicies desde cero ni reviertas cambios ajenos.

Cuando el usuario diga `cierra sesion`, interpreta:

> Deja la sesion reproducible: valida lo que corresponda, registra chat/devlog si
> toca, inventaria Git, prepara commit/push segun la politica local del repo y
> deja pendientes claros. En Coworkia, `cierra sesion` implica commit y push por
> defecto salvo que David pida explicitamente omitirlos.

## Procedimiento: inicia sesion

1. Leer este protocolo o su adaptacion local.
2. Leer instrucciones del agente y del repo:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `.github/copilot-instructions.md`
   - `.claude/multiagent.md`
   - `README.md`
   - `CONTRIBUTING.md`
3. Si existe `memory/`, leer en este orden:
   - `memory/INDEX.md`
   - `memory/PURPOSE.md`
   - `memory/STRUCTURE.md`
   - `memory/ROSTER.md`, si existe
   - `memory/SNAPSHOT.md`, si la pregunta depende de memoria reciente
4. Si existe `tools/init_chat.py`, resolver el chat activo:
   - `python tools/init_chat.py`
   - leer completo el `chats/chat_YYYY-MM-DD.md` resultante.
5. Si existe devlog:
   - `python tools/devlog.py view --limit 20`
   - o leer el ultimo tramo de `devlog/DEVLOG.md`.
6. Mapear el repo sin modificarlo:
   - carpetas top-level;
   - manifiestos (`requirements.txt`, `pyproject.toml`, `package.json`,
     `Makefile`, `docker-compose.yml`, `.env.example`, etc.);
   - docs, tests, scripts, apps, notebooks, datasets y builds.
7. Revisar Git de forma no destructiva:
   - `git status --short --branch`
   - `git log -1 --oneline`
   - `git branch --show-current`
   - `git remote -v`
   - `git diff --stat`
   - `git diff --name-only`
8. Revisar cambios pendientes como trabajo vivo. No asumir que son basura.
9. Si hay `artifacts/sprints/`, backlog, ADRs o timelines, consultar solo lo
   necesario para entender la continuacion.
10. Responder con:
   - rama y ultimo commit;
   - estado limpio/sucio;
   - fuentes de memoria consultadas;
   - cambios pendientes relevantes;
   - decisiones, bloqueos o siguientes pasos detectados;
   - siguiente accion recomendada.

## Procedimiento: sigue / continua

`sigue` no es un cierre ni una pregunta abstracta. Es una orden de continuacion.

1. Hacer un inicio ligero:
   - chat del dia;
   - devlog reciente;
   - `git status --short --branch`;
   - `git diff --name-only`.
2. Identificar la tarea activa por este orden:
   - ultima instruccion directa del usuario;
   - ultimo `SIGUIENTE:`;
   - cambios no cerrados en Git;
   - ultimo hito incompleto en devlog/sprint;
   - siguiente paso natural de la tarea en curso.
3. Continuar ejecutando si la accion es clara.
4. Si hay ambiguedad real y peligrosa, preguntar una vez. Si no, hacer la
   suposicion conservadora y seguir.

## Procedimiento: cierra sesion

1. Revisar estado:
   - `git status --short --branch`
   - `git diff --stat`
   - `git diff --name-only`
2. Ejecutar validaciones proporcionales al trabajo:
   - tests unitarios o smoke tests tocados;
   - build o generador documental si se modifico documentacion generada;
   - `python tools/memory_check.py` si existe;
   - `python tools/snapshot_structure.py --check` si se tocaron carpetas o memoria;
   - validadores especificos del repo.
3. Escribir en el chat diario solo al final, append-only, si hay algo util:
   - resumen de cambio;
   - `MEMORIA:` para acuerdos duraderos;
   - `BLOQUEO:` para impedimentos concretos;
   - `SIGUIENTE:` para la accion siguiente.
4. Anadir devlog si aplica:
   - decision cerrada;
   - feature completada;
   - memoria con impacto operativo;
   - bloqueo abierto/cerrado;
   - revert;
   - cambio documental estructural.
5. Si se usaron marcadores de memoria y existe sync:
   - `python agents/orchestrator_agent.py sync-chat-memory`
6. Si existe timeline diario y el cierre lo requiere:
   - `python tools/timeline.py`
7. Preparar commit si el usuario lo pidio o si la convencion local lo exige.
   - incluir solo archivos de la sesion;
   - no mezclar cambios ajenos;
   - no hacer push sin intencion explicita o politica local que lo autorice.
8. Entregar inventario final:
   - archivos cambiados;
   - validaciones ejecutadas;
   - commit/push si hubo;
   - pendientes y riesgos residuales.

## Devlog portable

Un devlog util no duplica cada commit. Registra hitos con impacto operacional.

Formato recomendado:

```bash
python tools/devlog.py append --agent Codex --area DOCS --status DONE \
  --title "Actualizar protocolo de sesion" \
  --summary "Nueva version portable integrada con memory, chats, devlog y Git."
```

Cada repo debe adaptar `--area` a sus dominios. Mantener areas genericas como
`DOCS`, `TOOLING`, `INFRA`, `GIT` ayuda cuando el sistema se porta a otro repo.

## Adaptador local opcional

Si el repo usa mucho este protocolo, conviene crear un script local:

```bash
python tools/session_protocol.py inicia
python tools/session_protocol.py cierra
python tools/session_protocol.py cierra --no-commit
python tools/session_protocol.py cierra --paths docs playbooks --commit-message "Update session protocol"
```

El adaptador no reemplaza al criterio del agente. Solo automatiza inventario:
memoria, chat, devlog, Git y resumen. En Coworkia, `tools/session_protocol.py`
es el adaptador local y respeta este playbook.

## Reglas de seguridad

- No usar `git reset --hard`, `git checkout --` ni borrados destructivos sin
  peticion explicita.
- No reescribir chats, devlog ni historiales append-only.
- No corregir "a ciegas" cambios no hechos por ti.
- No hacer commit mezclando archivos ajenos.
- No hacer push si el usuario no lo pidio o la politica local no lo autoriza.
- No versionar secretos, tokens, exports privados ni caches locales.
- Tratar notebooks, datasets, snapshots, builds y artefactos como trabajo vivo
  hasta entender su politica local.
- Si hay mojibake en chats, reparar con la herramienta local antes de seguir.

## Ajustes aprendidos al integrar Coworkia

Estos puntos son transferibles a otros repos con multiagentes:

- La memoria versionada manda sobre memorias locales de herramientas.
- `memory/STRUCTURE.md` debe actualizar narrativa y arbol cuando nace una
  carpeta top-level.
- El arbol generado debe excluir builds, caches, secretos y artefactos pesados
  regenerables.
- Un manual generado, por ejemplo `bookdown/_book/`, debe tener politica clara:
  versionado si es release artifact, ignorado si es regenerable local.
- Las rutas antiguas se detectan con busquedas amplias tras cambios grandes
  (`rg "docs/bookdown|REP|NOTION_DB_REPOS"` segun el caso).
- Un marcador como `MEMORIA:` conviene escribirlo en un mensaje nuevo y claro
  para que el parser lo capture.
- Los playbooks no son memoria canonica del proyecto: son patrones portables.
- El devlog registra hitos, no ruido.
- El cierre debe validar lo tocado y tambien las piezas de integracion que lo
  vuelven recuperable en la proxima sesion.

## Checklist para portar a un repo nuevo

- [ ] Crear o enlazar instrucciones de agente.
- [ ] Crear `memory/INDEX.md`, `PURPOSE.md` y `STRUCTURE.md` si el repo necesita
      memoria duradera.
- [ ] Crear `chats/` y plantilla diaria si habra varios agentes o sesiones largas.
- [ ] Crear `devlog/DEVLOG.md` y CLI o convencion append-only.
- [ ] Definir marcadores `MEMORIA:`, `BLOQUEO:` y `SIGUIENTE:`.
- [ ] Decidir que artefactos derivados se versionan y cuales van a `.gitignore`.
- [ ] Adaptar areas de devlog al dominio del repo.
- [ ] Documentar comandos de validacion minimos.
- [ ] Anadir un script tipo `tools/session_protocol.py` si aporta valor.
- [ ] Probar un ciclo completo: `inicia sesion` -> trabajo -> `cierra sesion`.
