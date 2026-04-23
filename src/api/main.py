from pathlib import Path

from fastapi import FastAPI, Request
from pydantic import BaseModel

from pipeline.retrieval_pipeline import run_rag, initialize_system, load_documents_recursive


app = FastAPI()


class Query(BaseModel):
    query: str
    top_k: int = 5


class Source(BaseModel):
    id: str
    text: str
    score: float


class SecurityMeta(BaseModel):
    masked: list
    blocked: bool
    detections: list


class Meta(BaseModel):
    compliance: dict
    security: SecurityMeta


class AnalyzeResponse(BaseModel):
    answer: str
    sources: list[Source]
    meta: Meta



############################################
##
## Startup
##
############################################
@app.on_event("startup")
def startup_event():

    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / "data/raw").resolve()

    # Loads .xml files from data/raw (simulates req tool api)
    documents = load_documents_recursive(target_path)
    app.state.system = initialize_system(documents)



############################################
##
## Route: Analyze User Input
##
############################################
@app.post("/tools/answer_with_requirements", response_model=AnalyzeResponse)
def analyze(request: Request, payload: Query):
    
    return run_rag(request.app.state.system, payload.query, payload.top_k)



############################################
##
## Route: Health Check
##
############################################   
@app.get("/health")
def health():

    if not hasattr(app.state, "system"):
        return {"status": "not_ready"}
    else:
        return {"status": "ready"}
