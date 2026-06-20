import requests


BASE_URL = "http://127.0.0.1:8000"


test_cases = [
    {
        "name": "Germany work visa",
        "input": {
            "question": "What should I check for a Germany work visa?",
            "topic": "immigration",
            "user_country": "Iran",
            "target_country": "Germany"
        },
        "expected_source": "germany_work_visa.txt"
    },
    {
        "name": "Tender extraction",
        "input": {
            "question": "What should I extract from a tender document?",
            "topic": "tender",
            "user_country": "Iran",
            "target_country": None
        },
        "expected_source": "tender_process.txt"
    },
    {
        "name": "Telecom provisioning",
        "input": {
            "question": "The customer service is active but cannot connect after provisioning. What should I check?",
            "topic": "telecom support",
            "user_country": "Iran",
            "target_country": None
        },
        "expected_source": "telecom_provisioning.txt"
    }
]


passed = 0
failed = 0

print("\nRAG Retrieval Evaluation")
print("=" * 80)

for case in test_cases:
    response = requests.post(
        f"{BASE_URL}/search",
        json=case["input"],
        timeout=120
    )

    print(f"\nTest: {case['name']}")

    if response.status_code != 200:
        print("Result: FAIL")
        print("Reason:", response.status_code, response.text)
        failed += 1
        continue

    results = response.json()

    retrieved_sources = [item["source"] for item in results]
    expected_source = case["expected_source"]

    print("Expected source:", expected_source)
    print("Retrieved sources:", retrieved_sources)

    if expected_source in retrieved_sources:
        print("Result: PASS")
        passed += 1
    else:
        print("Result: FAIL")
        failed += 1

    if results:
        print("Top result:")
        print({
            "source": results[0]["source"],
            "distance": results[0]["distance"],
            "preview": results[0]["content"][:180]
        })


print("\n" + "=" * 80)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {passed + failed}")

if failed > 0:
    exit(1)