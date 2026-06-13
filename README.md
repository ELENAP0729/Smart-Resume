# Smart Resume Analysis Assistant v5

React + FastAPI + LangGraph MVP for parsing resumes/documents into candidate intelligence notes, matching them against a job description, giving resume improvement suggestions, and saving analysis history.

## Fixes in v5
- Fixes `tools` vs `tool` validation errors.
- Fixes `0.7` vs `70` score validation errors.
- Adds robust normalization layer for LLM output before Pydantic validation.
- Adds history records API and frontend history panel.
- Works without Supabase by saving history into `backend/data/history.json`.

## Backend
```powershell
cd backend
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="your-new-api-key"
uvicorn app.main:app --reload --port 8000
```

## Frontend
Open a new terminal:
```powershell
cd frontend
npm install
npm run dev
```

Open: http://localhost:3000

## Optional Supabase
Run `backend/supabase_schema.sql` in Supabase SQL Editor and set these environment variables:
```powershell
$env:SUPABASE_URL="https://xxxx.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

If these are not set, the app uses local JSON history storage automatically.


## v6 updates
- Main title changed to Smart Resume Analysis Assistant.
- Added English / Chinese output language selector.
- Backend stores selected analysis language in history records.


## v7 updates
- Hero description rewritten to focus on resume-to-job matching.
- Added delete action for analysis history records.
- History records now preserve output language.
