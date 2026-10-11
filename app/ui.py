import os
import streamlit as st

# Load API key from Streamlit secrets (Cloud) or .env (local)
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

try:
    from app.rag import ingest_files, answer_question, UPLOAD_DIR
except ModuleNotFoundError:
    from rag import ingest_files, answer_question, UPLOAD_DIR

st.set_page_config(page_title="DocuMind", page_icon="📚", layout="wide")

st.title("📚 DocuMind")
st.caption("RAG-based document Q&A with source citations")

# --- Sidebar: upload ---
with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded = st.file_uploader(
        "Choose PDF, DOCX, or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Process", type="primary", disabled=not uploaded):
        with st.spinner("Uploading and embedding..."):
            saved_paths = []
            for f in uploaded:
                dest = os.path.join(UPLOAD_DIR, f.name)
                with open(dest, "wb") as out:
                    out.write(f.getbuffer())
                saved_paths.append(dest)

            try:
                chunk_count = ingest_files(saved_paths)
                st.success(f"✅ Ingested {len(saved_paths)} file(s) ({chunk_count} chunks)")
            except Exception as e:
                st.error(f"Upload failed: {e}")

    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📚 Sources"):
                for s in msg["sources"]:
                    st.markdown(f"**[{s['n']}]** {s['file']} (page {s['page']})")
                    st.caption(s["preview"] + "...")


# --- Chat input ---
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = answer_question(prompt)
                st.markdown(result["answer"])
                if result.get("sources"):
                    with st.expander("📚 Sources"):
                        for s in result["sources"]:
                            st.markdown(f"**[{s['n']}]** {s['file']} (page {s['page']})")
                            st.caption(s["preview"] + "...")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result.get("sources", [])
                })
            except Exception as e:
                st.error(f"Request failed: {e}")