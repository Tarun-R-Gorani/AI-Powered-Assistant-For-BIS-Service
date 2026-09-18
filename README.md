# AI-Powered Assistant for BIS Services

An AI-powered conversational assistant designed to help users understand and retrieve information from **Bureau of Indian Standards (BIS)** documents and standards.

The system combines **Retrieval-Augmented Generation (RAG)** with a conversational React interface to provide users with simple, relevant, and source-grounded answers from the BIS knowledge base.

---

## 🚀 Project Overview

BIS standards and technical documents can be extensive and difficult to navigate manually.

The **BIS AI Assistant** simplifies this process by allowing users to ask questions in natural language and receive relevant answers grounded in retrieved BIS documents.

### Key Capabilities

- 🤖 AI-powered question answering
- 📚 BIS standards knowledge base
- 🔎 Retrieval-Augmented Generation (RAG)
- 🧠 Semantic document retrieval
- 💬 Conversational chat interface
- 📌 Source-grounded responses
- 📖 Retrieved BIS source references
- ✨ Structured and readable AI responses
- 📱 Responsive user interface

---

## ✨ Features

### 💬 Conversational BIS Assistant

Users can ask questions about BIS standards using natural language.

Example:

> What about National Flag of India?

The assistant retrieves relevant information from the BIS knowledge base and generates a grounded response.

---

### 🔎 Retrieval-Augmented Generation

The system follows a RAG-based workflow:

1. User submits a question.
2. The question is converted into an embedding.
3. Relevant BIS document chunks are retrieved from the vector index.
4. Retrieved context is provided to the language model.
5. The model generates an answer based on the retrieved information.
6. Relevant BIS sources are displayed alongside the response.

This helps reduce unsupported or hallucinated answers.

---

### 📚 Source-Grounded Answers

Each AI response can include the BIS documents or standards retrieved during the search.

The interface displays:

- BIS Standard ID
- Document title / description
- Retrieved source information

This allows users to verify the information used to generate the answer.

---

### ✨ Structured Response Formatting

AI responses are presented using:

- Clear headings
- Bullet points
- Highlighted BIS standard references
- Readable spacing
- Source sections
- Copy-answer functionality

This makes technical BIS information easier to understand.

---

### 🖥️ Modern React Interface

The frontend provides:

- Clean conversational UI
- Example questions
- Responsive layout
- User and assistant message bubbles
- BIS source cards
- Copy response functionality
- Loading/error handling
- Mobile-friendly design

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │        User         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │  Conversational UI  │
                    └──────────┬──────────┘
                               │
                               │ HTTP POST
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │     REST API        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Query Processing   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Embedding Model   │
                    │ Semantic Retrieval  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FAISS Vector      │
                    │       Index         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Relevant BIS        │
                    │ Document Chunks     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       LLM           │
                    │ Grounded Generation │
                    └──────────┬──────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │   Answer + Retrieved Sources    │
              └─────────────────────────────────┘
