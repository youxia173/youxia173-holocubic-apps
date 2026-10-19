"""Keep final animation assets inside the application, never on Desktop."""
from pathlib import Path
DELIVERY_ROOT = Path(__file__).resolve().parents[1] / '素材'
DELIVERY_ROOT.mkdir(parents=True, exist_ok=True)
