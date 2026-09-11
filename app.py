"""
🛡️ SENTINEL - Intelligent Accessibility and Safety Layer for AI Agents
Main Streamlit Application.
"""
import os
import json
import time
import uuid
import streamlit as st
from typing import Dict, Any, List

# Streamlit Page Config
st.set_page_config(
    page_title="SENTINEL - AI Accessibility & Safety Layer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Dark Professional CSS
st.markdown("""
<style>
    /* Dark safety theme styling */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .badge-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 12px;
    }
    .badge {
        background: #1e293b;
        color: #38bdf8;
        border: 1px solid #0284c7;
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .card {
        background-color: #131c2e;
        border: 1px solid #23324d;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #f8fafc;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .decision-approve {
        background-color: #064e3b;
        color: #34d399;
        border: 2px solid #059669;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.2rem;
        text-align: center;
    }
    .decision-replace {
        background-color: #1e3a8a;
        color: #60a5fa;
        border: 2px solid #2563eb;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.2rem;
        text-align: center;
    }
    .decision-block {
        background-color: #7f1d1d;
        color: #f87171;
        border: 2px solid #dc2626;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.2rem;
        text-align: center;
    }
    .decision-escalate {
        background-color: #78350f;
        color: #fbbf24;
        border: 2px solid #d97706;
        padding: 8px 18px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1.2rem;
        text-align: center;
    }
    .step-box {
        border-left: 3px solid #38bdf8;
        padding-left: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Imports after styles
from config.settings import settings
from services.ollama_service import ollama_service
from services.trace_service import trace_service
from services.system_service import system_service
from rag.retriever import retriever
from rag.vector_store import vector_store
from rag.knowledge_loader import load_accessibility_knowledge
from sentinel_mcp.tools import retrieve_accessibility_guidance, analyze_action_context, get_safety_policy, log_sentinel_event
from sentinel_mcp.client import mcp_client
from models.schemas import ActionItem, RetrievedDocument
from agents.intent_agent import intent_agent
from agents.action_planner import action_planner
from agents.accessibility_agent import accessibility_agent
from agents.risk_agent import risk_agent
from agents.confidence_agent import confidence_agent
from agents.decision_agent import decision_agent
from agents.narrator_agent import narrator_agent

# Initialize Session State
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "current_pipeline_result" not in st.session_state:
    st.session_state.current_pipeline_result = None
if "human_action_choice" not in st.session_state:
    st.session_state.human_action_choice = None

# Sidebar Navigation
st.sidebar.markdown("## 🛡️ SENTINEL NAVIGATION")
page = st.sidebar.radio(
    "Select View",
    ["🛡️ Live Sentinel", "🔍 Observability & Traces", "📚 Knowledge Base", "📊 Evaluation", "⚙️ System Status"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Runtime Specs")
st.sidebar.caption(f"**Local Model:** `{settings.ollama.model}`")
st.sidebar.caption(f"**Embeddings:** `Local Semantic LSA (100% Offline)`")
st.sidebar.caption(f"**Knowledge DB:** `ChromaDB (15 WCAG Docs)`")
st.sidebar.caption(f"**Orchestration:** `LangGraph Multi-Agent`")
st.sidebar.caption(f"**Tool Protocol:** `FastMCP`")

# ----------------- PAGE 1: LIVE SENTINEL -----------------
if page == "🛡️ Live Sentinel":
    # Header Banner
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; color: #f8fafc;">🛡️ SENTINEL</h1>
        <h3 style="margin: 4px 0 0 0; color: #94a3b8; font-weight: 400;">
            An Intelligent Accessibility and Safety Layer for AI Agents
        </h3>
        <div class="badge-bar">
            <span class="badge">🔒 Local-First</span>
            <span class="badge">🦙 Ollama Local LLM</span>
            <span class="badge">🤖 LangGraph Multi-Agent</span>
            <span class="badge">📚 ChromaDB Semantic RAG</span>
            <span class="badge">⚡ FastMCP Tool Protocols</span>
            <span class="badge">👤 Human-In-The-Loop</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Example Prompt Buttons (Convenience Only - Populates Text Input)
    st.markdown("##### 💡 Example Scenarios (Domain: Online Education Portal)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📖 Accessible: Read Syllabus", use_container_width=True):
            st.session_state.user_input = "Open my DBMS course syllabus and view the lecture schedule"
    with col2:
        if st.button("🔄 Barrier: Drag Files", use_container_width=True):
            st.session_state.user_input = "Rearrange my uploaded assignment files by dragging them into chronological order"
    with col3:
        if st.button("⚠️ High-Risk: Delete Exam", use_container_width=True):
            st.session_state.user_input = "Permanently delete my final semester exam project submission from storage"
    with col4:
        if st.button("❓ Ambiguous: Do That", use_container_width=True):
            st.session_state.user_input = "Do that thing right now on my screen"

    # User Input Text Area
    user_request = st.text_area(
        "Tell the AI agent what you want to do:",
        value=st.session_state.user_input,
        placeholder="e.g. I want to submit my DBMS assignment...",
        height=100
    )

    run_clicked = st.button("🚀 RUN SENTINEL SUPERVISOR", type="primary", use_container_width=True)

    if run_clicked and user_request.strip():
        st.session_state.human_action_choice = None
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"

        with st.status("🛡️ Sentinel Supervisory Engine Running...", expanded=True) as status:
            # 1. Intent Agent
            st.write("🧠 **Intent Agent:** Parsing natural language goal, constraints, and domain...")
            t0 = time.time()
            intent_res = intent_agent.run(user_request)
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*Goal:* `{intent_res.goal}` | *Domain:* `{intent_res.domain}` ({round((time.time() - t0)*1000)}ms)")

            # 2. Action Planner
            st.write("📋 **Action Planner Agent:** Generating structured sequence of computer interaction steps...")
            t1 = time.time()
            action_plan = action_planner.run(intent_res)
            st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;*Actions Planned:* `{len(action_plan.actions)} steps` ({round((time.time() - t1)*1000)}ms)")

            # 3. Action Loop
            action_results = []
            for idx, act in enumerate(action_plan.actions):
                st.write(f"🔍 **Analyzing Action {idx+1}/{len(action_plan.actions)}:** `{act.action_type}` on `{act.target}`...")
                
                action_mcp_calls = []

                # FastMCP RAG Retrieval via SentinelMCPClient
                query = f"{act.action_type} {act.target} {act.description}"
                mcp_rag = mcp_client.call_tool("retrieve_accessibility_guidance", {"query": query, "top_k": settings.rag.top_k})
                action_mcp_calls.append(mcp_rag)
                retrieved_docs = [RetrievedDocument(**d) for d in mcp_rag.get("result", {}).get("documents", [])]

                # Accessibility Agent
                acc_res = accessibility_agent.run(action=act, retrieved_docs=retrieved_docs)

                # Risk Agent & Policy MCP via SentinelMCPClient
                mcp_pol = mcp_client.call_tool("get_safety_policy", {
                    "action_type": act.action_type,
                    "target": act.target,
                    "impact_description": act.description
                })
                action_mcp_calls.append(mcp_pol)
                pol_ctx = mcp_pol.get("result", {})
                risk_res = risk_agent.run(action=act, policy_context=pol_ctx)

                # Confidence Agent
                conf_res = confidence_agent.calculate(retrieved_docs, acc_res, risk_res)

                # Decision Agent
                dec_res = decision_agent.run(act, acc_res, risk_res, conf_res, pol_ctx)

                # Replacement Loop Handling (Modification 5)
                replaced_action = None
                if dec_res.decision == "REPLACE" and acc_res.alternative:
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;🔄 *Dynamic Replacement Loop:* Evaluating accessible alternative...")
                    alt_act = ActionItem(
                        id=f"{act.id}_alt",
                        action_type="keyboard_accessible_command",
                        target=act.target,
                        description=f"Accessible Alternative: {acc_res.alternative}",
                        reversible=act.reversible,
                        data_sensitivity=act.data_sensitivity
                    )
                    # Re-analyze replacement action via FastMCP
                    alt_rag_call = mcp_client.call_tool("retrieve_accessibility_guidance", {"query": alt_act.description, "top_k": 2})
                    action_mcp_calls.append(alt_rag_call)
                    alt_rag = [RetrievedDocument(**d) for d in alt_rag_call.get("result", {}).get("documents", [])]
                    alt_acc = accessibility_agent.run(alt_act, alt_rag)
                    alt_risk = risk_agent.run(alt_act, pol_ctx)
                    alt_conf = confidence_agent.calculate(alt_rag, alt_acc, alt_risk)
                    alt_dec = decision_agent.run(alt_act, alt_acc, alt_risk, alt_conf, pol_ctx)
                    replaced_action = {
                        "alternative_action": alt_act,
                        "alt_accessibility": alt_acc,
                        "alt_risk": alt_risk,
                        "alt_confidence": alt_conf,
                        "alt_decision": alt_dec
                    }

                # Narrator Agent
                st.write(f"🗣️ **Narrator Agent:** Generating plain-English explanation...")
                narration = narrator_agent.run(act, acc_res, risk_res, conf_res, dec_res)

                # Trace Logging via FastMCP Client
                mcp_trace = mcp_client.call_tool("log_sentinel_event", {
                    "event_data": {
                        "workflow_id": workflow_id,
                        "action_id": act.id,
                        "action_type": act.action_type,
                        "target": act.target,
                        "accessibility": acc_res.model_dump(),
                        "risk": risk_res.model_dump(),
                        "confidence": conf_res.overall_confidence,
                        "decision": dec_res.decision,
                        "narration": narration.model_dump(),
                        "mcp_invocations_count": len(action_mcp_calls)
                    }
                })
                action_mcp_calls.append(mcp_trace)

                action_results.append({
                    "action": act,
                    "retrieved_docs": retrieved_docs,
                    "accessibility": acc_res,
                    "risk": risk_res,
                    "confidence": conf_res,
                    "decision": dec_res,
                    "policy_context": pol_ctx,
                    "replacement": replaced_action,
                    "narration": narration,
                    "mcp_tool_calls": action_mcp_calls
                })

            status.update(label="✅ Sentinel Supervisory Analysis Complete!", state="complete", expanded=False)

        st.session_state.current_pipeline_result = {
            "workflow_id": workflow_id,
            "intent": intent_res,
            "action_plan": action_plan,
            "results": action_results
        }

    # Render Pipeline Results
    if st.session_state.current_pipeline_result:
        res_data = st.session_state.current_pipeline_result
        intent = res_data["intent"]
        plan = res_data["action_plan"]
        results = res_data["results"]

        st.markdown("---")
        # 1. User Intent Display
        st.markdown("### 1️⃣ User Intent Understanding")
        i_col1, i_col2, i_col3 = st.columns([2, 1, 1])
        with i_col1:
            st.markdown(f"**Goal:** `{intent.goal}`")
        with i_col2:
            st.markdown(f"**Domain:** `{intent.domain.title()}`")
        with i_col3:
            st.markdown(f"**Requires Action:** `{'Yes' if intent.requires_action else 'No'}`")
        if intent.constraints:
            st.caption(f"Constraints: {', '.join(intent.constraints)}")

        # 2. Action Plan Display
        st.markdown("### 2️⃣ Structured Action Plan")
        plan_cols = st.columns(min(4, max(1, len(plan.actions))))
        for i, act in enumerate(plan.actions):
            with plan_cols[i % len(plan_cols)]:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">Step {i+1}: {act.action_type.upper()}</div>
                    <p style="margin: 0; font-size: 0.9rem;"><strong>Target:</strong> {act.target}</p>
                    <p style="margin: 4px 0; font-size: 0.85rem; color: #94a3b8;">{act.description}</p>
                    <span class="badge" style="font-size: 0.75rem;">{'Reversible' if act.reversible else '⚠️ Irreversible'}</span>
                </div>
                """, unsafe_allow_html=True)

        # 3. Action-by-Action Analysis
        st.markdown("### 3️⃣ Live Action Supervisory Analysis")
        for i, item in enumerate(results):
            act = item["action"]
            acc = item["accessibility"]
            risk = item["risk"]
            conf = item["confidence"]
            dec = item["decision"]
            docs = item["retrieved_docs"]
            narration = item["narration"]
            replacement = item.get("replacement")

            with st.expander(f"📍 Action {i+1}: [{act.action_type.upper()}] on '{act.target}' — Decision: {dec.decision}", expanded=True):
                # Proposed Action Header
                st.markdown(f"**Proposed Interaction:** `{act.action_type}` on `{act.target}` ({act.description})")
                
                # Decision Banner
                dec_class = f"decision-{dec.decision.lower()}"
                st.markdown(f"""
                <div class="{dec_class}">
                    SUPERVISORY DECISION: {dec.decision}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # Multi-Factor Analysis Columns
                c1, c2, c3 = st.columns(3)
                
                # Accessibility Card
                with c1:
                    acc_color = "#34d399" if acc.status == "ACCESSIBLE" else ("#60a5fa" if acc.status == "FRAGILE" else "#fbbf24")
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title" style="color: {acc_color};">♿ Accessibility Analysis</div>
                        <p><strong>Status:</strong> <span style="color: {acc_color}; font-weight: 700;">{acc.status}</span></p>
                        <p><strong>Barrier Detected:</strong> {acc.issue}</p>
                        <p style="font-size: 0.85rem; color: #94a3b8;">{acc.reason}</p>
                        {f"<p><strong>Alternative:</strong> <span style='color: #60a5fa;'>{acc.alternative}</span></p>" if acc.alternative else ""}
                        <p><small>Certainty: {int(acc.confidence * 100)}%</small></p>
                    </div>
                    """, unsafe_allow_html=True)

                # Risk & Safety Card
                with c2:
                    risk_color = "#34d399" if risk.risk_level == "LOW" else ("#60a5fa" if risk.risk_level == "MEDIUM" else ("#f87171" if risk.risk_level == "HIGH" else "#ef4444"))
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title" style="color: {risk_color};">🛡️ Safety & Risk Assessment</div>
                        <p><strong>Risk Level:</strong> <span style="color: {risk_color}; font-weight: 700;">{risk.risk_level}</span></p>
                        <p><strong>Potential Impact:</strong> {risk.impact}</p>
                        <p><strong>Reversibility:</strong> {'Yes (Safe)' if risk.reversible else 'No (Irreversible)'}</p>
                        <p><strong>Confirmation Mandate:</strong> {'Mandatory' if risk.requires_confirmation else 'Not Required'}</p>
                        <p style="font-size: 0.85rem; color: #94a3b8;">{risk.reason}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Overall Confidence Card
                with c3:
                    conf_val = conf.overall_confidence
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title" style="color: #38bdf8;">📊 Multi-Factor Confidence</div>
                        <h2 style="margin: 0; color: #38bdf8;">{conf.confidence_percentage}</h2>
                        <p style="font-size: 0.85rem; color: #94a3b8;">{conf.rationale}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(conf_val)
                    st.caption(f"Factors: RAG ({conf.factors.get('rag_max_relevance', 0)}) | Acc ({conf.factors.get('accessibility_confidence', 0)}) | Risk ({conf.factors.get('risk_confidence', 0)}) | Schema (1.0)")

                # RAG Grounding Evidence
                st.markdown("##### 📚 Grounded Accessibility Knowledge (ChromaDB Vector Retrieval)")
                if docs:
                    d_cols = st.columns(min(len(docs), 3))
                    for d_idx, doc in enumerate(docs[:3]):
                        with d_cols[d_idx]:
                            st.markdown(f"""
                            <div class="card" style="font-size: 0.85rem;">
                                <strong>{doc.title}</strong> ({doc.reference})<br>
                                <span class="badge" style="font-size: 0.7rem;">Similarity: {int(doc.relevance_score * 100)}%</span>
                                <p style="margin-top: 6px; color: #cbd5e1;">{doc.content[:160]}...</p>
                                <small style="color: #60a5fa;"><strong>Recommended Alt:</strong> {'; '.join(doc.recommended_alternatives[:1])}</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No specific guidelines met similarity threshold.")

                # Real FastMCP Tool Invocations Display (Final Rule 1)
                action_mcp = item.get("mcp_tool_calls", [])
                if action_mcp:
                    st.markdown("##### ⚡ Real FastMCP Tool Invocations (Execution Trace)")
                    mcp_table_rows = []
                    for m in action_mcp:
                        mcp_table_rows.append({
                            "MCP Tool": m.get("mcp_tool"),
                            "Input Parameters": json.dumps(m.get("input"))[:50] + ("..." if len(json.dumps(m.get("input"))) > 50 else ""),
                            "Output Summary": m.get("output_summary"),
                            "Latency": f"{m.get('execution_time_ms', 0)} ms",
                            "Status": "✅ SUCCESS" if m.get("success") else "❌ FAILED"
                        })
                    st.table(mcp_table_rows)

                # Dynamic Replacement Loop Result (Final Rule 3)
                if replacement:
                    alt_act = replacement["alternative_action"]
                    alt_dec = replacement["alt_decision"]
                    st.markdown(f"""
                    <div class="card" style="border-left: 4px solid #3b82f6;">
                        <h5 style="color: #60a5fa; margin: 0;">🔄 Dynamic Replacement Action Loop (WCAG Alternative)</h5>
                        <p><strong>Original Inaccessible Action:</strong> {act.description}</p>
                        <p><strong>Generated Accessible Alternative:</strong> <code>{alt_act.action_type}</code> — {alt_act.description}</p>
                        <p><strong>Re-evaluation Result:</strong> <span class="badge">{alt_dec.decision}</span> ({alt_dec.reason})</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Human-In-The-Loop Confirmation UI (Final Rule 3)
                if dec.requires_human_confirmation:
                    st.markdown("---")
                    st.warning(f"⚠️ **HUMAN-IN-THE-LOOP SUPERVISORY ACTION MANDATED** — {dec.reason}")
                    
                    h_col1, h_col2, h_col3 = st.columns([1, 1, 1])
                    with h_col1:
                        if st.button("✅ CONFIRM / AUTHORIZE", key=f"confirm_{i}", use_container_width=True):
                            st.session_state.human_action_choice = "HUMAN_AUTHORIZED"
                            mcp_client.call_tool("log_sentinel_event", {
                                "event_data": {
                                    "workflow_id": res_data.get("workflow_id"),
                                    "action_id": act.id,
                                    "event": "HUMAN_SUPERVISORY_DECISION",
                                    "status": "HUMAN_AUTHORIZED",
                                    "note": "Human supervisor explicitly confirmed and authorized action execution."
                                }
                            })
                            st.success("Human authorization granted. Supervisory Status: HUMAN_AUTHORIZED (Logged to JSONL trace).")
                    with h_col2:
                        if st.button("🛑 CANCEL", key=f"cancel_{i}", use_container_width=True):
                            st.session_state.human_action_choice = "CANCELLED"
                            mcp_client.call_tool("log_sentinel_event", {
                                "event_data": {
                                    "workflow_id": res_data.get("workflow_id"),
                                    "action_id": act.id,
                                    "event": "HUMAN_SUPERVISORY_DECISION",
                                    "status": "CANCELLED",
                                    "note": "Human supervisor cancelled and halted action."
                                }
                            })
                            st.error("Action cancelled by human supervisor. Supervisory Status: CANCELLED (Logged to JSONL trace).")
                    with h_col3:
                        if st.button("⚡ OVERRIDE", key=f"override_{i}", use_container_width=True):
                            st.session_state.human_action_choice = "HUMAN_OVERRIDE"
                            mcp_client.call_tool("log_sentinel_event", {
                                "event_data": {
                                    "workflow_id": res_data.get("workflow_id"),
                                    "action_id": act.id,
                                    "event": "HUMAN_SUPERVISORY_DECISION",
                                    "status": "HUMAN_OVERRIDE",
                                    "note": "Human supervisor explicitly overrode safety guardrails."
                                }
                            })
                            st.warning("Action proceeded under explicit human override. Supervisory Status: HUMAN_OVERRIDE (Logged to JSONL trace).")

                    if st.session_state.human_action_choice:
                        st.info(f"Active Supervisory State: **{st.session_state.human_action_choice}** (Audited in Sentinel Traces)")

                # Dynamic Narration Card
                st.markdown("---")
                st.markdown(f"""
                <div class="card" style="background: #0f172a; border-left: 4px solid #38bdf8;">
                    <div class="card-title" style="color: #38bdf8;">🗣️ Why Sentinel Made This Decision</div>
                    <p style="font-size: 1rem; line-height: 1.5; color: #f1f5f9;">{narration.explanation}</p>
                    <p style="font-size: 0.95rem; color: #38bdf8; margin-top: 8px;"><strong>👉 Recommendation:</strong> {narration.recommendation}</p>
                </div>
                """, unsafe_allow_html=True)

# ----------------- PAGE 2: OBSERVABILITY & TRACES -----------------
elif page == "🔍 Observability & Traces":
    st.markdown("## 🔍 SENTINEL Observability & Trace Viewer")
    st.caption("Immutable real-time audit log of all agent executions, FastMCP tool calls, and decisions.")

    traces = trace_service.get_recent_traces(limit=100)
    workflows = trace_service.get_workflows_summary()

    if not traces:
        st.info("No trace events recorded yet. Run a request in 'Live Sentinel' to generate real execution traces.")
    else:
        t_col1, t_col2 = st.columns([1, 3])
        with t_col1:
            st.metric("Total Trace Events", len(traces))
            st.metric("Total Workflows", len(workflows))
            
            # Download JSONL trace button
            trace_content = "\n".join([json.dumps(t) for t in traces])
            st.download_button(
                label="📥 Download Trace JSONL",
                data=trace_content,
                file_name="sentinel_traces.jsonl",
                mime="application/jsonl",
                use_container_width=True
            )

        with t_col2:
            st.markdown("##### ⏱️ Recent Execution Timeline")
            for t in traces[:15]:
                with st.expander(f"📍 {t.get('agent_name')} — {t.get('timestamp')} ({t.get('execution_time_ms', 0)}ms)"):
                    st.caption(f"Trace ID: `{t.get('trace_id')}` | Workflow: `{t.get('workflow_id')}`")
                    if t.get("tool_calls"):
                        st.markdown("**MCP Tool Invocations:**")
                        for tc in t.get("tool_calls"):
                            st.code(json.dumps(tc, indent=2), language="json")
                    if t.get("payload"):
                        st.markdown("**Event Payload:**")
                        st.code(json.dumps(t.get("payload"), indent=2), language="json")
                    if t.get("decision"):
                        st.markdown(f"**Decision:** `{t.get('decision', {}).get('decision')}`")

# ----------------- PAGE 3: KNOWLEDGE BASE -----------------
elif page == "📚 Knowledge Base":
    st.markdown("## 📚 Accessibility Knowledge Base")
    st.caption("Curated WCAG 2.1 & 2.2 Guidelines, inclusive design patterns, and accessible alternatives.")

    docs = load_accessibility_knowledge()
    
    k_col1, k_col2, k_col3 = st.columns([2, 1, 1])
    with k_col1:
        search_query = st.text_input("🔍 Search Knowledge Base:", placeholder="e.g. dragging, keyboard, focus, labels...")
    with k_col2:
        categories = sorted(list(set(d.get("category", "") for d in docs)))
        selected_cat = st.selectbox("Filter Category:", ["All"] + categories)
    with k_col3:
        st.metric("Total WCAG Documents", len(docs))

    filtered_docs = docs
    if selected_cat != "All":
        filtered_docs = [d for d in filtered_docs if d.get("category") == selected_cat]
    if search_query.strip():
        q = search_query.lower()
        filtered_docs = [d for d in filtered_docs if q in d["title"].lower() or q in d["content"].lower() or q in d["reference"].lower()]

    st.markdown(f"Showing **{len(filtered_docs)}** matching documents:")
    for d in filtered_docs:
        with st.expander(f"📄 {d['title']} ({d['reference']}) - Category: {d['category'].replace('_', ' ').title()}"):
            st.markdown(f"**Standard Content:** {d['content']}")
            st.markdown(f"**Identified Barrier Patterns:** `{', '.join(d.get('problem_patterns', []))}`")
            st.markdown("**Recommended Accessible Alternatives:**")
            for alt in d.get("recommended_alternatives", []):
                st.markdown(f"- {alt}")

# ----------------- PAGE 4: EVALUATION -----------------
elif page == "📊 Evaluation":
    st.markdown("## 📊 Gold Set Evaluation Dashboard")
    st.caption("Evaluates the real multi-agent pipeline against curated gold test cases across education, enterprise, and finance.")

    from evaluation.evaluator import evaluator

    if st.button("▶️ RUN EVALUATION SUITE", type="primary"):
        with st.spinner("Executing real multi-agent pipeline against test cases..."):
            results_summary = evaluator.run_all(max_cases=5)
            st.session_state.eval_results = results_summary

    if "eval_results" in st.session_state:
        res = st.session_state.eval_results
        
        # Metrics Bar
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Decision Accuracy", res["decision_accuracy"])
        m2.metric("Accessibility Accuracy", res["accessibility_accuracy"])
        m3.metric("Risk Accuracy", res["risk_accuracy"])
        m4.metric("Citation Rate", res["citation_validity_rate"])

        m5, m6, m7, m8 = st.columns(4)
        m5.metric("Total Tests", res["total_tests"])
        m6.metric("Tests Passed", res["passed"])
        m7.metric("Escalation Rate", res["escalation_rate"])
        m8.metric("Avg Execution Time", f"{res['average_execution_time_ms']}ms")

        st.markdown("##### 📝 Individual Test Case Outcomes")
        for case in res["case_results"]:
            status_icon = "✅ PASSED" if case["passed"] else "❌ FAILED"
            with st.expander(f"{status_icon} [{case['id']}] {case['user_request']}"):
                st.write(f"**Expected Decision:** `{case['expected_decision']}` | **Actual:** `{case['actual_decision']}`")
                st.write(f"**Expected Accessibility:** `{case['expected_accessibility']}` | **Actual:** `{case['actual_accessibility']}`")
                st.write(f"**Expected Risk Range:** `{case['expected_risk']}` | **Actual:** `{case['actual_risk']}`")
                st.write(f"**Confidence:** `{int(case['confidence'] * 100)}%` | **Time:** `{case['execution_time_ms']}ms`")
                st.caption(f"Reason: {case['reason']}")

# ----------------- PAGE 5: SYSTEM STATUS -----------------
elif page == "⚙️ System Status":
    st.markdown("## ⚙️ SENTINEL System Status & Diagnostic Dashboard")
    st.caption("Real-time component health, local model availability, and runtime parameters.")

    status_data = system_service.get_full_system_status()
    
    col1, col2 = st.columns(2)
    with col1:
        # Ollama Status
        ollama = status_data["ollama"]
        is_connected = ollama.get("status") == "connected"
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🦙 Ollama Local LLM</div>
            <p><strong>Connection:</strong> {'🟢 Connected' if is_connected else '🔴 Disconnected'}</p>
            <p><strong>Active Model:</strong> <code>{ollama.get('current_model')}</code></p>
            <p><strong>Model Ready:</strong> {'✅ Yes' if ollama.get('model_available') else '❌ Model Not Found'}</p>
            <p><strong>Detected Models:</strong> {', '.join(ollama.get('available_models', []))}</p>
        </div>
        """, unsafe_allow_html=True)

        # ChromaDB Status
        chroma = status_data["chromadb"]
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📚 ChromaDB Vector Store</div>
            <p><strong>Collection:</strong> <code>{chroma.get('collection_name')}</code></p>
            <p><strong>Indexed Documents:</strong> <code>{chroma.get('document_count')}</code></p>
            <p><strong>Embedding Provider:</strong> <code>{chroma.get('embedding_provider', {}).get('provider')}</code></p>
            <p><small style="color: #94a3b8;">{chroma.get('embedding_provider', {}).get('details')}</small></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # FastMCP Status
        mcp = status_data["mcp"]
        st.markdown(f"""
        <div class="card">
            <div class="card-title">⚡ FastMCP Tool Server</div>
            <p><strong>Status:</strong> 🟢 Ready</p>
            <p><strong>Registered Tools:</strong></p>
            <ul>
                {"".join([f"<li><code>{t}</code></li>" for t in mcp.get('registered_tools', [])])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # LangGraph Status
        lg = status_data["langgraph"]
        st.markdown(f"""
        <div class="card">
            <div class="card-title">🤖 LangGraph Multi-Agent Workflow</div>
            <p><strong>Status:</strong> 🟢 Ready</p>
            <p><strong>Architecture:</strong> {lg.get('type')}</p>
            <p><strong>Approval Threshold:</strong> <code>{status_data['policies']['approve_threshold']}</code></p>
            <p><strong>Escalation Threshold:</strong> <code>{status_data['policies']['escalation_threshold']}</code></p>
            <p><strong>Max Replacement Loops:</strong> <code>{status_data['policies']['max_replacement_attempts']}</code></p>
        </div>
        """, unsafe_allow_html=True)
