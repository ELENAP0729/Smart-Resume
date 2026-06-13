import json
from typing import Any, Dict, TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from . import __init__  # noqa
from app.config import settings
from app.schemas import CandidateNote
from app.normalizer import normalize_candidate_note_data


class CandidateState(TypedDict, total=False):
    document_text: str
    source_type: str
    job_description: str
    language: str
    cleaned_text: str
    raw_note: Dict[str, Any]
    note: CandidateNote


def get_llm():
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in PowerShell with: $env:OPENAI_API_KEY=\"your-key\"")
    return ChatOpenAI(model=settings.model_name, temperature=0.15, api_key=settings.openai_api_key)


def clean_text_node(state: CandidateState) -> CandidateState:
    text = (state.get("document_text") or "")[:30000]
    state["cleaned_text"] = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return state


def analyse_node(state: CandidateState) -> CandidateState:
    llm = get_llm()
    job_description = state.get("job_description") or ""
    language = state.get("language") or "English"
    language_instruction = "Write every user-facing string in Simplified Chinese." if language.lower().startswith("chinese") or language.startswith("中文") else "Write every user-facing string in clear professional English."
    prompt = f"""
You are Aelpha's Candidate Evidence Intelligence Agent.
Convert the candidate document into strict JSON only. No markdown.
{language_instruction}

Important schema rules:
- evidence_map.category must be one of: technical, soft, domain, tool. Use singular "tool", never "tools".
- all scores must be integers from 0 to 100, not decimals from 0 to 1.
- confidence can be 0 to 1 or 0 to 100.

Candidate document source type: {state.get('source_type', 'uploaded document')}
Candidate document text:
{state.get('cleaned_text', '')}

Output language: {language}

Target job description or requirements:
{job_description if job_description else 'No job description provided. Still provide general career fit analysis.'}

Return JSON with exactly these top-level keys:
{{
  "profile_summary": "string",
  "extracted_skills": ["string"],
  "evidence_map": [
    {{"skill":"string", "category":"technical|soft|domain|tool", "evidence":"string", "source":"string", "confidence": 0.85}}
  ],
  "capability_scores": [
    {{"capability":"Technical execution", "score": 80, "reason":"string"}}
  ],
  "career_fit_suggestions": ["string"],
  "missing_information": ["string"],
  "recommended_follow_up_questions": ["string"],
  "job_fit_analysis": {{
    "target_role_summary": "string",
    "overall_match_score": 70,
    "matched_requirements": ["string"],
    "missing_requirements": ["string"],
    "transferable_strengths": ["string"],
    "risk_factors": ["string"],
    "hiring_recommendation": "string",
    "interview_questions": ["string"]
  }},
  "resume_optimization": {{
    "summary": "string",
    "priority_fixes": ["string"],
    "missing_keywords": ["string"],
    "rewritten_bullets": ["string"],
    "structure_suggestions": ["string"]
  }}
}}
"""
    response = llm.invoke(prompt)
    content = response.content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.lower().startswith("json"):
            content = content[4:].strip()
    try:
        raw = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Model did not return valid JSON: {exc}. Raw response: {content[:1000]}")
    state["raw_note"] = raw
    return state


def validate_node(state: CandidateState) -> CandidateState:
    normalized = normalize_candidate_note_data(state.get("raw_note") or {})
    try:
        state["note"] = CandidateNote.model_validate(normalized)
    except Exception as exc:
        raise ValueError(f"Model returned invalid CandidateNote after normalization: {exc}")
    return state


builder = StateGraph(CandidateState)
builder.add_node("clean_text", clean_text_node)
builder.add_node("analyse", analyse_node)
builder.add_node("validate", validate_node)
builder.set_entry_point("clean_text")
builder.add_edge("clean_text", "analyse")
builder.add_edge("analyse", "validate")
builder.add_edge("validate", END)
candidate_graph = builder.compile()
