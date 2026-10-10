import os
import shutil
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# Config
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
EMBED_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"
GROQ_MODEL = "openai/gpt-oss-20b"
TOP_K = 3
PERSIST_DIR = "./chroma_db_app"
UPLOAD_DIR = "./data/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Embeddings (loaded once at startup)
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBED_MODEL,
            model_kwargs={"device": "cpu"}
        )
    return _embeddings


def load_document(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    docs = loader.load()
    for d in docs:
        d.metadata["source_file"] = os.path.basename(file_path)
    return docs


def ingest_files(file_paths):
    """Load, chunk, embed files and store in ChromaDB. Returns chunk count."""
    all_docs = []
    for path in file_paths:
        all_docs.extend(load_document(path))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(all_docs)
    for i, c in enumerate(chunks):
        c.metadata["chunk_id"] = i

    # Wipe and rebuild vector store
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)

    Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=PERSIST_DIR
    )
    return len(chunks)


def get_vectorstore():
    if not os.path.exists(PERSIST_DIR):
        return None
    return Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=get_embeddings()
    )


def format_docs_with_citations(docs):
    formatted = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source_file", "unknown")
        page = doc.metadata.get("page_label", doc.metadata.get("page", "?"))
        formatted.append(f"[{i}] ({source}, page {page})\n{doc.page_content}")
    return "\n\n".join(formatted)


PROMPT_TEMPLATE = """You are a helpful research assistant that answers questions strictly from the provided context.

RULES:
1. Answer ONLY using the information in the context below.
2. Every factual claim must end with a citation like [1] or [2].
3. If multiple sources support a claim, cite all: [1][3].
4. If the answer is NOT in the context, respond exactly: "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer (with inline citations):"""


def answer_question(question: str):
    """Returns dict with answer and list of sources."""
    vs = get_vectorstore()
    if vs is None:
        return {"answer": "No documents uploaded yet.", "sources": []}

    retriever = vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K}
    )
    docs = retriever.invoke(question)
    context = format_docs_with_citations(docs)

    llm = ChatGroq(
        model_name=GROQ_MODEL,
        temperature=0,
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    sources = []
    for i, d in enumerate(docs, start=1):
        sources.append({
            "n": i,
            "file": d.metadata.get("source_file", "unknown"),
            "page": d.metadata.get("page_label", d.metadata.get("page", "?")),
            "preview": d.page_content[:200].replace("\n", " ").strip(),
        })

    return {"answer": answer, "sources": sources}