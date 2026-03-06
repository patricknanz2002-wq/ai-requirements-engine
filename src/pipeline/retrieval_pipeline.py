import xml.etree.ElementTree as ET
from pathlib import Path

from embedding.embedder import RequirementsEmbedder
from lm_output.LLMService import LLMService
from retrieval.vector_Store import InMemoryVectorStore


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
        text = (
            description_element.text.strip() if description_element is not None else ""
        )

        documents.append({"id": req_id, "text": text})

    return documents


############################################
##
## Method: req_text_encoder
##
############################################
def run_retrieval_pipeline(documents):

    print("[✓] Creating embeddings...")

    # Creating two different lists for ids and texts
    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]

    embedder = RequirementsEmbedder()
    vectorized_texts = embedder.encode(texts)

    store = InMemoryVectorStore()
    store.add(ids, vectorized_texts)

    # Optimization for faster access
    doc_lookup = {doc["id"]: doc["text"] for doc in documents}

    print("[✓] System ready\n")

    llm = LLMService()
    while True:
        print("\n\nEnter a requirement, which shall be compared (or type 'exit'):\n")
        query_text = input("> ")

        if query_text.lower() == "exit":
            print("\nExiting demo.")
            break

        vectorized_query = embedder.encode([query_text])[0]
        top_search_results = store.search(vectorized_query, 5)

        lmArray = []

        for i, (reqId, score) in enumerate(top_search_results, start=1):
            text = doc_lookup.get(reqId, "[Text not found]")
            lmArray.append((reqId, text, score))

        answer = llm.output_answer(query_text, lmArray)
        print(answer)


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
