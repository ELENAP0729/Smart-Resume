from pathlib import Path
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.parsers import parse_uploaded_file
from app.agents.candidate_graph import candidate_graph
from app.history_store import save_history, list_history, get_history, delete_history

app = FastAPI(title="Smart Resume Analysis Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyse")
async def analyse_candidate(
    file: UploadFile = File(...),
    job_description: str = Form(""),
    language: str = Form("English"),
):
    suffix = Path(file.filename or "upload.txt").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = Path(tmp.name)
    try:
        text, source_type = parse_uploaded_file(tmp_path, file.filename or "upload")
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file.")
        result_state = candidate_graph.invoke({
            "document_text": text,
            "source_type": source_type,
            "job_description": job_description,
            "language": language,
        })
        note = result_state["note"]
        result = note.model_dump()
        match_score = 0
        if note.job_fit_analysis:
            match_score = note.job_fit_analysis.overall_match_score
        history = save_history(file.filename or "upload", job_description, match_score, result, language)
        return {"result": result, "history_id": history.get("id")}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass


@app.get("/api/history")
def history():
    records = list_history()
    return [
        {
            "id": r.get("id"),
            "created_at": r.get("created_at"),
            "filename": r.get("filename"),
            "job_description": r.get("job_description", ""),
            "language": r.get("language", "English"),
            "match_score": r.get("match_score", 0),
        }
        for r in records
    ]


@app.get("/api/history/{record_id}")
def history_detail(record_id: str):
    record = get_history(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="History record not found")
    return record


@app.delete("/api/history/{record_id}")
def history_delete(record_id: str):
    deleted = delete_history(record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="History record not found")
    return {"deleted": True, "id": record_id}
