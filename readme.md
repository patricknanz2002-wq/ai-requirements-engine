# AI Requirements Engine

A prototype AI system for semantic requirement retrieval using embedding-based similarity search.
The system indexes structured XML requirements and exposes semantic search via a REST API and CLI demo.

Author: Patrick Nanz

## Contents

- [Quickstart](#quickstart)
- [Project Goal](#1-project-goal)
- [Architecture Overview](#2-architecture-overview)
- [Tech Stack](#3-tech-stack)
- [Project Variants](#4-project-variants)
- [How to Run](#5-how-to-run)
- [API Layer](#6-api-layer)
- [Core Components](#7-core-components)
- [Testing](#8-testing)
- [Project Structure](#9-project-structure)

## Quickstart

Clone the repository and install dependencies:

```bash 
pip install -e .
```
Run the interactive demo:

```bash
python demo.py
```

## 1. Project Goal

This project implements the core retrieval component of a Retrieval-Augmented Generation (RAG) architecture.  
It enables semantic comparison of customer requirements to identify previously implemented similar requirements.



## 2. Architecture Overview

Requirements are stored as individual XML files (simulating ALM/PLM systems such as Polarion or DOORS), containing structured metadata (title, status, owner, description).
→ Document Loader  
→ SentenceTransformers Embeddings  
→ In-Memory Vector Store  
→ Cosine Similarity Search  

```mermaid
flowchart LR

User[User / Client]
API[FastAPI Service]
Embedder[Embedding Service]
VectorStore[Vector Index]
Data[(XML Requirements)]

User -->|Search Request| API
API -->|Startup| Data
API --> Embedder
Embedder --> VectorStore
VectorStore -->|Top-K Results| API
API --> User
```

For a detailed architecture overview see /docs/architecture.md



## 3. Tech Stack

- Python
- FastAPI
- SentenceTransformers
- NumPy
- Uvicorn
- Pydantic
- In-memory vector similarity search
- REST API


## 4. Project Variants

The repository currently contains two variants of the system:

### main branch
Core semantic requirement retrieval engine using embedding-based similarity search.

### llm branch
Experimental extension that integrates an LLM (OpenAI GPT-4o-mini) to generate explanations for retrieved requirements.


The LLM branch requires an OpenAI API key:

```bash
export OPENAI_API_KEY=<your_api_key>
```

### API Differences

The LLM variant extends the API.

main branch:

POST /search  
Returns the most similar requirements based on embedding similarity.

llm branch:

POST /analyze  
Returns the similar requirements along with an LLM-generated explanation of why they are semantically related.

## 5. How to Run

### Run with Docker Compose

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

### Run with Docker

Build the container:
```bash
docker build -t ai-requirements-engine .
```

Run the API:
```bash 
docker run -p 8000:8000 ai-requirements-engine
```

The API will be available at:
http://localhost:8000/docs

### Run CLI Demo

You can run an interactive demo of the retrieval engine:

```bash 
python demo.py
```

The demo will:

1. Load all XML requirements from data/raw/
2. Generate embeddings for the requirements
3. Build an in-memory vector index
4. Allow interactive similarity search via the command line

### Run LLM Variant

To try the LLM-based explanation layer:

```bash
git checkout llm
pip install -e .
python demo.py
```



## 6. API Layer

The retrieval engine is exposed via a REST API using FastAPI.

### Startup Behavior

On application startup:

- All XML requirements are loaded
- Text content is extracted
- Embeddings are generated once
- An in-memory vector index is built
- Documents remain cached in RAM for fast retrieval

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

POST /search

Request Body:
```json
{
	"query": "customer requirement text",
	"top_k": 3
}
```
Response:
```json
[
	{
		"id": "REQ-1191",
		"similarity": 0.87,
		"text": "To ensure a long battery life..."
	}
]
```

Note:  
In the **llm branch** the search endpoint is extended by an additional endpoint:

POST /analyze

This endpoint returns the retrieved requirements along with an LLM-generated explanation of their semantic similarity.

### Run API

Start the API server:

uvicorn src.api.main:app --reload

Open Swagger UI:
http://localhost:8000/docs



## 7. Core Components

- embedding/ → Embedding service using SentenceTransformers
- retrieval/ → Custom in-memory vector store
- pipeline/ → Retrieval orchestration logic



## 8. Testing

The project includes automated tests using pytest.

Run tests with:

pytest

Test coverage includes:
- API health endpoint
- embedding service behavior
- API request handling



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
	├── retrieval/        Vector store and similarity search
	├── pipeline/         Document loading and retrieval pipeline
	└── tests/            Automated tests
```