import sys
from pathlib import Path

# Make top-level modules (core, report) importable from tests/ without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
