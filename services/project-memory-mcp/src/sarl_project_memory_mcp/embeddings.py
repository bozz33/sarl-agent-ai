from __future__ import annotations

import math

import httpx


class EmbeddingsDisabled:
    enabled = False

    async def embed_document(self, text: str) -> list[float] | None:
        return None

    async def embed_query(self, text: str) -> list[float] | None:
        return None


class GeminiEmbeddings:
    enabled = True

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-embedding-001",
        dimension: int = 768,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required for Gemini embeddings")
        self.api_key = api_key
        self.model = model.removeprefix("models/")
        self.dimension = dimension
        self.timeout = timeout

    async def _embed(self, text: str, task_type: str) -> list[float]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:embedContent"
        )
        payload = {
            "model": f"models/{self.model}",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
            "outputDimensionality": self.dimension,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key,
                },
                json=payload,
            )
            response.raise_for_status()
        values = response.json()["embedding"]["values"]
        if len(values) != self.dimension:
            raise RuntimeError(
                f"embedding dimension mismatch: {len(values)} != {self.dimension}"
            )
        norm = math.sqrt(sum(float(value) ** 2 for value in values))
        if norm == 0:
            raise RuntimeError("embedding has zero norm")
        return [float(value) / norm for value in values]

    async def embed_document(self, text: str) -> list[float]:
        return await self._embed(text, "RETRIEVAL_DOCUMENT")

    async def embed_query(self, text: str) -> list[float]:
        return await self._embed(text, "RETRIEVAL_QUERY")
