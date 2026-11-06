"""Orchestrates generate -> evaluate -> feedback -> bounded regeneration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evaluator import Evaluation, RubricEvaluator
from .memory import PersistentMemory
from .providers import MockProvider, OpenAIProvider, ProviderError


class LessonAgent:
    def __init__(
        self,
        provider: MockProvider | OpenAIProvider,
        project_root: str | Path,
        max_retries: int = 2,
    ) -> None:
        if not 0 <= max_retries <= 2:
            raise ValueError("max_retries must be between 0 and 2")
        self.provider = provider
        self.root = Path(project_root)
        self.max_retries = max_retries
        self.evaluator = RubricEvaluator()
        self.memory = PersistentMemory(self.root / "memory" / "agent_memory.json")
        self.outputs = self.root / "outputs"
        self.outputs.mkdir(parents=True, exist_ok=True)

    def run(self, topic: str) -> dict[str, Any]:
        knowledge_path = self.root / "data" / "knowledge_base.md"
        knowledge = knowledge_path.read_text(encoding="utf-8")
        attempts: list[dict[str, Any]] = []
        feedback: list[str] = []
        final_lesson = ""
        final_eval: Evaluation | None = None

        for attempt_number in range(1, self.max_retries + 2):
            memory_rules = self.memory.rules_for_prompt()
            lesson = self.provider.generate_lesson(topic, knowledge, feedback, memory_rules)
            judge = self.provider.judge_lesson(topic, lesson, knowledge)
            evaluation = self.evaluator.evaluate(topic, lesson, knowledge, judge)
            attempts.append({
                "attempt": attempt_number,
                "passed": evaluation.passed,
                "checks": [item.to_dict() for item in evaluation.checks],
            })
            final_lesson, final_eval = lesson, evaluation

            failed_names = [item.name for item in evaluation.failures]
            reasons = [f"{item.name}: {item.reason}" for item in evaluation.failures]
            # Memory is updated on every evaluation, so later runs can benefit.
            self.memory.record_run(failed_names, reasons)

            if evaluation.passed:
                break
            if attempt_number <= self.max_retries:
                feedback = reasons

        assert final_eval is not None
        report = {
            "topic": topic,
            "provider": self.provider.name,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "max_retries": self.max_retries,
            "attempt_count": len(attempts),
            "passed": final_eval.passed,
            "attempts": attempts,
            "generation_context": getattr(self.provider, "generation_context", None),
            "memory_after_run": self.memory.data,
        }
        self._write_outputs(topic, final_lesson, attempts, report, final_eval)
        return report

    def _write_outputs(
        self,
        topic: str,
        lesson: str,
        attempts: list[dict[str, Any]],
        report: dict[str, Any],
        final_eval: Evaluation,
    ) -> None:
        (self.outputs / "final_lesson.md").write_text(
            f"# Final lesson: {topic}\n\n{lesson.strip()}\n", encoding="utf-8"
        )
        (self.outputs / "run_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        lines = [
            f"# Rejection log — {topic}",
            "",
            f"Provider: `{self.provider.name}`  ",
            f"Attempts used: **{len(attempts)}**  ",
            f"Final status: **{'PASS' if final_eval.passed else 'REJECTED — retry limit reached'}**",
            "",
        ]
        for attempt in attempts:
            lines.extend([f"## Attempt {attempt['attempt']} — {'PASS' if attempt['passed'] else 'REJECTED'}", ""])
            for check in attempt["checks"]:
                mark = "PASS" if check["passed"] else "FAIL"
                lines.append(f"- **{mark} — {check['name']}**: {check['reason']}")
            lines.append("")
        lines.extend([
            "## What changed after rejection?",
            "",
            "The generator received the failed check names and their reasons before the next attempt. "
            "The persistent memory also saved reusable writing rules, such as defining technical words "
            "and walking through a real-world example. The rubric stayed unchanged; only the generation "
            "guidance improved.",
            "",
        ])
        (self.outputs / "rejection_log.md").write_text("\n".join(lines), encoding="utf-8")


def build_provider(provider_name: str, deliberate_error: bool = False, model: str | None = None):
    if provider_name == "mock":
        return MockProvider(deliberate_error=deliberate_error)
    if provider_name == "openai":
        return OpenAIProvider(model=model, deliberate_error=deliberate_error)
    raise ValueError("provider must be 'mock' or 'openai'")
