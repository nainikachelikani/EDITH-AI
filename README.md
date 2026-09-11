# 🛡️ EDITH-AI

### **An Intelligent Accessibility & Safety Layer for AI Agents**

> **EDITH-AI supervises computer-use AI before actions are authorized — making agentic computer interaction more accessible, safer, explainable, and accountable.**

<p align="center">
  <img src="assets/edith-dashboard.jpeg" alt="EDITH-AI" width="900">
</p>

**Team:** Techies404  
**Hackathon Track:** **Track 02 — Assistive, Accessible & Inclusive Tech**  
**Secondary Strength:** Trustworthy, Responsible & Secure AI  
**AI Runtime:** Local Ollama  
**Orchestration:** LangGraph  
**Grounding:** ChromaDB Semantic RAG  
**Tools:** FastMCP  
**Interface:** Streamlit  
**License:** MIT

---

## 👥 Team Techies404

| Member | Roll Number |
|---|---|
| **Rohit Reddy A** | AM.SC.U4CSE24209 |
| **Nainika Chelikani** | AM.SC.U4AIE24110 |
| **Maragada Yasaswi** | AM.SC.U4CSE24235 |
| **Nekkanti Venkata Avinash Krishna** | AM.SC.U4CYS24032 |
| **Shaik Hussain Basha** | AM.SC.U4CYS24043 |
| **Rishik Kotha** | AM.SC.U4AIE24126 |

---

# 1. 🎯 Problem Statement

Computer-use AI agents can increasingly navigate software, click controls, fill forms, upload files, submit information, and perform other actions on behalf of users. The problem is that **an agent being able to perform an action does not mean the action is accessible, understandable, or safe for the person using the agent**.

Two important risks emerge:

### ♿ Accessibility risk

An agent may choose interactions that create barriers for users with visual, motor, cognitive, or other accessibility needs, such as:

- mouse-dependent interactions;
- drag-and-drop operations without an accessible alternative;
- unclear focus behavior;
- unlabeled controls;
- inaccessible form interactions; and
- other interface patterns that are difficult to operate without precise visual or pointer interaction.

### 🛡️ Safety and trust risk

An agent may also propose high-impact or difficult-to-reverse actions such as:

- deleting information;
- submitting a final application or assignment;
- sending an important message;
- modifying data; or
- confirming a consequential operation.

Users need a system that does **more than blindly execute an AI agent's plan**.

They need a supervisory layer that can understand the proposed action, inspect supporting accessibility evidence, evaluate risk and confidence, explain the decision, and involve the human whenever automation should not proceed automatically.

---

# 2. 💡 Our Solution

## What is EDITH-AI?

**EDITH-AI is a domain-independent supervisory layer for computer-use AI agents.**

It does **not** replace the underlying computer-use agent.

Instead, EDITH-AI sits between the agent and the action-execution layer:

```text
User
  │
  ▼
Computer-Use AI Agent
  │
  │  Proposed Action
  ▼
┌─────────────────────────────────────────┐
│                EDITH-AI                 │
│                                         │
│ Intent • Accessibility • Risk           │
│ RAG • Confidence • Guardrails           │
│ Human Oversight • Narration • Tracing   │
└────────────────────┬────────────────────┘
                     │
             ┌───────┼────────┐
             ▼       ▼        ▼
          APPROVE  REPLACE   BLOCK
                     │        │
                     ▼        ▼
               Better Action Human Review

                     ▲
                     │
                 ESCALATE
```

For every proposed action, EDITH-AI asks:

> **Is this interaction accessible?**  
> **Is this action sufficiently safe?**  
> **Do we have enough evidence and confidence?**  
> **Should the user be involved before anything consequential happens?**

The result is one of four transparent supervisory outcomes:

| Decision | Meaning |
|---|---|
| 🟢 **APPROVE** | The proposed action is sufficiently safe, accessible, and supported by evidence. |
| 🔄 **REPLACE** | The proposed action may create an accessibility barrier, so EDITH-AI generates a more accessible alternative and re-evaluates it. |
| 🔴 **BLOCK** | The action is too high-impact or otherwise violates a safety guardrail for automatic authorization. |
| 🟠 **ESCALATE** | Evidence or confidence is insufficient; the system requires human review rather than guessing. |

---

# 3. ⭐ What Makes EDITH-AI Different?

### 1. Accessibility is part of the control loop

Accessibility is not treated as an afterthought or a static website audit.

EDITH-AI evaluates the **actual proposed action** an AI wants to perform and uses retrieved accessibility evidence to determine whether a safer or more accessible interaction should be used.

### 2. Safety is action-aware

Risk is evaluated using factors such as:

- potential impact;
- reversibility;
- data sensitivity;
- consequence of failure;
- applicable safety policies; and
- uncertainty.

High-impact actions can require explicit human authorization.

### 3. Decisions are grounded rather than invented

Accessibility decisions are grounded in a local semantic knowledge base rather than relying only on an LLM's memory.

The system retrieves relevant evidence and surfaces the associated accessibility reference.

### 4. Uncertainty is a first-class state

When evidence is weak, the action is ambiguous, or confidence is insufficient, EDITH-AI does not pretend to know the answer.

It **ESCALATES**.

### 5. The system is auditable

Agent steps, tool calls, retrieved evidence, confidence, decisions, and human interventions are recorded in structured execution traces.

---

# 4. 🏗️ System Architecture

```text
                           USER REQUEST
                                │
                                ▼
                       ┌─────────────────┐
                       │  INTENT AGENT   │
                       │     Ollama      │
                       └────────┬────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   ACTION PLANNER      │
                    │      Ollama            │
                    └───────────┬────────────┘
                                │
                         Proposed Actions
                                │
                                ▼
                 ┌─────────────────────────────┐
                 │  FOR EACH PROPOSED ACTION   │
                 └──────────────┬──────────────┘
                                │
                                ▼
                  ┌────────────────────────┐
                  │  RAG / MCP RETRIEVAL   │
                  │      ChromaDB          │
                  └────────────┬───────────┘
                               │
                               ▼
                ┌──────────────────────────────┐
                │   ACCESSIBILITY AGENT         │
                │   Evidence + Barrier Analysis│
                └─────────────┬────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │       RISK AGENT             │
                │ Impact + Reversibility +     │
                │ Safety Policy Analysis       │
                └─────────────┬────────────────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │     CONFIDENCE ENGINE        │
                │ RAG + Evidence + Agent       │
                │ Certainty + Schema Validity  │
                └─────────────┬────────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │     DECISION AGENT      │
                 └────────────┬────────────┘
                              │
              ┌───────────────┼─────────────────┐
              ▼               ▼                 ▼
          APPROVE          REPLACE             BLOCK
              │               │                 │
              │               ▼                 ▼
              │       Generate Alternative   Human Review /
              │               │               Authorization
              │               ▼
              │         Re-evaluate
              │
              └───────────────┬─────────────────┐
                              │                 │
                              ▼                 ▼
                         ESCALATE           NARRATOR
                              │                 │
                              ▼                 ▼
                         HUMAN REVIEW       Explanation
                                                │
                                                ▼
                                         TRACE LOGGER
```

The workflow is implemented as a **real LangGraph StateGraph with state handoffs and conditional routing**, rather than a single prompt that attempts to perform every responsibility.

---

# 5. 🤖 Multi-Agent Architecture

EDITH-AI separates responsibilities into cooperating nodes.

### 🧠 Intent Agent

Converts the user's natural-language request into a structured goal, domain, and constraints.

**Input:** user request  
**Output:** structured intent

### 📋 Action Planner Agent

Breaks the goal into granular proposed computer actions.

**Input:** structured intent  
**Output:** structured action plan

### ♿ Accessibility Agent

Examines the proposed interaction using retrieved accessibility evidence and determines whether the action could create an accessibility barrier.

**Input:** proposed action + retrieved evidence  
**Output:** accessibility status, issue, citations, alternative, confidence

### 🛡️ Risk Agent

Analyzes impact, reversibility, consequences, data sensitivity, and applicable safety policies.

**Input:** structured action + policy context  
**Output:** risk level, impact, reversibility, confirmation requirement, confidence

### 📊 Confidence Agent

Computes a normalized multi-factor confidence score using independently derived signals such as retrieval relevance, evidence coverage, agent certainty, and schema validity.

**Output:** confidence score + factor breakdown

### ⚖️ Decision Agent

Combines accessibility, risk, confidence, and configurable policies to select:

`APPROVE` · `REPLACE` · `BLOCK` · `ESCALATE`

### 🗣️ Narrator Agent

Converts the technical outcome into concise, user-friendly language explaining:

- what the agent wanted to do;
- what EDITH-AI found;
- why the decision was made; and
- what will happen next.

---

# 6. 🔄 Dynamic Replacement Loop

One of EDITH-AI's defining behaviors is the **REPLACE** path.

Instead of simply rejecting an inaccessible interaction:

```text
Proposed Action
      │
      ▼
Accessibility Barrier
      │
      ▼
Retrieve Evidence
      │
      ▼
Generate Accessible Alternative
      │
      ▼
New Proposed Action
      │
      ▼
Re-evaluate
      │
      ├──► APPROVE
      └──► ESCALATE
```

Example:

```text
Original:
Drag an assignment into a new position

             ↓

Accessibility analysis:
Potential pointer-dependent interaction

             ↓

Retrieved evidence:
Relevant WCAG / accessibility guidance

             ↓

Alternative:
Keyboard-accessible move controls

             ↓

Re-evaluate alternative

             ↓

APPROVE or ESCALATE
```

Replacement attempts are bounded by configuration to prevent infinite loops.

---

# 7. 📚 Grounded RAG with ChromaDB

EDITH-AI uses a persistent local **ChromaDB** vector store containing curated accessibility knowledge.

The knowledge base includes topics such as:

- **WCAG 2.1.1 — Keyboard**
- **WCAG 2.4.3 — Focus Order**
- **WCAG 2.4.7 — Focus Visible**
- **WCAG 2.5.7 — Dragging Movements**
- **WCAG 2.5.8 — Target Size**
- **WCAG 3.3.2 — Labels or Instructions**
- **WCAG 3.3.4 — Error Prevention**
- **WCAG 4.1.2 — Name, Role, Value**
- drag-and-drop accessibility patterns;
- mouse-dependent interaction patterns;
- unlabeled/icon-only controls;
- form accessibility;
- focus management;
- timing-related interactions; and
- accessible alternatives.

### RAG pipeline

```text
Proposed Action
      │
      ▼
Semantic Query
      │
      ▼
Local Embedding
      │
      ▼
ChromaDB
      │
      ▼
Relevant Documents
      │
      ▼
Accessibility Agent
      │
      ▼
Decision + Citation
```

Each retrieved result contains structured metadata including:

- document ID;
- title;
- accessibility reference;
- category;
- content;
- relevance score; and
- recommended alternative.

### Why RAG?

Instead of:

> "The model thinks this looks inaccessible."

EDITH-AI can provide:

> "This action was flagged based on retrieved accessibility guidance, including the relevant reference and supporting evidence."

This makes the system more **grounded, explainable, and auditable**.

---

# 8. 🔧 FastMCP Tool Use

EDITH-AI uses **FastMCP** to expose real tools used by the supervisory workflow.

Core tools include:

| Tool | Purpose |
|---|---|
| `retrieve_accessibility_guidance` | Performs semantic retrieval from ChromaDB and returns ranked evidence. |
| `get_safety_policy` | Retrieves applicable safety-policy information for a structured action. |
| `log_sentinel_event` | Records structured audit information into the execution trace. |
| `analyze_action_context` | Extracts structured context used for downstream accessibility/risk analysis. |

The tool layer is designed so the agent workflow receives **real tool outputs**, not prewritten demo results.

Tool execution records include:

- tool name;
- input;
- output summary;
- status; and
- execution time.

---

# 9. 🧮 Dynamic Confidence Scoring

Confidence is not a hardcoded value and is not randomly generated.

EDITH-AI derives a normalized confidence score from multiple evidence signals.

Conceptually:

```text
Overall Confidence
        =
Weighted combination of:

• RAG relevance
• Accessibility-agent certainty
• Risk-agent certainty
• Schema validity
• Evidence coverage
```

The weights are configurable rather than buried inside agent prompts.

A typical configuration can include:

```yaml
confidence_weights:
  rag_relevance: 0.25
  accessibility: 0.25
  risk: 0.20
  schema_validity: 0.15
  evidence_coverage: 0.15
```

This gives the system an explicit answer to:

> **"How sure are we, and why?"**

---

# 10. 🛡️ Guardrails & Safety Policy Engine

Safety policies are represented as configurable data rather than scattered keyword-based conditions.

The policy engine considers structured action properties such as:

- impact;
- reversibility;
- data sensitivity;
- potential consequence;
- confirmation requirement; and
- uncertainty.

### Decision principles

```text
HIGH / CRITICAL IMPACT
        │
        ▼
Do not automatically authorize
        │
        ▼
Human confirmation / review

LOW CONFIDENCE
        │
        ▼
ESCALATE

ACCESSIBILITY BARRIER
        │
        ▼
REPLACE with accessible alternative
        │
        ▼
Re-evaluate

Sufficient evidence + safe action
        │
        ▼
APPROVE
```

Thresholds and weights are configurable in `config/policies.yaml`.

---

# 11. 👤 Human-in-the-Loop

EDITH-AI treats human control as a safety mechanism rather than an error state.

High-impact or uncertain decisions can pause the workflow.

### Confirmation states

```text
PENDING_CONFIRMATION
        │
        ├── CONFIRM ──► HUMAN_AUTHORIZED
        │
        ├── CANCEL  ──► ACTION_CANCELLED
        │
        └── OVERRIDE ─► HUMAN_OVERRIDE
```

The user's decision is recorded in the audit trace.

The UI clearly distinguishes:

- **ACTION AUTHORIZED**
- **ACTION CANCELLED**
- **ACTION REQUIRES HUMAN REVIEW**

EDITH-AI only claims an external action was executed when a real execution layer is actually connected. In the demonstration environment, it acts as the **authorization and supervision layer**.

---

# 12. 🔍 Observability & Auditability

Every important workflow step generates a structured trace.

The JSONL trace records information such as:

```json
{
  "trace_id": "uuid",
  "workflow_id": "uuid",
  "timestamp": "ISO-8601",
  "agent_name": "Accessibility Agent",
  "input_summary": "Proposed interaction",
  "output_summary": "Accessibility analysis",
  "tool_calls": [],
  "retrieved_documents": [],
  "confidence": 0.87,
  "risk": "MEDIUM",
  "decision": "REPLACE",
  "execution_time_ms": 42
}
```

This enables judges and developers to inspect:

- what happened;
- which agent acted;
- which tools were called;
- what evidence was retrieved;
- why the system made a decision;
- how confident it was; and
- when a human intervened.

---

# 13. 🧪 Evaluation

EDITH-AI includes a gold-set evaluation suite with diverse requests covering:

- accessible actions;
- accessibility barriers;
- high-impact actions;
- ambiguous requests;
- form interactions;
- drag/reorder interactions;
- destructive actions; and
- multiple application domains.

The evaluation framework measures:

### Decision Accuracy
How often EDITH-AI selects the expected supervisory outcome.

### Accessibility Classification Accuracy
How accurately it identifies accessibility barriers.

### Risk Classification Accuracy
How accurately it identifies the risk category.

### Citation Validity Rate
How often replacement/accessibility decisions are supported by valid retrieved evidence.

### Escalation Rate
How often uncertain actions are correctly routed to human review.

### Execution Time
How efficiently the workflow completes.

The evaluation is designed to run through the **actual EDITH-AI pipeline**, rather than comparing static responses.

---

# 14. 🔐 Security & Privacy

EDITH-AI follows a **local-first architecture**.

### Local AI

LLM reasoning runs through:

**Ollama**

The system does not require an OpenAI, Anthropic, Gemini, or other cloud LLM API.

### Data handling

The repository should contain:

- no API keys;
- no passwords;
- no real payment credentials;
- no real user data; and
- no sensitive personal information.

The demo uses synthetic/local data.

### Why local-first matters

For an accessibility and safety supervisor, keeping reasoning local can reduce unnecessary exposure of user actions and sensitive context to external model providers.

---

# 15. 🖥️ Application Interface

EDITH-AI provides a Streamlit dashboard designed around the supervisor's decision process.

## Live Sentinel

The primary interface shows:

1. User request
2. Detected intent
3. Proposed action plan
4. Agent execution pipeline
5. RAG evidence
6. Accessibility analysis
7. Risk analysis
8. Confidence factors
9. Final decision
10. Human confirmation when required
11. Dynamic narration

## Observability

Shows:

- workflow timeline;
- agents;
- MCP tool calls;
- retrieved evidence;
- confidence;
- decisions;
- execution timing; and
- trace downloads.

## Knowledge Base

Shows the indexed accessibility knowledge and its references.

## System Status

Shows the health of:

- Ollama;
- selected LLM;
- embedding provider;
- ChromaDB;
- FastMCP; and
- knowledge-base indexing.

---

# 16. 🧩 Technology Stack

| Layer | Technology | Role |
|---|---|---|
| Local LLM | **Ollama** | Local reasoning and natural-language generation |
| Agent Orchestration | **LangGraph** | Stateful multi-agent workflow and conditional routing |
| Vector Database | **ChromaDB** | Semantic accessibility knowledge retrieval |
| Embeddings | **Local embedding provider** | Converts queries/documents for semantic search |
| Tool Protocol | **FastMCP** | Real callable tools for retrieval, policies, and tracing |
| Data Validation | **Pydantic** | Validated structured agent outputs |
| Configuration | **YAML / Environment Variables** | Thresholds, weights, models, paths |
| UI | **Streamlit** | Interactive demonstration dashboard |
| Tracing | **JSONL** | Auditable execution records |
| Evaluation | **Python evaluation suite** | Gold-set testing and metrics |

---

# 17. 📁 Project Structure

```text
edith-ai/
│
├── app.py
├── demo.py
├── requirements.txt
├── README.md
├── .env.example
├── pyproject.toml
│
├── agents/
│   ├── intent_agent.py
│   ├── action_planner.py
│   ├── accessibility_agent.py
│   ├── risk_agent.py
│   ├── confidence_agent.py
│   ├── decision_agent.py
│   └── narrator_agent.py
│
├── graph/
│   └── sentinel_graph.py
│
├── rag/
│   ├── embeddings.py
│   ├── knowledge_loader.py
│   ├── vector_store.py
│   └── retriever.py
│
├── mcp/
│   ├── server.py
│   └── tools.py
│
├── safety/
│   ├── policy_engine.py
│   └── guardrails.py
│
├── services/
│   ├── ollama_service.py
│   ├── trace_service.py
│   └── system_service.py
│
├── models/
│   ├── schemas.py
│   └── state.py
│
├── config/
│   ├── settings.yaml
│   ├── policies.yaml
│   └── settings.py
│
├── data/
│   ├── accessibility_knowledge.json
│   └── safety_policy.json
│
├── evaluation/
│   ├── gold_set.json
│   └── evaluator.py
│
├── storage/
│   ├── chroma/
│   └── traces/
│
└── tests/
    ├── test_rag.py
    ├── test_agents.py
    ├── test_tools.py
    └── test_graph.py
```

---

# 18. 🚀 Quick Start

## Prerequisites

- Python 3.10+
- Ollama
- A locally installed Ollama LLM
- A local embedding model/provider compatible with the configured RAG setup

### Recommended local model configuration

```env
OLLAMA_MODEL=llama3.2:latest
OLLAMA_BASE_URL=http://localhost:11434
```

The actual model is configurable and should match an installed local model.

---

## 1. Create and activate a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Verify Ollama

```bash
ollama list
```

Then verify the configured model is available:

```bash
ollama run llama3.2:latest
```

---

## 4. Run the smoke test

The smoke test validates the core backend before relying on the dashboard:

```bash
python demo.py
```

A successful run should show the real flow:

```text
User Request
      ↓
Intent
      ↓
Action Plan
      ↓
RAG Retrieval
      ↓
Accessibility Analysis
      ↓
Risk Analysis
      ↓
Confidence
      ↓
Decision
      ↓
Narration
      ↓
Trace
```

---

## 5. Run tests

```bash
python -m pytest tests/ -v
```

---

## 6. Launch EDITH-AI

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

# 19. 🎬 Demonstration Scenarios

The demonstration uses an education-oriented workflow while keeping EDITH-AI itself domain-independent.

### Scenario A — Accessible Action

**User request:**

> "Open my course syllabus and read the lecture schedule."

Expected supervisory behavior:

```text
Intent understood
       ↓
Action planned
       ↓
Accessibility analysis
       ↓
Risk analysis
       ↓
Sufficient confidence
       ↓
APPROVE
```

---

### Scenario B — Accessibility Barrier

**User request:**

> "Rearrange my uploaded assignment files by dragging them."

Expected behavior:

```text
Action proposed
       ↓
Semantic accessibility retrieval
       ↓
Relevant accessibility evidence
       ↓
Potential dragging barrier detected
       ↓
REPLACE
       ↓
Generate accessible alternative
       ↓
Re-evaluate alternative
```

The important point is that the system **retrieves evidence and dynamically derives the alternative**, rather than using a hardcoded `"drag" → `"WCAG 2.5.7"` mapping.

---

### Scenario C — High-Impact Action

**User request:**

> "Permanently delete my semester project submission."

Expected behavior:

```text
Action proposed
       ↓
Risk analysis
       ↓
High impact / difficult to reverse
       ↓
BLOCK
       ↓
Human confirmation required
       ↓
CONFIRM / CANCEL / OVERRIDE
       ↓
Human decision recorded in trace
```

---

### Scenario D — Ambiguous Request

**User request:**

> "Do that thing on my screen."

Expected behavior:

```text
Ambiguous intent
       ↓
Weak evidence / insufficient context
       ↓
Low confidence
       ↓
ESCALATE
       ↓
Human review
```

The system does not invent an action simply to appear confident.

---

# 20. 🧠 Why This Is Agentic AI

EDITH-AI is not a chatbot with a safety prompt.

It uses a **stateful multi-agent workflow** in which specialized nodes:

- understand goals;
- plan actions;
- retrieve external knowledge through tools;
- analyze accessibility;
- analyze safety;
- calculate confidence;
- make a policy-aware decision;
- request human intervention when necessary;
- narrate the result; and
- record the complete execution trace.

This separation of responsibilities makes the supervisory process observable, testable, and extensible.

---

# 21. 🏆 Hackathon Requirement Mapping

| Hackathon Requirement | EDITH-AI Implementation |
|---|---|
| **Multi-Agent Orchestration** | Real LangGraph StateGraph with specialized agent nodes and conditional routing |
| **Tool Use / MCP** | FastMCP tools for retrieval, policy access, context analysis, and trace logging |
| **RAG Grounding** | ChromaDB semantic retrieval over curated accessibility knowledge |
| **Confidence & Guardrails** | Multi-factor confidence + configurable safety policies and thresholds |
| **Escalation / Resilience** | Low-confidence and uncertain actions are routed to human review |
| **Observability** | Structured JSONL workflow traces with agent/tool/decision details |
| **Evaluation** | Gold-set evaluation for decisions, accessibility, risk, citations, escalation, and timing |
| **Security & Data Care** | Local Ollama architecture and synthetic demo data; no secrets in the repository |

---

# 22. 🌍 Domain Independence

Although the primary demonstration is an education workflow, EDITH-AI is intentionally designed as a reusable supervisory layer.

Potential application domains include:

```text
Education
   │
Healthcare
   │
Government Services
   │
Enterprise Software
   │
Financial Workflows
   │
E-Commerce
   │
Accessibility-Focused Applications
```

The domain is not the product.

**The supervisory capability is the product.**

---

# 23. 🔬 Design Principles

### Evidence before confidence

When useful evidence exists, retrieve it and expose it.

### Uncertainty is safer than guessing

Low confidence should lead to escalation rather than fabricated certainty.

### Human control for consequential actions

High-impact operations should not receive silent automatic authorization.

### Accessibility at action time

Evaluate the interaction the agent actually proposes, not merely the website in isolation.

### Configuration over hidden rules

Safety thresholds, confidence weights, and policies should be visible and adjustable.

### Auditability by default

Every meaningful decision should be traceable.

### Local-first AI

Use local model inference wherever practical for privacy, controllability, and predictable deployment.

---

# 24. 📈 Future Extensions

The MVP establishes the supervisory architecture. Future versions can add:

- direct integration with browser/computer-use agents;
- richer accessibility-tree analysis;
- voice input and speech narration;
- additional assistive interaction modalities;
- larger accessibility knowledge bases;
- domain-specific policy packs;
- richer execution simulators;
- stronger automated safety evaluation;
- accessibility-personalization profiles; and
- enterprise deployment and governance controls.

---

# 25. 👨‍💻 Team Techies404

Built with focus on **accessible AI, responsible autonomy, and meaningful human control**.

### Product

# **EDITH-AI**

### Team

**Techies404**

- **Rohit Reddy A** — AM.SC.U4CSE24209
- **Nainika Chelikani** — AM.SC.U4AIE24110
- **Maragada Yasaswi** — AM.SC.U4CSE24235
- **Nekkanti Venkata Avinash Krishna** — AM.SC.U4CYS24032
- **Shaik Hussain Basha** — AM.SC.U4CYS24043
- **Rishik Kotha** — AM.SC.U4AIE24126

---

## 🔗 Project Links

**Public GitHub Repository:**  
`https://github.com/nainikachelikani/EDITH-AI`

**Demo Video:**  
`https://youtu.be/CWumCDVMr7w`

---

## ✅ Final Project Summary

> **EDITH-AI is an intelligent, local-first supervisory layer for computer-use AI agents. It uses LangGraph multi-agent orchestration, Ollama local reasoning, ChromaDB semantic RAG, FastMCP tools, configurable safety policies, multi-factor confidence, and human-in-the-loop controls to evaluate proposed actions before authorization. EDITH-AI can approve safe actions, replace inaccessible interactions with accessible alternatives, block high-impact operations, and escalate uncertain decisions for human review—while maintaining an auditable trace of the entire process.**

---

**Track 02 — Assistive, Accessible & Inclusive Tech**  
**Techies404 · EDITH-AI**
