from __future__ import annotations
from streamlit_ace import st_ace
import time
import streamlit as st
import plotly.graph_objects as go

import agent
from state import (
    init_state,
    reset_state,
    save_state,
    switch_user,
    record_topic,
    add_history,
    register_evaluation,
    register_hint,
    register_interview_pass,
    XP_TO_LEVEL,
    BADGES,
)
from utils import active_provider

st.set_page_config(
    page_title="Agentic AI Coding Tutor",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  .main .block-container { padding-top: 1.5rem; max-width: 1300px; }

  /* ── Tutor styles ── */
  .verdict-correct   { background:#10b98120; border-left:4px solid #10b981; padding:0.75rem 1rem; border-radius:6px; }
  .verdict-partial   { background:#f59e0b20; border-left:4px solid #f59e0b; padding:0.75rem 1rem; border-radius:6px; }
  .verdict-incorrect { background:#ef444420; border-left:4px solid #ef4444; padding:0.75rem 1rem; border-radius:6px; }
  .badge-pill { display:inline-block; padding:0.25rem 0.6rem; margin:0.15rem; background:#6366f120; border:1px solid #6366f1; border-radius:999px; font-size:0.85rem; }
  .agent-suggestion { background:#0ea5e915; border-left:4px solid #0ea5e9; padding:0.75rem 1rem; border-radius:6px; margin-bottom:1rem; }

  /* ── Honor Code ── */
  .honor-box { background:#0f172a; border:2px solid #6366f1; border-radius:12px; padding:2rem 2.5rem; max-width:680px; margin:4rem auto; }
  .honor-title { font-size:1.5rem; font-weight:700; color:#e2e8f0; margin-bottom:0.25rem; }
  .honor-subtitle { color:#94a3b8; margin-bottom:1.5rem; font-size:0.95rem; }
  .honor-rule { background:#1e293b; border-left:3px solid #6366f1; border-radius:6px; padding:0.6rem 1rem; margin:0.5rem 0; color:#cbd5e1; font-size:0.92rem; }
  .cheat-warning { background:#ef444415; border:1px solid #ef4444; border-radius:8px; padding:0.75rem 1rem; color:#fca5a5; margin-bottom:1rem; }
  .cheat-count-badge { display:inline-block; background:#ef444430; border:1px solid #ef4444; border-radius:999px; padding:0.15rem 0.6rem; font-size:0.8rem; color:#fca5a5; margin-left:0.5rem; }

  /* ── Profile Dashboard ── */
  .stApp { background:#060b14; background-image: radial-gradient(ellipse at 10% 20%, #1a1040 0%, transparent 50%), radial-gradient(ellipse at 90% 80%, #0a1a2e 0%, transparent 50%); }

  .profile-hero { background:linear-gradient(135deg,#0f1729 0%,#131e35 50%,#0d1525 100%); border:1px solid #1e3058; border-radius:20px; padding:2.5rem 3rem; margin-bottom:1.5rem; position:relative; overflow:hidden; }
  .profile-hero::before { content:''; position:absolute; top:-60px; right:-60px; width:240px; height:240px; background:radial-gradient(circle,#6366f130 0%,transparent 70%); border-radius:50%; }
  .hero-name { font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800; color:#f0f6ff; margin:0; letter-spacing:-0.5px; }
  .hero-sub { color:#64748b; font-size:0.85rem; margin-top:0.3rem; font-family:'DM Mono',monospace; }
  .hero-level-badge { display:inline-flex; align-items:center; gap:0.5rem; background:linear-gradient(135deg,#6366f1,#8b5cf6); border-radius:999px; padding:0.4rem 1.2rem; font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem; color:white; margin-top:0.8rem; box-shadow:0 4px 20px #6366f140; }
  .hero-xp-label { font-family:'DM Mono',monospace; font-size:0.75rem; color:#475569; margin-bottom:0.3rem; margin-top:0.8rem; }
  .hero-xp-bar { height:7px; background:#1e293b; border-radius:999px; overflow:hidden; }
  .hero-xp-fill { height:100%; background:linear-gradient(90deg,#6366f1,#0ea5e9); border-radius:999px; }

  .stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1.5rem; }
  .stat-card { background:#0d1525; border:1px solid #1a2d4a; border-radius:14px; padding:1.4rem 1.2rem; text-align:center; position:relative; overflow:hidden; transition:transform 0.2s,border-color 0.2s; }
  .stat-card:hover { transform:translateY(-2px); border-color:#6366f150; }
  .stat-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; border-radius:14px 14px 0 0; }
  .stat-card.blue::before  { background:linear-gradient(90deg,#0ea5e9,#38bdf8); }
  .stat-card.purple::before { background:linear-gradient(90deg,#6366f1,#8b5cf6); }
  .stat-card.green::before  { background:linear-gradient(90deg,#10b981,#34d399); }
  .stat-card.amber::before  { background:linear-gradient(90deg,#f59e0b,#fbbf24); }
  .stat-value { font-family:'Syne',sans-serif; font-size:2.4rem; font-weight:800; color:#f0f6ff; line-height:1; }
  .stat-label { font-size:0.75rem; color:#64748b; margin-top:0.4rem; text-transform:uppercase; letter-spacing:1px; }
  .stat-icon { font-size:1.5rem; margin-bottom:0.5rem; display:block; }

  .section-title { font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:2px; margin-bottom:1rem; display:flex; align-items:center; gap:0.5rem; }
  .section-title::after { content:''; flex:1; height:1px; background:#1e293b; }

  .chart-card { background:#0d1525; border:1px solid #1a2d4a; border-radius:16px; padding:1.5rem; height:100%; }
  .chart-title { font-family:'Syne',sans-serif; font-size:0.9rem; font-weight:700; color:#cbd5e1; margin-bottom:1rem; }

  .badge-grid { display:flex; flex-wrap:wrap; gap:0.75rem; }
  .badge-item { background:linear-gradient(135deg,#1e293b,#0f1729); border:1px solid #2d4a7a; border-radius:12px; padding:0.8rem 1.2rem; display:flex; align-items:center; gap:0.6rem; font-size:0.85rem; color:#cbd5e1; transition:transform 0.2s,border-color 0.2s; }
  .badge-item:hover { transform:translateY(-2px); border-color:#6366f170; }
  .badge-emoji { font-size:1.4rem; }
  .badge-name { font-family:'Syne',sans-serif; font-weight:600; color:#e2e8f0; font-size:0.8rem; }

  .integrity-clean { background:#10b98115; border:1px solid #10b98140; border-radius:12px; padding:1.2rem 1.5rem; color:#6ee7b7; display:flex; align-items:center; gap:0.8rem; font-size:0.9rem; }
  .integrity-flagged { background:#ef444415; border:1px solid #ef444440; border-radius:12px; padding:1.2rem 1.5rem; color:#fca5a5; font-size:0.9rem; }
  .flag-entry { font-family:'DM Mono',monospace; font-size:0.75rem; color:#f87171; margin:0.2rem 0; padding-left:1rem; }

  .logout-card { background:#0d1525; border:1px solid #1a2d4a; border-radius:16px; padding:1.5rem 2rem; display:flex; align-items:center; justify-content:space-between; }
  .topic-pill { display:inline-block; background:#1e293b; border:1px solid #2d4a7a; border-radius:999px; padding:0.2rem 0.7rem; font-size:0.78rem; color:#94a3b8; margin:0.2rem; font-family:'DM Mono',monospace; }

  /* Page nav tabs */
  div[data-testid="stHorizontalBlock"] > div { min-width: 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# User Credentials
# ─────────────────────────────────────────────
USERS = {
    "admin":     "admin123",
    "harshitha": "python2024",
    "student1":  "pass1234",
    "student2":  "pass5678",
}

# ─────────────────────────────────────────────
# Session state init
# ─────────────────────────────────────────────
for key, default in [
    ("logged_in", False),
    ("honor_accepted", False),
    ("honor_name", ""),
    ("login_error", ""),
    ("start_time", time.time()),
    ("cheat_count", 0),
    ("cheat_log", []),
    ("hint_exhausted", False),
    ("xp_awarded", False),
    ("solution_text", ""),
    ("easier_question_text", ""),
    ("active_page", "tutor"),   # "tutor" | "profile"
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# STEP 1 — Login
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("""
<div style="background:#0f172a;border:2px solid #6366f1;border-radius:16px;
            padding:2.5rem 2.5rem 2rem;margin-top:4rem;">
  <div style="text-align:center;margin-bottom:1.5rem;">
    <span style="font-size:2.8rem;">🤖</span>
    <h2 style="color:#e2e8f0;margin:0.4rem 0 0.2rem;">Agentic AI Tutor</h2>
    <p style="color:#94a3b8;font-size:0.9rem;margin:0;">Sign in to continue</p>
  </div>
</div>
""", unsafe_allow_html=True)
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("🔒 Password", placeholder="Enter your password", type="password", key="login_pass")
        if st.session_state.login_error:
            st.error(st.session_state.login_error)
        if st.button("Login →", use_container_width=True, type="primary"):
            uname = username.strip().lower()
            if not uname or not password:
                st.session_state.login_error = "Please enter both username and password."
                st.rerun()
            elif uname not in USERS:
                st.session_state.login_error = "❌ Username not found."
                st.rerun()
            elif USERS[uname] != password:
                st.session_state.login_error = "❌ Incorrect password."
                st.rerun()
            else:
                # Save any previous user's state then switch
                old_name = st.session_state.get("honor_name", "")
                switch_user(st.session_state, old_name, uname)
                st.session_state.logged_in = True
                st.session_state.honor_name = uname.capitalize()
                st.session_state.login_error = ""
                st.rerun()
        st.markdown("<p style='text-align:center;color:#475569;font-size:0.8rem;margin-top:1rem;'>Contact your instructor if you don't have credentials.</p>", unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# STEP 2 — Honor Code
# ─────────────────────────────────────────────
if not st.session_state.honor_accepted:
    st.markdown(f"""
<div class="honor-box">
  <div class="honor-title">📜 Honor Code Agreement</div>
  <div class="honor-subtitle">Welcome, <strong>{st.session_state.honor_name}</strong>! Please read and accept the academic integrity pledge before continuing.</div>
  <div class="honor-rule">🚫 I will <strong>not copy-paste solutions</strong> from the internet, AI tools, or peers.</div>
  <div class="honor-rule">🧠 I will make a <strong>genuine attempt</strong> at every challenge before asking for a hint.</div>
  <div class="honor-rule">💡 I understand that <strong>hints exist to guide</strong> me, not to give away full solutions.</div>
  <div class="honor-rule">🎤 During Interview Mode, I will solve the problem <strong>independently and honestly</strong>.</div>
  <div class="honor-rule">📊 I acknowledge that <strong>my activity is logged</strong> for integrity review.</div>
  <div class="honor-rule">🤝 I understand that <strong>violations reduce my score</strong> and flag my session.</div>
</div>
""", unsafe_allow_html=True)
    _, col_b, _ = st.columns([1, 2, 1])
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        agreed = st.checkbox("✅ I have read and agree to the Honor Code above.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Enter the Tutor", use_container_width=True, type="primary"):
                if not agreed:
                    st.error("You must agree to the Honor Code to continue.")
                else:
                    st.session_state.honor_accepted = True
                    st.session_state.start_time = time.time()
                    st.rerun()
        with c2:
            if st.button("← Logout", use_container_width=True):
                old_name = st.session_state.get("honor_name", "")
                switch_user(st.session_state, old_name, "")
                for key in ["logged_in", "honor_accepted", "honor_name", "cheat_count", "cheat_log", "start_time", "login_error"]:
                    st.session_state.pop(key, None)
                st.rerun()
    st.stop()

# ─────────────────────────────────────────────
# Anti-Cheat
# ─────────────────────────────────────────────
CHEAT_PATTERNS = ["import solution", "# copied", "# from stackoverflow", "# chatgpt", "# gpt", "paste solution here", "exec(", "eval(", "__import__"]
MAX_PASTE_LINES = 60
HINT_LIMIT = 3

def _check_for_cheating(answer: str, hint_count: int) -> list[str]:
    violations = []
    lower = answer.lower()
    for pat in CHEAT_PATTERNS:
        if pat in lower:
            violations.append(f"Suspicious pattern detected: `{pat}`")
    if len(answer.strip().splitlines()) > MAX_PASTE_LINES:
        violations.append("Answer is unusually long — possible copy-paste detected.")
    if hint_count >= HINT_LIMIT:
        violations.append(f"Excessive hint usage ({hint_count} hints on one challenge).")
    return violations

def _log_violation(reason: str):
    ts = time.strftime("%H:%M:%S")
    st.session_state.cheat_log.append(f"[{ts}] {reason}")
    st.session_state.cheat_count += 1

# ─────────────────────────────────────────────
# State + Provider
# ─────────────────────────────────────────────
state = init_state(st.session_state)
state.provider = active_provider()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 Agentic Tutor")

    cheat_badge = (
        f"<span class='cheat-count-badge'>⚠️ {st.session_state.cheat_count} flag(s)</span>"
        if st.session_state.cheat_count > 0 else ""
    )
    st.markdown(f"👤 **{st.session_state.honor_name}** {cheat_badge}", unsafe_allow_html=True)
    st.caption("Honor Code: ✅ Signed")

    provider_label = "🟢 Groq (live)" if state.provider == "groq" else "🟡 Offline fallback"
    st.caption(f"Provider: **{provider_label}**")
    if state.provider == "offline":
        st.info("No `GROQ_API_KEY` detected. Add one to `.env` for richer lessons & evaluations.", icon="ℹ️")

    st.markdown("---")

    # ── Page Navigation ──
    st.markdown("### 🗂️ Navigation")
    nav_col1, nav_col2 = st.columns(2)
    with nav_col1:
        if st.button("🤖 Tutor", use_container_width=True,
                     type="primary" if st.session_state.active_page == "tutor" else "secondary"):
            st.session_state.active_page = "tutor"
            st.rerun()
    with nav_col2:
        if st.button("👤 Profile", use_container_width=True,
                     type="primary" if st.session_state.active_page == "profile" else "secondary"):
            st.session_state.active_page = "profile"
            st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    topic_input = st.text_area(
        "📝 What do you want to learn?",
        value=state.topic,
        placeholder="Type anything — e.g.\n• loops in Python\n• how neural networks work",
        height=100,
    )
    if topic_input.strip():
        state.topic = topic_input.strip()

    LANGUAGES = ["N/A (No code required)", "Python", "Java", "C", "C++", "JavaScript", "TypeScript", "Go", "Rust"]
    lang_index = LANGUAGES.index(state.language) if state.language in LANGUAGES else 0
    state.language = st.selectbox("💻 Programming Language", LANGUAGES, index=lang_index)

    if state.language == "N/A (No code required)":
        st.markdown("<div style='background:#7c3aed20;border-left:3px solid #7c3aed;padding:0.4rem 0.8rem;border-radius:6px;font-size:0.82rem;color:#c4b5fd;'>🧠 <strong>Concept Mode</strong></div>", unsafe_allow_html=True)

    state.difficulty = st.slider("Difficulty (auto-adapts)", 1, 4, value=state.difficulty)

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
        st.markdown(" ".join(f"<span class='badge-pill'>{BADGES[b]}</span>" for b in state.badges), unsafe_allow_html=True)

    st.markdown("---")
    if st.session_state.cheat_log:
        with st.expander(f"🚨 Integrity Log ({len(st.session_state.cheat_log)} entries)"):
            for entry in st.session_state.cheat_log:
                st.caption(entry)

    if st.button("🔄 Reset session", use_container_width=True):
        reset_state(st.session_state)
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["_confirm_logout"] = True
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# PAGE: TUTOR
# ═══════════════════════════════════════════════════════════════
if st.session_state.active_page == "tutor":

    st.title("Agentic AI Coding & Interview Assistant")
    st.caption("Teach → Test → Evaluate → Adapt → Repeat. Works in any language, on any topic.")

    if st.session_state.cheat_count > 0:
        st.markdown(
            f"<div class='cheat-warning'>⚠️ <strong>Integrity Notice:</strong> "
            f"Your session has been flagged <strong>{st.session_state.cheat_count} time(s)</strong>. "
            f"XP gains are reduced by 50% until the flag clears.</div>",
            unsafe_allow_html=True,
        )

    suggested = agent.decide_next_action(state)
    st.markdown(
        f"<div class='agent-suggestion'>🧭 <b>Agent suggests:</b> "
        f"<code>{suggested.upper()}</code> — {agent.explain_decision(state, suggested)}</div>",
        unsafe_allow_html=True,
    )

    b1, b2, b3, b4, b5 = st.columns(5)
    do_teach     = b1.button("📘 Teach",             use_container_width=True, type="primary" if suggested == "teach" else "secondary")
    do_challenge = b2.button("🎯 Start Challenge",   use_container_width=True, type="primary" if suggested == "challenge" else "secondary")
    do_hint      = b3.button("💡 Hint",              use_container_width=True, type="primary" if suggested == "hint" else "secondary")
    do_interview = b4.button("🎤 Interview Mode",    use_container_width=True, type="primary" if suggested == "interview" else "secondary")
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
        st.session_state["hint_count"] = 0
        st.session_state["hint_exhausted"] = False
        st.session_state["solution_text"] = ""
        st.session_state["easier_question_text"] = ""
        st.session_state["xp_awarded"] = False
        add_history(state, "agent", f"**Challenge** ({prov})\n\n{text}")

    if do_interview:
        record_topic(state, state.topic, state.language)
        with st.spinner("Setting up the interview question…"):
            text, prov = agent.interview(state, time_limit=10 + 5 * state.difficulty)
        state.last_challenge = text
        state.last_user_answer = ""
        state.last_verdict = ""
        state.phase = "interview"
        st.session_state["hint_count"] = 0
        st.session_state["hint_exhausted"] = False
        st.session_state["solution_text"] = ""
        st.session_state["easier_question_text"] = ""
        st.session_state["xp_awarded"] = False
        add_history(state, "agent", f"**Interview Question** ({prov})\n\n{text}")

    if do_hint:
        if not state.last_challenge:
            st.warning("Start a challenge first — there's nothing to hint at yet.")
        elif st.session_state.get("hint_exhausted", False):
            st.warning("⛔ You've used all 3 hints. The solution and an easier question are shown below.")
        else:
            current_hints = st.session_state.get("hint_count", 0)
            if HINT_LIMIT - current_hints <= 0:
                st.session_state["hint_exhausted"] = True
                _log_violation("Hint limit (3) reached — solution revealed")
                with st.spinner("Generating solution and an easier follow-up question…"):
                    sol_text, sol_prov   = agent.generate_solution(state)
                    easy_text, easy_prov = agent.generate_easier_question(state)
                st.session_state["solution_text"] = sol_text
                st.session_state["easier_question_text"] = easy_text
                state.last_challenge = easy_text
                state.last_user_answer = ""
                state.last_verdict = ""
                state.phase = "challenged"
                state.difficulty = max(1, state.difficulty - 1)
                st.session_state["hint_count"] = 0
                st.session_state["xp_awarded"] = False
                add_history(state, "agent", f"**Solution Revealed** ({sol_prov})\n\n{sol_text}\n\n**Easier Follow-up** ({easy_prov})\n\n{easy_text}")
                st.rerun()
            else:
                st.session_state["hint_count"] = current_hints + 1
                used = st.session_state["hint_count"]
                left_after = HINT_LIMIT - used
                with st.spinner(f"Thinking of hint {used}/{HINT_LIMIT}…"):
                    text, prov = agent.hint(state, answer=state.last_user_answer)
                state.last_hint = text
                register_hint(state)
                add_history(state, "agent", f"**Hint {used}/{HINT_LIMIT}** ({prov})\n\n{text}")
                if left_after == 0:
                    st.warning("⚠️ That was your **last hint (3/3)**. Click 💡 Hint once more to reveal the solution.")
                else:
                    st.info(f"💡 Hint {used}/{HINT_LIMIT} given. You have **{left_after} hint(s)** remaining.")

    hint_used = st.session_state.get("hint_count", 0)
    if state.phase in ("challenged", "interview") and not st.session_state.get("hint_exhausted"):
        hint_remaining = HINT_LIMIT - hint_used
        color = "#ef4444" if hint_remaining == 0 else ("#f59e0b" if hint_remaining == 1 else "#10b981")
        st.markdown(
            f"<span style='background:{color}20;border:1px solid {color};border-radius:999px;"
            f"padding:0.2rem 0.8rem;font-size:0.85rem;color:{color};'>"
            f"💡 Hints used: {hint_used}/{HINT_LIMIT}</span>",
            unsafe_allow_html=True,
        )

    if st.session_state.get("hint_exhausted") and st.session_state.get("solution_text"):
        st.markdown("""<div style="background:#ef444415;border:2px solid #ef4444;border-radius:10px;padding:1rem 1.2rem;margin-bottom:1rem;">
  <strong style="color:#fca5a5;">⛔ Hint limit reached — Solution Revealed</strong>
  <p style="color:#fca5a5;font-size:0.85rem;margin:0.3rem 0 0;">Study the solution carefully, then try the easier follow-up question below.</p>
</div>""", unsafe_allow_html=True)
        with st.expander("✅ View Full Solution", expanded=True):
            st.markdown(st.session_state["solution_text"])

    left, right = st.columns([1.1, 1])

    with left:
        st.subheader("📖 Current")
        if state.phase == "idle":
            st.info("Pick a topic in the sidebar and click **Teach** or **Auto** to begin.")
        elif state.phase == "taught" and state.last_lesson:
            st.markdown(state.last_lesson)
        elif state.phase in ("challenged", "interview", "evaluated") and state.last_challenge:
            if st.session_state.get("hint_exhausted") and st.session_state.get("easier_question_text"):
                st.markdown("### 🔁 Easier Follow-up Question")
                st.markdown("<small style='color:#94a3b8;'>Difficulty stepped down — master this first!</small>", unsafe_allow_html=True)
                st.markdown(st.session_state["easier_question_text"])
            elif state.phase == "interview":
                st.markdown("### 🎤 Interview Question")
                st.markdown(state.last_challenge)
            else:
                st.markdown("### 🎯 Challenge")
                st.markdown(state.last_challenge)
            if state.last_hint and not st.session_state.get("hint_exhausted"):
                st.markdown(f"<div style='background:#0ea5e915;border-left:3px solid #0ea5e9;padding:0.5rem 0.8rem;border-radius:6px;margin-top:0.5rem;'>💡 <strong>Last hint:</strong> {state.last_hint}</div>", unsafe_allow_html=True)
        elif state.last_lesson:
            st.markdown(state.last_lesson)

    with right:
        st.subheader("✍️ Your Answer")
        _na_mode = state.language.strip().upper().startswith("N/A")
        if _na_mode:
            st.markdown("<small style='color:#a78bfa;'>🧠 Concept Mode — write your explanation below</small>", unsafe_allow_html=True)
            answer = st.text_area(
                "Your answer",
                value=state.last_user_answer,
                placeholder="Write your explanation here...\n\n• Describe the concept in your own words\n• Use examples, diagrams (in text), or step-by-step breakdowns\n• No code needed!",
                height=300,
                label_visibility="collapsed",
                key="concept_answer",
            )
        else:
            editor_lang = {"Python": "python", "Java": "java", "C": "c_cpp", "C++": "c_cpp", "JavaScript": "javascript", "TypeScript": "typescript", "Go": "golang", "Rust": "rust"}.get(state.language, "python")
            answer = st_ace(value=state.last_user_answer, language=editor_lang, theme="monokai", height=300, font_size=14, tab_size=4, show_gutter=True, wrap=True, auto_update=True, key="ace_editor")

        s1, s2 = st.columns(2)
        submit = s1.button("✅ Submit Answer", use_container_width=True, type="primary")
        clear  = s2.button("🧹 Clear",         use_container_width=True)

        if clear:
            state.last_user_answer = ""
            st.rerun()

        if submit:
            if not state.last_challenge:
                st.warning("There's no active challenge — click **Start Challenge** or **Interview Mode** first.")
            elif not answer.strip():
                st.warning("Please write an answer before submitting.")
            else:
                hint_count = st.session_state.get("hint_count", 0)
                violations = _check_for_cheating(answer, hint_count)
                for v in violations:
                    _log_violation(v)
                if violations:
                    st.markdown("<div class='cheat-warning'>🚨 <strong>Integrity Check Failed:</strong><br>" + "<br>".join(f"• {v}" for v in violations) + "<br><br>Your submission was still evaluated but flagged. XP reward is reduced by 50%.</div>", unsafe_allow_html=True)

                state.last_user_answer = answer
                with st.spinner("Evaluating your answer…"):
                    if state.phase == "interview":
                        result, prov = agent.evaluate_interview(state, answer)
                    else:
                        result, prov = agent.evaluate(state, answer)

                state.last_verdict  = result["verdict"]
                state.last_feedback = result["feedback"]
                state.last_hint     = result["hint"]

                if violations and result["verdict"] == "CORRECT":
                    result["verdict"] = "PARTIAL"
                    result["feedback"] += " *(XP reduced 50% due to integrity flag)*"

                if result["verdict"] == "CORRECT" and not st.session_state.get("xp_awarded", False):
                    new_badges = register_evaluation(state, result["verdict"])
                    if state.phase == "interview":
                        new_badges += register_interview_pass(state)
                    st.session_state["xp_awarded"] = True
                elif result["verdict"] == "CORRECT" and st.session_state.get("xp_awarded", False):
                    new_badges = []
                    result["feedback"] += " *(XP already awarded for this challenge — start a new one!)*"
                else:
                    new_badges = register_evaluation(state, result["verdict"])

                state.phase = "evaluated"
                add_history(state, "agent", f"**Evaluation** ({prov}) — **{result['verdict']}**\n\n{result['feedback']}" + (f"\n\n💡 _Hint:_ {result['hint']}" if result["hint"] else ""))
                _toast_badges(new_badges)
                save_state(st.session_state)
                st.rerun()

    if state.last_verdict:
        cls  = {"CORRECT": "verdict-correct", "PARTIAL": "verdict-partial", "INCORRECT": "verdict-incorrect"}.get(state.last_verdict, "verdict-partial")
        icon = {"CORRECT": "✅", "PARTIAL": "🟡", "INCORRECT": "❌"}[state.last_verdict]
        hint_html = f"<br/><br/>💡 <b>Hint:</b> {state.last_hint}" if state.last_hint else ""
        st.markdown(f"<div class='{cls}'>{icon} <b>{state.last_verdict}</b> — {state.last_feedback}{hint_html}</div>", unsafe_allow_html=True)

    with st.expander(f"🗒️ Session history ({len(state.history)} entries)", expanded=False):
        if not state.history:
            st.caption("Nothing yet — your lessons, challenges, and evaluations will show up here.")
        for i, msg in enumerate(reversed(state.history[-20:])):
            st.markdown(f"**{len(state.history)-i}.** {msg['content']}")
            st.markdown("---")

    st.caption("Built with Streamlit • Groq Llama 3.3 • Offline fallback always available")


# ═══════════════════════════════════════════════════════════════
# PAGE: PROFILE DASHBOARD
# ═══════════════════════════════════════════════════════════════
elif st.session_state.active_page == "profile":

    username    = st.session_state.get("honor_name", "Student")
    cheat_count = st.session_state.get("cheat_count", 0)
    cheat_log   = st.session_state.get("cheat_log", [])
    start_time  = st.session_state.get("start_time", time.time())

    elapsed_sec = int(time.time() - start_time)
    elapsed_min = elapsed_sec // 60
    elapsed_hrs = elapsed_min // 60
    session_str = f"{elapsed_hrs}h {elapsed_min % 60}m" if elapsed_hrs else f"{elapsed_min}m {elapsed_sec % 60}s"

    xp_into_level = state.xp_into_level
    xp_pct = min(100, int((xp_into_level / XP_TO_LEVEL) * 100))

    easy_solved   = getattr(state, "easy_solved", 0)
    medium_solved = getattr(state, "medium_solved", 0)
    hard_solved   = getattr(state, "hard_solved", 0)

    # Fallback estimate
    if easy_solved == medium_solved == hard_solved == 0 and state.total_correct > 0:
        d, total = state.difficulty, state.total_correct
        if d <= 1:   easy_solved = total
        elif d == 2: easy_solved = total // 2; medium_solved = total - easy_solved
        elif d == 3: medium_solved = total // 2; hard_solved = total - medium_solved
        else:        hard_solved = total

    xp_history    = getattr(state, "xp_history", [])
    if not xp_history and state.xp > 0:
        pts = min(state.total_correct + 3, 15)
        xp_history = [round(state.xp * (i / max(pts, 1)) ** 1.4) for i in range(pts + 1)]

    topic_history = list(dict.fromkeys(getattr(state, "topic_history", [])))

    # ── Hero ──
    st.markdown(f"""
<div class="profile-hero">
  <div style="display:flex;align-items:flex-start;gap:2rem;flex-wrap:wrap;">
    <div style="flex:1;min-width:220px;">
      <p class="hero-sub">STUDENT PROFILE</p>
      <h1 class="hero-name">👤 {username}</h1>
      <div class="hero-level-badge">⚡ Level {state.level} &nbsp;·&nbsp; {state.xp} XP total</div>
      <div class="hero-xp-label">{xp_into_level} / {XP_TO_LEVEL} XP to Level {state.level + 1}</div>
      <div class="hero-xp-bar"><div class="hero-xp-fill" style="width:{xp_pct}%"></div></div>
      <div style="font-family:'DM Mono',monospace;font-size:0.78rem;color:#475569;margin-top:0.5rem;">🕐 Session: {session_str}</div>
    </div>
    <div style="display:flex;flex-direction:column;gap:0.5rem;align-items:flex-end;min-width:160px;">
      <div style="background:#10b98115;border:1px solid #10b98140;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#6ee7b7;">✅ Honor Code Signed</div>
      {"<div style='background:#ef444415;border:1px solid #ef444440;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#fca5a5;'>⚠️ " + str(cheat_count) + " Flag(s)</div>" if cheat_count else ""}
      <div style="background:#1e293b;border:1px solid #2d4a7a;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#64748b;font-family:'DM Mono',monospace;">{state.topic or "No topic yet"}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Stat Cards ──
    acc_pct = f"{state.accuracy * 100:.0f}%"
    st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card blue"><span class="stat-icon">🎯</span><div class="stat-value">{state.total_correct}</div><div class="stat-label">Solved</div></div>
  <div class="stat-card purple"><span class="stat-icon">🔥</span><div class="stat-value">{state.correct_streak}</div><div class="stat-label">Streak</div></div>
  <div class="stat-card green"><span class="stat-icon">📊</span><div class="stat-value">{acc_pct}</div><div class="stat-label">Accuracy</div></div>
  <div class="stat-card amber"><span class="stat-icon">🏆</span><div class="stat-value">{len(state.badges)}</div><div class="stat-label">Badges</div></div>
</div>
""", unsafe_allow_html=True)

    # ── Charts Row ──
    col_pie, col_xp = st.columns([1, 1.6])

    with col_pie:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📂 Questions by Difficulty</div>', unsafe_allow_html=True)
        total_qs = easy_solved + medium_solved + hard_solved
        if total_qs == 0:
            st.markdown("<div style='height:260px;display:flex;align-items:center;justify-content:center;color:#334155;font-size:0.9rem;text-align:center;'>No questions solved yet.<br>Start a challenge!</div>", unsafe_allow_html=True)
        else:
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Easy", "Medium", "Hard"],
                values=[easy_solved, medium_solved, hard_solved],
                hole=0.62,
                marker=dict(colors=["#10b981", "#f59e0b", "#ef4444"], line=dict(color="#060b14", width=3)),
                textinfo="percent",
                textfont=dict(family="DM Sans", size=13, color="white"),
                hovertemplate="<b>%{label}</b><br>%{value} solved<br>%{percent}<extra></extra>",
            )])
            fig_pie.add_annotation(
                text=f"<b>{total_qs}</b><br><span style='font-size:11px'>solved</span>",
                x=0.5, y=0.5,
                font=dict(size=22, color="#f0f6ff", family="Syne"),
                showarrow=False,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=10, r=10), height=280,
                legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.05, font=dict(color="#94a3b8", size=12)),
            )
            st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_xp:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📈 XP Progression</div>', unsafe_allow_html=True)
        if len(xp_history) < 2:
            st.markdown("<div style='height:260px;display:flex;align-items:center;justify-content:center;color:#334155;font-size:0.9rem;text-align:center;'>Solve more challenges to see your XP growth!</div>", unsafe_allow_html=True)
        else:
            fig_xp = go.Figure()
            fig_xp.add_trace(go.Scatter(
                x=list(range(len(xp_history))), y=xp_history,
                fill="tozeroy", fillcolor="rgba(99,102,241,0.12)",
                line=dict(color="#6366f1", width=2.5), mode="lines",
                hovertemplate="Challenge %{x}<br><b>%{y} XP</b><extra></extra>",
            ))
            # Level-up star markers
            for i, val in enumerate(xp_history):
                if i > 0 and (val // XP_TO_LEVEL) > (xp_history[i-1] // XP_TO_LEVEL):
                    fig_xp.add_trace(go.Scatter(
                        x=[i], y=[val], mode="markers",
                        marker=dict(color="#f59e0b", size=12, symbol="star", line=dict(color="#060b14", width=2)),
                        showlegend=False,
                        hovertemplate=f"<b>Level Up!</b><br>{val} XP<extra></extra>",
                    ))
            fig_xp.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=30, l=40, r=10), height=280, showlegend=False, hovermode="x unified",
                xaxis=dict(title="Challenges", title_font=dict(color="#475569", size=11), tickfont=dict(color="#475569", size=10), gridcolor="#1a2d4a", zeroline=False),
                yaxis=dict(title="Total XP",   title_font=dict(color="#475569", size=11), tickfont=dict(color="#475569", size=10), gridcolor="#1a2d4a", zeroline=False),
            )
            st.plotly_chart(fig_xp, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bar chart + Topics ──
    col_bar, col_info = st.columns([1.6, 1])

    with col_bar:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">📊 Performance by Difficulty Level</div>', unsafe_allow_html=True)
        correct_by_diff = [easy_solved, medium_solved, hard_solved, max(0, state.total_correct - easy_solved - medium_solved - hard_solved)]
        diff_labels = ["Level 1 Easy", "Level 2 Medium", "Level 3 Hard", "Level 4 Expert"]
        bar_colors  = ["#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        if sum(correct_by_diff) == 0:
            st.markdown("<div style='height:220px;display:flex;align-items:center;justify-content:center;color:#334155;font-size:0.9rem;text-align:center;'>No data yet — answer some challenges!</div>", unsafe_allow_html=True)
        else:
            fig_bar = go.Figure()
            for label, val, color in zip(diff_labels, correct_by_diff, bar_colors):
                fig_bar.add_trace(go.Bar(
                    x=[label], y=[val], name=label,
                    marker=dict(color=color, opacity=0.85),
                    hovertemplate=f"<b>{label}</b><br>%{{y}} solved<extra></extra>",
                    text=[val], textposition="outside",
                    textfont=dict(color="#94a3b8", size=12),
                ))
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=20, b=10, l=30, r=10), height=240, showlegend=False, bargap=0.4,
                xaxis=dict(tickfont=dict(color="#94a3b8", size=11), gridcolor="#1a2d4a", zeroline=False),
                yaxis=dict(tickfont=dict(color="#475569", size=10), gridcolor="#1a2d4a", zeroline=False),
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_info:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">🗂️ Topics Explored</div>', unsafe_allow_html=True)
        if topic_history:
            pills = "".join(f"<span class='topic-pill'>{t}</span>" for t in topic_history[:12])
            st.markdown(f"<div>{pills}</div>", unsafe_allow_html=True)
            if len(topic_history) > 12:
                st.caption(f"+ {len(topic_history) - 12} more topics")
        else:
            st.markdown("<div style='color:#334155;font-size:0.88rem;font-style:italic;padding:0.5rem;'>No topics explored yet.</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="chart-title">💻 Current Language</div>', unsafe_allow_html=True)
        lang = state.language or "Not set"
        lang_color = "#6366f1" if lang == "Python" else ("#0ea5e9" if lang == "JavaScript" else "#10b981")
        st.markdown(f"<span style='background:{lang_color}20;border:1px solid {lang_color}50;border-radius:8px;padding:0.4rem 1rem;color:{lang_color};font-family:DM Mono,monospace;font-size:0.85rem;'>{lang}</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Badges ──
    st.markdown('<div class="section-title">🏆 Badges Earned</div>', unsafe_allow_html=True)
    BADGE_META = {
        "first_correct":  ("🎯", "First Blood",      "Solved your very first challenge"),
        "streak_3":       ("🔥", "On Fire",           "3-challenge winning streak"),
        "streak_5":       ("⚡", "Lightning",         "5-challenge winning streak"),
        "accuracy_80":    ("🎖️", "Sharpshooter",      "Maintained 80%+ accuracy"),
        "level_2":        ("🥈", "Level 2",           "Reached Level 2"),
        "level_3":        ("🥇", "Level 3",           "Reached Level 3"),
        "level_5":        ("💎", "Diamond",           "Reached Level 5"),
        "interview_pass": ("🎤", "Interview Ready",   "Passed an interview challenge"),
        "topic_explorer": ("🗺️", "Explorer",          "Studied 3+ different topics"),
        "century":        ("💯", "Century",           "Answered 100+ challenges"),
    }
    if state.badges:
        badge_html = '<div class="badge-grid">'
        for bk in state.badges:
            info = BADGE_META.get(bk)
            if info:
                emoji, name, desc = info
            else:
                raw = BADGES.get(bk, f"🏅 {bk}")
                emoji = raw[0] if raw else "🏅"
                name  = bk.replace("_", " ").title()
                desc  = raw
            badge_html += f'<div class="badge-item" title="{desc}"><span class="badge-emoji">{emoji}</span><div><div class="badge-name">{name}</div><div style="font-size:0.7rem;color:#64748b;">{desc}</div></div></div>'
        badge_html += '</div>'
        st.markdown(badge_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='background:#0d1525;border:1px solid #1a2d4a;border-radius:12px;padding:2rem;text-align:center;color:#334155;font-size:0.9rem;'>No badges yet — solve challenges to earn your first one! 🎯</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Integrity ──
    st.markdown('<div class="section-title">🛡️ Academic Integrity</div>', unsafe_allow_html=True)
    if cheat_count == 0:
        st.markdown('<div class="integrity-clean"><span style="font-size:1.8rem;">✅</span><div><strong style="color:#6ee7b7;">Clean Record</strong><br>No integrity flags on your session. Keep up the honest work!</div></div>', unsafe_allow_html=True)
    else:
        entries_html = "".join(f"<div class='flag-entry'>→ {e}</div>" for e in cheat_log)
        st.markdown(f'<div class="integrity-flagged"><div style="font-weight:700;margin-bottom:0.5rem;">⚠️ {cheat_count} Flag(s) Recorded</div><div style="font-size:0.82rem;margin-bottom:0.5rem;">XP rewards are reduced by 50% while flags are active.</div>{entries_html}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Session / Logout ──
    st.markdown('<div class="section-title">🚪 Session</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="logout-card"><div><strong style="color:#e2e8f0;font-family:Syne,sans-serif;">Signed in as {username}</strong><div style="color:#64748b;font-size:0.85rem;margin-top:0.2rem;">Session active · {session_str} · {state.total_correct} challenges solved</div></div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    lc1, lc2, lc3 = st.columns([1, 1, 2])
    with lc1:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["_confirm_logout"] = True
    with lc2:
        if st.button("🤖 Back to Tutor", use_container_width=True, type="primary"):
            st.session_state.active_page = "tutor"
            st.rerun()

    if st.session_state.get("_confirm_logout"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.warning("⚠️ Are you sure you want to logout? Your session progress will be cleared.")
        cc1, cc2, _ = st.columns([1, 1, 2])
        with cc1:
            if st.button("✅ Yes, Logout", use_container_width=True, type="primary"):
                old_name = st.session_state.get("honor_name", "")
                switch_user(st.session_state, old_name, "")
                for k in ["logged_in", "honor_accepted", "honor_name", "cheat_count", "cheat_log",
                          "start_time", "login_error", "hint_count", "hint_exhausted",
                          "solution_text", "easier_question_text", "xp_awarded", "_confirm_logout", "active_page"]:
                    st.session_state.pop(k, None)
                st.rerun()
        with cc2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state["_confirm_logout"] = False
                st.rerun()

    st.markdown("<br><br><div style='text-align:center;color:#1e293b;font-size:0.72rem;font-family:DM Mono,monospace;padding-bottom:2rem;'>Agentic AI Tutor · Profile Dashboard · Built with Streamlit & Plotly</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Global logout confirm (from sidebar button)
# ─────────────────────────────────────────────
if st.session_state.get("_confirm_logout") and st.session_state.active_page == "tutor":
    st.markdown("<br>", unsafe_allow_html=True)
    st.warning("⚠️ Are you sure you want to logout?")
    cc1, cc2, _ = st.columns([1, 1, 3])
    with cc1:
        if st.button("✅ Yes, Logout", key="logout_confirm_tutor", use_container_width=True, type="primary"):
            old_name = st.session_state.get("honor_name", "")
            switch_user(st.session_state, old_name, "")
            for k in ["logged_in", "honor_accepted", "honor_name", "cheat_count", "cheat_log",
                      "start_time", "login_error", "hint_count", "hint_exhausted",
                      "solution_text", "easier_question_text", "xp_awarded", "_confirm_logout", "active_page"]:
                st.session_state.pop(k, None)
            st.rerun()
    with cc2:
        if st.button("❌ Cancel", key="logout_cancel_tutor", use_container_width=True):
            st.session_state["_confirm_logout"] = False
            st.rerun()