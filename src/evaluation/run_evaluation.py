from pathlib import Path
from pipeline.retrieval_pipeline import load_documents_recursive
from retrieval.vector_Store import InMemoryVectorStore
from requirement_encoder import RequirementEncoder
from retrieval_evaluator import RetrievalEvaluator
from llm_evaluator import LLMEvaluator

from test_set_definition import TEST_SETS, TOP_K, THRESHOLD


def collect_results(store, documents: list) -> list:

    encoder = RequirementEncoder()

    ids = [doc["id"] for doc in documents]
    texts = [doc["text"] for doc in documents]
    doc_dict = {doc["id"]: doc["text"] for doc in documents}

    vectors = encoder.encode(texts)
    store.add(ids, vectors)

    results_summary = []

    for testset in TEST_SETS:
        query = testset["query"]
        expected_ids = testset["expected_ids"]

        encoded_query = encoder.encode([query])[0]
        search_results = store.search(encoded_query, TOP_K)

        result_ids= [rid for rid, _ in search_results]
        scores = [score for _, score in search_results]
        retrieved_texts = [doc_dict[rid] for rid in result_ids]

        results_summary.append({
            "query": query,
            "expected": expected_ids,
            "results": result_ids,
            "scores": scores,
            "texts" : retrieved_texts
        })

    return results_summary


def main():
    data_path = "data/raw"
    base_path = Path(__file__).resolve().parent.parent.parent
    target_path = (base_path / data_path).resolve()

    store = InMemoryVectorStore()
    retrieval_evaluator = RetrievalEvaluator()

    documents = load_documents_recursive(target_path)
    results = collect_results(store, documents)

    evaluation_data = retrieval_evaluator.summarize_retrieval(results)
    retrieval_evaluator.print_output(evaluation_data)

    print("========================================")
    print("======== Starting LLM Evaluation =======")
    print("==== This may take a few minutes... ====")
    print("========================================")
    llm_evaluator = LLMEvaluator()
    evaluation = llm_evaluator.summarize_llm(results)
    llm_evaluator.print_llm_output(evaluation)


if __name__ == "__main__":
    main()