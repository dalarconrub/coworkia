"""
Wrappers para la API de GitHub.
Usa la API REST v3 para obtener información de repositorios.
Documentación: https://docs.github.com/en/rest
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"


def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


# ─── REPOSITORIOS ────────────────────────────────────────────────────────────

def get_user_repos(per_page: int = 100) -> list[dict]:
    """
    Obtiene todos los repos del usuario autenticado (paginado).
    Incluye privados si el token tiene scope 'repo'.
    """
    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"{BASE_URL}/user/repos",
            headers=_headers(),
            params={
                "per_page": per_page,
                "page": page,
                "affiliation": "owner",
                "sort": "updated",
                "direction": "desc",
            },
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_repo(owner: str, name: str) -> dict:
    """Obtiene info detallada de un repositorio."""
    resp = requests.get(f"{BASE_URL}/repos/{owner}/{name}", headers=_headers())
    resp.raise_for_status()
    return resp.json()


def get_repo_languages(owner: str, name: str) -> dict:
    """Obtiene los lenguajes de un repositorio (nombre → bytes)."""
    resp = requests.get(
        f"{BASE_URL}/repos/{owner}/{name}/languages", headers=_headers()
    )
    resp.raise_for_status()
    return resp.json()


def get_repo_topics(owner: str, name: str) -> list[str]:
    """Obtiene los topics/tags de un repositorio."""
    resp = requests.get(
        f"{BASE_URL}/repos/{owner}/{name}/topics",
        headers={**_headers(), "Accept": "application/vnd.github.mercy-preview+json"},
    )
    resp.raise_for_status()
    return resp.json().get("names", [])


# ─── UTILIDADES ──────────────────────────────────────────────────────────────

def extract_repo_info(repo: dict) -> dict:
    """Extrae campos relevantes de un repo para catalogar."""
    return {
        "nombre": repo["name"],
        "full_name": repo["full_name"],
        "descripcion": repo.get("description") or "",
        "url": repo["html_url"],
        "lenguaje_principal": repo.get("language") or "",
        "visibilidad": "Privado" if repo["private"] else "Público",
        "estrellas": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "ultima_actividad": repo.get("pushed_at", "")[:10] if repo.get("pushed_at") else "",
        "creado": repo.get("created_at", "")[:10] if repo.get("created_at") else "",
        "fork": repo.get("fork", False),
        "archivado": repo.get("archived", False),
        "topics": repo.get("topics", []),
    }
