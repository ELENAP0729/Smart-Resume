from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
import json
from typing import Any, Dict, List, Optional
from .config import settings

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"


def _read_local() -> List[Dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write_local(records: List[Dict[str, Any]]) -> None:
    HISTORY_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def save_history(filename: str, job_description: str, match_score: int, result: Dict[str, Any], language: str = "English") -> Dict[str, Any]:
    record = {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "filename": filename,
        "job_description": job_description or "",
        "match_score": match_score or 0,
        "language": language or "English",
        "result": result,
    }

    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            from supabase import create_client
            client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            resp = client.table("candidate_analysis_history").insert(record).execute()
            if resp.data:
                return resp.data[0]
        except Exception:
            pass

    records = _read_local()
    records.insert(0, record)
    _write_local(records[:100])
    return record


def list_history() -> List[Dict[str, Any]]:
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            from supabase import create_client
            client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            resp = client.table("candidate_analysis_history").select("*").order("created_at", desc=True).limit(100).execute()
            return resp.data or []
        except Exception:
            pass
    return _read_local()


def get_history(record_id: str) -> Optional[Dict[str, Any]]:
    for record in list_history():
        if record.get("id") == record_id:
            return record
    return None


def delete_history(record_id: str) -> bool:
    if settings.supabase_url and settings.supabase_service_role_key:
        try:
            from supabase import create_client
            client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            client.table("candidate_analysis_history").delete().eq("id", record_id).execute()
            return True
        except Exception:
            pass

    records = _read_local()
    before = len(records)
    records = [record for record in records if record.get("id") != record_id]
    _write_local(records)
    return len(records) < before
