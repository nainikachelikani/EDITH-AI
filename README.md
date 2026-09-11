# 🛡️ EDITH-AI
> **"An Intelligent Accessibility and Safety Layer for AI Agents"**

🏆 **Hackathon Track:** Track 02 — Assistive, Accessible & Inclusive Tech  
🔒 **Core Paradigm:** Local-First Responsible AI & Human-in-the-Loop Supervision  

---

## 📌 Problem

AI computer-use agents are increasingly capable of interacting directly with software interfaces: clicking buttons, filling forms, dragging elements, submitting assignments, sending messages, and modifying database records. However, autonomous agents suffer from two systemic failures:

1. **Accessibility Barriers:** Agents frequently execute interactions that exclude users with motor, visual, cognitive, or speech disabilities (e.g., mouse-only hover traps, drag-and-drop file reordering without keyboard equivalents, tiny touch targets, and unlabeled icon buttons).
2. **Safety & Irreversibility Risks:** Agents often carry out high-impact or permanent actions without human confirmation (e.g., permanently deleting project files, submitting final binding exams, or transmitting unauthorized broadcasts).

---

## 💡 Solution

**EDITH-AI is NOT another computer-use agent.**  
EDITH-AI is an intelligent, domain-independent supervisory layer that sits between an AI computer-use agent and the action execution layer.

Every proposed interaction is intercepted and dynamically evaluated against:
- **WCAG 2.1 & 2.2 Accessibility Guidelines** via persistent ChromaDB semantic RAG.
- **Configurable Safety Guardrails** evaluating reversibility, impact, and confirmation policies.
- **Multi-Factor Confidence Scoring** combining RAG relevance, evidence coverage, agent certainty, and schema validation.
- **Transparent Supervisory Decisions:** `APPROVE`, `REPLACE` (with dynamic accessible alternatives), `BLOCK` (mandating human confirmation), or `ESCALATE` (human review under uncertainty).

---

## 🏛️ System Architecture

```text
                                 USER REQUEST
                                      │
                                      ▼
                               [ INTENT AGENT ]
                          (Goal, Domain, Constraints)
                                      │
                                      ▼
                           [ ACTION PLANNER AGENT ]
                        (Decomposes into action steps)
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
               [ For Each Action ]           [ Next Action / Finish ]
                         │
                         ▼
              [ ACCESSIBILITY RAG RETRIEVAL ]
                (ChromaDB semantic search +
                 FastMCP retrieve_accessibility_guidance)
                         │
                         ▼
              [ ACCESSIBILITY AGENT ]
                (WCAG compliance, barrier detection,
                 accessible alternatives)
                         │
                         ▼
              [ RISK & SAFETY POLICY AGENT ]
                (Impact, reversibility, data/safety_policy.json,
                 FastMCP get_safety_policy)
                         │
                         ▼
              [ CONFIDENCE AGENT ]
                (Dynamic weighted score: RAG relevance,
                 evidence coverage, agent confidence, schema validity)
                         │
                         ▼
              [ DECISION AGENT ]
                (config/policies.yaml thresholds)
                         │
          ┌──────────────┼──────────────┬──────────────┐
          ▼              ▼              ▼              ▼
     [ APPROVE ]    [ REPLACE ]     [ BLOCK ]     [ ESCALATE ]
          │              │              │              │
          │              ▼              ▼              ▼
          │      [ REPLACEMENT LOOP ] [ HUMAN CONFIRM ] [ HUMAN REVIEW ]
          │      (Dynamic alternative)  (Wait/Resume)    (Wait/Resume)
          │              │              │              │
          └──────────────┴───────┬──────┴──────────────┘
                                 │
                                 ▼
                         [ NARRATOR AGENT ]
                     (Dynamic plain-English rationale)
                                 │
                                 ▼
                          [ TRACE LOGGER ]
                     (FastMCP log_sentinel_event ->
                      storage/traces/sentinel_traces.jsonl)
```

---

## 🤖 Multi-Agent Architecture (LangGraph)

EDITH-AI implements a real **LangGraph StateGraph** featuring 7 independent, cooperating agents:

1. **Intent Agent (`agents/intent_agent.py`):** Understands high-level user goals, application domains, and constraints using Ollama structured JSON.
2. **Action Planner Agent (`agents/action_planner.py`):** Decomposes user goals into granular computer action steps (e.g. click, navigate, upload, drag, delete).
3. **Accessibility Agent (`agents/accessibility_agent.py`):** Grounded in retrieved WCAG guidelines, detects potential accessibility barriers and devises accessible alternatives.
4. **Risk Agent (`agents/risk_agent.py`):** Evaluates operational impact, reversibility, data sensitivity, and policy rules.
5. **Confidence Agent (`agents/confidence_agent.py`):** Computes a normalized mathematical score ($0.0 - 1.0$) based on RAG relevance, agent agreement, and evidence coverage.
6. **Decision Agent (`agents/decision_agent.py`):** Applies configurable thresholds from `config/policies.yaml` to output transparent supervisory decisions.
7. **Narrator Agent (`agents/narrator_agent.py`):** Synthesizes technical findings into plain-English explanations and next steps.

---

## 📚 ChromaDB Semantic RAG

EDITH-AI's accessibility knowledge base (`data/accessibility_knowledge.json`) contains 15+ curated documents covering:
- **WCAG 2.1.1 Keyboard Accessibility** (single-pointer and keyboard operation)
- **WCAG 2.4.7 Focus Visible & 2.4.3 Focus Order** (focus styling and modal trap prevention)
- **WCAG 2.5.7 Dragging Movements** (alternatives to drag-and-drop actions)
- **WCAG 2.5.8 Target Size** (minimum 24x24px click bounding boxes)
- **WCAG 3.3.2 Labels or Instructions** (accessible names and form hints)
- **WCAG 4.1.2 Name, Role, Value** (screen reader accessibility and ARIA states)
- **WCAG 3.3.4 Error Prevention** (confirmations for legal, financial, or data-modifying actions)
- **WCAG 1.4.3 Contrast Minimum** (visual legibility)

Embeddings run locally and offline via ChromaDB with dense semantic projection, guaranteeing zero external cloud API dependencies.

---

## ⚡ FastMCP Tool Integration

EDITH-AI exposes and invokes real **FastMCP** tools (`sentinel_mcp/tools.py`):
- `retrieve_accessibility_guidance(query, top_k)`: Queries ChromaDB and returns ranked guidelines, citations, and alternatives.
- `analyze_action_context(action_type, target, description)`: Inspects interactivity modality and barrier patterns.
- `get_safety_policy(action_type, target, impact_description)`: Matches configurable policies from `data/safety_policy.json`.
- `log_sentinel_event(event_data)`: Writes structured audit records to `storage/traces/sentinel_traces.jsonl`.

Every tool call records real inputs, outputs, success status, and execution timings in milliseconds.

---

## 📊 Dynamic Confidence Calculation

Confidence is never hardcoded. It is calculated dynamically from five weighted factors configured in `config/policies.yaml`:

$$\text{Confidence} = \frac{w_1 \cdot R + w_2 \cdot A + w_3 \cdot S + w_4 \cdot V + w_5 \cdot C}{\sum w_i}$$

Where:
- $R$ = **RAG Relevance:** Highest similarity score from retrieved knowledge.
- $A$ = **Accessibility Certainty:** Self-reported certainty of the Accessibility Agent.
- $S$ = **Safety & Risk Certainty:** Self-reported certainty of the Risk Agent.
- $V$ = **Schema Validity:** Strict Pydantic output compliance ($1.0$ if valid).
- $C$ = **Evidence Coverage:** Ratio of retrieved documents exceeding the similarity threshold.

---

## 🛡️ Guardrails & Policy Engine

Policies are declared as data in `data/safety_policy.json` and thresholds in `config/policies.yaml`:
- **Approve Threshold:** $\ge 0.75$ (Action is safe and accessible)
- **Escalation Threshold:** $< 0.55$ (Uncertainty or ambiguous request $\rightarrow$ `ESCALATE`)
- **Accessibility Barrier:** Status `FRAGILE` $\rightarrow$ `REPLACE` (Re-analyzes replacement action; if max replacement attempts exceeded $\rightarrow$ `ESCALATE`)
- **Critical/High Risk:** Status `HIGH` or `CRITICAL` $\rightarrow$ `BLOCK` (Mandates human confirmation)

---

## 👤 Human-in-the-Loop Semantics

EDITH-AI enforces supervisory human-in-the-loop semantics:
- `PENDING_CONFIRMATION`: High-risk action paused awaiting sign-off.
- `HUMAN_AUTHORIZED`: User confirms action $\rightarrow$ supervisory approval granted.
- `ACTION CANCELLED`: User cancels action $\rightarrow$ execution aborted.
- `HUMAN_OVERRIDE`: User explicitly overrides safety recommendations $\rightarrow$ logged in trace.

---

## 🔍 Observability & Tracing

All agent actions, tool calls, and decisions are appended in real-time to `storage/traces/sentinel_traces.jsonl`. Each record includes:
- Unique `trace_id` and `workflow_id` (UUID)
- ISO-8601 UTC timestamp
- Agent name & execution time (ms)
- Input parameters & structured outputs
- Downloadable directly from the Streamlit UI.

---

## 🧪 Gold Set Evaluation

EDITH-AI includes an automated evaluation suite (`evaluation/gold_set.json` & `evaluation/evaluator.py`) with 16 diverse test cases covering education, enterprise, and finance domains. Evaluates:
- Decision Accuracy
- Accessibility Classification Accuracy
- Risk Classification Accuracy
- Citation Validity Rate
- Escalation Rate & Execution Time

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.10+ (Tested and verified on Python 3.14.3)
- Ollama running locally (`http://localhost:11434`) with `llama3.2:latest`

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Verify Local Ollama
```bash
ollama list
# Should display llama3.2:latest
```

### 3. Run Automated Tests
```bash
python -m pytest -v
# Verified: 16/16 tests passing!
```

### 4. Launch Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Demo Walkthrough

1. **Accessible Action:** Type `"Open my DBMS course syllabus and view the lecture schedule"` $\rightarrow$ Decision: `APPROVE`.
2. **Accessibility Barrier:** Type `"Rearrange my uploaded assignment files by dragging them into folders"` $\rightarrow$ Decision: `REPLACE` (WCAG 2.5.7, suggests keyboard-accessible reordering buttons, executes dynamic replacement loop).
3. **High-Risk Action:** Type `"Permanently delete my semester exam submission"` $\rightarrow$ Decision: `BLOCK` (Displays data loss warning and presents `CONFIRM`, `CANCEL`, and `OVERRIDE` controls).
4. **Ambiguous Request:** Type `"Do that thing on my screen"` $\rightarrow$ Decision: `ESCALATE` (Escalates to human review due to low confidence).
