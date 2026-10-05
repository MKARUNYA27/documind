# 📚 DocuMind — RAG Document Q&A

A Retrieval-Augmented Generation (RAG) chatbot that answers questions from your uploaded documents with **source citations**.

## Features

- 📄 **Multi-format ingestion** — PDF, DOCX, TXT
- 🔍 **Semantic search** using `all-MiniLM-L6-v2` embeddings + ChromaDB
- 💬 **Citations** — every answer cites the source document and page
- 🛡️ **Hallucination guard** — refuses to answer when context is insufficient
- ⚡ **Fast LLM responses** via Groq's LLaMA models

## Architecture
