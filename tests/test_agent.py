"""Integration tests for retry feedback, persistent memory, and bounded retries."""

import shutil
import tempfile
import unittest
from pathlib import Path

from lesson_agent.agent import LessonAgent
from lesson_agent.providers import MockProvider


class AgentLoopTests(unittest.TestCase):
    def make_project(self, root: Path) -> None:
        (root / "data").mkdir(parents=True, exist_ok=True)
        source = Path(__file__).resolve().parents[1] / "data" / "knowledge_base.md"
        shutil.copy2(source, root / "data" / "knowledge_base.md")

    def test_rejects_then_regenerates_and_saves_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            provider = MockProvider(deliberate_error=True)
            agent = LessonAgent(provider, root, max_retries=2)
            report = agent.run("RAG")

            self.assertTrue(report["passed"])
            self.assertEqual(report["attempt_count"], 2)
            self.assertFalse(report["attempts"][0]["passed"])
            self.assertTrue(report["attempts"][1]["passed"])
            self.assertEqual(len(provider.generation_context[1]["feedback_received"]), 6)
            self.assertEqual(len(provider.generation_context[1]["memory_rules_received"]), 6)
            self.assertTrue((root / "outputs" / "rejection_log.md").exists())
            self.assertEqual(report["memory_after_run"]["total_runs"], 2)

    def test_retry_limit_cannot_exceed_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_project(root)
            with self.assertRaises(ValueError):
                LessonAgent(MockProvider(), root, max_retries=3)


if __name__ == "__main__":
    unittest.main()
