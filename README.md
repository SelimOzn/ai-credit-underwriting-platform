# AI Credit Underwriting Multi-Agent Platform

An advanced, production-ready Credit Underwriting Platform powered by Generative AI and multi-agent orchestration. This system evaluates loan applications autonomously using local LLMs, incorporates a Human-in-the-Loop (HITL) mechanism for manual reviews, and provides full observability and state persistence.

## Features

*   **Multi-Agent Orchestration:** Utilizes LangGraph to coordinate multiple AI agents (Data Collector, Financial Analyst, Risk Analyst, Policy Agent, Supervisor, and Explainability) to make robust credit decisions.
*   **Human-in-the-Loop (HITL):** Applications requiring manual intervention are paused and queued. Human agents can review and resolve them via the Streamlit UI, allowing the AI workflow to gracefully resume.
*   **State Persistence:** Powered by `AsyncSqliteSaver`, ensuring zero data loss and persistent memory for the AI graph across server restarts.
*   **Full Observability:** Integrated with LangSmith for tracing, debugging, and monitoring LLM token usage and latency.
*   **Containerized Architecture:** Fully containerized using Docker & Docker Compose, including a dedicated local Ollama service with GPU support.
*   **Comprehensive Dashboards:** Streamlit frontend includes a Loan Application Form, History Dashboard, Human Review Queue, and an Executive Dashboard for analytics.

## Architecture

The platform is divided into three main microservices:
1.  **Frontend (`credit_ai_frontend`):** A Streamlit application running on port `8501`.
2.  **Backend (`credit_ai_backend`):** An asynchronous FastAPI server running on port `8000`. Handles API requests, database updates, and LangGraph workflow execution.
3.  **Local LLM (`ollama_service`):** An Ollama container running on port `11434` providing local inference via GPU.

## Prerequisites

*   **Docker & Docker Compose** installed.
*   **NVIDIA GPU** with container toolkit configured (required for Ollama GPU acceleration).
*   **Python 3.12+** (if running locally without Docker).

## Setup & Installation

**1. Clone the repository and navigate to the root directory:**
```bash
git clone <your-repository-url>
cd ai-credit-underwriting-platform
```
**2. Configure Environment Variables:**

Create a `.env` file in the root directory for LangSmith observability:
```dotenv
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://eu.api.smith.langchain.com"
LANGCHAIN_API_KEY="your_langsmith_api_key_here"
LANGCHAIN_PROJECT="Credit-Underwriting-Prod"
```
**3. Run the application via Docker Compose:**

```bash
docker-compose up --build -d
```
*Note: This will download the necessary Ollama models, build the Python images, and bind the volumes for data persistence.*

## Usage
Once the containers are up and running, you can access the following services:
* **Frontend UI:** `http://localhost:8501`
  * *New Application: Submit new loan applications to the AI workflow.*
  * *Human Review Queue: Approve or reject paused applications.*
  * *Executive Dashboard: View risk score distributions and approval rates.*
* **Backend API Documentation:** `http://localhost:8000/docs`

## Testing
The project includes a robust testing infrastructure using `pytest` and `unittest.mock` 
to simulate database operations and LLM inferences without executing real network calls.

To run the test suite:
```bash
  # If running locally (make sure to install requirements first)
pytest tests/ -v
```
**Test Coverage Includes:**
* **API Tests:** Endpoint validation, JSON payload parsing, and HTTP response codes (`tests/test_api.py`).
* **Agent Tests:** Verifying individual agent behaviors and outputs (`tests/test_agents.py`).
* **Graph Tests:** Validating the LangGraph edge/node transitions (`tests/test_graph.py`).
* **Financial Tools:** Verifying DTI, LTI, and risk score calculations (`tests/test_financial.py`).

## Directory Structure
```plaintext
ai-credit-underwriting-platform/
├── app/                      # FastAPI Backend & LangGraph Logic
│   ├── agents/               # AI Agent Definitions
│   ├── graph/                # LangGraph Workflow Builder
│   ├── models/               # Pydantic Models & State Schemas
│   ├── services/             # Database & External Integrations
│   └── tools/                # Financial Calculation Tools
├── data/                     # SQLite Databases (checkpoints.db, application.db)
├── tests/                    # Pytest Suite
├── ui/                       # Streamlit Frontend UI
├── .env                      # Environment Variables
├── docker-compose.yml        # Docker Services Configuration
├── Dockerfile.backend        # Backend Image Definition
├── Dockerfile.frontend       # Frontend Image Definition
└── requirements.txt          # Python Dependencies
```

## MLOps & Observability
This project utilizes LangSmith for MLOps. Ensure your `.env` is correctly configured. As applications are evaluated, you can monitor:
* Agent traces and decision pathways.
* Latency for individual graph nodes.
* Token usage and LLM costs.
* System inputs and outputs per state transition.
