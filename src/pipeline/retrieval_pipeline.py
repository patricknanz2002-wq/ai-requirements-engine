import xml.etree.ElementTree as ET

from pathlib import Path
from embedding.embedder import RequirementsEmbedder
from lm_output.LLMService import LLMService
from retrieval.vector_Database import DatabaseVectorStore

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
        req_id = title_element.text.strip() if title_element is not None else file.stem

        # Empty string fallback avoids None issues during embedding
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

    requirements_store = DatabaseVectorStore("requirements")
    embedder = RequirementsEmbedder() 

    print("[✓] Checking collection...")
    requirements_store.create_collection()

    print("[✓] Checking for new requirements...")
    database_ids = set(requirements_store.get_req_ids_of_collection())

    # Identify documents that are not yet stored in the vector database
    missing_docs = [
        doc for doc in documents
        if doc["id"] not in database_ids
    ]

    print(f"[✓] {len(missing_docs)} new requirements found")

    if missing_docs: 
        print("[✓] Creating embeddings...") 
        ids = [doc["id"] for doc in missing_docs] 
        texts = [doc["text"] for doc in missing_docs] 
        
        # Convert texts into vector embeddings for similarity search
        vectorized_texts = embedder.encode(texts) 

        # Store embeddings together with original metadata
        requirements_store.add(ids,texts,vectorized_texts)

    print("[✓] System ready\n")

    # Try to initialize LLM for explanation generation
    try:
        llm = LLMService()
        llm_available = True
    except RuntimeError as e:
        print(e)
        print("[!] LLM disabled. Showing retrieval results only.\n")
        llm_available = False

    # Interactive CLI loop for manual testing
    while True:
        print("\n\nEnter a requirement, which shall be compared (or type 'exit'):\n")
        query_text = input("> ")

        if not query_text.strip():
            print("Please enter a valid query.")
            continue

        if query_text.lower() == "exit":
            print("\nExiting demo.")
            break

        print("Searching similar requirements...")

        # Embed query and perform semantic search
        vectorized_query = embedder.encode([query_text])[0]
        top_search_results = requirements_store.search(vectorized_query, 5)

        print("\nTop similar requirements:\n")

        for req_id, text, score in top_search_results:
            print(f"{req_id} | {score:.3f}")
            print(text)
            print()

        # Optionally generate LLM-based explanation of results
        if llm_available:
            answer = llm.output_answer(query_text, top_search_results)
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
