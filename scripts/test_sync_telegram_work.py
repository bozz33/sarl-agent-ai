#!/usr/bin/env python3
"""Unit tests for Telegram-to-Kanban classification."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("sync-telegram-work.py")
spec = importlib.util.spec_from_file_location("sync_telegram_work", SCRIPT)
assert spec and spec.loader
sync_telegram_work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_telegram_work)


class TelegramWorkClassificationTest(unittest.TestCase):
    def test_simple_question_is_not_trackable(self) -> None:
        classification = sync_telegram_work.classify_message("Pourquoi le dashboard est vide ?")

        self.assertEqual(classification["intent"], "question")
        self.assertEqual(classification["execution"], "no_dispatch")
        self.assertIs(classification["trackable"], False)

    def test_low_risk_summary_is_ready(self) -> None:
        classification = sync_telegram_work.classify_message(
            "Prépare un résumé des missions ouvertes avec un petit rapport de suivi pour demain."
        )

        self.assertIn(classification["intent"], {"research", "task"})
        self.assertEqual(classification["risk"], "low")
        self.assertEqual(classification["execution"], "auto_dispatch_allowed")
        self.assertEqual(classification["initial_status"], "ready")
        self.assertIs(classification["trackable"], True)

    def test_production_deploy_needs_human_validation(self) -> None:
        classification = sync_telegram_work.classify_message(
            "Déploie la nouvelle version en prod et vérifie le serveur après la mise en production."
        )

        self.assertEqual(classification["intent"], "deploy")
        self.assertEqual(classification["risk"], "high")
        self.assertEqual(classification["execution"], "needs_human")
        self.assertEqual(classification["initial_status"], "blocked")
        self.assertIs(classification["trackable"], True)

    def test_medium_risk_technical_change_is_blocked(self) -> None:
        classification = sync_telegram_work.classify_message(
            "Implémente la classification Telegram dans Hermes Workspace et modifie la configuration."
        )

        self.assertEqual(classification["intent"], "task")
        self.assertEqual(classification["risk"], "medium")
        self.assertEqual(classification["execution"], "needs_human")
        self.assertEqual(classification["initial_status"], "blocked")
        self.assertIs(classification["trackable"], True)


if __name__ == "__main__":
    unittest.main()
