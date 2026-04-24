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