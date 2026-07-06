"""Make task1 DoIP helpers importable from task2 scripts."""

from __future__ import annotations

import sys
from pathlib import Path

_TASK1_SCRIPTS = Path(__file__).resolve().parents[2] / "task1" / "scripts"
if str(_TASK1_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_TASK1_SCRIPTS))
