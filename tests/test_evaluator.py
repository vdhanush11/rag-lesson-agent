"""Unit tests for hard pass/fail behaviour."""

import unittest
from pathlib import Path

from lesson_agent.evaluator import RubricEvaluator
from lesson_agent.lesson_templates import BAD_LESSON, GOOD_LESSON


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = RubricEvaluator()
        self.knowledge = Path(__file__).resolve().parents[1].joinpath("data", "knowledge_base.md").read_text(encoding="utf-8")

    def test_deliberately_weak_lesson_is_rejected(self):
        result = self.evaluator.evaluate("RAG", BAD_LESSON, self.knowledge)
        self.assertFalse(result.passed)
        self.assertGreater(len(result.failures), 0)

    def test_complete_lesson_passes_local_rubric(self):
        result = self.evaluator.evaluate("RAG", GOOD_LESSON, self.knowledge)
        self.assertTrue(result.passed, [f"{f.name}: {f.reason}" for f in result.failures])

    def test_all_six_binary_checks_are_present(self):
        result = self.evaluator.evaluate("RAG", GOOD_LESSON, self.knowledge)
        self.assertEqual(len(result.checks), 6)
        self.assertTrue(all(isinstance(check.passed, bool) for check in result.checks))


if __name__ == "__main__":
    unittest.main()
