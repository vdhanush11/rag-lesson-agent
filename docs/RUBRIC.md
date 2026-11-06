# Evaluation Rubric — Six Binary Quality Gates

**Decision rule:** PASS only when all six checks pass. No weighted score and no partial credit. In OpenAI mode, a check must pass both its deterministic local gate and the LLM judge.

| ID | Dimension | Hard pass condition | Failure example |
|---|---|---|---|
| R1 | Accurate and grounded | Explains retrieve-before-generate, describes embeddings as numerical representations, and clearly says RAG does not guarantee perfect accuracy. The LLM judge must find no unsupported claim against the trusted notes. | “RAG always gives correct answers.” |
| R2 | Beginner-friendly language | At least 450 words and average sentence length no more than 24 words; the LLM judge must find it understandable for a beginner. | Uses dense technical paragraphs without explaining the idea. |
| R3 | Teaches by example | The example section includes a familiar situation and at least three clearly labelled steps; the LLM judge must find that the example actually demonstrates the workflow. | “A student asks a question. RAG answers it.” |
| R4 | No unexplained jargon | Defines chunk, embedding, vector database, context, retrieval, generation, and hallucination in plain English; expands RAG and LLM. The LLM judge must find the explanations clear. | Uses “embedding” and “vector database” without explanation. |
| R5 | Covers key points | Includes all seven required sections and core concepts: Retrieval-Augmented Generation, chunk, embedding, vector database, context, retrieval, generation, and large language model. The LLM judge must confirm the lesson covers definition, purpose, workflow, and limits. | Explains only what RAG stands for, without the workflow or limitations. |
| R6 | Coherent teaching flow | Sections appear in order: definition → importance → process → example → limitations → glossary → recap; the LLM judge must confirm the explanation flows logically. | Starts with embeddings before explaining what RAG is. |

## Why these gates?

- R1 protects learners from misinformation.
- R2 makes the lesson accessible to the stated audience.
- R3 proves the lesson teaches a process rather than listing terms.
- R4 prevents technical vocabulary from blocking understanding.
- R5 prevents important ideas from being omitted.
- R6 makes the lesson easier to follow from zero background.

## Retry policy

First attempt + maximum two retries. Each failed check produces a named reason. The next generation receives those reasons. The retry limit is enforced in code and cannot exceed two.
