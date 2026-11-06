"""Persistent, lightweight memory for learning from repeated failures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MEMORY: dict[str, Any] = {
    "schema_version": 1,
    "total_runs": 0,
    "failure_counts": {},
    "learned_rules": {},
    "recent_failures": [],
}

FAILURE_TO_RULE = {
    "accuracy_grounded": "State only facts supported by the trusted notes; mention limitations and never promise perfect accuracy.",
    "beginner_friendly": "Use short sentences, familiar words, and explain each new idea before using it.",
    "teaches_by_example": "Use one everyday scenario and walk through it in at least three numbered steps.",
    "jargon_explained": "Define every technical term and abbreviation at first use, then repeat the definitions in a plain-English glossary.",
    "key_coverage": "Cover the definition, importance, complete workflow, example, and limitations before the recap.",
    "coherent_flow": "Teach in this order: simple definition, reason to care, preparation, step-by-step workflow, example, limitations, recap.",
}


class PersistentMemory:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return json.loads(json.dumps(DEFAULT_MEMORY))
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or loaded.get("schema_version") != 1:
                raise ValueError("Unsupported memory schema")
            merged = json.loads(json.dumps(DEFAULT_MEMORY))
            merged.update(loaded)
            return merged
        except (OSError, json.JSONDecodeError, ValueError):
            # Preserve a broken file for inspection instead of silently overwriting it.
            backup = self.path.with_suffix(self.path.suffix + ".corrupt")
            if self.path.exists() and not backup.exists():
                self.path.replace(backup)
            return json.loads(json.dumps(DEFAULT_MEMORY))

    def rules_for_prompt(self, limit: int = 6) -> list[str]:
        ranked = sorted(
            self.data.get("learned_rules", {}).items(),
            key=lambda pair: (pair[1].get("count", 0), pair[0]),
            reverse=True,
        )
        return [item[1]["rule"] for item in ranked[:limit]]

    def record_run(self, failed_check_names: list[str], reasons: list[str]) -> None:
        self.data["total_runs"] = int(self.data.get("total_runs", 0)) + 1
        counts = self.data.setdefault("failure_counts", {})
        rules = self.data.setdefault("learned_rules", {})
        for name in failed_check_names:
            counts[name] = int(counts.get(name, 0)) + 1
            current = rules.get(name, {"rule": FAILURE_TO_RULE.get(name, "Fix the failed quality check."), "count": 0})
            current["count"] = int(current.get("count", 0)) + 1
            rules[name] = current
        recent = self.data.setdefault("recent_failures", [])
        if failed_check_names:
            recent.append({"checks": failed_check_names, "reasons": reasons[:6]})
            self.data["recent_failures"] = recent[-20:]
        self.save()

    def save(self) -> None:
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temp_path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        temp_path.replace(self.path)
