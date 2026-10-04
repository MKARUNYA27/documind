import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="DocuMind", page_icon="📚", layout="wide")

st.title("📚 DocuMind")
st.caption("RAG-based document Q&A with source citations")

with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded = st.file_uploader(
        "Choose PDF, DOCX, or TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if st.button("Process", type="primary", disabled=not uploaded):
        with st.spinner("Uploading and embedding..."):
            files = [("files", (f.name, f.getvalue())) for f in uploaded]
            try:
                r = requests.post(f"{API_URL}/upload", files=files, timeout=600)
                r.raise_for_status()
                data = r.json()
                st.success(f"✅ {data['message']} ({data['chunks']} chunks)")
            except Exception as e:
                st.error(f"Upload failed: {e}")

    st.divider()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


# Chat history
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

# Input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                r = requests.post(f"{API_URL}/chat", json={"question": prompt}, timeout=120)
                r.raise_for_status()
                data = r.json()
                st.markdown(data["answer"])
                if data.get("sources"):
                    with st.expander("📚 Sources"):
                        for s in data["sources"]:
                            st.markdown(f"**[{s['n']}]** {s['file']} (page {s['page']})")
                            st.caption(s["preview"] + "...")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data["answer"],
                    "sources": data.get("sources", [])
                })
            except Exception as e:
                st.error(f"Request failed: {e}")