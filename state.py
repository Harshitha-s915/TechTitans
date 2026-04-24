from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

XP_PER_CORRECT = 25
XP_PER_PARTIAL = 10
XP_PER_HINT_USE = -3
XP_TO_LEVEL = 100  # XP needed per UI level

DIFF_MIN, DIFF_MAX = 1, 4

BADGES = {
    "first_blood": "🩸 First Blood — solved your first challenge",
    "streak_3":    "🔥 On Fire — 3 correct in a row",
    "streak_5":    "⚡ Unstoppable — 5 correct in a row",
    "interviewer": "🎤 Interview Ready — passed an interview question",
    "polyglot":    "🌐 Polyglot — practiced 3+ languages",
    "explorer":    "🧭 Explorer — practiced 5+ topics",
}