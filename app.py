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