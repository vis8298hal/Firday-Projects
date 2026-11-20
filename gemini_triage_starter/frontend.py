import json
from pathlib import Path
from typing import Callable
import streamlit as st
from triage import run_triage as AGENT_RUNNER

PROJECT_CONFIG = {
    "page_title": "Enterprise AI Helpdesk",
    "page_icon": "🤖",
    "header_title": "🛠️ Enterprise IT Helpdesk Triage Agent",
    "subtitle": "Modular LangChain + Gemini + Human-in-the-Loop Boilerplate",
    "sidebar_title": "📋 Grounding Rules / Context",
    "default_context": (
        "Policy 1.1: Single-user VPN lockouts are Medium priority and require a VPN token reset.\n"
        "Policy 1.2: Hardware failures on expired warranties are Low priority.\n"
        "Policy 1.3: Hardware failures on active warranties are High priority."
    ),
    "default_query": "Hi, I'm EMP-101. I changed my password 10 mins ago and now Cisco VPN won't let me connect!",
    "db_preview_path": Path(__file__).parent / "data" / "responses" /  "employees.json",
    "audit_log_path": Path(__file__).parent / "data" / "resources" / "approved_actions.json",
}

def init_session_state():
    defaults = {
        "agent_response": None,
        "action_approved": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
def render_sidebar():
    with st.sidebar:
        st.header(PROJECT_CONFIG["sidebar_title"])
        context_input = st.text_area(
            "System Context / Policy:",
            value=PROJECT_CONFIG["default_context"],
            height=170,
        )

        db_path = PROJECT_CONFIG.get("db_preview_path")
        if db_path and db_path.exists():
            st.divider()
            st.subheader(f"🗄️ Data Source (`{db_path.name}`)")
            st.json(json.loads(db_path.read_text(encoding="utf-8")))

        return context_input
def render_results_and_hitl(response: dict):
    st.divider()
    st.subheader("📊 Structured Agent Output")

    # 1. Dynamic KPI Row (renders however many metrics your backend returns)
    metrics = response.get("metrics", {})
    if metrics:
        cols = st.columns(len(metrics))
        for col, (label, value) in zip(cols, metrics.items()):
            col.metric(label, value)

    # 2. Primary Decision Callout
    if response.get("primary_message"):
        st.info(f"**Recommended Action:** {response['primary_message']}")

    # 3. Expandable Traces & Raw JSON
    if response.get("tool_trace"):
        with st.expander("🔍 Tool Execution Trace"):
            st.code(response["tool_trace"], language="json")

    if response.get("raw_payload"):
        with st.expander("🧾 Raw Validated JSON Payload"):
            st.json(response["raw_payload"])

    # 4. Generic Human-in-the-Loop (HITL) Approval Gate
    st.subheader("🛡️ Human-in-the-Loop Approval Gate")
    audit_path: Path = PROJECT_CONFIG["audit_log_path"]

    if not st.session_state.action_approved:
        if st.button("✅ Approve & Commit Action"):
            audit_path.parent.mkdir(parents=True, exist_ok=True)
            existing = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else []
            existing.append(response["raw_payload"])
            audit_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
            st.session_state.action_approved = True
            st.rerun()
    else:
        st.success(f"Action approved and logged to `{audit_path.name}`!")

def launch_ui(agent_fn: Callable):
    st.set_page_config(
        page_title=PROJECT_CONFIG["page_title"],
        page_icon=PROJECT_CONFIG["page_icon"],
        layout="wide",
    )
    init_session_state()
    context_text = render_sidebar()

    st.title(PROJECT_CONFIG["header_title"])
    st.caption(PROJECT_CONFIG["subtitle"])

    user_query = st.text_area(
        "Input Prompt / Ticket:",
        value=PROJECT_CONFIG["default_query"],
        height=100,
    )

    if st.button("🚀 Run Agent", type="primary"):
        st.session_state.action_approved = False
        with st.status("Executing Agent Workflow...", expanded=True) as status:
            result = agent_fn(
                user_input=user_query,
                context_rules=context_text,
                on_step=lambda msg: st.write(msg),
            )
            st.session_state.agent_response = result
            status.update(label="✅ Execution Complete!", state="complete", expanded=False)

    if st.session_state.agent_response:
        render_results_and_hitl(st.session_state.agent_response)

if __name__ == "__main__":
    launch_ui(AGENT_RUNNER)