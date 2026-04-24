from __future__ import annotations
import streamlit as st

import agent
from state import (
    init_state,
    reset_state,
    record_topic,
    add_history,
    register_evaluation,
    register_hint,
    register_interview_pass,
    XP_TO_LEVEL,
)
from utils import active_provider

st.set_page_config(
    page_title="Agentic AI Coding Tutor",
    page_icon="🤖",
    layout="wide",
)

st.markdown(
    """
    <style>
      .main .block-container { padding-top: 2rem; max-width: 1200px; }
      .verdict-correct   { background:#10b98120; border-left:4px solid #10b981;
                           padding:0.75rem 1rem; border-radius:6px; }
      .verdict-partial   { background:#f59e0b20; border-left:4px solid #f59e0b;
                           padding:0.75rem 1rem; border-radius:6px; }
      .verdict-incorrect { background:#ef444420; border-left:4px solid #ef4444;
                           padding:0.75rem 1rem; border-radius:6px; }
      .badge-pill { display:inline-block; padding:0.25rem 0.6rem; margin:0.15rem;
                    background:#6366f120; border:1px solid #6366f1;
                    border-radius:999px; font-size:0.85rem; }
      .agent-suggestion { background:#0ea5e915; border-left:4px solid #0ea5e9;
                          padding:0.75rem 1rem; border-radius:6px;
                          margin-bottom:1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

state = init_state(st.session_state)
state.provider = active_provider()

with st.sidebar:
    st.title("🤖 Agentic Tutor")

    provider_label = "🟢 Groq (live)" if state.provider == "groq" else "🟡 Offline fallback"
    st.caption(f"Provider: **{provider_label}**")
    if state.provider == "offline":
        st.info(
            "No `GROQ_API_KEY` detected. Add one to `.env` for richer "
            "lessons & evaluations. The app still works fully offline.",
            icon="ℹ️",
        )

    st.markdown("### ⚙️ Settings")

    common_topics = [
        "loops", "arrays", "functions", "recursion", "conditionals",
        "strings", "dictionaries", "classes", "pointers", "OOP",
        "sorting", "searching", "data structures", "custom…",
    ]
    pick = st.selectbox("Topic", common_topics, index=common_topics.index(state.topic) if state.topic in common_topics else 0)
    if pick == "custom…":
        state.topic = st.text_input("Custom topic", value=state.topic, placeholder="e.g. binary search")
    else:
        state.topic = pick

    state.language = st.selectbox(
        "Language",
        ["Python", "Java", "C", "C++", "JavaScript", "TypeScript", "Go", "Rust"],
        index=0 if state.language == "Python" else
              ["Python", "Java", "C", "C++", "JavaScript", "TypeScript", "Go", "Rust"].index(state.language),
    )

    state.difficulty = st.slider(
        "Difficulty (auto-adapts)", 1, 4, value=state.difficulty,
        help="The agent will bump this up when you do well, down when you struggle.",
    )

    st.markdown("---")
    st.markdown("### 🎮 Stats")
    c1, c2 = st.columns(2)
    c1.metric("Level", state.level)
    c2.metric("XP", state.xp)
    st.progress(state.xp_into_level / XP_TO_LEVEL, text=f"{state.xp_into_level}/{XP_TO_LEVEL} XP to next level")
    c3, c4, c5 = st.columns(3)
    c3.metric("Streak", state.correct_streak)
    c4.metric("Correct", state.total_correct)
    c5.metric("Accuracy", f"{state.accuracy*100:.0f}%")

    if state.badges:
        st.markdown("### 🏆 Badges")
        from state import BADGES
        st.markdown(
            " ".join(f"<span class='badge-pill'>{BADGES[b]}</span>" for b in state.badges),
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("🔄 Reset session", use_container_width=True):
        reset_state(st.session_state)
        st.rerun()

st.title("Agentic AI Coding & Interview Assistant")
st.caption("Teach → Test → Evaluate → Adapt → Repeat. Works in any language, on any topic.")

suggested = agent.decide_next_action(state)
st.markdown(
    f"<div class='agent-suggestion'>🧭 <b>Agent suggests:</b> "
    f"<code>{suggested.upper()}</code> — {agent.explain_decision(state, suggested)}</div>",
    unsafe_allow_html=True,
)

b1, b2, b3, b4, b5 = st.columns(5)
do_teach     = b1.button("📘 Teach",        use_container_width=True, type="primary" if suggested == "teach" else "secondary")
do_challenge = b2.button("🎯 Start Challenge", use_container_width=True, type="primary" if suggested == "challenge" else "secondary")
do_hint      = b3.button("💡 Hint",         use_container_width=True, type="primary" if suggested == "hint" else "secondary")
do_interview = b4.button("🎤 Interview Mode", use_container_width=True, type="primary" if suggested == "interview" else "secondary")
do_auto      = b5.button("✨ Auto (do suggested)", use_container_width=True)

if do_auto:
    if   suggested == "teach":     do_teach = True
    elif suggested == "challenge": do_challenge = True
    elif suggested == "hint":      do_hint = True
    elif suggested == "interview": do_interview = True

def _toast_badges(badges):
    for b in badges:
        st.toast(f"🏆 New badge: {b}", icon="🎉")


if do_teach:
    record_topic(state, state.topic, state.language)
    with st.spinner(f"Preparing a lesson on **{state.topic}** in {state.language}…"):
        text, prov = agent.teach(state)
    state.last_lesson = text
    state.phase = "taught"
    add_history(state, "agent", f"**Lesson** ({prov})\n\n{text}")

if do_challenge:
    record_topic(state, state.topic, state.language)
    with st.spinner("Generating a challenge…"):
        text, prov = agent.challenge(state)
    state.last_challenge = text
    state.last_user_answer = ""
    state.last_verdict = ""
    state.phase = "challenged"
    add_history(state, "agent", f"**Challenge** ({prov})\n\n{text}")

if do_interview:
    record_topic(state, state.topic, state.language)
    with st.spinner("Setting up the interview question…"):
        text, prov = agent.interview(state, time_limit=10 + 5 * state.difficulty)
    state.last_challenge = text
    state.last_user_answer = ""
    state.last_verdict = ""
    state.phase = "interview"
    add_history(state, "agent", f"**Interview Question** ({prov})\n\n{text}")

if do_hint:
    if not state.last_challenge:
        st.warning("Start a challenge first — there's nothing to hint at yet.")
    else:
        with st.spinner("Thinking of a nudge…"):
            text, prov = agent.hint(state, answer=state.last_user_answer)
        state.last_hint = text
        register_hint(state)
        add_history(state, "agent", f"**Hint** ({prov})\n\n{text}")

left, right = st.columns([1.1, 1])

with left:
    st.subheader("📖 Current")
    if state.phase == "idle":
        st.info("Pick a topic in the sidebar and click **Teach** or **Auto** to begin.")
    elif state.phase == "taught" and state.last_lesson:
        st.markdown(state.last_lesson)
    elif state.phase in ("challenged", "interview", "evaluated") and state.last_challenge:
        if state.phase == "interview":
            st.markdown("### 🎤 Interview Question")
        else:
            st.markdown("### 🎯 Challenge")
        st.markdown(state.last_challenge)
        if state.last_hint:
            st.markdown(f"💡 **Last hint:** {state.last_hint}")
    elif state.last_lesson:
        st.markdown(state.last_lesson)

with right:
    st.subheader("✍️ Your Answer")
    answer = st.text_area(
        f"Write your {state.language} solution here",
        value=state.last_user_answer,
        height=260,
        placeholder=f"# Write your {state.language} solution and click Submit Answer",
        label_visibility="collapsed",
    )
    s1, s2 = st.columns(2)
    submit  = s1.button("✅ Submit Answer", use_container_width=True, type="primary")
    clear   = s2.button("🧹 Clear",         use_container_width=True)

    if clear:
        state.last_user_answer = ""
        st.rerun()

    if submit:
        if not state.last_challenge:
            st.warning("There's no active challenge — click **Start Challenge** or **Interview Mode** first.")
        elif not answer.strip():
            st.warning("Please write an answer before submitting.")
        else:
            state.last_user_answer = answer
            with st.spinner("Evaluating your answer…"):
                if state.phase == "interview":
                    result, prov = agent.evaluate_interview(state, answer)
                else:
                    result, prov = agent.evaluate(state, answer)

            state.last_verdict = result["verdict"]
            state.last_feedback = result["feedback"]
            state.last_hint = result["hint"]
            new_badges = register_evaluation(state, result["verdict"])
            if state.phase == "interview" and result["verdict"] == "CORRECT":
                new_badges += register_interview_pass(state)
            state.phase = "evaluated"

            add_history(
                state, "agent",
                f"**Evaluation** ({prov}) — **{result['verdict']}**\n\n{result['feedback']}"
                + (f"\n\n💡 _Hint:_ {result['hint']}" if result["hint"] else "")
            )
            _toast_badges(new_badges)
            st.rerun()
