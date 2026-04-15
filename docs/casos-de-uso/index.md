# Casos de uso — Coworkia

Este directorio define **casos de uso canónicos** para guiar mejoras de integración entre sistemas (Todoist/Notion/Obsidian/GitHub/Paperpile) y la capa de trazabilidad `B0A-INX`.

## Cómo usar estos casos

- **Editar sin miedo**: estos documentos son la “fuente de requisitos” operativa.
- **Un caso → mejoras**: cada caso debe terminar en “Gaps” (lo que falta) y “Mejoras propuestas” (acciones concretas).
- **Regla de autoridad**: no mezclar fuentes de verdad. MAR vive en Todoist, PTN/KIT/REP/BIB viven en Notion, documentos viven en Obsidian, y `INX-ENLACES` es la base puente.

## Índice

- `00-template.md` — plantilla para nuevos casos
- `01-captura-todoist-zinbox.md` — capturar y clasificar en Inbox + MAR (checklist v2, reglas canónicas, `mar_check`)
- `02-tarea-a-proyecto-ptn-con-inx.md` — tarea → proyecto PTN + INX (checklist v2, `inx_sync_todoist.bat`)
- `03-nota-obsidian-desde-ptn.md` — nota Obsidian + log + INX (checklist v2, `inx_sync_obsidian.bat`)
- `04-sync-diario-inx.md` — sincronización diaria y verificación de coherencia
- `05-github-rep-enlazado-a-ptn.md` — importar repo a REP y enlazar a PTN
- `06-paperpile-bib-enlazado.md` — importar paper a BIB y enlazar a PTN/Obsidian
