import json
import logging

import requests
from fastapi import HTTPException

from app.core.config import settings


class OllamaService:
    def extract_json_from_text(self, text: str) -> dict:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            raise ValueError("No JSON object found in model output.")

        json_text = text[start:end + 1]
        return json.loads(json_text)

    def generate_json(self, prompt: str) -> tuple[str, dict]:
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2
            }
        }

        try:
            response = requests.post(
                settings.ollama_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

        except requests.RequestException as error:
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to Ollama: {str(error)}"
            )

        data = response.json()
        raw_output = data.get("response", "")

        logging.info("Raw model output: %s", raw_output)

        parsed_output = self.extract_json_from_text(raw_output)

        return raw_output, parsed_output