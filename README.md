# 📚 DocuMind — RAG Document Q&A

A Retrieval-Augmented Generation (RAG) chatbot that answers questions from your uploaded documents with **source citations**.

## Features

- 📄 **Multi-format ingestion** — PDF, DOCX, TXT
- 🔍 **Semantic search** using `all-MiniLM-L6-v2` embeddings + ChromaDB
- 💬 **Citations** — every answer cites the source document and page
- 🛡️ **Hallucination guard** — refuses to answer when context is insufficient
- ⚡ **Fast LLM responses** via Groq's LLaMA models

## Architecture
## Tech Stack

- **Backend:** FastAPI, Uvicorn
- **Frontend:** Streamlit
- **Orchestration:** LangChain
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
- **Vector DB:** ChromaDB
- **LLM:** Groq (`openai/gpt-oss-20b`)
- **Deployment:** Docker on Render

## How to Use

1. Upload one or more documents (PDF/DOCX/TXT) via the sidebar
2. Click **Process**
3. Ask questions in the chat
4. Every answer includes `[1]`, `[2]` citations linked to sources
## Setup (Local)

```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
uvicorn app.main:app --port 8000 &
streamlit run app/ui.py