"""Hard pass/fail rubric combining deterministic checks and an optional LLM judge."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    reason: str
    evidence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Evaluation:
    passed: bool
    checks: list[CheckResult]

    @property
    def failures(self) -> list[CheckResult]:
        return [check for check in self.checks if not check.passed]

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "checks": [c.to_dict() for c in self.checks]}


REQUIRED_HEADINGS = [
    "what is rag", "why does rag matter", "how does rag work",
    "a simple example", "what rag cannot do", "key words in plain english",
    "quick recap",
]

REQUIRED_CONCEPTS = [
    "retrieval-augmented generation", "chunk", "embedding", "vector database",
    "context", "retrieval", "generation", "large language model",
]

JARGON_DEFINITIONS = {
    "chunk": ["small piece", "smaller piece", "short piece"],
    "embedding": ["list of numbers", "numerical representation", "number-based representation"],
    "vector database": ["stores embeddings", "stores vectors", "searches for similar", "tool that stores", "stores these number-based representations"],
    "context": ["information given", "information supplied", "text given"],
    "retrieval": ["finding and bringing", "find and bring", "searching for"],
    "generation": ["creating a new answer", "writing an answer", "create an answer"],
    "hallucination": ["sounds believable but is false", "sounds true but isn't", "not supported"],
}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _heading_present(text: str, heading: str) -> bool:
    pattern = r"^#{1,4}\s+.*" + re.escape(heading) + r".*$"
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is not None


def _sentence_average_words(text: str) -> float:
    cleaned = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", cleaned) if s.strip()]
    if not sentences:
        return 999.0
    counts = [len(re.findall(r"\b[\w'-]+\b", s)) for s in sentences]
    return sum(counts) / len(counts)


def _definition_exists(text: str, term: str, clues: list[str]) -> bool:
    # Check the explicit glossary first. This avoids mistaking the expansion
    # "Retrieval-Augmented Generation" for an unexplained use of "retrieval".
    glossary_match = re.search(
        r"^#{1,4}\s+.*key words in plain english.*$", text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if glossary_match:
        glossary_tail = text[glossary_match.end():]
        recap_match = re.search(r"^#{1,4}\s+.*quick recap.*$", glossary_tail, flags=re.IGNORECASE | re.MULTILINE)
        glossary = glossary_tail[:recap_match.start()] if recap_match else glossary_tail
        escaped_term = re.escape(term)
        for line in glossary.splitlines():
            if re.search(r"\b" + escaped_term + r"\b", line, flags=re.IGNORECASE):
                normalized_line = _normalise(line)
                if any(clue in normalized_line for clue in clues):
                    return True

    # Also accept a clear definition within a short distance of the first use.
    normalized = _normalise(text)
    position = normalized.find(term)
    if position < 0:
        return False
    nearby = normalized[position: position + 320]
    return any(clue in nearby for clue in clues)


class RubricEvaluator:
    """All criteria are binary; an overall pass requires all six checks to pass."""

    def evaluate(self, topic: str, lesson: str, knowledge: str, judge: dict[str, Any] | None = None) -> Evaluation:
        normalized = _normalise(lesson)
        checks: list[CheckResult] = []

        # 1) Accuracy: enforce key facts and limitations locally, then combine with judge.
        fact_anchors = {
            "explains retrieve-before-generate": "retriev" in normalized and "generat" in normalized,
            "explains embeddings as numbers": "embedding" in normalized and ("list of numbers" in normalized or "numerical representation" in normalized or "number" in normalized),
            "does not promise perfect accuracy": any(p in normalized for p in ["does not guarantee", "cannot guarantee", "does not promise", "cannot promise", "not guarantee"]),
        }
        missing_facts = [name for name, ok in fact_anchors.items() if not ok]
        local_accuracy = not missing_facts
        checks.append(self._combine(
            "accuracy_grounded", local_accuracy,
            "All required factual anchors are present and the lesson avoids a guarantee." if local_accuracy else "Missing factual safeguard(s): " + ", ".join(missing_facts) + ".",
            "; ".join(name for name, ok in fact_anchors.items() if ok), judge,
        ))

        # 2) Beginner-friendly language: use measurable readability as a guardrail.
        avg_words = _sentence_average_words(lesson)
        word_count = len(re.findall(r"\b[\w'-]+\b", lesson))
        local_beginner = avg_words <= 24 and word_count >= 450
        checks.append(self._combine(
            "beginner_friendly", local_beginner,
            f"Average sentence length is {avg_words:.1f} words and lesson length is {word_count} words; limits are <=24 and >=450." if local_beginner else f"Readability guardrail failed: average sentence length {avg_words:.1f} words; lesson length {word_count} words (need <=24 words per sentence and >=450 total words).",
            f"average_sentence_words={avg_words:.1f}; word_count={word_count}", judge,
        ))

        # 3) Example: require a tangible scenario and a three-step walk-through.
        example_section = self._section(lesson, "a simple example", "what rag cannot do")
        steps = len(re.findall(r"\bstep\s*[1-3]\b", example_section, flags=re.IGNORECASE))
        scenario_words = any(w in example_section.lower() for w in ["college", "student", "handbook", "library", "shop", "customer", "school"])
        local_example = steps >= 3 and scenario_words
        checks.append(self._combine(
            "teaches_by_example", local_example,
            "Example contains a familiar scenario and at least three numbered steps." if local_example else f"Example needs a familiar real-world scenario and at least three numbered steps; found {steps} step labels.",
            f"step_labels={steps}; familiar_scenario={scenario_words}", judge,
        ))

        # 4) Jargon: required words must be explained near where introduced.
        missing_definitions = [term for term, clues in JARGON_DEFINITIONS.items() if not _definition_exists(lesson, term, clues)]
        # RAG and LLM must also be expanded at first use.
        acronym_ok = "retrieval-augmented generation" in normalized and "large language model" in normalized
        local_jargon = not missing_definitions and acronym_ok
        checks.append(self._combine(
            "jargon_explained", local_jargon,
            "Required technical terms are explained in plain English." if local_jargon else "Missing or unclear definitions: " + ", ".join(missing_definitions + ([] if acronym_ok else ["RAG / LLM abbreviation expansion"])) + ".",
            "checked: " + ", ".join(JARGON_DEFINITIONS.keys()), judge,
        ))

        # 5) Coverage: required sections plus key workflow vocabulary.
        missing_headings = [heading for heading in REQUIRED_HEADINGS if not _heading_present(lesson, heading)]
        missing_concepts = [term for term in REQUIRED_CONCEPTS if term not in normalized]
        local_coverage = not missing_headings and not missing_concepts
        checks.append(self._combine(
            "key_coverage", local_coverage,
            "All required lesson sections and core RAG concepts are covered." if local_coverage else "Missing headings: " + (", ".join(missing_headings) or "none") + "; missing concepts: " + (", ".join(missing_concepts) or "none") + ".",
            f"headings={len(REQUIRED_HEADINGS)-len(missing_headings)}/{len(REQUIRED_HEADINGS)}; concepts={len(REQUIRED_CONCEPTS)-len(missing_concepts)}/{len(REQUIRED_CONCEPTS)}", judge,
        ))

        # 6) Coherent flow: headings must appear in the required instructional order.
        positions = [self._heading_position(lesson, heading) for heading in REQUIRED_HEADINGS]
        local_flow = all(position >= 0 for position in positions) and positions == sorted(positions)
        checks.append(self._combine(
            "coherent_flow", local_flow,
            "Sections appear in the expected teaching order." if local_flow else "Sections are missing or out of order; use definition → importance → process → example → limits → glossary → recap.",
            "heading_positions=" + ",".join(str(p) for p in positions), judge,
        ))

        return Evaluation(passed=all(c.passed for c in checks), checks=checks)

    @staticmethod
    def _combine(name: str, local_pass: bool, local_reason: str, evidence: str, judge: dict[str, Any] | None) -> CheckResult:
        if judge is None:
            return CheckResult(name, local_pass, local_reason, evidence)
        judged = judge.get(name, {})
        ai_pass = judged.get("pass") is True
        ai_reason = judged.get("reason", "LLM judge supplied no reason.")
        passed = local_pass and ai_pass
        if passed:
            reason = local_reason + " LLM judge: " + ai_reason
        elif not local_pass and not ai_pass:
            reason = local_reason + " LLM judge also failed: " + ai_reason
        elif not local_pass:
            reason = local_reason + " LLM judge passed, but a hard local check failed."
        else:
            reason = "LLM judge failed: " + ai_reason
        return CheckResult(name, passed, reason, evidence)

    @staticmethod
    def _section(lesson: str, start_heading: str, end_heading: str) -> str:
        start = re.search(r"^#{1,4}\s+.*" + re.escape(start_heading) + r".*$", lesson, flags=re.I | re.M)
        if not start:
            return ""
        tail = lesson[start.end():]
        end = re.search(r"^#{1,4}\s+.*" + re.escape(end_heading) + r".*$", tail, flags=re.I | re.M)
        return tail[:end.start()] if end else tail

    @staticmethod
    def _heading_position(lesson: str, heading: str) -> int:
        match = re.search(r"^#{1,4}\s+.*" + re.escape(heading) + r".*$", lesson, flags=re.I | re.M)
        return match.start() if match else -1
