from __future__ import annotations
from typing import Tuple, Dict

# prompts and utils imported from user's project folder
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

# ─────────────────────────────────────────────────────────────────
# Helper — detect N/A mode
# ─────────────────────────────────────────────────────────────────
def _is_na(language: str) -> bool:
    """Return True when user selected N/A (no programming language required)."""
    return language.strip().upper().startswith("N/A")


def _na_teach_prompt(topic: str, difficulty: int) -> str:
    return (
        f"You are an expert tutor. The student wants to learn: \"{topic}\".\n"
        f"This topic does NOT require any programming language — teach it conceptually.\n"
        f"Difficulty level: {difficulty}/4.\n\n"
        f"Structure your response as:\n"
        f"### 📌 What is it?\n"
        f"(Clear 2-3 sentence definition)\n\n"
        f"### 🧠 Key Concepts\n"
        f"(Bullet points of the most important ideas)\n\n"
        f"### 🗺️ How it works\n"
        f"(Step-by-step explanation or flowchart in text/markdown)\n\n"
        f"### 💡 Real-world Example\n"
        f"(A concrete, relatable example)\n\n"
        f"### ❓ Quick Check\n"
        f"(One question to test the student's understanding)\n\n"
        f"Use markdown formatting. No code blocks unless absolutely necessary."
    )


def _na_challenge_prompt(topic: str, difficulty: int) -> str:
    return (
        f"Generate a conceptual challenge (NO coding required) about: \"{topic}\".\n"
        f"Difficulty: {difficulty}/4.\n\n"
        f"Format:\n"
        f"**Problem:** (A short-answer, diagram, or explanation task)\n"
        f"**What to do:** (Clear instructions — explain, draw, list, compare, etc.)\n"
        f"**Expected:** (What a correct answer should include)\n"
        f"**Hint if stuck:** (One subtle nudge — do NOT give the answer)\n\n"
        f"Make it thought-provoking but answerable in a few sentences or a short diagram."
    )


def _na_evaluate_prompt(challenge: str, answer: str, topic: str, difficulty: int) -> str:
    return (
        f"Evaluate this student's conceptual answer about \"{topic}\" (no code involved).\n\n"
        f"Challenge:\n{challenge}\n\n"
        f"Student's answer:\n{answer}\n\n"
        f"Reply in EXACTLY this format:\n"
        f"VERDICT: CORRECT / PARTIAL / INCORRECT\n"
        f"FEEDBACK: (2-3 sentences — what they got right, what's missing)\n"
        f"HINT: (one guiding sentence if PARTIAL/INCORRECT, else N/A)\n\n"
        f"Be fair — partial credit for partially correct conceptual answers."
    )


def _na_hint_prompt(challenge: str, answer: str, topic: str) -> str:
    return (
        f"The student is stuck on this conceptual question about \"{topic}\":\n\n"
        f"{challenge}\n\n"
        f"Their attempt:\n{answer or '(no attempt yet)'}\n\n"
        f"Give ONE short, guiding hint (max 2 sentences). "
        f"Do NOT give the answer. Point them in the right direction conceptually."
    )


def _na_solution_prompt(challenge: str, answer: str, topic: str) -> str:
    return (
        f"The student exhausted all hints on this conceptual question about \"{topic}\":\n\n"
        f"{challenge}\n\n"
        f"Their last attempt:\n{answer or '(no attempt)'}\n\n"
        f"Provide the COMPLETE ideal answer with explanation. Use bullet points, "
        f"diagrams in markdown/text, and clear language. Be thorough and educational."
    )


def _na_easier_prompt(challenge: str, topic: str, difficulty: int) -> str:
    easier = max(1, difficulty - 1)
    return (
        f"The student struggled with this conceptual question about \"{topic}\" "
        f"(difficulty {difficulty}/4):\n\n{challenge}\n\n"
        f"Generate a SIMPLER related question at difficulty {easier}/4. "
        f"Same topic, smaller scope. No code required. "
        f"Format: **Problem**, **What to do**, **Expected**, **Hint if stuck**."
    )


def _na_fallback_lesson(topic: str) -> str:
    return (
        f"### 📌 {topic}\n\n"
        f"_(Offline mode — connect a Groq API key for a full conceptual lesson.)_\n\n"
        f"**Key idea:** {topic} is a concept worth exploring step by step.\n\n"
        f"**Try:** Search for a diagram or flowchart of '{topic}' to get started.\n\n"
        f"**Quick Check:** Can you describe '{topic}' in one sentence?"
    )


def _na_fallback_challenge(topic: str) -> str:
    return (
        f"**Problem:** Explain the concept of \"{topic}\" in your own words.\n\n"
        f"**What to do:** Write 3-5 sentences describing what it is, "
        f"how it works, and where it's used.\n\n"
        f"**Expected:** A clear, accurate explanation with at least one real-world example.\n\n"
        f"**Hint if stuck:** Think about the problem it solves first."
    )


# ─────────────────────────────────────────────────────────────────
# Core Action Functions
# ─────────────────────────────────────────────────────────────────

def teach(state: AgentState) -> Tuple[str, str]:
    """Return (lesson_markdown, provider_used)."""
    if _is_na(state.language):
        fallback = _na_fallback_lesson(state.topic)
        text, provider = llm_complete(
            SYSTEM_PROMPT,
            _na_teach_prompt(state.topic, state.difficulty),
            fallback=fallback,
            temperature=0.4,
        )
    else:
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
    if _is_na(state.language):
        fallback = _na_fallback_challenge(state.topic)
        text, provider = llm_complete(
            SYSTEM_PROMPT,
            _na_challenge_prompt(state.topic, state.difficulty),
            fallback=fallback,
            temperature=0.6,
        )
    else:
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
    if _is_na(state.language):
        fallback = (
            f"VERDICT: PARTIAL\n"
            f"FEEDBACK: Your answer touches on the topic but needs more depth. "
            f"(Offline mode — connect Groq for detailed feedback.)\n"
            f"HINT: Try to be more specific about how {state.topic} works."
        )
        text, provider = llm_complete(
            SYSTEM_PROMPT,
            _na_evaluate_prompt(
                state.last_challenge, answer, state.topic, state.difficulty
            ),
            fallback=fallback,
            temperature=0.2,
        )
    else:
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
    if _is_na(state.language):
        fallback = (
            f"Think about the core purpose of {state.topic}. "
            f"What problem does it solve? Start from that angle."
        )
        text, provider = llm_complete(
            SYSTEM_PROMPT,
            _na_hint_prompt(state.last_challenge, answer, state.topic),
            fallback=fallback,
            temperature=0.5,
            max_tokens=200,
        )
    else:
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
    if _is_na(state.language):
        fallback = (
            f"**Interview Question:** Explain {state.topic} as if presenting to a "
            f"non-technical stakeholder. Cover: what it is, how it works, and why it matters.\n\n"
            f"**Time limit:** {time_limit} minutes\n\n"
            f"**Evaluated on:** Clarity, accuracy, structure, and real-world relevance."
        )
        prompt = (
            f"Generate a conceptual interview question about \"{state.topic}\" "
            f"(no coding required, difficulty {state.difficulty}/4). "
            f"It should be the kind asked in system design, AI theory, or product interviews.\n\n"
            f"Format:\n**Interview Question:** ...\n**Time limit:** {time_limit} minutes\n"
            f"**Evaluated on:** (3 bullet criteria)"
        )
        text, provider = llm_complete(SYSTEM_PROMPT, prompt, fallback=fallback, temperature=0.6)
    else:
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
    if _is_na(state.language):
        fallback = (
            f"VERDICT: PARTIAL\n"
            f"FEEDBACK: Your answer shows understanding but could be more structured. "
            f"(Offline — connect Groq for full evaluation.)\n"
            f"HINT: Structure your answer: define → explain → example → impact."
        )
        prompt = (
            f"Evaluate this interview answer about \"{state.topic}\" (no code involved):\n\n"
            f"Question:\n{state.last_challenge}\n\n"
            f"Answer:\n{answer}\n\n"
            f"Reply in format:\nVERDICT: CORRECT / PARTIAL / INCORRECT\n"
            f"FEEDBACK: (3 sentences — correctness, clarity, depth)\n"
            f"HINT: (improvement tip or N/A)"
        )
        text, provider = llm_complete(SYSTEM_PROMPT, prompt, fallback=fallback, temperature=0.2)
    else:
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


def generate_solution(state: AgentState) -> Tuple[str, str]:
    """Full solution revealed after 3 hints exhausted."""
    if _is_na(state.language):
        fallback = (
            f"**Complete Answer for:** {state.topic}\n\n"
            f"_(Offline — connect Groq for a detailed conceptual solution.)_\n\n"
            f"Re-read the question, research the topic, and try to explain it step by step."
        )
        text, provider = llm_complete(
            SYSTEM_PROMPT,
            _na_solution_prompt(state.last_challenge, state.last_user_answer, state.topic),
            fallback=fallback,
            temperature=0.3,
        )
    else:
        fallback = (
            f"```{state.language.lower()}\n"
            f"# Solution for: {state.topic} in {state.language}\n"
            f"# (Offline mode — connect Groq for full solution)\n"
            f"```"
        )
        prompt = (
            f"The student used all 3 hints and couldn't solve:\n\n"
            f"{state.last_challenge}\n\n"
            f"Their last attempt:\n{state.last_user_answer or '(no attempt)'}\n\n"
            f"Provide the COMPLETE, well-commented solution in {state.language}. "
            f"Explain each key line. Be educational."
        )
        text, provider = llm_complete(SYSTEM_PROMPT, prompt, fallback=fallback, temperature=0.3)
    return text, provider


def generate_easier_question(state: AgentState) -> Tuple[str, str]:
    """Simpler follow-up question after hint exhaustion."""
    easier_difficulty = max(1, state.difficulty - 1)
    if _is_na(state.language):
        fallback = _na_fallback_challenge(state.topic)
        text, provider = llm_complete(
            SYSTEM_PROMPT,
            _na_easier_prompt(state.last_challenge, state.topic, state.difficulty),
            fallback=fallback,
            temperature=0.6,
        )
    else:
        fallback = offline_challenge(state.topic, state.language, easier_difficulty)
        prompt = (
            f"The student struggled with this {state.topic} challenge (difficulty {state.difficulty}/4):\n\n"
            f"{state.last_challenge}\n\n"
            f"Generate a SIMPLER related challenge on {state.topic} "
            f"at difficulty {easier_difficulty}/4 in {state.language}. "
            f"Same concept, smaller scope. Format: **Problem**, **Input**, **Output**, **Example**."
        )
        text, provider = llm_complete(SYSTEM_PROMPT, prompt, fallback=fallback, temperature=0.6)
    return text, provider


# ─────────────────────────────────────────────────────────────────
# Agent Decision Logic
# ─────────────────────────────────────────────────────────────────

def decide_next_action(state: AgentState) -> str:
    """
    Returns one of: 'teach' | 'challenge' | 'evaluate' | 'hint' | 'interview'
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


def explain_decision(state: AgentState, action: str) -> str:
    """Human-readable reason for the suggested next action."""
    na = _is_na(state.language)
    reasons = {
        "teach":     f"You haven't learned this topic yet — let's start with a {'conceptual lesson' if na else 'quick lesson'}.",
        "challenge": f"Time to test your understanding with a {'conceptual question' if na else 'coding challenge'}.",
        "evaluate":  "Submit your answer and I'll grade it.",
        "hint":      f"You've missed {state.wrong_streak} in a row — here's a nudge.",
        "interview": f"You're on a {state.correct_streak}-streak — let's try a {'conceptual interview question' if na else 'real interview question'}.",
    }
    return reasons.get(action, "Let's continue.")