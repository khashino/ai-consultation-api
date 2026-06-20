import json
import logging
from urllib.parse import urlparse

import requests
from fastapi import HTTPException

from app.core.config import settings


class OllamaService:
    def get_ollama_base_url(self) -> str:
        parsed = urlparse(settings.ollama_url)

        if not parsed.scheme or not parsed.netloc:
            return "http://localhost:11434"

        return f"{parsed.scheme}://{parsed.netloc}"

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

    def list_models(self) -> dict:
        url = f"{self.get_ollama_base_url()}/api/tags"

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()

        except requests.RequestException as error:
            raise HTTPException(
                status_code=503,
                detail=f"Could not fetch Ollama models: {str(error)}"
            )

        data = response.json()
        models = data.get("models", [])

        model_names = [
            model.get("name")
            for model in models
            if model.get("name")
        ]

        return {
            "current_model": settings.ollama_model,
            "models": model_names,
            "raw_models": models
        }

    def get_current_model(self) -> dict:
        return {
            "current_model": settings.ollama_model
        }

    def set_model(self, model_name: str) -> dict:
        available = self.list_models()
        model_names = available["models"]

        if model_name not in model_names:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Model is not available in Ollama: {model_name}",
                    "available_models": model_names
                }
            )

        settings.set_ollama_model(model_name)

        return {
            "message": "Ollama model updated successfully.",
            "current_model": settings.ollama_model,
            "available_models": model_names
        }

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