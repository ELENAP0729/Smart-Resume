from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


def normalize_score(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        value = value.strip().lower().replace("%", "").replace("score:", "")
        if "/" in value:
            value = value.split("/")[0].strip()
        try:
            value = float(value)
        except ValueError:
            return 0
    if isinstance(value, float):
        if 0 <= value <= 1:
            return round(value * 100)
        return round(value)
    if isinstance(value, int):
        return value
    return 0


def normalize_category(value: Any) -> str:
    if value is None:
        return "technical"
    v = str(value).strip().lower().replace("-", "_")
    category_map = {
        "tech": "technical",
        "technical_skill": "technical",
        "technical skills": "technical",
        "technical_skills": "technical",
        "hard skill": "technical",
        "hard skills": "technical",
        "hard_skills": "technical",
        "programming": "technical",
        "engineering": "technical",
        "soft_skill": "soft",
        "soft skills": "soft",
        "soft_skills": "soft",
        "communication": "soft",
        "leadership": "soft",
        "domain_skill": "domain",
        "domain skills": "domain",
        "domain_skills": "domain",
        "industry": "domain",
        "business": "domain",
        "tools": "tool",
        "tooling": "tool",
        "software": "tool",
        "platform": "tool",
        "platforms": "tool",
        "framework": "tool",
        "frameworks": "tool",
        "library": "tool",
        "libraries": "tool",
    }
    v = category_map.get(v, v)
    if v not in {"technical", "soft", "domain", "tool"}:
        return "technical"
    return v


def ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if x is not None]
    if isinstance(value, str):
        if not value.strip():
            return []
        return [x.strip() for x in value.replace(";", ",").split(",") if x.strip()]
    return [str(value)]


class EvidenceItem(BaseModel):
    skill: str = ""
    category: Literal["technical", "soft", "domain", "tool"] = "technical"
    evidence: str = ""
    source: str = "Uploaded document"
    confidence: float = 0.0

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, value):
        return normalize_category(value)

    @field_validator("confidence", mode="before")
    @classmethod
    def validate_confidence(cls, value):
        return min(max(normalize_score(value) / 100, 0), 1)


class CapabilityScore(BaseModel):
    capability: str = ""
    score: int = 0
    reason: str = ""

    @field_validator("score", mode="before")
    @classmethod
    def validate_score(cls, value):
        return min(max(normalize_score(value), 0), 100)


class JobFitAnalysis(BaseModel):
    target_role_summary: str = ""
    overall_match_score: int = 0
    matched_requirements: List[str] = Field(default_factory=list)
    missing_requirements: List[str] = Field(default_factory=list)
    transferable_strengths: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)
    hiring_recommendation: str = ""
    interview_questions: List[str] = Field(default_factory=list)

    @field_validator("overall_match_score", mode="before")
    @classmethod
    def validate_overall_match_score(cls, value):
        return min(max(normalize_score(value), 0), 100)

    @field_validator("matched_requirements", "missing_requirements", "transferable_strengths", "risk_factors", "interview_questions", mode="before")
    @classmethod
    def validate_lists(cls, value):
        return ensure_list(value)


class ResumeOptimization(BaseModel):
    summary: str = ""
    priority_fixes: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    rewritten_bullets: List[str] = Field(default_factory=list)
    structure_suggestions: List[str] = Field(default_factory=list)

    @field_validator("priority_fixes", "missing_keywords", "rewritten_bullets", "structure_suggestions", mode="before")
    @classmethod
    def validate_lists(cls, value):
        return ensure_list(value)


class CandidateNote(BaseModel):
    profile_summary: str = ""
    extracted_skills: List[str] = Field(default_factory=list)
    evidence_map: List[EvidenceItem] = Field(default_factory=list)
    capability_scores: List[CapabilityScore] = Field(default_factory=list)
    career_fit_suggestions: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    recommended_follow_up_questions: List[str] = Field(default_factory=list)
    job_fit_analysis: Optional[JobFitAnalysis] = None
    resume_optimization: Optional[ResumeOptimization] = None

    @field_validator("extracted_skills", "career_fit_suggestions", "missing_information", "recommended_follow_up_questions", mode="before")
    @classmethod
    def validate_lists(cls, value):
        return ensure_list(value)


class HistoryRecord(BaseModel):
    id: str
    created_at: str
    filename: str
    job_description: str = ""
    match_score: int = 0
    result: CandidateNote
