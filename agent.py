from __future__ import annotations
from typing import Tuple, Dict

from prompts import (
    SYSTEM_PROMPT,
    TEACH_PROMPT,
    CHALLENGE_PROMPT,
    EVALUATE_PROMPT,
    HINT_PROMPT,
    INTERVIEW_PROMPT,
    INTERVIEW_EVAL_PROMPT,
)
from utils import (
    llm_complete,
    parse_evaluation,
    offline_lesson,
    offline_challenge,
    offline_evaluate,
    offline_hint,
    offline_interview,
)
from state import AgentState