import requests


API_BASE = "http://127.0.0.1:8000"


def test_health() -> None:
    response = requests.get(f"{API_BASE}/", timeout=30)
    print("Health check:")
    print(response.status_code)
    print(response.json())


def test_ask() -> None:
    payload = {
        "question": "What should I check for a Germany work visa?",
        "topic": "immigration",
        "user_country": "Iran",
        "target_country": "Germany"
    }

    response = requests.post(
        f"{API_BASE}/ask",
        json=payload,
        timeout=180
    )

    print("\nAsk response:")
    print(response.status_code)
    print(response.json())


def test_chat() -> None:
    payload = {
        "session_id": "script-test-session",
        "message": "Why are embeddings important for Persian RAG?",
        "topic": "AI",
        "user_country": "Iran",
        "target_country": None
    }

    response = requests.post(
        f"{API_BASE}/chat",
        json=payload,
        timeout=180
    )

    print("\nChat response:")
    print(response.status_code)
    print(response.json())


if __name__ == "__main__":
    test_health()
    test_ask()
    test_chat()