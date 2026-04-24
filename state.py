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

    # Profile / dashboard extras
    xp_history: List[int] = field(default_factory=list)
    topic_history: List[str] = field(default_factory=list)
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0

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


# ─────────────────────────────────────────────────────────────────
# Per-user state key  →  "agent_state:<username>"
# Falls back to the old global key if username is not set yet
# (e.g. during login page render before honor_name is written)
# ─────────────────────────────────────────────────────────────────
_GLOBAL_KEY = "agent_state"   # legacy / fallback
_ALL_USERS_KEY = "all_user_states"  # dict: username -> serialised state dict


def _user_key(session_state) -> str:
    """Return the session_state key for the currently logged-in user."""
    username = (session_state.get("honor_name") or "").strip().lower()
    if username:
        return f"agent_state:{username}"
    return _GLOBAL_KEY


def _load_persisted(session_state, username: str) -> AgentState:
    """
    Restore a previously saved AgentState for `username` if one exists.
    Stored in session_state[_ALL_USERS_KEY][username] as a plain dict so
    that switching users in the same browser session restores the right data.
    """
    all_states: dict = session_state.get(_ALL_USERS_KEY, {})
    saved: dict | None = all_states.get(username)
    if not saved:
        return AgentState()

    # Build AgentState from saved dict, ignoring unknown keys gracefully
    valid_fields = {f.name for f in AgentState.__dataclass_fields__.values()}
    filtered = {k: v for k, v in saved.items() if k in valid_fields}
    return AgentState(**filtered)


def _persist(session_state, username: str, state: AgentState) -> None:
    """Save current AgentState into the cross-user store."""
    if not username:
        return
    if _ALL_USERS_KEY not in session_state:
        session_state[_ALL_USERS_KEY] = {}
    session_state[_ALL_USERS_KEY][username] = asdict(state)


def init_state(session_state) -> AgentState:
    """
    Return the AgentState for the currently logged-in user.
    - First call for a user  → load from persisted store (or create fresh).
    - Subsequent calls       → return the already-attached instance.
    """
    key = _user_key(session_state)
    username = (session_state.get("honor_name") or "").strip().lower()

    if key not in session_state:
        # Load persisted state for this user (or brand-new AgentState)
        session_state[key] = _load_persisted(session_state, username)

    return session_state[key]


def save_state(session_state) -> None:
    """
    Explicitly persist the current user's state into the cross-user store.
    Call this after any mutation you want to survive a user switch.
    """
    key = _user_key(session_state)
    username = (session_state.get("honor_name") or "").strip().lower()
    if key in session_state:
        _persist(session_state, username, session_state[key])


def reset_state(session_state) -> AgentState:
    """Reset only the current user's state; other users are untouched."""
    key = _user_key(session_state)
    username = (session_state.get("honor_name") or "").strip().lower()
    fresh = AgentState()
    session_state[key] = fresh
    _persist(session_state, username, fresh)
    return fresh


def switch_user(session_state, old_username: str, new_username: str) -> None:
    """
    Called on logout / login transition.
    1. Saves the old user's state.
    2. Removes the old key so the new user starts fresh from their own store.
    """
    old_key = f"agent_state:{old_username.strip().lower()}" if old_username else _GLOBAL_KEY
    if old_key in session_state:
        _persist(session_state, old_username.strip().lower(), session_state[old_key])
        del session_state[old_key]

    # Also clear the legacy global key if it exists
    if _GLOBAL_KEY in session_state:
        del session_state[_GLOBAL_KEY]


# ─────────────────────────────────────────────────────────────────
# Domain helpers (unchanged logic, same signatures)
# ─────────────────────────────────────────────────────────────────

def record_topic(s: AgentState, topic: str, language: str) -> None:
    if topic and topic not in s.topics_seen:
        s.topics_seen.append(topic)
    if language and language not in s.languages_seen:
        s.languages_seen.append(language)
    # Also track for profile topic pills (deduplicated)
    if topic and topic not in s.topic_history:
        s.topic_history.append(topic)
    _check_coverage_badges(s)


def add_history(s: AgentState, role: str, content: str) -> None:
    s.history.append({"role": role, "content": content})


def register_evaluation(s: AgentState, verdict: str) -> List[str]:
    """Update streaks, XP, difficulty. Returns list of newly earned badge strings."""
    verdict = (verdict or "").upper().strip()
    earned: List[str] = []

    if verdict == "CORRECT":
        s.total_correct += 1
        s.correct_streak += 1
        s.wrong_streak = 0
        s.xp += XP_PER_CORRECT
        # Track XP history snapshot
        s.xp_history.append(s.xp)
        # Track difficulty breakdown
        if s.difficulty == 1:
            s.easy_solved += 1
        elif s.difficulty == 2:
            s.medium_solved += 1
        else:
            s.hard_solved += 1
        if s.total_correct == 1:
            earned += _award(s, "first_blood")
        if s.correct_streak == 3:
            earned += _award(s, "streak_3")
        if s.correct_streak == 5:
            earned += _award(s, "streak_5")
    elif verdict == "PARTIAL":
        s.total_partial += 1
        s.correct_streak = 0
        s.xp += XP_PER_PARTIAL
    else:  # INCORRECT or unknown
        s.total_wrong += 1
        s.wrong_streak += 1
        s.correct_streak = 0

    _adapt_difficulty(s)
    earned += _check_coverage_badges(s)
    return earned


def register_hint(s: AgentState) -> None:
    s.hints_used += 1
    s.xp = max(0, s.xp + XP_PER_HINT_USE)


def register_interview_pass(s: AgentState) -> List[str]:
    return _award(s, "interviewer")


def _adapt_difficulty(s: AgentState) -> None:
    """2 correct in a row → bump up. 2 wrong in a row → drop down."""
    if s.correct_streak >= 2 and s.difficulty < DIFF_MAX:
        s.difficulty += 1
        s.correct_streak = 0
    elif s.wrong_streak >= 2 and s.difficulty > DIFF_MIN:
        s.difficulty -= 1
        s.wrong_streak = 0


def _award(s: AgentState, badge_key: str) -> List[str]:
    if badge_key in BADGES and badge_key not in s.badges:
        s.badges.append(badge_key)
        return [BADGES[badge_key]]
    return []


def _check_coverage_badges(s: AgentState) -> List[str]:
    earned: List[str] = []
    if len(s.languages_seen) >= 3:
        earned += _award(s, "polyglot")
    if len(s.topics_seen) >= 5:
        earned += _award(s, "explorer")
    return earned


def to_dict(s: AgentState) -> Dict[str, Any]:
    return asdict(s)