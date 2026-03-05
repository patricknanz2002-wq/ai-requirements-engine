from pathlib import Path

from src.pipeline.retrieval_pipeline import (
    load_documents_recursive,
    run_retrieval_pipeline,
)


def main():

    print("""
AI Requirements Engine Demo
───────────────────────────
""")

    print("[✓] Loading requirements...")

    data_path = "data/raw"
    base_path = Path(__file__).resolve().parent
    target_path = (base_path / data_path).resolve()

    documents = load_documents_recursive(target_path)

    print(f"[✓] {len(documents)} requirements loaded")

    run_retrieval_pipeline(documents)


if __name__ == "__main__":
    main()
