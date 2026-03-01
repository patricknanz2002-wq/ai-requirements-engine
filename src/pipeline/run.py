from pathlib import Path
from src.embedding.embedder import RequirementsEmbedder
from src.retrieval.vector_Store import InMemoryVectorStore

############################################
##
## Method: Document Loader
##
############################################
def load_documents_recursive(target_path: Path) -> list[dict]:

    if not target_path.exists():
        raise FileNotFoundError(f"Path {target_path} for >>method load_documents_recursive<< does not exist.")
    
    documents = []

    # Creating dictionaries as list in documents
    for file in target_path.rglob("*.txt"):
       documents.append({
           "id": file.stem,
           "text": file.read_text(encoding="utf-8", errors="ignore")
       })

    return documents

############################################
##
## Method: req_text_encoder
##
############################################
def run_retrieval_pipeline(documents):
    
    # Creating two lists out of the documents list containing the dictionaries
    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]
    
    # Encode all texts getting a list with vectors
    embedder = RequirementsEmbedder()
    vectorized_texts = embedder.encode(texts)
    
    # Saving vectors 
    store = InMemoryVectorStore()
    store.add(ids,vectorized_texts)

    # Creating, encoding and comparing search term
    query_text = input("Please enter the customer requirement text to compare: ")
    vectorized_query = embedder.encode([query_text])[0]
    top_search_results = store.search(vectorized_query, 1)
    
    # Creating a dictionary, loading id and text of each entry in documents list
    doc_lookup = {doc["id"]: doc["text"] for doc in documents}

    # Getting text for each top_search_result
    for reqId, score in top_search_results:
        text = doc_lookup[reqId]
        print(f'"{text}" — Similarity: {score * 100:.2f}%')
    
############################################
##
## Run
##
############################################
def main():
    data_path = "data/raw"
    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / data_path).resolve()

    documents = load_documents_recursive(target_path)
    run_retrieval_pipeline(documents)

if __name__ == "__main__":
    main()