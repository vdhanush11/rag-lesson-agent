# Rejection log — RAG (Retrieval-Augmented Generation)

Provider: `mock`  
Attempts used: **2**  
Final status: **PASS**

## Attempt 1 — REJECTED

- **FAIL — accuracy_grounded**: Missing factual safeguard(s): explains embeddings as numbers, does not promise perfect accuracy. LLM judge passed, but a hard local check failed.
- **FAIL — beginner_friendly**: Readability guardrail failed: average sentence length 7.6 words; lesson length 53 words (need <=24 words per sentence and >=450 total words). LLM judge passed, but a hard local check failed.
- **FAIL — teaches_by_example**: Example needs a familiar real-world scenario and at least three numbered steps; found 0 step labels. LLM judge passed, but a hard local check failed.
- **FAIL — jargon_explained**: Missing or unclear definitions: chunk, embedding, vector database, context, retrieval, generation, hallucination, RAG / LLM abbreviation expansion. LLM judge passed, but a hard local check failed.
- **FAIL — key_coverage**: Missing headings: what is rag, why does rag matter, how does rag work, a simple example, what rag cannot do, key words in plain english, quick recap; missing concepts: retrieval-augmented generation, chunk, context, retrieval, generation, large language model. LLM judge passed, but a hard local check failed.
- **FAIL — coherent_flow**: Sections are missing or out of order; use definition → importance → process → example → limits → glossary → recap. LLM judge passed, but a hard local check failed.

## Attempt 2 — PASS

- **PASS — accuracy_grounded**: All required factual anchors are present and the lesson avoids a guarantee. LLM judge: Mock judge: factual checks are handled by the local rubric.
- **PASS — beginner_friendly**: Average sentence length is 12.8 words and lesson length is 974 words; limits are <=24 and >=450. LLM judge: Mock judge: readability checks are handled by the local rubric.
- **PASS — teaches_by_example**: Example contains a familiar scenario and at least three numbered steps. LLM judge: Mock judge: example structure is checked locally.
- **PASS — jargon_explained**: Required technical terms are explained in plain English. LLM judge: Mock judge: glossary definitions are checked locally.
- **PASS — key_coverage**: All required lesson sections and core RAG concepts are covered. LLM judge: Mock judge: required concepts and sections are checked locally.
- **PASS — coherent_flow**: Sections appear in the expected teaching order. LLM judge: Mock judge: section order is checked locally.

## What changed after rejection?

The generator received the failed check names and their reasons before the next attempt. The persistent memory also saved reusable writing rules, such as defining technical words and walking through a real-world example. The rubric stayed unchanged; only the generation guidance improved.
