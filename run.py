#!/usr/bin/env python3
"""Run the self-evaluating RAG lesson generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from lesson_agent.agent import LessonAgent, build_provider
from lesson_agent.providers import ProviderError


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")

    parser = argparse.ArgumentParser(description="Generate, evaluate, and revise a beginner lesson.")
    parser.add_argument("--topic", default="RAG (Retrieval-Augmented Generation)", help="Lesson topic")
    parser.add_argument("--provider", choices=["mock", "openai"], default="mock", help="Use local demo or OpenAI API")
    parser.add_argument("--max-retries", type=int, choices=[0, 1, 2], default=2, help="Maximum regeneration attempts")
    parser.add_argument("--demo", action="store_true", help="Inject a deliberate first-attempt quality error")
    parser.add_argument("--model", default=None, help="Override OPENAI_MODEL for API mode")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    try:
        provider = build_provider(args.provider, deliberate_error=args.demo, model=args.model)
        agent = LessonAgent(provider=provider, project_root=root, max_retries=args.max_retries)
        report = agent.run(args.topic)
    except (ProviderError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print("\n=== AGENT RUN SUMMARY ===")
    print(f"Topic: {report['topic']}")
    print(f"Provider: {report['provider']}")
    print(f"Attempts: {report['attempt_count']} / {report['max_retries'] + 1} maximum")
    print(f"Final status: {'PASS' if report['passed'] else 'REJECTED'}")
    for attempt in report["attempts"]:
        print(f"\nAttempt {attempt['attempt']}: {'PASS' if attempt['passed'] else 'REJECTED'}")
        for check in attempt["checks"]:
            print(f"  [{'PASS' if check['passed'] else 'FAIL'}] {check['name']}: {check['reason']}")
    print("\nFiles written:")
    print("  outputs/final_lesson.md")
    print("  outputs/rejection_log.md")
    print("  outputs/run_report.json")
    print("  memory/agent_memory.json")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
