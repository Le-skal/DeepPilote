"""
Script pour lancer l'API DeepPilot.

Usage:
    python scripts/run_api.py
    python scripts/run_api.py --port 8080
    python scripts/run_api.py --reload
"""

import argparse
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import uvicorn


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(description="Lance l'API DeepPilot")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Adresse d'écoute (défaut: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port d'écoute (défaut: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Active le rechargement automatique (dev)",
    )
    args = parser.parse_args()

    print(f"[START] Lancement de l'API sur http://{args.host}:{args.port}")
    print(f"[DOCS] Documentation: http://{args.host}:{args.port}/docs")
    print("Press CTRL+C to stop")

    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
