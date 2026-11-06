# Trusted knowledge notes: Introduction to RAG

Use these notes as the factual boundary for the beginner lesson.

1. RAG stands for Retrieval-Augmented Generation.
2. A RAG system looks up relevant information from a collection of documents before asking a language model to write an answer.
3. A common pipeline is: prepare documents -> split them into smaller chunks -> create an embedding for each chunk -> store embeddings and text in a searchable vector database -> receive a user question -> embed/search the question -> retrieve relevant chunks -> place the chunks in the model's prompt as context -> generate an answer.
4. An embedding is a numerical representation of text. Text with related meaning often has embeddings that are close in the embedding space.
5. A vector database stores embeddings and supports similarity search. It usually stores or points to the original text as well.
6. A chunk is a small piece of a longer document. Chunking helps retrieve only the most relevant parts instead of sending every document to the model.
7. Context is the information supplied to the language model for the current answer.
8. RAG can make answers more relevant to a chosen knowledge collection and can make it easier to show source references when the system keeps source metadata.
9. RAG does not guarantee that every answer is correct. It can still fail when documents are missing, outdated, poorly split, incorrectly retrieved, or misunderstood by the language model.
10. RAG is useful when answers should use information from a specific or changing collection, such as company policies, course notes, manuals, or product documents.
11. RAG is not the same as model fine-tuning. RAG supplies information at answer time; fine-tuning changes model parameters through additional training.
12. A large language model (LLM) is a model that can understand and generate text. The generator uses the retrieved context to prepare an answer.

Avoid claiming that RAG completely removes hallucinations, guarantees factual answers, or automatically updates the model's training data.
