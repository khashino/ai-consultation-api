import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.core.config import settings
from app.dependencies import document_service


def ingest_all_txt_files() -> None:
    knowledge_path = Path(settings.knowledge_dir)

    if not knowledge_path.exists():
        print(f"Knowledge directory does not exist: {knowledge_path}")
        return

    txt_files = list(knowledge_path.glob("*.txt"))

    if not txt_files:
        print(f"No .txt files found in: {knowledge_path}")
        return

    print(f"Found {len(txt_files)} text files.")

    for file_path in txt_files:
        text = file_path.read_text(encoding="utf-8")
        chunks = document_service.chunk_text(text)

        if not chunks:
            print(f"Skipped empty file: {file_path.name}")
            continue

        chunk_count = document_service.vector_store_service.upsert_chunks(
            filename=file_path.name,
            chunks=chunks
        )

        print(f"Ingested {file_path.name}: {chunk_count} chunks")


if __name__ == "__main__":
    ingest_all_txt_files()