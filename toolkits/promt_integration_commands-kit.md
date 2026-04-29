````md
# Prompt: Integración y uso del starter kit `.ai/commands`

Quiero que revises e integres en este repo un starter kit portable de comandos para agentes IA ubicado en:

```text
.ai/commands/
````

---

## 1. Qué es el starter kit

El starter kit `.ai/commands` es una convención portable para definir comandos tipo `/` mediante archivos Markdown.

Cada archivo representa un comando reutilizable que encapsula un prompt estructurado.

Estructura:

```text
.ai/
├── README.md
├── COMMANDS.md
└── commands/
    ├── think.md
    ├── plan.md
    ├── debug.md
    ├── architecture.md
    ├── refactor.md
    ├── review.md
    ├── test.md
    ├── docs.md
    ├── security.md
    ├── research.md
    ├── decision.md
    └── handoff.md
```

La finalidad es que cualquier agente pueda interpretar comandos como:

```text
/plan implementar autenticación
/debug error en endpoint
/architecture rediseñar módulo
```

---

## 2. Cómo funcionan los comandos

Un comando `/` es una forma abreviada de cargar un prompt estructurado.

Ejemplo:

```text
/debug error al validar JWT
```

Debe procesarse así:

1. Detectar el comando (`debug`)
2. Localizar el archivo:

```text
.ai/commands/debug.md
```

3. Leer sus instrucciones
4. Aplicarlas al problema proporcionado
5. Usar herramientas disponibles si existen
6. Generar la respuesta siguiendo el formato definido en el comando

---

## 3. Instalación desde ZIP en cualquier repo

Para instalar el starter kit:

1. Descomprimir el archivo ZIP
2. Copiar la carpeta `.ai/` en la raíz del repositorio

Estructura final:

```text
mi-repo/
├── .ai/
│   ├── README.md
│   ├── COMMANDS.md
│   └── commands/
│       ├── think.md
│       ├── plan.md
│       ├── debug.md
│       └── ...
├── src/
├── tests/
└── ...
```

Importante:

* La carpeta `.ai/` debe estar en la raíz
* No ubicarla dentro de `src/`, `docs/` u otras subcarpetas

---

## 4. Integración en un sistema multiagente

Todos los agentes deben ser capaces de usar estos comandos de forma uniforme.

Añadir la siguiente regla global al sistema:

````md
## Interpretación de comandos `/`

Cuando un mensaje comience por `/`, interpretar la primera palabra como un comando.

Ejemplo:

```text
/plan añadir sistema de login
````

Procedimiento:

1. Extraer el nombre del comando (`plan`)
2. Buscar el archivo:

```text
.ai/commands/plan.md
```

3. Leer su contenido
4. Aplicar sus instrucciones al resto del mensaje
5. Generar la respuesta según el formato del comando

Si el comando no existe:

* Informar al usuario
* Mostrar los comandos disponibles desde `.ai/COMMANDS.md`

````

---

## 5. Regla para cualquier agente

Todos los agentes deben seguir este flujo:

1. Si el mensaje empieza por `/`, activar modo comando
2. Cargar el archivo correspondiente
3. Aplicar las instrucciones del comando
4. Usar herramientas disponibles
5. No inventar archivos ni resultados
6. Declarar limitaciones si no puede completar alguna acción

---

## 6. Ejemplo de funcionamiento

Entrada:

```text
/debug El endpoint /api/login devuelve 500 cuando el token está caducado
````

Proceso:

```text
1. Detectar comando: debug
2. Leer .ai/commands/debug.md
3. Aplicar razonamiento de diagnóstico
4. Analizar posibles causas
5. Proponer verificación
6. Recomendar solución mínima
```

Salida esperada:

```md
## Síntoma

...

## Señales relevantes

...

## Hipótesis de causa raíz

| Rank | Hipótesis | Evidencia | Prueba |
|---|---|---|---|

## Cambio mínimo recomendado

...

## Verificación

...
```

---

## 7. Resultado esperado de la integración

Se espera que:

1. La carpeta `.ai/commands` esté correctamente ubicada
2. Los agentes interpreten comandos `/` automáticamente
3. Se añada una regla global en:

   * AGENTS.md
   * CLAUDE.md
   * documentación interna del sistema
4. Se documente el uso básico en el README del repo
5. No se modifique código funcional innecesariamente

---

## 8. Comandos disponibles

```text
/think
/plan
/debug
/architecture
/refactor
/review
/test
/docs
/security
/research
/decision
/handoff
```

---

## 9. Objetivo final

El objetivo es que cualquier agente del sistema multiagente pueda ejecutar:

```text
/<comando> <tarea>
```

y automáticamente:

* cargar el comando adecuado
* aplicar su lógica
* devolver una respuesta estructurada y consistente

Sin necesidad de escribir prompts complejos manualmente.


