## Imports

Carpeta de staging para bundles de importacion locales que sirven como fuente de entrada a agentes y herramientas.

Uso actual:

- `google_keep/`: exportaciones descomprimidas de Google Takeout para alimentar `agents/kit_agent.py importar-keep` y `sincronizar-keep`.

Reglas:

- No guardar secretos fuera de exports locales necesarios.
- Preferir datos crudos descomprimidos, no zips.
- Tratar este contenido como input operativo, no como fuente de verdad curada.
