from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


HOOK = Path(__file__).resolve().parents[1] / "sarl-policy-guard.py"
SPEC = importlib.util.spec_from_file_location("sarl_policy_guard", HOOK)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def payload(command: str, tool_name: str = "terminal") -> dict:
    return {"tool_name": tool_name, "tool_input": {"command": command}}


class PolicyGuardTests(unittest.TestCase):
    def assertBlocked(self, command: str, expected_rule: str) -> None:
        blocked, rule, _ = MODULE.evaluate(payload(command))
        self.assertTrue(blocked)
        self.assertEqual(rule, expected_rule)

    def test_blocks_recursive_delete(self) -> None:
        self.assertBlocked("rm -rf /root/project", "recursive-delete")

    def test_blocks_compose_down(self) -> None:
        self.assertBlocked("docker compose down", "docker-compose-down")

    def test_blocks_database_drop(self) -> None:
        self.assertBlocked('psql -c "DROP TABLE users"', "database-destructive")

    def test_blocks_secret_write(self) -> None:
        blocked, rule, _ = MODULE.evaluate(
            {
                "tool_name": "write_file",
                "tool_input": {"path": "/root/project/.secrets/key"},
            }
        )
        self.assertTrue(blocked)
        self.assertEqual(rule, "sensitive-path")

    def test_allows_negative_secret_exposure_probe(self) -> None:
        blocked, rule, _ = MODULE.evaluate(
            payload(
                "id; test ! -e /root/CascadeProjects; "
                "test ! -e /workspace/.secrets; python --version"
            )
        )
        self.assertFalse(blocked)
        self.assertEqual(rule, "")

    def test_still_blocks_secret_read(self) -> None:
        self.assertBlocked(
            "cat /workspace/.secrets/provider.env",
            "sensitive-path",
        )

    def test_still_blocks_secret_write_from_terminal(self) -> None:
        self.assertBlocked(
            "printf token > /workspace/.secrets/provider.env",
            "sensitive-path",
        )

    def test_allows_read_only_commands(self) -> None:
        blocked, _, _ = MODULE.evaluate(payload("git status --short"))
        self.assertFalse(blocked)

    def test_allows_non_write_tool(self) -> None:
        blocked, _, _ = MODULE.evaluate(payload("rm -rf /", "read_file"))
        self.assertFalse(blocked)


if __name__ == "__main__":
    unittest.main()
