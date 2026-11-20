"""Horta Viva · Citizen Assist AI.

Ponto de entrada da interface textual. Execute a partir da raiz do repositório:

    python src/sistema.py
"""

import sys

from modulos.interface_texto import executar


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    raise SystemExit(executar())
