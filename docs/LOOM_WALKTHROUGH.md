# Loom Walkthrough Script (15–20 Minutes)

Record with your face visible and your screen shared. Speak slowly and use your own words. The suggested timing is flexible; show the actual terminal output rather than only describing it.

## 0:00–2:00 — Introduction

“Hi, I’m Dhanush. This is my take-home assessment for the GenAI Engineer — Content Systems role. I built a self-evaluating lesson generator. It does not only generate a lesson. It checks the lesson against six pass/fail rules, rejects weak content, sends the reasons back to the generator, and retries up to two times.”

Show the project folder and README.

## 2:00–5:00 — Architecture

Open `docs/ARCHITECTURE.md` and explain the flow:

1. Topic and trusted knowledge enter the system.
2. The generator writes the lesson.
3. The evaluator checks six criteria.
4. If any check fails, feedback goes back to generation.
5. Memory stores what failed so future runs can improve.
6. A passing lesson, rejection log, and JSON report are saved.

Explain that the rubric stays fixed while the prompt guidance learns from failures.

## 5:00–8:00 — Explain the code

Open these files in order:

- `run.py`: command-line entry point and retry setting.
- `lesson_agent/agent.py`: the generate/evaluate/retry loop.
- `lesson_agent/evaluator.py`: the six hard checks.
- `lesson_agent/memory.py`: persistent failure memory.
- `lesson_agent/providers.py`: offline demo and live API provider.

Avoid reading every line. Explain the responsibility of each file.

## 8:00–12:00 — Run the deliberate-error demo

In a terminal opened at the repository root, run:

```bash
python run.py --demo
```

Point out that the mock provider deliberately returns a poor first lesson. Show the failed checks in the terminal. Explain that the system does not ship it because all six checks must pass.

Then show the next attempt. The retry call receives the failed reasons and the rules learned in memory. The mock provider returns a prepared passing lesson to keep the demonstration deterministic. If you have configured an API key, use this stronger live-model demonstration instead:

```bash
python run.py --provider openai --demo --max-retries 2
```

In this mode, the injected weak draft is evaluated, and the live model writes the next version using the rejection feedback. Point out the final PASS and bounded attempt count. Open `outputs/run_report.json` to show the feedback and memory rules received by each mock generation call (or describe the feedback sent in API mode).

## 12:00–15:00 — Inspect outputs and memory

Open:

- `outputs/rejection_log.md`: what failed and why.
- `outputs/final_lesson.md`: the final beginner lesson.
- `outputs/run_report.json`: machine-readable attempt history.
- `memory/agent_memory.json`: persistent failure counts and learned prompt rules.

Explain how a later run can reuse the rules saved from earlier failures.

## 15:00–17:00 — Tests and API mode

Run:

```bash
python -m unittest discover -s tests -v
```

Explain that mock mode makes the assessment reproducible without an API key. Briefly show the OpenAI command in the README. Do not reveal your API key on screen.

## 17:00–19:00 — Design choices and limitations

Explain:

- Hybrid evaluation: code checks objective requirements; an LLM judge checks meaning.
- All checks are binary; no score averaging.
- Maximum two retries guarantees termination.
- Memory improves generation instructions, but does not lower the rubric.
- The current knowledge source is a small trusted notes file; a production version could retrieve from a document collection and preserve citations.

## 19:00–20:00 — Closing

“To summarise, the project demonstrates the complete content quality loop: generate, evaluate, reject when necessary, learn from the failure, regenerate, and ship only when every required check passes. Thank you.”

## Recording checklist

- [ ] Face visible and camera enabled.
- [ ] Screen shared with terminal and code editor visible.
- [ ] Run `python run.py --demo` live.
- [ ] Clearly show at least one deliberate failure.
- [ ] Show the rejection reason and regenerated passing lesson.
- [ ] Show the final lesson and persistent memory.
- [ ] Do not show API keys, passwords, or private account details.
