import time

import xml.etree.ElementTree as ET

from pathlib import Path
from embedding.embedder import RequirementsEmbedder
from lm_output.LLMService import LLMService
from retrieval.vector_Store import InMemoryVectorStore
from retrieval.vector_Database import DatabaseVectorStore
from compliance.disclosures import ComplianceDisclosures
from security.query_Security import SecurityLayer


############################################
##
## Method: Document Loader
##
############################################
def load_documents_recursive(target_path: Path) -> list[dict]:

    if not target_path.exists():
        raise FileNotFoundError(
            f"Path {target_path} for >>method load_documents_recursive<< does not exist."
        )

    documents = []

    # Recursively parse all XML files and extract requirement ID + text
    for file in target_path.rglob("*.xml"):
        tree = ET.parse(file)
        root = tree.getroot()

        title_element = root.find("title")
        description_element = root.find("requirement")

        # Fallback to filename if no title is provided
        req_id = (
            title_element.text.strip()
            if title_element is not None and title_element.text
            else file.stem
            )

        # Empty string fallback avoids None issues during embedding
        text = (
            description_element.text.strip()
            if description_element is not None and description_element.text
            else ""
            )

        documents.append({"id": req_id, "text": text})

    return documents



############################################
##
## Method: System initialization
##
############################################
def initialize_system(documents):
    embedder = RequirementsEmbedder()
    security = SecurityLayer()
    store = None

    # Check Qdrant availability qdrant_available = True
    qdrant_available = False

    for i in range(15):
        try:
            store = DatabaseVectorStore()
            database_ids = set(store.get_req_ids_of_collection())
            print("[✓] Using Qdrant vector store")
            qdrant_available = True
            break
        except Exception:
            print(f"Waiting for Qdrant in startup... ({i+1}/15)")
            time.sleep(2)

    if not qdrant_available:
        print("[i] Qdrant not available → using InMemory store")
        store = InMemoryVectorStore()
        database_ids = set()

    # Decide what to index
    if qdrant_available:
        docs_to_add = [
            doc for doc in documents
            if doc["id"] not in database_ids
        ]
    else:
        docs_to_add = documents

    # Add embeddings
    if docs_to_add:
        print("[✓] Creating embeddings...")

        ids = [doc["id"] for doc in docs_to_add]
        texts = [doc["text"] for doc in docs_to_add]

        vectors = embedder.encode(texts)
        store.add(ids, vectors)

    doc_lookup = {doc["id"]: doc["text"] for doc in documents}

    print("[✓] System ready\n")
    print("----------------------------------------")
    print("LLM Status")
    print("----------------------------------------\n")

    try:
        llm = LLMService()
        llm_available = True
        print("[✓] LLM enabled (OPENAI_API_KEY configured)")
    except RuntimeError:
        llm = None
        llm_available = False
        print("[i] No OPENAI_API_KEY configured")
        print("[i] Running in retrieval-only mode")

    return {
        "embedder": embedder,
        "store": store,
        "security": security,
        "llm": llm,
        "llm_available": llm_available,
        "database_ids": database_ids,
        "doc_lookup": doc_lookup
    }



############################################
##
## Method: run_rag
##
############################################
def run_rag(system, query: str, top_k: int = 5):

    security_answer = system["security"].processQuery(query)

    if security_answer["blocked"]:
        return {
            "answer": "",
            "sources": [],
            "meta": {
                "compliance": {"warning": "Sensitive input detected"},
                "security": {
                    "masked": [],
                    "blocked": True
                }
            }
        }

    sanitized_query = security_answer["sanitized_query"]

    vector = system["embedder"].encode([sanitized_query])[0]
    results = system["store"].search(vector, top_k)

    sources = []
    retrieved = []

    for req_id, score in results:
        text = system["doc_lookup"].get(req_id, "")
        sources.append({
            "id": req_id,
            "text": text,
            "score": float(score)
        })
        retrieved.append((req_id, text, score))

    answer = "[!] LLM disabled."
    if system["llm_available"]:
        answer = system["llm"].output_answer(sanitized_query, retrieved)

    compliance = ComplianceDisclosures(system["llm_available"], 30).compliance_dict()
    masked_types = sorted(set(d["type"] for d in security_answer["detections"]))

    return {
        "answer": answer,
        "sources": sources,
        "meta": {
            "compliance": compliance,
            "security": {
                "masked": masked_types,
                "blocked": security_answer["blocked"],
                    "detections": security_answer["detections"]
            }
        }
    }



############################################
##
## Method: run_cli_demo()
##
############################################
def run_cli_demo(system):

    while True:
        print("\n\nEnter a requirement to compare (or type 'exit'):\n")
        query = input("> ")

        if query.lower() == "exit":
            print("\nExiting demo.")
            break

        if not query.strip():
            print("Please enter a valid query.")
            continue

        # Pipeline aufrufen
        result = run_rag(system, query)

        # Security Block
        if result["meta"]["security"]["blocked"]:
            print("\n[!] Sensitive data detected. Query blocked.\n")
            continue

        # Masking Info
        if result["meta"]["security"]["masked"]:
            print("\n[i] Sensitive data was masked.")
            print(f"[i] Masked: {result['meta']['security']['masked']}\n")

        print("Searching similar requirements...")

        # Retrieval Output
        print("\nTop similar requirements:\n")

        for s in result["sources"]:
            print(f"{s['id']} | Similarity Score: {s['score']:.3f}")
            print(s["text"])
            print()

        # LLM Output
        if system["llm_available"]:
            print(result["answer"])



############################################
##
## Run
##
############################################
def run():
  
    # Resolve absolute path to data directory (independent of execution context)
    print("[✓] Loading requirements...")
    data_path = "data/raw"
    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / data_path).resolve()

    documents = load_documents_recursive(target_path)

    print(f"[✓] {len(documents)} requirements loaded")
    system = initialize_system(documents)
    run_cli_demo(system)


if __name__ == "__main__":
    run()