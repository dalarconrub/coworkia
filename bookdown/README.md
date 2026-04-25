# Bookdown Coworkia

Manual navegable del proyecto Coworkia. La fuente canonica del orden de capitulos es `_bookdown.yml`.

## Render

```bash
python bookdown/generate_static_html.py
```

Genera:

- `bookdown/_book/index.html`

## Validacion

```bash
python bookdown/validate_static_html.py
python -m pytest tests/test_bookdown_static_html.py -q
```

El validador comprueba que los capitulos declarados existen, que el HTML se ha generado, que las tablas y enlaces no quedan como Markdown crudo, que no hay IDs duplicados, y que los anchors internos apuntan a IDs existentes.

## Mantenimiento

Cada vez que cambie un flujo, script, test o carpeta relevante:

1. actualiza el capitulo correspondiente;
2. actualiza las tablas maestras;
3. actualiza `_bookdown.yml` si hay capitulo nuevo;
4. regenera HTML;
5. ejecuta el validador y el test.
