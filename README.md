# AI Requirements Engine

An AI system for semantic requirement retrieval using embedding-based similarity search with both in-memory and persistent vector storage options, designed as a core component of a Retrieval-Augmented Generation (RAG) pipeline.
The system indexes structured XML requirements and exposes semantic search via a REST API, a CLI demo, and a Streamlit web interface.

Author: Patrick Nanz

## Live API Demo

Public API deployment (AWS EC2 + Docker):

Swagger UI:  
http://51.20.45.195:8000/docs

Example request:

POST /analyze

```json
{
  "query": "The system shall support multi-factor authentication",
  "top_k": 3
}
```

## Contents

- [Quickstart](#quickstart)
- [Project Goal](#1-project-goal)
- [Architecture Overview](#2-architecture-overview)
- [Tech Stack](#3-tech-stack)
- [How to Run](#4-how-to-run)
- [API Layer](#5-api-layer)
- [Core Components](#6-core-components)
- [Testing](#7-testing)
- [User Interface](#8-user-interface)
- [Project Structure](#9-project-structure)
- [Evaluation](#10-evaluation)


## Quickstart

Clone the repository and install dependencies:

```bash
pip install -e .
```

(Optional) Set your OpenAI API key for LLM-based explanations:

```bash
export OPENAI_API_KEY=<your_api_key>
```

### Run CLI Demo (no setup required)

```bash
python demo.py
```

The demo runs fully in-memory and does not require Docker or a database.



## 1. Project Goal

This project implements the core retrieval component of a Retrieval-Augmented Generation (RAG) architecture.  
It enables semantic comparison of customer requirements to identify previously implemented similar requirements.



## 2. Architecture Overview

Requirements are stored as individual XML files (simulating ALM/PLM systems such as Polarion or DOORS), containing structured metadata (title, status, owner, description). The retrieval engine can be accessed through different clients, including a CLI demo and a Streamlit-based web interface, both communicating with the FastAPI service.

→ Document Loader  
→ SentenceTransformers embeddings  
→ Vector Storage (Qdrant for persistent mode, in-memory for demo)
→ Cosine Similarity Search  

```mermaid
flowchart LR

CLI["CLI Demo"]
UI["Streamlit UI"]
API["FastAPI Service"]
Embedder["Embedding Service"]
VectorDB["Qdrant Vector DB"]
LLM["LLM Explanation Service"]
Data[(XML Requirements)]
Loader["XML Document Loader"]

API -->|Startup| Data
API --> Embedder

Embedder --> VectorDB
VectorDB -->|Top-K Results| API

API -->|Optional Explanation| LLM
LLM --> API

CLI -->|CLI Query| Loader
Loader --> Embedder
Embedder --> CLIStore["In-Memory Vector Store"]
CLIStore --> CLI

API -->|Top-K Results| UI

```

For a detailed architecture overview see [docs/architecture.md](docs/architecture.md).

## 3. Tech Stack

- Python
- FastAPI
- SentenceTransformers (all-MiniLM-L6-v2)
- NumPy
- Uvicorn
- Pydantic
- Qdrant (vector database)
- REST API
- Streamlit (web UI)

## 4. How to Run

Before running the `/analyze` endpoint, configure your API key:

```bash
export OPENAI_API_KEY=<your_api_key>
```
If no API key is provided, the `/analyze` endpoint will not be available.

### Run with Docker Compose

This setup starts:
- FastAPI application
- Qdrant vector database (for persistent embedding storage)

Start the API service:
```bash 
docker compose up --build
```

The API will be available at:
http://localhost:8000/docs

Stop the service with:
```bash 
docker compose down
```

### Run CLI Demo

The CLI demo provides a simplified, self-contained version of the retrieval pipeline.

It uses:

- An in-memory vector store
- Local embedding generation
- No external services

Run the demo:

```bash
python demo.py
```

The demo will:

1. Load all XML requirements from `data/raw/`
2. Generate embeddings for the requirements
3. Store embeddings in an in-memory vector store
4. Perform semantic similarity search
5. Allow interactive queries via the command line

Notes:

- No Docker setup is required
- No Qdrant instance is needed
- The demo is intended for quick local testing and experimentation


### Run Web UI

The project also includes a Streamlit-based web interface for interacting with the API.

Start the UI:

```bash
streamlit run src/ui/app.py
```

The interface will be available at:
http://localhost:8501


## 5. API Layer

The retrieval engine is exposed via a REST API using FastAPI.

### Startup Behavior

On application startup:

- All XML requirements are loaded
- Text content is extracted
- Embeddings are generated and stored in the Qdrant vector database
- Existing embeddings are reused across restarts
- Only new requirements are embedded and indexed (incremental indexing)

### Available Endpoints

#### Health Check

GET /health

Response:
```json
{
	"status": "ready"
}
```
#### Semantic Search

POST /analyze

Request Body:
```json
{
	"query": "customer requirement text",
	"top_k": 3
}
```
Response:
```json
{
  "results": [
    {
      "id": "REQ-1191",
      "similarity": 0.87,
      "text": "To ensure a long battery life..."
    }
  ],
  "llm_explanation": "Explanation why the retrieved requirements match the query."
}
```

This endpoint returns the retrieved requirements along with an LLM-generated explanation of their semantic similarity.

### Run API

Start the API server:

```bash
uvicorn src.api.main:app --reload
```


## 6. Core Components

- embedding/ → Embedding service using SentenceTransformers
- retrieval/ → Qdrant-based vector database integration
- pipeline/ → Retrieval orchestration logic



## 7. Testing

The project includes automated tests using pytest.

Run tests with:

```bash
pytest
```

Test coverage includes:
- API health endpoint
- embedding service behavior
- API request handling


### 8. User Interface

The project includes a Streamlit-based web interface that allows users to interactively query the retrieval API.

The interface provides a simple way to enter requirement text, configure the number of returned results, and inspect semantically similar requirements identified by the embedding-based retrieval engine. 

For each retrieved requirement, the UI displays the similarity score and the original requirement text.  
The interface additionally shows an automatically generated explanation describing why the retrieved requirements are semantically related to the query.

The UI communicates with the FastAPI backend via the `/analyze` endpoint and serves as a lightweight demonstration layer for the retrieval system.


## 9. Project Structure

```
ai-requirements-engine/
│
├── demo.py               CLI demo for semantic requirement search
├── README.md
├── pyproject.toml
│
├── data/
│   └── raw/              XML requirement documents
│
├── docs/
│   └── architecture.md
│
└── src/
    ├── api/              FastAPI service layer
    ├── embedding/        Embedding generation (SentenceTransformers)
    ├── lm_output/        LLM explanation service
    ├── retrieval/        Vector store and similarity search
    ├── pipeline/         Document loading and retrieval pipeline
    ├── tests/            Automated tests
    └── ui/               Streamlit web interface
```

## 10. Evaluation

The project includes an evaluation framework for both the retrieval component and the LLM-based explanation layer.

The evaluation is designed to assess:

* Retrieval quality (semantic similarity performance)
* LLM grounding and correctness
* Overall system reliability

### Evaluation Pipeline

The evaluation pipeline consists of two stages:

1. Retrieval Evaluation
2. LLM Evaluation

It uses a predefined test set of queries with expected requirement IDs.

Run the evaluation with:

```bash
python src/evaluation/run_evaluation.py
```

---

### Test Set Definition

Test queries and expected results are defined in:

src/evaluation/test_set_definition.py

Each test case contains:

* A natural language query
* A set of expected requirement IDs

Example:

```python
{
    "query": "system protection and security mechanisms",
    "expected_ids": ["REQ-0134", "REQ-0042"]
}
```

---

### Retrieval Evaluation

The retrieval evaluation measures how well the vector search returns relevant requirements.

Implemented in:
retrieval_evaluator.py

#### Metrics

* Hit Rate @ K
  Fraction of queries where at least one correct requirement is retrieved

* Recall
  Fraction of expected requirements that were retrieved

* Precision
  Fraction of retrieved requirements that are correct

* Top-1 Accuracy
  Whether the top result is correct

* Top-K Accuracy
  Whether any result in top-K is correct

* Confidence Metrics

  * Score difference between top results
  * Retrieval confidence score
  * Score distribution analysis

#### Additional Analysis

* Identification of low-confidence queries
* Detection of unsafe retrieval cases (small score gaps)
* Extraction of cases of interest for debugging

---

### LLM Evaluation

The LLM evaluation assesses whether the generated explanations are correct and grounded in the retrieved requirements.

Implemented in:
llm_evaluator.py

#### Evaluation Dimensions

* Answer Correctness (LLM-as-a-Judge)

  * Uses a secondary LLM to verify correctness
  * Detects hallucinations and incorrect mappings

* Semantic Grounding

  * Compares explanation text to requirement text using embeddings
  * Computes a mismatch rate

* ID Consistency

  * Detects usage of invalid or hallucinated requirement IDs

* Groundness Metrics

  * Word overlap between explanations and source texts
  * Coverage of retrieved requirement IDs

#### Output

The evaluation produces:

* Accuracy statistics (correct / incorrect / unknown)
* Grounding metrics
* Invalid ID rate
* List of incorrect cases with explanations

---

### End-to-End Evaluation Flow

The full evaluation process:

1. Load XML requirements
2. Encode requirements into embeddings
3. Store embeddings in vector database
4. Execute test queries
5. Evaluate retrieval results
6. Generate LLM explanations
7. Evaluate LLM outputs

Main script:
run_evaluation.py

---

### Notes

* The LLM evaluation requires a valid OpenAI API key
* Evaluation runtime depends on the number of test queries
* LLM-based evaluation may take several minutes

