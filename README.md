# Self-Evaluating Lesson Content Generator

**Take-home assessment:** GenAI Engineer — Content Systems  
**Submission topic:** Introduction to RAG (Retrieval-Augmented Generation)

This project builds an agent that generates a beginner lesson, checks it against six binary quality gates, feeds rejection reasons back to the generator, and stops after a maximum of two retries. It also stores reusable lessons from failures in persistent JSON memory.

## 1. What is included?

| File or folder | Purpose |
|---|---|
| `run.py` | Command-line entry point |
| `lesson_agent/agent.py` | Controls generate → evaluate → feedback → retry |
| `lesson_agent/evaluator.py` | Six hard pass/fail checks |
| `lesson_agent/providers.py` | Mock provider and OpenAI API provider |
| `lesson_agent/memory.py` | Saves failure counts and learned prompt rules across runs |
| `data/knowledge_base.md` | Trusted factual notes used to ground the lesson |
| `outputs/final_lesson.md` | Passing beginner lesson from the demo run |
| `outputs/Final_RAG_Beginner_Lesson.docx` | Formatted three-page lesson document for Google Docs / Word upload |
| `outputs/rejection_log.md` | What failed, why it failed, and what changed |
| `outputs/run_report.json` | Machine-readable attempt-by-attempt results |
| `docs/ARCHITECTURE.md` | Design and trade-off explanation |
| `docs/RUBRIC.md` | Complete pass/fail rubric |
| `docs/LOOM_WALKTHROUGH.md` | Suggested 15–20 minute video structure and demo script |
| `tests/` | Automated tests for rejection and passing behaviour |

## 2. Requirements

- Python 3.10 or newer
- No API key is needed for the demo mode
- An OpenAI API key is needed only for live LLM mode

## 3. Run the complete demo (no API key)

Open a terminal in the project folder and run:

```bash
python run.py --demo
```

The demo intentionally produces a weak first lesson. The evaluator rejects it, records the failed checks, and passes the reasons plus learned memory rules into the next generation call. With the mock provider, a prepared passing lesson keeps the loop repeatable without a network connection. With the OpenAI provider, the first response is deliberately weak and the second response is generated live using the rejection feedback. `outputs/run_report.json` records the feedback and memory rules supplied to the mock generation calls.

The demo writes or updates:

```text
outputs/final_lesson.md
outputs/rejection_log.md
outputs/run_report.json
memory/agent_memory.json
```

To run the mock provider without injecting an error:

```bash
python run.py
```

## 4. Run with a real LLM API

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependency:

```bash
pip install -r requirements.txt
```

Set the API key in your terminal. Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="paste-your-key-here"
```

macOS/Linux:

```bash
export OPENAI_API_KEY="paste-your-key-here"
```

Run the agent with live generation and live evaluation:

```bash
python run.py --provider openai --topic "Introduction to RAG" --max-retries 2
```

To demonstrate a deliberate first-attempt failure followed by a live model regeneration:

```bash
python run.py --provider openai --demo --max-retries 2
```

Optionally select another model supported by your account:

```bash
python run.py --provider openai --model "gpt-4o-mini"
```

Keep API keys private. Do not commit `.env` or paste a key into source code.

## 5. Run tests

```bash
python -m unittest discover -s tests -v
```

## 6. How the agent decides to ship

There are six gates: accuracy and grounding, beginner-friendly language, teaching by example, jargon explanations, key-point coverage, and coherent teaching flow. Every gate is boolean. A lesson ships only when **all six pass**. One failure rejects the lesson and creates specific feedback for the next attempt.

The retry count is bounded: the first generation plus no more than two regenerations. The agent therefore always terminates.

## 7. Memory and self-evolution

After every evaluation, the agent stores failed check names, counts, reasons, and a reusable writing rule in `memory/agent_memory.json`. On future runs, the most frequent learned rules are added to the generation prompt. For example, repeated jargon failures strengthen the instruction to define every technical word at first use.

The evaluator rubric is deliberately not rewritten by the agent. Changing the pass bar based on a failure could reward weaker content. The system learns how to meet the same standard, not how to lower it.

## 8. Scope note

The current rubric and trusted knowledge file are specifically designed for the assessment topic, Introduction to RAG. Changing `--topic` changes the displayed topic and generation instruction, but a different subject would also require an updated knowledge file, required concepts, glossary, and rubric checks.

## 9. Important implementation note

The local checks are hard gates in both modes. In OpenAI mode, a separate LLM judge also reviews semantic quality; both the local gate and LLM judge must pass a criterion. In mock mode, the fixed demo judge keeps the demonstration repeatable, while the same local rubric catches the deliberate error. This makes the project testable without network access and shows the full workflow reliably during a video demonstration.

## 10. Publish the GitHub repository

Create an empty repository on GitHub, then run these commands from the project folder (replace the URL with your repository URL):

```bash
git init
git add .
git commit -m "Build self-evaluating RAG lesson generator"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/rag-lesson-agent.git
git push -u origin main
```

For the document link, upload `outputs/Final_RAG_Beginner_Lesson.docx` to Google Drive, open it with Google Docs, and use **Share → General access → Anyone with the link → Viewer** if your assessment rules permit public link access. Copy that share link into the submission form.

