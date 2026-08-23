"""
UI Package for Language Learning App.
"""

import sys
from pathlib import Path

# Ensure src and project root are always in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_PATH = _PROJECT_ROOT / "src"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))
