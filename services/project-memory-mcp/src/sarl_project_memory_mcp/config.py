from __future__ import annotations

import os
from dataclasses import dataclass

from .policy import normalize_allowed_projects


@dataclass(frozen=True)
class Settings:
    database_url: str
    allowed_projects: frozenset[str]
    embedding_provider: str
    embedding_model: str
    embedding_api_key: str
    embedding_dimension: int
    embedding_timeout: float
    max_search_results: int

    @classmethod
    def from_env(cls) -> "Settings":
        database_url = os.environ.get("SARL_MEMORY_DATABASE_URL", "").strip()
        if not database_url:
            raise RuntimeError("SARL_MEMORY_DATABASE_URL is required")
        max_results = int(os.environ.get("SARL_MEMORY_MAX_SEARCH_RESULTS", "20"))
        if max_results < 1 or max_results > 100:
            raise RuntimeError("SARL_MEMORY_MAX_SEARCH_RESULTS must be between 1 and 100")
        dimension = int(os.environ.get("SARL_MEMORY_EMBEDDING_DIMENSION", "768"))
        if dimension not in {768, 1536, 3072}:
            raise RuntimeError(
                "SARL_MEMORY_EMBEDDING_DIMENSION must be 768, 1536 or 3072"
            )
        return cls(
            database_url=database_url,
            allowed_projects=normalize_allowed_projects(
                os.environ.get("SARL_MEMORY_ALLOWED_PROJECTS", "")
            ),
            embedding_provider=os.environ.get(
                "SARL_MEMORY_EMBEDDING_PROVIDER", "disabled"
            ).strip(),
            embedding_model=os.environ.get(
                "SARL_MEMORY_EMBEDDING_MODEL", ""
            ).strip(),
            embedding_api_key=(
                os.environ.get("GEMINI_API_KEY")
                or os.environ.get("GOOGLE_API_KEY")
                or ""
            ).strip(),
            embedding_dimension=dimension,
            embedding_timeout=float(
                os.environ.get("SARL_MEMORY_EMBEDDING_TIMEOUT", "30")
            ),
            max_search_results=max_results,
        )
