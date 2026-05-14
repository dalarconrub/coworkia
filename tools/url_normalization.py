"""
Normalizacion conservadora de URLs para dedupe en KIT.

Objetivo: que la misma lectura/bookmark no duplique filas por parametros de
tracking o fragmentos locales. No intenta resolver canonical URLs remotas.
"""

from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "igshid",
    "mc_cid",
    "mc_eid",
    "mkt_tok",
    "ref",
    "spm",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}

TRACKING_PREFIXES = ("utm_",)


def canonical_url(raw_url: str | None) -> str:
    """Devuelve una URL estable para dedupe local.

    Cambios deliberadamente conservadores:
    - host y scheme en minusculas;
    - elimina fragment (#...);
    - elimina parametros de tracking conocidos;
    - ordena parametros restantes;
    - elimina barra final salvo en la raiz.
    """
    if not raw_url:
        return ""
    raw_url = raw_url.strip()
    if not raw_url:
        return ""

    parts = urlsplit(raw_url)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path or ""
    if len(path) > 1:
        path = path.rstrip("/")

    filtered = []
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        low_key = key.lower()
        if low_key in TRACKING_PARAMS or any(low_key.startswith(prefix) for prefix in TRACKING_PREFIXES):
            continue
        filtered.append((key, value))
    query = urlencode(sorted(filtered))
    return urlunsplit((scheme, netloc, path, query, ""))
