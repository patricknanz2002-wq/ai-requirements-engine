########################################
##
## 	AI Requirements Engine
##
########################################


Author: Patrick Nanz

A modular semantic retrieval engine for comparing and reusing textual requirements using embedding-based similarity search.


#########################
##
## 1. Project Goal
##
#########################
This project implements the core retrieval component of a Retrieval-Augmented Generation (RAG) architecture.  
It enables semantic comparison of customer requirements to identify previously implemented similar requirements.


#########################
##
## 2. Architecture Overview
##
#########################
Requirements are stored as individual XML files (simulating ALM/PLM systems like Polarion or Doors), containing structured metadata (title, status, owner, description).
→ Document Loader  
→ SentenceTransformer Embeddings  
→ In-Memory Vector Store  
→ Cosine Similarity Search  


#########################
##
## 3. Tech Stack
##
#########################
- Python
- sentence-transformers
- NumPy
- Modular src-based architecture


#########################
##
## 4. How to Run
##
#########################
1. Install dependencies:

Bash:	pip install -r requirements.txt
Add: 	add .xml requirement files to: "data/raw/"
Run:	python -m src.pipeline.run

Enter a requirement text when prompted.


#########################
##
## 5. Core Components
##
#########################
- embedding/ → Embedding service using SentenceTransformers
- retrieval/ → Custom in-memory vector store
- pipeline/ → Retrieval orchestration logic


#########################
##
## 6. API Layer
##
#########################
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


#########################
##
## 7. Next Steps
##
#########################
- Docker containerization
- Cloud deployment
- Extension to full RAG architecture