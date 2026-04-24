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
def teach(state: AgentState) -> Tuple[str, str]:
    """Return (lesson_markdown, provider_used)."""
    fallback = offline_lesson(state.topic, state.language, state.difficulty)
    text, provider = llm_complete(
        SYSTEM_PROMPT,
        TEACH_PROMPT.format(
            topic=state.topic,
            language=state.language,
            difficulty=state.difficulty,
        ),
        fallback=fallback,
        temperature=0.4,
    )
    return text, provider
def challenge(state: AgentState) -> Tuple[str, str]:
    fallback = offline_challenge(state.topic, state.language, state.difficulty)
    text, provider = llm_complete(
        SYSTEM_PROMPT,
        CHALLENGE_PROMPT.format(
            topic=state.topic,
            language=state.language,
            difficulty=state.difficulty,
        ),
        fallback=fallback,
        temperature=0.7,
    )
    return text, provider
def evaluate(state: AgentState, answer: str) -> Tuple[Dict, str]:
    fallback = offline_evaluate(state.last_challenge, answer, state.topic, state.language)
    text, provider = llm_complete(
        SYSTEM_PROMPT,
        EVALUATE_PROMPT.format(
            topic=state.topic,
            language=state.language,
            difficulty=state.difficulty,
            challenge=state.last_challenge or "(no challenge in context)",
            answer=answer,
        ),
        fallback=fallback,
        temperature=0.2,
    )
    return parse_evaluation(text), provider