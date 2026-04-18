# Casos de uso — Coworkia

Este directorio define **casos de uso canónicos** para guiar mejoras de integración entre sistemas (Todoist/Notion/Obsidian/GitHub/Paperpile) y la capa de trazabilidad `B0A-INX`.

## Cómo usar estos casos

- **Editar sin miedo**: estos documentos son la “fuente de requisitos” operativa.
- **Un caso → mejoras**: cada caso debe terminar en “Gaps” (lo que falta) y “Mejoras propuestas” (acciones concretas).
- **Regla de autoridad**: no mezclar fuentes de verdad. MAR vive en Todoist, PTN/KIT/REP/BIB viven en Notion, documentos viven en Obsidian, y `INX-ENLACES` es la base puente.

## Índice

- `00-template.md` — plantilla para nuevos casos
- `00-template.md` — plantilla para nuevos casos, alineada con claves INX vigentes (`github:<Nombre>`, `paperpile:<citekey>`)
- `01-captura-todoist-zinbox.md` — capturar y clasificar en el inbox normal + MAR (checklist v2, reglas canónicas, `mar_check`)
- `02-tarea-a-proyecto-ptn-con-inx.md` — tarea → proyecto PTN + INX (checklist v2, `inx_sync_todoist.bat`)
- `03-nota-obsidian-desde-ptn.md` — nota Obsidian + log + INX (checklist v2, `inx_sync_obsidian.bat`)
- `04-sync-diario-inx.md` — sincronización diaria y verificación de coherencia (`inx_daily`)
- `05-github-rep-enlazado-a-ptn.md` — importar repo a REP y enlazar a PTN, con sync GitHub → INX ya disponible
- `06-paperpile-bib-enlazado.md` — importar paper a BIB y enlazar a PTN/Obsidian, con sync Paperpile → INX ya disponible
- `07-promocion-obsidian-a-ptn.md` — promover nota Obsidian a PTN-Notas (inverso del caso 03), con `promote_obsidian_to_ptn.py` + gaps de cruce INX bidireccional
