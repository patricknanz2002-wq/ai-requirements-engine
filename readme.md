## 	AI Requirements Engine



Author: Patrick Nanz

A modular semantic retrieval engine for comparing and reusing textual requirements using embedding-based similarity search.


## 1. Project Goal

This project implements the core retrieval component of a Retrieval-Augmented Generation (RAG) architecture.  
It enables semantic comparison of customer requirements to identify previously implemented similar requirements.



## 2. Architecture Overview

Requirements are stored as individual XML files (simulating ALM/PLM systems like Polarion or Doors), containing structured metadata (title, status, owner, description).
→ Document Loader  
→ SentenceTransformer Embeddings  
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
- sentence-transformers
- NumPy
- Modular src-based architecture


## 4. How to Run

Install dependencies:
pip install -r requirements.txt

Add `.xml` requirement files to:
data/raw/

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


## 5. Core Components

- embedding/ → Embedding service using SentenceTransformers
- retrieval/ → Custom in-memory vector store
- pipeline/ → Retrieval orchestration logic



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
	{
  		"status": "ready"
	}

#### Semantic Search

POST /search

Request Body:
	{
  		"query": "customer requirement text",
  		"top_k": 3
	}

Response:
	[
  		{
    			"id": "REQ-1191",
    			"similarity": 0.87,
    			"text": "To ensure a long battery life..."
  		}
	]

### Run API

Start the API server:

uvicorn src.api.main:app --reload

Open Swagger UI:
http://127.0.0.1:8000/docs



## 7. Testing

The project includes automated tests using pytest.

Run tests with:

pytest

Test coverage includes:
- API health endpoint
- embedding service behavior
- API request handling



## 8. Project Structure

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



## 9. Next Steps

- Docker containerization
- Cloud deployment
- Extension to full RAG architecture