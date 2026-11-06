# Final lesson: RAG (Retrieval-Augmented Generation)

# Introduction to RAG (Retrieval-Augmented Generation): A Beginner's Lesson

## 1. What is RAG?

**RAG** means **Retrieval-Augmented Generation**. It is a way to help an AI answer a question by finding useful information first and then writing an answer using that information.

Think about an open-book exam. You read the question, look through your textbook for the useful page, and then write your answer. RAG follows a similar idea: it searches trusted documents first, gives the useful parts to an AI model, and asks the model to answer.

A **large language model (LLM)** is an AI system that can understand and create text. On its own, an LLM may not know the latest information in your private company files or course notes. RAG gives it useful information at the time of the question.

## 2. Why does RAG matter?

Imagine a college has 500 pages of course notes. A student asks, “What is the attendance rule for the final exam?” Sending all 500 pages to the AI every time may be slow, costly, and confusing. RAG searches the notes and sends only the parts that seem useful.

RAG is helpful when answers need information from a particular set of documents, such as company rules, help guides, product manuals, or classroom notes. It can make answers more relevant to those documents. A system can also show where the information came from when it keeps the document names and page details.

RAG does **not** guarantee a correct answer. The AI can still make a mistake when the source files are wrong, old, incomplete, or when the search finds the wrong paragraph.

## 3. How does RAG work?

A basic RAG system has two stages: preparing the documents and answering a question.

### Stage A: Prepare the documents

1. **Collect documents.** Add the files the system is allowed to search, such as PDF notes or help articles.
2. **Split them into chunks.** A **chunk** is a small piece of a longer document. For example, a 20-page guide can be divided into short sections. Smaller pieces help the system find the useful part instead of returning the whole guide.
3. **Create embeddings.** An **embedding** is a list of numbers that represents the meaning of a piece of text. Text with similar meaning often has numbers that are close to one another. This helps the computer search by meaning, not only by exact matching words.
4. **Store them for search.** A **vector database** is a tool that stores these number-based representations and helps find similar ones quickly. The system also keeps the original text so it can send readable information to the AI.

### Stage B: Answer a question

5. **Receive a question.** The student asks, “What is the attendance rule for the final exam?”
6. **Search for useful chunks.** The system turns the question into an embedding and searches for chunks with a similar meaning. This step is called **retrieval**: finding and bringing back useful information.
7. **Give the results to the AI.** The retrieved text is added to the AI's **context**. Context means the information given to the model for this particular answer.
8. **Generate an answer.** The language model reads the question and the retrieved context, then writes a response. This is the **generation** part of RAG.

The simple flow is: **Question → Search documents → Retrieve useful text → Give text to the AI → Generate answer.**

## 4. A simple example

Suppose your college handbook says: “Students must have at least 75% attendance to write the final examination.” The handbook is already added to the RAG system.

**Step 1 — Ask:** You type, “How much attendance do I need for the final exam?”

**Step 2 — Find:** The system searches the handbook and finds the paragraph that mentions 75% attendance. It does not need to send every page of the handbook.

**Step 3 — Answer:** The system gives that paragraph to the language model. The model replies, “You need at least 75% attendance to write the final examination,” and can show the handbook as its source if source details were saved.

This is different from asking an AI to answer from memory alone. The RAG system first looks for information in the selected handbook and then uses the result to prepare its answer.

## 5. What RAG cannot do

RAG is useful, but it is not magic. It may give a poor answer if the needed document was never added, if a document is outdated, or if the search retrieves an unrelated section. The language model may also misunderstand the retrieved text.

To improve a RAG system, teams should keep documents up to date, split them into sensible chunks, test the search results, and check whether answers match their sources. Important answers should still be reviewed when mistakes could cause harm.

## 6. Key words in plain English

- **Retrieval:** finding and bringing back useful information.
- **Generation:** creating a new answer or piece of text.
- **Chunk:** a small piece of a longer document.
- **Embedding:** a list of numbers that represents the meaning of text.
- **Vector database:** a tool that stores embeddings and searches for similar ones.
- **Context:** information given to the AI model for the current answer.
- **Hallucination:** an answer that sounds believable but is false or not supported by the available information.

## 7. Quick recap

RAG means Retrieval-Augmented Generation. It helps an AI answer with information found in selected documents. The system breaks documents into chunks, represents them as embeddings, stores them for search, retrieves useful text for a question, and gives that text to a language model as context. The model then generates an answer. RAG can improve relevance, but it cannot promise that every answer is correct.

**Check your understanding:** If a student asks about a rule in a college handbook, what should happen before the AI writes an answer? The system should search the handbook, retrieve the relevant passage, and give it to the AI as context.
