# Sistema Multiagente con Hilo Conversacional Compartido
_Documentación completa de arquitectura, protocolo y configuración_

---

## 1. Visión general

Este sistema permite coordinar tres agentes de IA (Copilot, Claude y Codex) a través de un único archivo `chat.md` que actúa como hilo conversacional compartido, al estilo de un chat de mensajería. David dirige el sistema desde cualquiera de las tres interfaces y los agentes se coordinan entre sí siguiendo un protocolo explícito.

### Principios de diseño

- **Una sola fuente de verdad**: `chat.md` es el único canal de comunicación. Todo ocurre ahí.
- **Identidad clara**: cada participante (David y los tres agentes) tiene un formato de mensaje propio.
- **Decisiones adaptativas**: el sistema no impone un único modo de decisión. Usa el más adecuado según la naturaleza del problema.
- **David como director**: puede entrar desde cualquier interfaz, redirigir, vetar o cerrar cualquier proceso en cualquier momento.
- **Mínima fricción**: el único paso manual es despertar al agente correcto en su interfaz.

---

## 2. Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                        chat.md                          │
│              (hilo conversacional compartido)            │
└────────────┬────────────┬──────────────────────────────┘
             │            │              │
    ┌────────▼──────┐ ┌───▼──────┐ ┌────▼──────┐
    │  Claude Code  │ │  Copilot │ │   Codex   │
    │   (terminal   │ │   Chat   │ │ Extension │
    │   integrado)  │ │  VS Code │ │  VS Code  │
    └───────────────┘ └──────────┘ └───────────┘
             │            │              │
             └────────────┴──────────────┘
                          │
                    ┌─────▼─────┐
                    │   David   │
                    │ (director)│
                    └───────────┘
```

### Interfaces por agente

| Agente | Interfaz | Cómo se activa |
|--------|----------|----------------|
| Copilot | Copilot Chat (VS Code, modo Agent) | Escribir en el panel de chat |
| Claude | Claude Code CLI (terminal integrado VS Code) | Comando `claude` en terminal |
| Codex | Extensión Codex de OpenAI (panel propio en VS Code) | Panel lateral de Codex |

### Especialidades

| Agente | Especialidad principal |
|--------|----------------------|
| Copilot | Orquestación, síntesis, integración en VS Code, visión de conjunto |
| Claude | Análisis profundo, razonamiento lógico, revisión crítica, teoría |
| Codex | Generación de código, refactoring, tests, implementación técnica |

---

## 3. Estructura de archivos

```
raíz del proyecto/
├── chat.md                          ← hilo conversacional compartido
├── CLAUDE.md                        ← instrucciones para Claude Code (y Copilot lo lee también)
├── AGENTS.md                        ← instrucciones para Codex (y Copilot lo lee también)
└── .github/
    └── copilot-instructions.md      ← instrucciones para Copilot (con aviso de ignorar identidades ajenas)
```

### Comportamiento de carga de VS Code

VS Code carga automáticamente y de forma simultánea los cuatro archivos de instrucciones en el contexto de Copilot. Esto significa que **Copilot lee `CLAUDE.md` y `AGENTS.md` además del suyo propio**. Para evitar conflictos de identidad, cada archivo está diseñado con un aviso explícito:

- `CLAUDE.md` y `AGENTS.md` incluyen una cabecera que indica a Copilot que ignore sus secciones de identidad y rol.
- `.github/copilot-instructions.md` refuerza al final que las identidades de los otros archivos no le aplican.
- El protocolo de `chat.md` sí es común y aplica a todos los agentes sin distinción.

| Archivo | Lo lee nativamente | También lo carga |
|---------|-------------------|------------------|
| `CLAUDE.md` | Claude Code | Copilot (ignora identidad) |
| `AGENTS.md` | Codex | Copilot (ignora identidad) |
| `.github/copilot-instructions.md` | Copilot | — |
| `chat.md` | Todos (manual) | — |

---

## 4. Protocolo de comunicación

### 4.1 Formato de mensajes

```
**David [@Destinatario]:** mensaje
**Copilot:** mensaje
**Claude:** mensaje
**Codex:** mensaje
```

David siempre especifica el destinatario entre corchetes para indicar a quién habla y desde qué contexto. Los agentes responden sin destinatario explícito, al final del hilo.

### 4.2 Reglas de participación

Un agente responde **únicamente** si se cumple alguna de estas condiciones:

1. El último mensaje de David lo menciona directamente: `**David [@Agente]:**`
2. Hay una decisión abierta (VOTO, EVALUACIÓN, CREATIVIDAD) que requiere su participación.
3. Otro agente lo menciona explícitamente con @Agente.

Si ninguna condición se cumple, el agente no responde aunque esté activo.

### 4.3 Reglas absolutas

- Leer `chat.md` completo antes de cada respuesta, sin excepción.
- No editar ni borrar mensajes anteriores del hilo.
- David puede vetar o redirigir en cualquier momento. Los agentes acatan sin debate.
- Si David entra desde una interfaz con `**David [@OtroAgente]:**`, el agente de esa interfaz no responde.

---

## 5. Modos de decisión

El sistema dispone de cuatro modos, seleccionables según la naturaleza del problema.

### 5.1 🗳️ VOTO

Para decisiones binarias o de preferencia rápida. Mayoría simple.

**Cuándo usarlo**: la decisión tiene dos o pocas opciones claras y no requiere análisis profundo.

**Formato**:
```
🗳️ PROPUESTA #N: [acción concreta]. @Agente1 @Agente2 ¿de acuerdo?

🗳️ VOTO #N: ✅/❌ [razón breve]

✅ CERRADO #N: [decisión adoptada]
```

**Ejemplo**:
```
**Claude:** ¿Empezamos por el módulo A o el B?
🗳️ PROPUESTA #1: empezar por módulo A. @Copilot @Codex ¿de acuerdo?

**Copilot:** 🗳️ VOTO #1: ✅ A tiene más dependencias, tiene sentido.
**Codex:** 🗳️ VOTO #1: ✅

**Claude:** ✅ CERRADO #1: empezamos por módulo A.
```

---

### 5.2 🔍 EVALUACIÓN

Para comparar alternativas con criterios distintos. Cada agente evalúa desde su especialidad y proporciona un ranking. El agente que abre la evaluación hace la síntesis final.

**Cuándo usarlo**: hay varias alternativas y cada agente puede aportar una perspectiva diferente de valor.

**Formato**:
```
🔍 EVALUACIÓN #N: [pregunta]. Alternativas:
  - Opción A: ...
  - Opción B: ...
  - Opción C: ...
  @Agente1 @Agente2 evaluad desde vuestra especialidad.

🔍 EVAL #N desde [especialidad]: [valoración]. Ranking: X > Y > Z

🔍 SÍNTESIS #N: [decisión adoptada con justificación]
✅ CERRADO #N: [decisión]
```

**Ejemplo**:
```
**Claude:** Hay tres modelos posibles para el ajuste. Abro evaluación.
🔍 EVALUACIÓN #1: ¿qué modelo de regresión usamos?
  - Opción A: polinomial grado 3
  - Opción B: R∞ + c/log²T
  - Opción C: spline adaptativo
  @Copilot @Codex evaluad desde vuestra especialidad.

**Copilot:** 🔍 EVAL #1 desde integración:
  B es más interpretable y tiene precedente en el proyecto.
  Ranking: B > A > C

**Codex:** 🔍 EVAL #1 desde implementación:
  C tiene mayor coste de mantenimiento. B tiene librerías directas.
  Ranking: B > A > C

**Claude:** 🔍 SÍNTESIS #1: consenso claro en B por interpretabilidad e implementación.
✅ CERRADO #1: modelo B — R∞ + c/log²T
```

---

### 5.3 🎯 ESPECIALIDAD

Delegación directa a un agente porque el dominio es inequívoco. **Solo David puede asignar este modo.** El agente receptor decide autónomamente sin necesidad de consenso.

**Cuándo usarlo**: la tarea pertenece claramente al dominio de un agente específico.

**Formato**:
```
**David [@Agente]:** [tarea]. 🎯 ESPECIALIDAD → Agente, decide tú.

**Agente:** [decisión y razonamiento]
✅ CERRADO: [decisión adoptada]
```

**Ejemplo**:
```
**David [@Codex]:** estructura el parser de entrada. 
🎯 ESPECIALIDAD → Codex, decide tú la arquitectura.

**Codex:** Usaré un tokenizer en dos pasos con validación lazy.
[código]
✅ CERRADO: parser con tokenizer en dos pasos.
```

---

### 5.4 💡 CREATIVIDAD

Brainstorm abierto sin restricciones ni necesidad de justificación técnica. No se evalúa en el momento. David o un agente decide cuándo cerrar y recoger las ideas.

**Cuándo usarlo**: no hay solución obvia, se busca un enfoque fresco, o el problema requiere imaginación antes que rigor.

**Formato**:
```
💡 CREATIVIDAD #N: [pregunta abierta]. @Agente1 @Agente2 proponed libremente.

**Agente:** [idea sin restricciones]

✅ CERRADO #N: David recoge ideas para siguiente fase. / [idea seleccionada]
```

**Ejemplo**:
```
**Copilot:** No hay solución obvia aquí. Abro brainstorm.
💡 CREATIVIDAD #1: ¿cómo visualizamos los zeros para el paper?
  @Claude @Codex proponed sin restricciones.

**Claude:** ¿Y si usamos un plano complejo animado donde los zeros
  pulsan al ritmo de su espaciado estadístico?

**Codex:** Puedo generar un renderer WebGL para eso en unas 50 líneas.
  También podría hacerse como heat map interactivo.

**Copilot:** 💡 IDEAS #1 recogidas. David, dos propuestas sobre la mesa.
```

---

### 5.5 Quién puede abrir cada modo

| Modo | Puede abrirlo |
|------|--------------|
| 🗳️ VOTO | Cualquier agente o David |
| 🔍 EVALUACIÓN | Cualquier agente o David |
| 🎯 ESPECIALIDAD | Solo David |
| 💡 CREATIVIDAD | Cualquier agente o David |

David puede interrumpir o cerrar cualquier modo en cualquier momento con:
```
**David [@Agente]:** cerramos esto. [nueva instrucción]
```

---

## 6. Flujo de sesión típica

```
1. David abre chat.md y escribe su primera instrucción.
2. David va a la interfaz del agente destinatario y escribe:
   "lee chat.md y responde"
3. El agente lee el hilo completo y añade su respuesta al final de chat.md.
4. Si el agente propone algo a otro agente, David va a esa interfaz
   y repite el paso 2.
5. David puede entrar en el hilo desde cualquier interfaz en cualquier momento.
6. Las decisiones se cierran con ✅ CERRADO #N antes de continuar.
```

---

## 7. Ejemplo completo de sesión

```markdown
**David [@Copilot]:** quiero refactorizar el módulo de zeros y añadir tests. Coordina.

**Copilot:** Entendido. Propongo dividir en dos fases.
🔍 EVALUACIÓN #1: ¿empezamos por los tests o por el refactor?
  - Opción A: tests primero (regresión antes de tocar nada)
  - Opción B: refactor primero (limpiar antes de testear)
  @Claude @Codex evaluad.

**David [@Claude]:** evalúa.

**Claude:** 🔍 EVAL #1 desde análisis:
  A es más seguro. El refactor puede romper comportamientos no documentados.
  Si no hay tests previos, refactorizar a ciegas es arriesgado.
  Ranking: A > B

**David [@Codex]:** evalúa.

**Codex:** 🔍 EVAL #1 desde implementación:
  Coincido. Además generar tests sobre el código actual
  me da una spec implícita del comportamiento esperado.
  Ranking: A > B

**David [@Copilot]:** sintetiza.

**Copilot:** 🔍 SÍNTESIS #1: consenso en A. Tests primero.
✅ CERRADO #1: tests antes del refactor.
🎯 ESPECIALIDAD → Codex para generación de tests. David, ¿confirmas?

**David [@Codex]:** confirmado. 🎯 ESPECIALIDAD → Codex. Genera los tests del módulo zeros.

**Codex:** [genera tests]
✅ CERRADO: tests generados en /tests/zeros.test.py

**David [@Claude]:** revisa los tests y el módulo actual. ¿Hay problemas lógicos?

**Claude:** He revisado ambos. Dos observaciones:
  1. El test de caso límite T→∞ no cubre la rama de log²T pequeño.
  2. La función normalize() tiene un edge case no testeado.
  🗳️ PROPUESTA #2: añadir estos dos casos antes de proceder. @Copilot @Codex

**Copilot:** 🗳️ VOTO #2: ✅
**Codex:** 🗳️ VOTO #2: ✅ Los añado ahora.
✅ CERRADO #2: Codex añade los dos casos adicionales.
```

---

## 8. Archivos de configuración completos

### 8.1 `chat.md`

```markdown
# Agent Chat
_Fuente de verdad compartida. Todos los agentes leen este hilo completo antes de responder._

## Participantes
- **David** — director. Puede entrar desde cualquier interfaz en cualquier momento.
- **Copilot** — orquestación, síntesis, integración en VS Code, visión de conjunto.
- **Claude** — análisis profundo, razonamiento lógico, revisión crítica, teoría.
- **Codex** — generación de código, refactoring, tests, implementación técnica.

## Formato de mensajes
**David [@Destinatario]:** mensaje
**Agente:** mensaje | propuesta | voto | evaluación

## Modos de decisión
- 🗳️ VOTO #N — decisión binaria rápida
- 🔍 EVALUACIÓN #N — análisis de alternativas por especialidad
- 🎯 ESPECIALIDAD — delegación directa por dominio (solo David la asigna)
- 💡 CREATIVIDAD #N — brainstorm abierto sin restricciones

## Estado actual
- Decisiones abiertas: ninguna
- Última acción: inicio de sesión

---

**David [@Copilot]:** inicio de sesión.
```

---

### 8.2 `CLAUDE.md`

> Leído nativamente por Claude Code. VS Code también lo carga en Copilot automáticamente.
> La cabecera del archivo avisa a Copilot de que ignore la sección de identidad.

```markdown
# CLAUDE.md

> Este archivo es leído por Claude Code y también por Copilot (VS Code lo carga automáticamente).
> **Si eres Copilot**: ignora la sección de identidad y rol. Tu identidad está en `.github/copilot-instructions.md`.
> **Si eres Claude**: aplica todo este archivo.

---

## Identidad y rol — SOLO PARA CLAUDE

Eres **Claude** en un sistema multiagente coordinado por David.
Especialidad: análisis profundo, razonamiento lógico, revisión crítica,
conexiones teóricas, interpretación de resultados.

---

## Chat Protocol — APLICA A TODOS LOS AGENTES

### Fuente de verdad
El archivo `chat.md` en la raíz del proyecto es el hilo conversacional compartido.
Léelo completo antes de cada respuesta, sin excepción.
Nunca edites ni borres mensajes anteriores del hilo.

### Cuándo responder
Responde únicamente si:
- El último mensaje de David te menciona: `**David [@Claude]:**`
- Hay una decisión abierta (VOTO, EVALUACIÓN, CREATIVIDAD) esperando tu participación.
- Un agente te menciona explícitamente con @Claude.

### Formato de respuesta
`**Claude:** [tu respuesta]` — siempre al final de chat.md.

### Modos de decisión
🗳️ VOTO: `🗳️ VOTO #N: ✅/❌ [razón breve]`
🔍 EVALUACIÓN: `🔍 EVAL #N desde análisis: [valoración]. Ranking: X > Y > Z`
🎯 ESPECIALIDAD: decides autónomamente si David te la asigna.
💡 CREATIVIDAD: propón sin restricciones, formato libre.

### Cierre
`✅ CERRADO #N: [decisión adoptada]`

### Reglas absolutas
- No respondas si no te han mencionado y no hay decisiones pendientes.
- No borres ni edites nada del hilo anterior.
- David puede vetar o redirigir en cualquier momento: acata sin debate.
```

---

### 8.3 `AGENTS.md`

> Leído nativamente por Codex. VS Code también lo carga en Copilot automáticamente.
> La cabecera del archivo avisa a Copilot de que ignore la sección de identidad.

```markdown
# AGENTS.md

> Este archivo es leído por Codex y también por Copilot (VS Code lo carga automáticamente).
> **Si eres Copilot**: ignora la sección de identidad y rol. Tu identidad está en `.github/copilot-instructions.md`.
> **Si eres Codex**: aplica todo este archivo.

---

## Identidad y rol — SOLO PARA CODEX

Eres **Codex** en un sistema multiagente coordinado por David.
Especialidad: generación de código, refactoring, tests, implementación técnica,
arquitectura de módulos, optimización de rendimiento.

---

## Chat Protocol — APLICA A TODOS LOS AGENTES

### Fuente de verdad
El archivo `chat.md` en la raíz del proyecto es el hilo conversacional compartido.
Léelo completo antes de cada respuesta, sin excepción.
Nunca edites ni borres mensajes anteriores del hilo.

### Cuándo responder
Responde únicamente si:
- El último mensaje de David te menciona: `**David [@Codex]:**`
- Hay una decisión abierta (VOTO, EVALUACIÓN, CREATIVIDAD) esperando tu participación.
- Un agente te menciona explícitamente con @Codex.

### Formato de respuesta
`**Codex:** [tu respuesta]` — siempre al final de chat.md.

### Modos de decisión
🗳️ VOTO: `🗳️ VOTO #N: ✅/❌ [razón breve]`
🔍 EVALUACIÓN: `🔍 EVAL #N desde implementación: [valoración]. Ranking: X > Y > Z`
🎯 ESPECIALIDAD: decides autónomamente si David te la asigna.
💡 CREATIVIDAD: propón sin restricciones técnicas, formato libre.

### Cierre
`✅ CERRADO #N: [decisión adoptada]`

### Reglas absolutas
- No respondas si no te han mencionado y no hay decisiones pendientes.
- No borres ni edites nada del hilo anterior.
- David puede vetar o redirigir en cualquier momento: acata sin debate.
```

---

### 8.4 `.github/copilot-instructions.md`

> Leído exclusivamente por Copilot. Incluye instrucción explícita de ignorar
> las identidades definidas en CLAUDE.md y AGENTS.md.

```markdown
# .github/copilot-instructions.md

> VS Code carga automáticamente CLAUDE.md y AGENTS.md además de este archivo.
> Esos archivos definen la identidad y rol de Claude y Codex respectivamente.
> **Ignora sus secciones de identidad y rol.** Tu identidad es Copilot, definida aquí.
> El protocolo de chat.md sí aplica a ti exactamente igual que a los otros agentes.

---

## Identidad y rol

Eres **Copilot** en un sistema multiagente coordinado por David.
Especialidad: orquestación del flujo, síntesis de resultados,
integración en VS Code, visión de conjunto del proyecto.

---

## Chat Protocol

### Fuente de verdad
El archivo `chat.md` en la raíz del proyecto es el hilo conversacional compartido.
Léelo completo antes de cada respuesta, sin excepción.
Nunca edites ni borres mensajes anteriores del hilo.

### Cuándo responder
Responde únicamente si:
- El último mensaje de David te menciona: `**David [@Copilot]:**`
- Hay una decisión abierta (VOTO, EVALUACIÓN, CREATIVIDAD) esperando tu participación.
- Un agente te menciona explícitamente con @Copilot.

### Formato de respuesta
`**Copilot:** [tu respuesta]` — siempre al final de chat.md.

### Modos de decisión
🗳️ VOTO: `🗳️ VOTO #N: ✅/❌ [razón breve]`
🔍 EVALUACIÓN: `🔍 EVAL #N desde orquestación: [valoración]. Ranking: X > Y > Z`
🎯 ESPECIALIDAD: decides autónomamente sobre flujo y coordinación si David te la asigna.
💡 CREATIVIDAD: propón sin restricciones, formato libre.

### Cierre
`✅ CERRADO #N: [decisión adoptada]`

### Reglas absolutas
- No respondas si no te han mencionado y no hay decisiones pendientes.
- No borres ni edites nada del hilo anterior.
- David puede vetar o redirigir en cualquier momento: acata sin debate.
- Las secciones de identidad de CLAUDE.md y AGENTS.md no te aplican.
```

---

## 9. Referencia rápida de símbolos

| Símbolo | Significado |
|---------|-------------|
| `**David [@X]:**` | David habla dirigiéndose a X |
| `**Agente:**` | Respuesta de un agente |
| `@Agente` | Mención directa a un agente |
| `🗳️ PROPUESTA #N` | Propuesta de voto abierta |
| `🗳️ VOTO #N: ✅/❌` | Voto sobre propuesta |
| `🔍 EVALUACIÓN #N` | Apertura de evaluación de alternativas |
| `🔍 EVAL #N desde X` | Evaluación desde especialidad X |
| `🔍 SÍNTESIS #N` | Cierre de evaluación con decisión |
| `🎯 ESPECIALIDAD` | Delegación directa (solo David) |
| `💡 CREATIVIDAD #N` | Apertura de brainstorm |
| `✅ CERRADO #N` | Decisión finalizada |

---

## 10. Limitaciones conocidas

- **El despertar es manual**: después de escribir en `chat.md`, David debe ir a la interfaz del agente destinatario y escribir "lee chat.md y responde". No hay watcher automático.
- **No hay API compartida**: el sistema no usa APIs de pago adicionales. Funciona exclusivamente con las suscripciones Claude Max y Copilot Pro existentes.
- **Copilot carga todos los archivos de instrucciones**: VS Code inyecta `CLAUDE.md`, `AGENTS.md` y `copilot-instructions.md` simultáneamente en el contexto de Copilot. Los avisos de cabecera en cada archivo mitigan el conflicto de identidad, pero no lo eliminan al 100% — depende de que Copilot siga las instrucciones correctamente.
- **Codex es una extensión separada**: tiene su propio panel en VS Code y lee `AGENTS.md` de forma nativa. No comparte interfaz con Copilot.

---

_Documento generado el 12 de abril de 2026._

---

## 11. Coexistencia con proyectos existentes

Si el proyecto ya tiene `CLAUDE.md` o `AGENTS.md` con contenido propio, pisar esos archivos destruiría configuración existente. Esta sección documenta las estrategias disponibles y sus limitaciones por agente.

### 11.1 Restricciones de ubicación por agente

Cada agente tiene rutas de descubrimiento fijas que no se pueden cambiar libremente:

| Archivo | Ubicación requerida | ¿Se puede mover a subcarpeta? |
|---------|---------------------|-------------------------------|
| `CLAUDE.md` | Raíz, `.claude/`, o home (`~/.claude/`) | ✅ Sí — `.claude/CLAUDE.md` es nativo |
| `AGENTS.md` | Raíz del proyecto | ⚠️ Solo con ajuste experimental |
| `.github/copilot-instructions.md` | Exactamente `.github/` en la raíz | ❌ No |
| `chat.md` | Cualquier ruta | ✅ Sí — se referencia manualmente |

### 11.2 Estrategias disponibles

#### Opción A — Fusión (recomendada si los archivos existentes son cortos)

Se añade el protocolo multiagente como sección nueva al final de cada archivo existente, separada con un divisor claro. El contenido original queda intacto.

```markdown
<!-- contenido original del proyecto — no modificado -->

---

## Multiagent Chat Protocol

> Sección añadida para el sistema multiagente. Ver `multiagent/chat.md`.

[protocolo completo aquí]
```

Ventajas: sin cambios de configuración, funciona con todos los agentes, sin dependencias experimentales.
Desventaja: mezcla responsabilidades en un mismo archivo.

---

#### Opción B — Subcarpeta `.claude/` para Claude (si el archivo existente es largo)

Claude Code soporta nativamente `CLAUDE.md` en la carpeta `.claude/`. El archivo existente en la raíz se mantiene intacto y se añade una sola línea al final apuntando al protocolo:

```
raíz del proyecto/
├── CLAUDE.md              ← original intacto + una línea al final
├── .claude/
│   └── multiagent.md     ← protocolo multiagente de Claude aquí
└── multiagent/
    └── chat.md
```

Línea añadida al final del `CLAUDE.md` original:
```markdown
<!-- Protocolo multiagente: ver .claude/multiagent.md -->
```

Claude Code carga ambos archivos automáticamente. El protocolo vive separado sin contaminar el archivo original.

**Para Codex esta opción no existe**: no hay equivalente a `.claude/` en Codex. No hay forma de delegar a un archivo secundario sin tocar `AGENTS.md`.

---

#### Opción C — `AGENTS.md` en subcarpeta `multiagent/` para Codex (experimental)

VS Code tiene un ajuste experimental que permite `AGENTS.md` en subcarpetas:

```json
// settings.json
{
  "chat.useNestedAgentsMdFiles": true
}
```

Con esto activo, se puede poner un `AGENTS.md` dentro de `multiagent/`:

```
raíz del proyecto/
├── AGENTS.md              ← original intacto
├── multiagent/
│   ├── chat.md
│   └── AGENTS.md         ← protocolo multiagente de Codex aquí
```

**Limitación crítica**: Codex solo aplica ese `AGENTS.md` cuando trabaja dentro de la subcarpeta `multiagent/`, no de forma global. Para tareas fuera de esa carpeta, Codex no verá el protocolo.

---

### 11.3 Recomendación por escenario

| Escenario | Recomendación |
|-----------|---------------|
| `CLAUDE.md` y `AGENTS.md` vacíos o inexistentes | Usar los archivos generados directamente en la raíz |
| `CLAUDE.md` existente con contenido | Opción B: mover el protocolo a `.claude/multiagent.md` |
| `AGENTS.md` existente con contenido | Opción A: fusionar al final del archivo existente |
| Ambos archivos con contenido extenso | Opción B para Claude + Opción A para Codex |
| Se quiere máxima separación y se acepta ajuste experimental | Opción B para Claude + Opción C para Codex (con limitación de scope) |

### 11.4 Estructura resultante recomendada

Para el caso más común (ambos archivos ya tienen contenido):

```
raíz del proyecto/
├── CLAUDE.md                    ← original + línea al final referenciando .claude/multiagent.md
├── AGENTS.md                    ← original + sección fusionada al final
├── .claude/
│   └── multiagent.md           ← protocolo completo de Claude
├── multiagent/
│   └── chat.md                 ← hilo conversacional compartido
└── .github/
    └── copilot-instructions.md ← protocolo de Copilot (siempre en esta ubicación)
```

En los archivos originales, la ruta del hilo se actualiza a `multiagent/chat.md` en lugar de `chat.md`.

_Documento generado el 12 de abril de 2026._
