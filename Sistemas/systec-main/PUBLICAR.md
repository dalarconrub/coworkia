# Cómo publicar la documentación con MkDocs

## Instalación

Si aún no has instalado las dependencias:

```bash
pip install -r requirements.txt
```

## Desarrollo local

Para previsualizar la documentación localmente:

```bash
python -m mkdocs serve
```

Esto iniciará un servidor local en `http://127.0.0.1:8000` que se actualiza automáticamente cuando cambias los archivos.

## Publicar en GitHub Pages

### Opción 1: Usando GitHub Actions (Recomendado)

1. Crea un archivo `.github/workflows/docs.yml` con el siguiente contenido:

```yaml
name: Deploy Docs

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - run: pip install -r requirements.txt
      - run: mkdocs gh-deploy --force
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

2. Habilita GitHub Pages en la configuración del repositorio:
   - Ve a Settings > Pages
   - Selecciona "Deploy from a branch"
   - Branch: `gh-pages` / `/ (root)`

### Opción 2: Publicación manual

```bash
python -m mkdocs gh-deploy
```

Esto creará una rama `gh-pages` con el sitio estático y lo publicará automáticamente.

## Estructura de archivos

- `index.md` - Página principal (en `docs/`)
- `docs/` - Contiene toda la documentación
- `mkdocs.yml` - Configuración de MkDocs
- `site/` - Carpeta generada con el sitio estático (no se sube a git)

## Notas

- **Sitio principal:** [https://MAR.netlify.app/](https://MAR.netlify.app/)
- **Sitio alternativo (GitHub Pages):** `https://dalarconrub.github.io/MAR/`
- Los cambios se reflejan automáticamente después del deploy
- La carpeta `site/` está en `.gitignore` y no debe subirse a git
