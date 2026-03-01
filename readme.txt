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
TXT Requirements  
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
Add: 	add .txt requirement files to: "data/raw/"
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
## 6. Next Steps
##
#########################
- API Layer (FastAPI)
- Docker containerization
- Cloud deployment
- Extension to full RAG architecture