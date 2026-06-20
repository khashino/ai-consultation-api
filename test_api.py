import requests


BASE_URL = "http://127.0.0.1:8000"


test_cases = [
    {
        "question": "Can I apply for a work visa with 3 years of backend development experience?",
        "topic": "immigration",
        "user_country": "Iran",
        "target_country": "Germany"
    },
    {
        "question": "Extract the important next steps from a tender request.",
        "topic": "tender",
        "user_country": "Iran",
        "target_country": None
    },
    {
        "question": "My internet service is active but the customer cannot connect after provisioning.",
        "topic": "telecom support",
        "user_country": "Iran",
        "target_country": None
    }
]


for index, payload in enumerate(test_cases, start=1):
    print("=" * 80)
    print(f"Test case {index}")
    print("Input:")
    print(payload)

    response = requests.post(f"{BASE_URL}/ask", json=payload, timeout=120)

    print("\nStatus:", response.status_code)
    print("Output:")
    print(response.json())