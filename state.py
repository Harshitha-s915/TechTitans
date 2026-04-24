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

@dataclass
class AgentState:
    # User selection
    topic: str = "loops"
    language: str = "Python"
    difficulty: int = 1

    # Agent phase: idle | taught | challenged | interview | evaluated
    phase: str = "idle"

    # Last generated artefacts
    last_lesson: str = ""
    last_challenge: str = ""
    last_hint: str = ""
    last_feedback: str = ""
    last_verdict: str = ""    # CORRECT | PARTIAL | INCORRECT
    last_user_answer: str = ""

    # Performance tracking (for adaptive difficulty)
    correct_streak: int = 0
    wrong_streak: int = 0
    total_correct: int = 0
    total_partial: int = 0
    total_wrong: int = 0
    hints_used: int = 0

    # Gamification
    xp: int = 0
    badges: List[str] = field(default_factory=list)

    # Coverage tracking (for badges)
    topics_seen: List[str] = field(default_factory=list)
    languages_seen: List[str] = field(default_factory=list)

    # Conversation log for the UI
    history: List[Dict[str, str]] = field(default_factory=list)

    # Provider info shown in sidebar
    provider: str = "offline"  # 'groq' or 'offline'

    # ---- Derived ----
    @property
    def level(self) -> int:
        return 1 + self.xp // XP_TO_LEVEL

    @property
    def xp_into_level(self) -> int:
        return self.xp % XP_TO_LEVEL

    @property
    def accuracy(self) -> float:
        total = self.total_correct + self.total_partial + self.total_wrong
        if total == 0:
            return 0.0
        return (self.total_correct + 0.5 * self.total_partial) / total

_KEY = "agent_state"


def init_state(session_state) -> AgentState:
    """Attach an AgentState to st.session_state; return the live instance."""
    if _KEY not in session_state:
        session_state[_KEY] = AgentState()
    return session_state[_KEY]


def reset_state(session_state) -> AgentState:
    session_state[_KEY] = AgentState()
    return session_state[_KEY]
