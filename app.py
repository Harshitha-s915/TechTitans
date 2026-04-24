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
