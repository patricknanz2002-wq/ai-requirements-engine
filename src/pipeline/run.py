from pathlib import Path
from src.embedding.embedder import RequirementsEmbedder
from src.retrieval.vector_Store import InMemoryVectorStore
import xml.etree.ElementTree as ET

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

    # Creating dictionaries and appending them to list "documents"
    for file in target_path.rglob("*.xml"):
        tree = ET.parse(file)
        root = tree.getroot()

        title_element = root.find("title")
        description_element = root.find("requirement")

        req_id = title_element.text.strip() if title_element is not None else file.stem
        text = description_element.text.strip() if description_element is not None else ""

        documents.append({
            "id": req_id,
            "text": text
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
    top_search_results = store.search(vectorized_query, 5)
    
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