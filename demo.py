import os
import warnings

# Silence HF + tokenizer noise
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

warnings.filterwarnings("ignore")

from pathlib import Path
from huggingface_hub.utils import logging as hf_logging
from transformers import logging as tf_logging

hf_logging.set_verbosity_error()
tf_logging.set_verbosity_error()
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
