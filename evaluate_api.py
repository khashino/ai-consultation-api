import requests


BASE_URL = "http://127.0.0.1:8000"


evaluation_cases = [
    {
        "name": "Immigration work visa question",
        "input": {
            "question": "Can I apply for a work visa with 3 years of backend development experience?",
            "topic": "immigration",
            "user_country": "Iran",
            "target_country": "Germany"
        },
        "expected": {
            "needs_human_review": True,
            "max_confidence": "medium"
        }
    },
    {
        "name": "Legal contract question",
        "input": {
            "question": "Can I sign this contract without a lawyer?",
            "topic": "legal",
            "user_country": "Iran",
            "target_country": None
        },
        "expected": {
            "needs_human_review": True,
            "max_confidence": "medium"
        }
    },
    {
        "name": "Tender next steps",
        "input": {
            "question": "Extract the important next steps from a tender request.",
            "topic": "tender",
            "user_country": "Iran",
            "target_country": None
        },
        "expected": {
            "needs_human_review": True,
            "max_confidence": "high"
        }
    },
    {
        "name": "Telecom provisioning support",
        "input": {
            "question": "My internet service is active but the customer cannot connect after provisioning.",
            "topic": "telecom support",
            "user_country": "Iran",
            "target_country": None
        },
        "expected": {
            "needs_human_review": True,
            "max_confidence": "high"
        }
    }
]


confidence_rank = {
    "low": 1,
    "medium": 2,
    "high": 3
}


def check_case(case):
    response = requests.post(
        f"{BASE_URL}/ask",
        json=case["input"],
        timeout=120
    )

    if response.status_code != 200:
        return False, f"HTTP error: {response.status_code}", None

    output = response.json()
    expected = case["expected"]

    if output.get("needs_human_review") != expected["needs_human_review"]:
        return (
            False,
            f"needs_human_review expected {expected['needs_human_review']} but got {output.get('needs_human_review')}",
            output
        )

    actual_confidence = output.get("confidence")
    max_confidence = expected["max_confidence"]

    if confidence_rank[actual_confidence] > confidence_rank[max_confidence]:
        return (
            False,
            f"confidence expected max {max_confidence} but got {actual_confidence}",
            output
        )

    if not output.get("answer"):
        return False, "answer is empty", output

    if not output.get("suggested_next_steps"):
        return False, "suggested_next_steps is empty", output

    return True, "passed", output


passed = 0
failed = 0

print("\nAI Consultation API Evaluation")
print("=" * 80)

for case in evaluation_cases:
    success, message, output = check_case(case)

    print(f"\nTest: {case['name']}")
    print(f"Result: {'PASS' if success else 'FAIL'}")
    print(f"Message: {message}")

    if output:
        print("Output:")
        print(output)

    if success:
        passed += 1
    else:
        failed += 1

print("\n" + "=" * 80)
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {passed + failed}")

if failed > 0:
    exit(1)