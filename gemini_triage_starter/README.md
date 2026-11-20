# Enterprise IT Helpdesk Triage & Auto-Lookup Agent

An AI-powered IT support triage prototype built with **LangChain**, **Google Gemini (AI Studio)**, and **FAISS**. Designed as a practical implementation of **Phases 1 & 2** of the *TCS AI Fridays Hackathon* study and rapid-prototyping roadmap, this project transforms unstructured employee support tickets into validated, policy-grounded JSON decisions.

---

## Architecture & Core Concepts

This project progresses through two foundational enterprise AI layers:

1. **Phase 1 — Structured Tool Calling (`easy_triage.py`)**
   * **Role-Bound Context:** Uses `SystemMessage` and `HumanMessage` boundaries with strict negative constraints to prevent hallucinations.
   * **Python Tool Calling (`@tool` + `.bind_tools()`):** Dynamically inspects employee IDs (e.g., `EMP-101`, `EMP-202`) against a simulated internal IT asset database (`MOCK_ASSET_DB`) to verify laptop models, VPN status, and warranty state.
   * **Constrained JSON Output (`.with_structured_output()`):** Enforces a strict Pydantic schema (`TriageDecision`) so downstream CRMs or UIs receive guaranteed structured payloads rather than free text.

2. **Phase 2 — Enterprise RAG & Grounded Citations (`rag_triage.py`)**
   * **Document Chunking:** Splits local policy documents (`it_policy.txt`) into focused, overlapping clauses via `RecursiveCharacterTextSplitter`.
   * **Local Vector Search:** Indexes policy chunks using free `GoogleGenerativeAIEmbeddings` (`models/text-embedding-004`) inside an in-memory **FAISS** vector store.
   * **Verifiable Citations:** Forces the LLM to output a `cited_policy` field mapping its priority and action plan back to the exact policy rule and source file.

---

## Project Structure

```text
gemini_triage_starter/
├── .venv/               # Isolated Python virtual environment
├── .env                 # Local API credentials (do not commit to Git)
├── setup.bat            # One-click Windows environment & dependency installer
├── run.bat              # One-click Windows execution script
├── it_policy.txt        # Synthetic enterprise IT SLA & hardware warranty policy
├── easy_triage.py       # Phase 1: Tool calling + Pydantic JSON triage agent
├── rag_triage.py        # Phase 2: FAISS RAG + tool calling + policy citations
└── README.md            # Project documentation