# Personal Productivity & IT Ops AI Assistant (`personal_productiv_and_it_ops_assistant`)

An autonomous CLI-based AI Agent built with Python and the **Google GenAI SDK (`google-genai`)**. Designed for **IT Operations (ITOps) and NOC environments**, this agent translates natural language instructions into deterministic, multi-step infrastructure workflows using **Function Calling (Tool Use)** and **ReAct** reasoning.

---

## Key Features

* **Autonomous Tool Orchestration:** Parses complex natural language prompts, breaks them down into logical steps, and dynamically invokes the required Python functions (server health checks, ticketing, file generation).
* **Deterministic SLA & Threshold Guardrails:** Evaluates live infrastructure metrics against strict business rules (e.g., triggering a `HIGH` priority ticket *only* if CPU usage exceeds `80%`), eliminating alert fatigue and false positives.
* **Zero-Hallucination Edge-Case Handling:** Safely handles missing or unconfigured infrastructure nodes (e.g., returning a clear `Not found` status rather than fabricating metrics).
* **Automated NOC Reporting:** Compiles audit findings, resource metrics, and ticket outcomes into a clean, structured Markdown report (`server_health_report.md`) saved directly to the workspace.

---

## How It Works (Architecture)

The agent operates on an iterative **Reason + Act (ReAct)** loop powered by Gemini:

1. **User Input:** The user enters a natural language command in the terminal.
2. **Intent & Tool Selection:** Gemini analyzes the prompt alongside the Python tool definitions registered in `main.py` and decides which functions to call and with what arguments.
3. **Local Execution:** The Python runtime executes the requested functions (e.g., querying server telemetry) and returns structured outputs back to the model.
4. **Decision & Action:** Based on the returned data and prompt conditions, Gemini evaluates thresholds, decides whether to escalate (open a ticket), and calls the reporting tool to persist the summary.

```text
[User Prompt] ──▶ [Gemini Model (google-genai)] ──▶ [Tool Call: check_server()]
                         ▲                                     │
                         └──────── [Telemetry Result] ─────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         ▼ (If CPU > 80%)                ▼ (Always)
             [Tool Call: create_ticket()]    [Tool Call: save_report()]
                                                         │
                                                         ▼
                                            [server_health_report.md]
```

---

## Example Usage & Output

### Terminal Interaction

```text
You: Check prod-db-01 and backup-node. If any server has CPU over 80%, open a HIGH priority ticket and save a report

Bot: ### Workflow Summary
1. **Server Health Checks:**
   - **`prod-db-01`**:
     - **Status:** ONLINE
     - **CPU Usage:** 78%
     - **Memory Usage:** 64%
   - **`backup-node`**:
     - **Status:** Not found (Server `'backup-node'` not found in tracking system)

2. **Threshold Evaluation & Ticket Creation:**
   - **Condition:** CPU > 80%
   - **Outcome:** `prod-db-01` is operating at 78% CPU, which is below the 80% threshold. Therefore, no `HIGH` priority ticket was generated.

3. **Report Generation:**
   - Saved report to: `server_health_report.md` documenting server statuses, resource metrics, and findings.
```

### What Happened Under the Hood:
1. **Multi-Target Tool Use:** The agent identified two distinct targets (`prod-db-01` and `backup-node`) and executed health checks for both.
2. **Smart Filtering:** Because `prod-db-01` was at `78%` CPU (`<= 80%`), the agent respected the SLA threshold and avoided creating unnecessary ticket noise.
3. **Safe Error Handling:** It accurately logged that `backup-node` does not exist in the tracking system without hallucinating data.
4. **Artifact Creation:** It automatically generated `server_health_report.md` in the local directory.

---

## Tech Stack

* **Language:** Python 3.10+
* **AI SDK:** `google-genai` (Gemini API with Function Calling)
* **Architecture:** Agentic Workflow / Tool Use / CLI

---

## Getting Started

### 1. Prerequisites
* Python 3.10 or higher
* A valid **Gemini API Key** from [Google AI Studio](https://google.com)

### 2. Installation

Clone the repository and install the official Google GenAI SDK:

```bash
git clone https://github.com
cd personal_productiv_and_it_ops_assistant
pip install google-genai
```

### 3. Configuration

Set your Gemini API key as an environment variable:

**Linux / macOS:**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**
```powershell
\$env:GEMINI_API_KEY="your_api_key_here"
```

### 4. Run the Assistant

```bash
python main.py
```

---

## Roadmap & Future Improvements

* [ ] **Human-in-the-Loop (HITL):** Add CLI confirmation prompts before executing high-impact actions (e.g., `HIGH` priority ticket creation or service restarts).
* [ ] **Live Infrastructure Integration:** Connect tools to real monitoring APIs (Prometheus, Zabbix, AWS CloudWatch) and ticketing systems (Jira, ServiceNow).
* [ ] **Node Discovery Tool:** Add a `list_servers()` tool so the agent can suggest valid hostnames when a typo or unknown node is queried.
