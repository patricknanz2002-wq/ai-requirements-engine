from pathlib import Path
from pipeline.retrieval_pipeline import load_documents_recursive
from retrieval.vector_Store import InMemoryVectorStore
from requirement_encoder import RequirementEncoder
from retrieval_evaluator import RetrievalEvaluator
from llm_evaluator import LLMEvaluator
from test_set_definition import TEST_SETS, TOP_K


############################################
##
## Method: collect_results
## Description: Runs retrieval over all test queries
## and collects structured results for evaluation
##
############################################
def collect_results(store, documents: list) -> list:

    encoder = RequirementEncoder()

    # Prepare document data
    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]
    doc_dict = {doc["id"]: doc["text"] for doc in documents}

    # Encode and store document embeddings
    vectors = encoder.encode(texts)
    store.add(ids, vectors)

    results_summary = []

    # Run retrieval for each test query
    for testset in TEST_SETS:
        query = testset["query"]
        expected_ids = testset["expected_ids"]

        # Encode query and retrieve top-k results
        encoded_query = encoder.encode([query])[0]
        search_results = store.search(encoded_query, TOP_K)

        # Extract structured results
        result_ids = [rid for rid, _ in search_results]
        scores = [score for _, score in search_results]
        retrieved_texts = [doc_dict[rid] for rid in result_ids]

        results_summary.append({
            "query": query,
            "expected": expected_ids,
            "results": result_ids,
            "scores": scores,
            "texts": retrieved_texts
        })

    return results_summary


############################################
##
## Method: main
## Description: End-to-end evaluation pipeline
## → loads data, runs retrieval evaluation,
## → optionally runs LLM-based evaluation
##
############################################
def main():
    data_path = "data/raw"

    # Resolve absolute path (independent of execution context)
    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / data_path).resolve()

    # Initialize components
    store = InMemoryVectorStore()
    retrieval_evaluator = RetrievalEvaluator()

    # Load documents and run retrieval
    documents = load_documents_recursive(target_path)
    results = collect_results(store, documents)

    # Retrieval evaluation
    evaluation_data = retrieval_evaluator.summarize_retrieval(results)
    retrieval_evaluator.print_output(evaluation_data)

    print("========================================")
    print("======== Starting LLM Evaluation =======")
    print("==== This may take a few minutes... ====")
    print("========================================")

    # LLM-based evaluation (optional, requires API key)
    try:
        llm_evaluator = LLMEvaluator()
        evaluation = llm_evaluator.summarize_llm(results)
        llm_evaluator.print_llm_output(evaluation)
    except RuntimeError:
        print("[i] No OPENAI_API_KEY configured")
        print("[i] Skipping LLM-based evaluation")


############################################
##
## Run
##
############################################
if __name__ == "__main__":
    main()