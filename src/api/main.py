import time

from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel

from embedding.embedder import RequirementsEmbedder
from lm_output.LLMService import LLMService
from pipeline.retrieval_pipeline import load_documents_recursive
from retrieval.vector_Database import DatabaseVectorStore
from compliance.disclosures import ComplianceDisclosures
from security.query_Security import SecurityLayer

app = FastAPI()


class Query(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: str
    similarity: float
    text: str


class SecurityResponse(BaseModel):
    masked: list
    blocked: bool


class AnalyzeResponse(BaseModel):
    results: list[SearchResult]
    llm_explanation: str
    compliance_message: dict
    security_response: SecurityResponse


############################################
##
## Startup
##
############################################
@app.on_event("startup")
def startup_event():

    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / "data/raw").resolve()

    app.state.embedder = RequirementsEmbedder()
    app.state.store = DatabaseVectorStore("requirements")
    app.state.security = SecurityLayer()

    # Loads .xml files from data/raw (simulates req tool api)
    documents = load_documents_recursive(target_path)

    # Check Qdrant availability qdrant_available = True
    qdrant_available = True

    # Detect new requirement files by comparing IDs with existing DB entries    
    # Only embed and store documents that are not already indexed (performance optimization)
    for i in range(30):
        try:
            database_ids = set(app.state.store.get_req_ids_of_collection())
            break
        except Exception:
            print(f"Waiting for Qdrant in startup... ({i+1}/30)")
            time.sleep(2)
    else:
        print("Qdrant not available – skipping sync")
        database_ids = set()
        qdrant_available = False

    # Detect missing documents
    missing_docs = [
        doc for doc in documents
        if doc["id"] not in database_ids
    ]

    if missing_docs and qdrant_available: 
        print("[✓] Creating embeddings...") 
        ids = [doc["id"] for doc in missing_docs] 
        texts = [doc["text"] for doc in missing_docs] 
        
        vectorized_texts = app.state.embedder.encode(texts) 
        app.state.store.add(ids,texts,vectorized_texts)

    # Initialize LLM service if API key is configured
    app.state.llm_available = False
    try:
        app.state.llm = LLMService()
        app.state.llm_available = True
    except RuntimeError as e:
        print(e)
        print("[!] LLM disabled. Showing retrieval results only.\n")


############################################
##
## Route: Analyze User Input
##
############################################
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: Request, payload: Query):

    # Convert user query into embedding to perform semantic similarity search
    security_answer = app.state.security.processQuery(payload.query)
    if security_answer["blocked"]:
        return {
            "results": [],
            "llm_explanation": "",
            "compliance_message": {
                "warning": "Sensitive input detected"
            },
            "security_response": {
                "masked": [],
                "blocked": True
            }
        }
    
    query_vector = request.app.state.embedder.encode([security_answer['sanitized_query']])[0]
    top_search_results = request.app.state.store.search(query_vector, payload.top_k)

    response = []
    lmArray = []

    # Transform search results into API response format
    for req_id, text, score in top_search_results:
        response.append(
            SearchResult(
                id=req_id,
                similarity=float(score),
                text=text
            )
        )
        lmArray.append((req_id, text, score))

    # Generating llm output.
    answer = "[!] LLM disabled."
    if request.app.state.llm_available:
        answer = request.app.state.llm.output_answer(security_answer["sanitized_query"], lmArray)

    # Generating compliance output.
    compliance = ComplianceDisclosures(app.state.llm_available,30).compliance_dict()

    masked_types = sorted(set(d["type"] for d in security_answer["detections"]))
    security = SecurityResponse(
        masked=masked_types,
        blocked=security_answer["blocked"]
    )

    return {"results": response, "llm_explanation": answer, "compliance_message": compliance, "security_response": security}


############################################
##
## Route: Health Check
##
############################################
@app.get("/health")
def health():

    if (
        not hasattr(app.state, "embedder")
        or not hasattr(app.state, "store")
    ):
        return {"status": "not_ready"}
    else:
        return {"status": "ready"}
