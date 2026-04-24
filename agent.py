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
def hint(state: AgentState, answer: str = "") -> Tuple[str, str]:
    fallback = offline_hint(state.last_challenge, answer, state.topic, state.language)
    text, provider = llm_complete(
        SYSTEM_PROMPT,
        HINT_PROMPT.format(
            challenge=state.last_challenge or "(no challenge yet)",
            answer=answer or "(empty)",
            language=state.language,
        ),
        fallback=fallback,
        temperature=0.5,
        max_tokens=300,
    )
    return text, provider

def interview(state: AgentState, time_limit: int = 15) -> Tuple[str, str]:
    fallback = offline_interview(state.topic, state.language, state.difficulty, time_limit)
    text, provider = llm_complete(
        SYSTEM_PROMPT,
        INTERVIEW_PROMPT.format(
            topic=state.topic,
            language=state.language,
            difficulty=state.difficulty,
            time_limit=time_limit,
        ),
        fallback=fallback,
        temperature=0.6,
    )
    return text, provider

def evaluate_interview(state: AgentState, answer: str) -> Tuple[Dict, str]:
    fallback = offline_evaluate(state.last_challenge, answer, state.topic, state.language)
    text, provider = llm_complete(
        SYSTEM_PROMPT,
        INTERVIEW_EVAL_PROMPT.format(
            topic=state.topic,
            language=state.language,
            challenge=state.last_challenge or "(no question)",
            answer=answer,
        ),
        fallback=fallback,
        temperature=0.2,
    )
    return parse_evaluation(text), provider

def decide_next_action(state: AgentState) -> str:
    """
    Returns one of: 'teach' | 'challenge' | 'evaluate' | 'hint' | 'interview'.

    Logic mirrors the spec:
      - new user (no phase yet) → TEACH
      - just taught → CHALLENGE
      - challenged but no submission tracked → wait (still 'evaluate' once they submit)
      - struggling (2+ wrong in a row OR last verdict INCORRECT) → HINT
      - performing well (3+ correct streak AND difficulty maxed-ish) → INTERVIEW
      - default → CHALLENGE
    """
    if state.phase == "idle":
        return "teach"

    if state.phase == "taught":
        return "challenge"

    if state.wrong_streak >= 2 or state.last_verdict == "INCORRECT":
        return "hint"

    if state.correct_streak >= 3 and state.difficulty >= 3:
        return "interview"

    if state.phase == "challenged":
        return "evaluate"

    return "challenge"
