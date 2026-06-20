import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.dependencies import vector_store_service


def test_retrieval() -> None:
    questions = [
        "What should I check for a Germany work visa?",
        "Why are embeddings important for Persian RAG?",
        "چرا کیفیت embedding برای RAG فارسی مهم است؟",
    ]

    for question in questions:
        print("=" * 80)
        print("QUESTION:")
        print(question)

        results = vector_store_service.search(question)

        if not results:
            print("No results found.")
            continue

        for index, item in enumerate(results, start=1):
            print("-" * 80)
            print(f"Result {index}")
            print(f"Source: {item.source}")
            print(f"Chunk: {item.chunk_index}")
            print(f"Distance: {item.distance}")
            print("Content:")
            print(item.content[:500])


if __name__ == "__main__":
    test_retrieval()