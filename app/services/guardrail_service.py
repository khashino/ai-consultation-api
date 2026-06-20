from app.models.schemas import ConsultationRequest, ConsultationResponse


class GuardrailService:
    def clean_sources(
        self,
        model_sources: list[str],
        valid_sources: set[str]
    ) -> list[str]:
        cleaned = [
            source for source in model_sources
            if source in valid_sources
        ]

        if cleaned:
            return sorted(set(cleaned))

        return sorted(valid_sources)

    def clean_suggested_steps(
        self,
        response: ConsultationResponse
    ) -> ConsultationResponse:
        bad_steps = {"step 1", "step 2", "step 3", "string"}

        normalized_steps = {
            step.strip().lower()
            for step in response.suggested_next_steps
        }

        if normalized_steps.intersection(bad_steps):
            response.suggested_next_steps = [
                "Check the relevant source document",
                "Ask a more specific question",
                "Request human review if needed"
            ]

            if response.confidence == "high":
                response.confidence = "low"

        return response

    def apply_safety_guardrails(
        self,
        request: ConsultationRequest,
        response: ConsultationResponse
    ) -> ConsultationResponse:
        text_to_check = f"{request.topic} {request.question}".lower()

        sensitive_keywords = [
            "immigration",
            "visa",
            "work visa",
            "residence permit",
            "legal",
            "contract",
            "lawyer",
            "medical",
            "health",
            "doctor",
            "financial",
            "investment",
            "tax",
            "loan",
            "insurance"
        ]

        is_sensitive = any(
            keyword in text_to_check
            for keyword in sensitive_keywords
        )

        if is_sensitive:
            response.needs_human_review = True

            if response.confidence == "high":
                response.confidence = "medium"

        return response