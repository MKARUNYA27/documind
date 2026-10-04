import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from app.rag import ingest_files, answer_question, UPLOAD_DIR

app = FastAPI(title="DocuMind API", version="1.0")


class ChatRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload(files: list[UploadFile] = File(...)):
    saved_paths = []
    for f in files:
        dest = os.path.join(UPLOAD_DIR, f.filename)
        with open(dest, "wb") as out:
            shutil.copyfileobj(f.file, out)
        saved_paths.append(dest)

    chunk_count = ingest_files(saved_paths)
    return {
        "message": f"Ingested {len(saved_paths)} file(s)",
        "files": [os.path.basename(p) for p in saved_paths],
        "chunks": chunk_count,
    }


@app.post("/chat")
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")
    return answer_question(req.question)