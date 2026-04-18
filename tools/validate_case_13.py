"""
Validacion del caso de uso 13: wikilinks cross-system del vault resuelven
contra INX-ENLACES.

Delega en `tools/obsidian_wikilinks.py audit`. Este validador es un alias
con el exit code esperado para `apps/validate_case_13.bat`.

Exit codes:
  0  OK (0 wikilinks o todos resuelven).
  1  Wikilinks rotos.
  2  Falta configuracion.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.obsidian_wikilinks import cmd_audit


class _Args:
    pass


if __name__ == "__main__":
    raise SystemExit(cmd_audit(_Args()))
