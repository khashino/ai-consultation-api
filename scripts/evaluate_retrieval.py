import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.dependencies import vector_store_service


TEST_CASES = [
    {
        "question": "Why are embeddings important for Persian RAG?",
        "expected_source": "persian_rag_guide.txt"
    },
    {
        "question": "چرا کیفیت embedding برای RAG فارسی مهم است؟",
        "expected_source": "persian_rag_guide.txt"
    },
    {
        "question": "What should I check for enterprise AI integration?",
        "expected_source": "enterprise_ai_integration.txt"
    },
    {
        "question": "Customer service is active but cannot connect. What should support check first?",
        "expected_source": "telecom_ai_support.txt"
    },
]


def evaluate_retrieval() -> None:
    total = len(TEST_CASES)
    passed = 0

    for index, test_case in enumerate(TEST_CASES, start=1):
        question = test_case["question"]
        expected_source = test_case["expected_source"]

        results = vector_store_service.search(question)
        returned_sources = {item.source for item in results}

        is_pass = expected_source in returned_sources

        if is_pass:
            passed += 1

        print("=" * 80)
        print(f"Test {index}")
        print(f"Question: {question}")
        print(f"Expected source: {expected_source}")
        print(f"Returned sources: {sorted(returned_sources)}")
        print(f"Result: {'PASS' if is_pass else 'FAIL'}")

    print("=" * 80)
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {(passed / total) * 100:.2f}%")


if __name__ == "__main__":
    evaluate_retrieval()