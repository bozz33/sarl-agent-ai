from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sarl_project_memory_mcp.policy import validate_memory_write
from sarl_project_memory_mcp.schemas import MemoryValidationError


ALLOWED = frozenset({"sarl-agent-ai", "blockdevs"})


class MemoryWritePolicyTests(unittest.TestCase):
    def test_valid_decision(self) -> None:
        memory = validate_memory_write(
            allowed_projects=ALLOWED,
            project_id="sarl-agent-ai",
            type="decision",
            content="Conserver le tunnel SSH comme secours.",
            truth_status="decision",
            confidence=0.95,
        )
        self.assertEqual(memory.project_id, "sarl-agent-ai")
        self.assertEqual(str(memory.confidence), "0.95")

    def test_decision_requires_decision_status(self) -> None:
        with self.assertRaises(MemoryValidationError):
            validate_memory_write(
                allowed_projects=ALLOWED,
                project_id="sarl-agent-ai",
                type="decision",
                content="Decision invalide.",
                truth_status="confirmed",
            )

    def test_hypothesis_requires_hypothesis_status(self) -> None:
        with self.assertRaises(MemoryValidationError):
            validate_memory_write(
                allowed_projects=ALLOWED,
                project_id="sarl-agent-ai",
                type="hypothesis",
                content="Hypothese invalide.",
                truth_status="confirmed",
            )

    def test_unknown_project_rejected(self) -> None:
        with self.assertRaises(MemoryValidationError):
            validate_memory_write(
                allowed_projects=ALLOWED,
                project_id="other-project",
                type="fact",
                content="Texte.",
                truth_status="confirmed",
            )

    def test_secret_content_rejected(self) -> None:
        with self.assertRaises(MemoryValidationError):
            validate_memory_write(
                allowed_projects=ALLOWED,
                project_id="sarl-agent-ai",
                type="fact",
                content="API_KEY=very-secret-value",
                truth_status="confirmed",
            )

    def test_env_source_rejected(self) -> None:
        with self.assertRaises(MemoryValidationError):
            validate_memory_write(
                allowed_projects=ALLOWED,
                project_id="sarl-agent-ai",
                type="fact",
                content="Configuration chargee.",
                truth_status="confirmed",
                source_path="/project/.env",
            )


if __name__ == "__main__":
    unittest.main()
