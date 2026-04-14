import xml.etree.ElementTree as ET

from pathlib import Path
from embedding.embedder import RequirementsEmbedder
from lm_output.LLMService import LLMService
from retrieval.vector_Store import InMemoryVectorStore
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
## Method: req_text_encoder
##
############################################
def run_retrieval_pipeline(documents):

    requirements_store = InMemoryVectorStore()
    embedder = RequirementsEmbedder() 
    security = SecurityLayer()

    print("[✓] Creating embeddings...") 
    ids = [doc["id"] for doc in documents] 
    texts = [doc["text"] for doc in documents] 
        
    # Convert texts into vector embeddings for similarity search
    vectorized_texts = embedder.encode(texts) 

    # Store embeddings together with original metadata
    requirements_store.add(ids,vectorized_texts)

    # Optimization for faster access
    doc_lookup = {doc["id"]: doc["text"] for doc in documents}

    print("[✓] System ready\n")

    print("----------------------------------------")
    print("LLM Status")
    print("----------------------------------------\n")
    # Try to initialize LLM for explanation generation
    try:
        llm = LLMService()
        llm_available = True
        print("[✓] LLM enabled (OPENAI_API_KEY configured)")
    except RuntimeError:
        llm_available = False
        print("[i] No OPENAI_API_KEY configured")
        print("[i] Running in retrieval-only mode")

    compliance = ComplianceDisclosures(llm_available,30)
    # Interactive CLI loop for manual testing
    print("\n"+compliance.ai_notice())
    print(compliance.data_use_summary())

    while True:
        print("\n\nEnter a requirement to compare (or type 'exit'):\n")
        original_query = input("> ")

        if original_query.lower() == "exit":
            print("\nExiting demo.")
            break

        if not original_query.strip():
            print("Please enter a valid query.")
            continue
    
        security_answer = security.processQuery(original_query)
        if security_answer["blocked"]:
            print("\n[!] Sensitive data detected. Query blocked.\n")
            continue
        
        sanitized_query = security_answer["sanitized_query"]

        if security_answer["detections"]:
            print("\n[i] Sensitive data was masked.")
            for detection in security_answer["detections"]:
                types = sorted(set(d["type"] for d in security_answer["detections"]))
                print(f"[i] Masked: {types}")
            print("")

        # Embed query and perform semantic search
        vectorized_query = embedder.encode([sanitized_query])[0]
        top_search_results = requirements_store.search(vectorized_query, 5)

        retrieved_results = []

        print("Searching similar requirements...")

        for i, (reqId, score) in enumerate(top_search_results, start=1):
            text = doc_lookup.get(reqId, "[Text not found]")
            retrieved_results.append((reqId, text, score))

        print("\nTop similar requirements:\n")

        for req_id, text, score in retrieved_results:
            print(f"{req_id} | Similarity Score: {score:.3f}")
            print(text)
            print()

        # Optionally generate LLM-based explanation of results
        if llm_available:
            answer = llm.output_answer(sanitized_query, retrieved_results)
            print(answer)


############################################
##
## Run
##
############################################
def main():
  
    # Resolve absolute path to data directory (independent of execution context)
    data_path = "data/raw"
    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / data_path).resolve()

    documents = load_documents_recursive(target_path)
    run_retrieval_pipeline(documents)


if __name__ == "__main__":
    main()
