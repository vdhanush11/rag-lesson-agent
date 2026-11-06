"""LLM and deterministic mock providers."""

from __future__ import annotations

import json
import os
from typing import Any

from .lesson_templates import BAD_LESSON, GOOD_LESSON


class ProviderError(RuntimeError):
    """Raised when an LLM provider cannot complete a request safely."""


class MockProvider:
    """A repeatable provider for demos and tests; no API key or network needed."""

    name = "mock"

    def __init__(self, deliberate_error: bool = False) -> None:
        self.deliberate_error = deliberate_error
        self.generation_calls = 0
        self.generation_context: list[dict[str, Any]] = []

    def generate_lesson(
        self,
        topic: str,
        knowledge: str,
        feedback: list[str],
        memory_rules: list[str],
    ) -> str:
        self.generation_calls += 1
        self.generation_context.append({
            "attempt": self.generation_calls,
            "feedback_received": list(feedback),
            "memory_rules_received": list(memory_rules),
        })
        if self.deliberate_error and self.generation_calls == 1:
            return BAD_LESSON
        return GOOD_LESSON.replace("Introduction to RAG", f"Introduction to {topic}", 1)

    def judge_lesson(self, topic: str, lesson: str, knowledge: str) -> dict[str, Any]:
        # The local rubric is the authority in demo mode. The evaluator will
        # combine this response with deterministic checks.
        return {
            "accuracy_grounded": {"pass": True, "reason": "Mock judge: factual checks are handled by the local rubric."},
            "beginner_friendly": {"pass": True, "reason": "Mock judge: readability checks are handled by the local rubric."},
            "teaches_by_example": {"pass": True, "reason": "Mock judge: example structure is checked locally."},
            "jargon_explained": {"pass": True, "reason": "Mock judge: glossary definitions are checked locally."},
            "key_coverage": {"pass": True, "reason": "Mock judge: required concepts and sections are checked locally."},
            "coherent_flow": {"pass": True, "reason": "Mock judge: section order is checked locally."},
        }


class OpenAIProvider:
    """OpenAI-compatible provider using the official OpenAI Python SDK."""

    name = "openai"

    def __init__(self, model: str | None = None, deliberate_error: bool = False) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ProviderError("OPENAI_API_KEY is missing. Add it to your environment or use --provider mock.")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderError("The OpenAI package is not installed. Run: pip install -r requirements.txt") from exc
        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.deliberate_error = deliberate_error
        self.generation_calls = 0

    def _chat(self, system: str, user: str, json_mode: bool = False) -> str:
        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if not content:
                raise ProviderError("The model returned an empty response.")
            return content
        except ProviderError:
            raise
        except Exception as exc:  # SDK/network errors should become actionable messages.
            raise ProviderError(f"LLM request failed: {exc}") from exc

    def generate_lesson(
        self,
        topic: str,
        knowledge: str,
        feedback: list[str],
        memory_rules: list[str],
    ) -> str:
        self.generation_calls += 1
        if self.deliberate_error and self.generation_calls == 1:
            # Inject a known weak draft so the real evaluator and judge can reject it.
            return BAD_LESSON
        system = (
            "You are a careful instructional designer. Write a standalone lesson for a learner "
            "who is new to computers and AI. Use simple English, short paragraphs, practical "
            "examples, and define every technical word. Use only the supplied trusted knowledge. "
            "Do not invent facts or claim that RAG guarantees correctness. Output Markdown only."
        )
        user = f"""Create a beginner lesson about: {topic}

TRUSTED KNOWLEDGE (use as factual boundary):
{knowledge}

REQUIRED STRUCTURE:
1. What is the topic?
2. Why does it matter?
3. How does it work? Explain in numbered steps.
4. A simple example with at least three clear steps.
5. What it cannot do / limitations.
6. Key words in plain English (define technical terms).
7. Quick recap and one understanding-check question.

QUALITY RULES:
- Assume the learner starts from zero.
- Prefer everyday words and explain abbreviations the first time.
- Use one running example that makes the steps easy to picture.
- Do not leave technical terms unexplained.
- Keep the teaching flow logical and self-contained.
- Include the important facts from the trusted knowledge, especially limitations.

PREVIOUS EVALUATION FAILURES TO FIX:
{chr(10).join('- ' + item for item in feedback) if feedback else '- None; this is the first attempt.'}

LESSONS FROM PREVIOUS RUNS:
{chr(10).join('- ' + item for item in memory_rules) if memory_rules else '- No stored lessons yet.'}
"""
        return self._chat(system, user)

    def judge_lesson(self, topic: str, lesson: str, knowledge: str) -> dict[str, Any]:
        system = (
            "You are a strict quality evaluator. Treat every criterion as pass or fail. "
            "Do not give partial credit. Be conservative: if evidence is missing, fail the check. "
            "Judge factual claims only against the trusted knowledge. Return valid JSON only."
        )
        user = f"""Evaluate this lesson about {topic}.

TRUSTED KNOWLEDGE:
{knowledge}

LESSON:
{lesson}

Return exactly one JSON object with these six keys. Each value must have:
{{"pass": true_or_false, "reason": "specific short reason with evidence"}}
Keys:
- accuracy_grounded: Is the lesson accurate and consistent with trusted knowledge? Does it avoid unsupported guarantees?
- beginner_friendly: Can a complete beginner understand the language and explanations?
- teaches_by_example: Is there a concrete example that demonstrates the idea, not just names it?
- jargon_explained: Are technical terms and abbreviations explained in simple language?
- key_coverage: Does it cover what it is, why it matters, the main workflow, and limitations?
- coherent_flow: Does the lesson teach ideas in a sensible order with clear transitions?
"""
        raw = self._chat(system, user, json_mode=True)
        try:
            data = json.loads(raw)
            expected = {
                "accuracy_grounded", "beginner_friendly", "teaches_by_example",
                "jargon_explained", "key_coverage", "coherent_flow",
            }
            if set(data) != expected:
                raise ValueError(f"Expected keys {sorted(expected)}, received {sorted(data)}")
            for key in expected:
                if not isinstance(data[key], dict) or not isinstance(data[key].get("pass"), bool):
                    raise ValueError(f"Invalid evaluator result for {key}")
                if not isinstance(data[key].get("reason"), str):
                    raise ValueError(f"Missing reason for {key}")
            return data
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            raise ProviderError(f"Evaluator returned invalid JSON or schema: {exc}") from exc
