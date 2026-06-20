import requests


API_BASE = "http://127.0.0.1:8000"


TEST_CASES = [
    {
        "name": "Germany work visa",
        "payload": {
            "question": "What should I check for a Germany work visa?",
            "topic": "immigration",
            "user_country": "Iran",
            "target_country": "Germany"
        }
    },
    {
        "name": "Persian RAG embeddings",
        "payload": {
            "question": "Why are embeddings important for Persian RAG?",
            "topic": "AI",
            "user_country": None,
            "target_country": None
        }
    },
    {
        "name": "Persian language RAG question",
        "payload": {
            "question": "چرا کیفیت embedding برای RAG فارسی مهم است؟",
            "topic": "AI",
            "user_country": None,
            "target_country": None
        }
    }
]


def evaluate_api() -> None:
    passed = 0

    for test_case in TEST_CASES:
        print("=" * 80)
        print(f"Test: {test_case['name']}")

        try:
            response = requests.post(
                f"{API_BASE}/ask",
                json=test_case["payload"],
                timeout=180
            )

            print(f"Status code: {response.status_code}")

            if response.status_code != 200:
                print("FAIL")
                print(response.text)
                continue

            data = response.json()

            required_fields = [
                "answer",
                "confidence",
                "needs_human_review",
                "suggested_next_steps",
                "sources"
            ]

            missing_fields = [
                field for field in required_fields
                if field not in data
            ]

            if missing_fields:
                print("FAIL")
                print(f"Missing fields: {missing_fields}")
                continue

            if data["confidence"] not in ["low", "medium", "high"]:
                print("FAIL")
                print("Invalid confidence value.")
                continue

            print("PASS")
            print("Answer:")
            print(data["answer"])
            print("Sources:")
            print(data["sources"])

            passed += 1

        except Exception as error:
            print("FAIL")
            print(str(error))

    print("=" * 80)
    print(f"Passed: {passed}/{len(TEST_CASES)}")


if __name__ == "__main__":
    evaluate_api()