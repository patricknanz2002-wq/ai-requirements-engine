from pathlib import Path


############################################
##
## Method: Document Loader
##
############################################
def load_documents_recursive(target_path: Path) -> list[dict]:

    if not target_path.exists():
        raise FileNotFoundError(f"Path {target_path} for >>method load_documents_recursive<< does not exist.")
    
    documents = []

    for file in target_path.rglob("*.txt"):
       documents.append({
           "id": file.stem,
           "text": file.read_text(encoding="utf-8", errors="ignore")
       })

    return documents





############################################
##
## Run
##
############################################

data_path = "data/raw"
base_path = Path(__file__).resolve().parent.parent
target_path = (base_path / data_path).resolve()

documents = load_documents_recursive(target_path)
print(documents)