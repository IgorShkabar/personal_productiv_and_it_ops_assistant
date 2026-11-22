# personal_productiv_and_it_ops_assistant

A chatbot: Theme: Personal `Productivity and IT Operations Assistant`.

## Project Structure

```text
hybrid_assistant_for_noc_dev_ops/
├── app/
│   ├── core/
│   │   └── config.py           # Environment configuration (Pydantic Settings)
│   ├── schemas/
│   │   └── incident.py         # Strict JSON output contract (IncidentReport)
│   ├── services/
│   │   ├── scrubber.py         # Zero-Trust IP & secret masking / unmasking
│   │   ├── finops_tracker.py   # Normalized Redis caching & token cost tracking
│   │   ├── rag_engine.py       # Qdrant vector search over SOP runbooks
│   │   ├── llm_router.py       # Hybrid Cloud / Local / Mock inference router
│   │   └── idempotency.py      # Atomic Redis lock & duplicate prevention for /create-ticket
│   ├── main.py                 # FastAPI backend (/analyze & /create-ticket)
│   └── ui.py                   # Streamlit operator & telemetry dashboard
├── evals/
│   ├── test_cases.json         # Security, RAG & severity test scenarios
│   └── run_eval.py             # Automated regression & idempotency test runner
├── knowledge_base/
│   ├── nginx_502_runbook.md
│   └── k8s_oomkilled_runbook.md
├── docker-compose.yml          # Qdrant & Redis infrastructure
├── requirements.txt
└── README.md

```

## Architecture & Pipeline

```text
Raw Incident Log
   │
   ▼
[1. Zero-Trust Scrubber] ──► Masks internal IPs, tokens & passwords ([REDACTED_IP_1])
   │
   ▼
[2. FinOps Redis Cache]  ──► Normalizes timestamp/PID & checks SHA-256 hash (\$0.00 hit)
   │ (cache miss)
   ▼
[3. Qdrant Vector RAG]   ──► Retrieves grounded SOP runbook from knowledge_base/
   │
   ▼
[4. Hybrid LLM Router]   ──► Routes to Cloud (OpenAI), Local (Ollama), or Mock (Pydantic JSON)
   │
   ▼
[5. In-Memory Unmasking] ──► Restores real IPs into diagnostic CLI command in RAM
   │
   ▼
[6. Idempotent Tool API] ──► POST /create-ticket (app/services/idempotency.py)
                             Uses Redis atomic lock (SET NX) to block duplicate tickets
```

## Live Demo Preview

### 1. Zero-Trust PII & Secret Masking + Grounded RAG
![Security Scrubber and RAG](docs/01_full_pipeline_cache_miss.png)

### 2. FinOps Redis Cache Hit ($0.00 Latency & Cost)
![FinOps Cache Hit](docs/02_finops_cache_hit.png)


## Key Engineering Features

* **Zero-Trust Data Scrubber (`app/services/scrubber.py`):** Regex-based middleware intercepts sensitive infrastructure data (IPv4, API keys, passwords) *before* leaving the perimeter, restoring placeholders only in memory for the final operator output.
* **Hybrid Inference Router (`app/services/llm_router.py`):** Strategy-pattern router allowing instant switching between cloud APIs, local on-premise models, and offline simulation mode without changing business logic.
* **Grounded RAG (`app/services/rag_engine.py`):** Uses **Qdrant** to ground LLM responses in internal Markdown runbooks, eliminating hallucinations and enforcing strict JSON schemas via **Pydantic**.
* **FinOps Telemetry & Caching (`app/services/finops_tracker.py`):** Tracks token usage, estimates USD cost per incident, and caches recurring alert storms in **Redis**.
* **Automated Evals (`evals/run_eval.py`):** Regression test suite verifying zero secret leakage and retrieval accuracy.

## Quick Start (Local Setup)

### 1. Start Infrastructure (Qdrant & Redis)
```bash
docker compose up -d
```

### 2. Install Python Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Run Backend & Demo UI
Open two terminal tabs:
```bash
# Terminal 1: FastAPI Backend
uvicorn app.main:app --reload

# Terminal 2: Streamlit Dashboard
streamlit run app/ui.py
```

### 4. Run Automated Quality & Security Evals
```bash
python3 evals/run_eval.py
```