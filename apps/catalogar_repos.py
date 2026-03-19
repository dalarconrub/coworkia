"""
Script de catalogación masiva de repos.
Asigna tipo, proceso y versión a los repos importados en Notion.
Ejecutar una vez tras la importación inicial.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from agents.github_agent import catalogar

# ─── PROCESOS (repos que forman parte de un mismo flujo) ─────────────────────

PROCESOS = {
    "Psicología Social": [
        "psicologia-social",
        "psicologia-social-tema-1",
        "psicologia-social-tema-1-b",
        "psicologia-social-tema-2",
        "psicologia-social-tema-3",
        "psicologia-social-tema-4",
        "psicologia-social-tema-5",
        "psicologia-social-tema-6",
        "psicologia-social-tema-8",
        "psicologia-social-tema-9",
        "psicologia-social-tema-9-b",
        "psicologia-social-tema-10",
        "psicologia-social-tema-11",
        "psicologia-social-tema-13",
        "Psicolog-a-Social-tema-12",
        "Psicologia-Social-bookdown",
        "psicologiasocial",
    ],
    "Cognifit": [
        "cognifit",
        "Cognifit-development",
        "Cognifit-master",
    ],
    "Headache Tracker": [
        "Headeche-tracker",
        "headache-tracker-app",
        "headache-tracker-render",
    ],
    "Video2PPT": [
        "video2ppt",
        "video2ppt_service",
    ],
    "Reproductor Marchas": [
        "reproductor-marchas",
        "reproductor-marchas-v2",
    ],
    "Comunidad": [
        "comunidadmd",
        "comunidadBook",
    ],
    "TFM": [
        "TFM_new",
        "tfm-sna-23.06.18",
        "tfm-ppt-23.06.25",
        "TFM-sna-final",
        "TFM-tex-final",
        "TFG-TFM_EPS",
    ],
    "Resumenet": [
        "resumenet",
        "resumennet",
    ],
    "Inquisit to PsychoPy": [
        "inquisit_to_psychopy_git",
        "inquisit_to_psychopy_git-2",
    ],
    "Medicina PEC": [
        "Medici-n-PEC-1",
        "Medici-n-PEC-1-Tarea",
    ],
    "LMS": [
        "LMS_Pipeline",
        "LMS_MD",
        "Frappme-LMS-Questions",
        "sensei-quiz-doc2txt",
    ],
    "Coworkia/Sistemas": [
        "coworkia",
        "systec",
        "DMS",
        "Sistema_ABGD",
    ],
    "Quiz App": [
        "quiz-app",
        "quizz-app-irt",
    ],
}

# ─── VERSIONES (repo → es versión mejorada de) ──────────────────────────────

VERSIONES = {
    "Cognifit-development": "cognifit",
    "Cognifit-master": "Cognifit-development",
    "headache-tracker-app": "Headeche-tracker",
    "headache-tracker-render": "headache-tracker-app",
    "reproductor-marchas-v2": "reproductor-marchas",
    "inquisit_to_psychopy_git-2": "inquisit_to_psychopy_git",
    "TFM-sna-final": "tfm-sna-23.06.18",
    "TFM-tex-final": "TFM_new",
    "video2ppt_service": "video2ppt",
    "resumennet": "resumenet",
    "psicologia-social-tema-1-b": "psicologia-social-tema-1",
    "psicologia-social-tema-9-b": "psicologia-social-tema-9",
    "quizz-app-irt": "quiz-app",
    "comunidadBook": "comunidadmd",
    "Psicologia-Social-bookdown": "psicologiasocial",
}

# ─── TIPOS ───────────────────────────────────────────────────────────────────

TIPOS = {
    # Proyectos — apps/sistemas con entidad propia
    "Proyecto": [
        "coworkia", "cognifit", "Cognifit-development", "Cognifit-master",
        "Headeche-tracker", "headache-tracker-app", "headache-tracker-render",
        "video2ppt", "video2ppt_service",
        "reproductor-marchas", "reproductor-marchas-v2",
        "quiz-app", "quizz-app-irt",
        "LMS_Pipeline", "LMS_MD", "Frappme-LMS-Questions",
        "SNAQUEST", "IGT-AI", "Coengine-demo", "luminosity",
        "comunidadmd", "comunidadBook",
        "resumenet", "resumennet",
        "berry-keating-riemann", "zero-platt",
        "seel", "analitica-foros-master",
        "Claude-chat-viewer", "IACANVA",
        "Antura", "DATA-SCIENCE-IA",
    ],
    # Ejercicios — material docente / trabajos académicos
    "Ejercicio": [
        "psicologia-social", "psicologia-social-tema-1", "psicologia-social-tema-1-b",
        "psicologia-social-tema-2", "psicologia-social-tema-3",
        "psicologia-social-tema-4", "psicologia-social-tema-5",
        "psicologia-social-tema-6", "psicologia-social-tema-8",
        "psicologia-social-tema-9", "psicologia-social-tema-9-b",
        "psicologia-social-tema-10", "psicologia-social-tema-11",
        "psicologia-social-tema-13", "Psicolog-a-Social-tema-12",
        "Psicologia-Social-bookdown", "psicologiasocial",
        "Medici-n-PEC-1", "Medici-n-PEC-1-Tarea",
        "ExamenBases", "PStema1exm",
        "Trabajo-2-PCA", "meangain_effect", "hedgesg_prepost",
        "Upo", "cursor-r",
    ],
    # Investigación — TFM, papers, tesis
    "Librería": [
        "TFM_new", "tfm-sna-23.06.18", "tfm-ppt-23.06.25",
        "TFM-sna-final", "TFM-tex-final", "TFG-TFM_EPS",
        "Paper-Down-Syndrome", "Tesis-Fran",
        "inquisit_to_psychopy_git", "inquisit_to_psychopy_git-2",
    ],
    # Config — sistemas, dotfiles, documentación de sistemas
    "Config": [
        "systec", "DMS", "Sistema_ABGD",
    ],
    # Templates
    "Template": [
        "template-tesina", "starter-hugo-academic", "academic", "autoCV",
    ],
    # Scripts
    "Script": [
        "promt-library", "sensei-quiz-doc2txt",
    ],
}


def main():
    total = 0
    errores = 0

    # 1. Asignar procesos
    print("=== ASIGNANDO PROCESOS ===\n")
    for proceso, repos in PROCESOS.items():
        for repo in repos:
            result = catalogar(repo, proceso=proceso)
            if "No se encontró" in result:
                print(f"  ✗ {repo}: no encontrado")
                errores += 1
            else:
                print(f"  ✓ {repo} → proceso: {proceso}")
                total += 1

    # 2. Asignar versiones
    print("\n=== ASIGNANDO VERSIONES ===\n")
    for repo, version_de in VERSIONES.items():
        result = catalogar(repo, version_de=version_de)
        if "No se encontró" in result:
            print(f"  ✗ {repo}: no encontrado")
            errores += 1
        else:
            print(f"  ✓ {repo} → versión de: {version_de}")
            total += 1

    # 3. Asignar tipos
    print("\n=== ASIGNANDO TIPOS ===\n")
    for tipo, repos in TIPOS.items():
        for repo in repos:
            result = catalogar(repo, tipo=tipo)
            if "No se encontró" in result:
                print(f"  ✗ {repo}: no encontrado")
                errores += 1
            else:
                print(f"  ✓ {repo} → tipo: {tipo}")
                total += 1

    print(f"\n=== CATALOGACIÓN COMPLETADA ===")
    print(f"  Actualizaciones: {total}")
    print(f"  Errores: {errores}")


if __name__ == "__main__":
    main()
