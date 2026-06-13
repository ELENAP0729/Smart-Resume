from typing import Any, Dict, List
from .schemas import normalize_category, normalize_score, ensure_list


def normalize_candidate_note_data(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        data = {}

    data.setdefault("profile_summary", "")
    data["extracted_skills"] = ensure_list(data.get("extracted_skills"))
    data["career_fit_suggestions"] = ensure_list(data.get("career_fit_suggestions"))
    data["missing_information"] = ensure_list(data.get("missing_information"))
    data["recommended_follow_up_questions"] = ensure_list(data.get("recommended_follow_up_questions"))

    evidence_map = data.get("evidence_map") or []
    if not isinstance(evidence_map, list):
        evidence_map = []
    clean_evidence = []
    for item in evidence_map:
        if not isinstance(item, dict):
            continue
        item["category"] = normalize_category(item.get("category"))
        item["confidence"] = min(max(normalize_score(item.get("confidence")) / 100, 0), 1)
        item.setdefault("skill", "")
        item.setdefault("evidence", "")
        item.setdefault("source", "Uploaded document")
        clean_evidence.append(item)
    data["evidence_map"] = clean_evidence

    scores = data.get("capability_scores") or []
    if not isinstance(scores, list):
        scores = []
    clean_scores = []
    for item in scores:
        if not isinstance(item, dict):
            continue
        item["score"] = min(max(normalize_score(item.get("score")), 0), 100)
        item.setdefault("capability", "")
        item.setdefault("reason", "")
        clean_scores.append(item)
    data["capability_scores"] = clean_scores

    job = data.get("job_fit_analysis")
    if isinstance(job, dict):
        job["overall_match_score"] = min(max(normalize_score(job.get("overall_match_score")), 0), 100)
        for key in ["matched_requirements", "missing_requirements", "transferable_strengths", "risk_factors", "interview_questions"]:
            job[key] = ensure_list(job.get(key))
        job.setdefault("target_role_summary", "")
        job.setdefault("hiring_recommendation", "")
        data["job_fit_analysis"] = job
    else:
        data["job_fit_analysis"] = None

    opt = data.get("resume_optimization")
    if isinstance(opt, dict):
        for key in ["priority_fixes", "missing_keywords", "rewritten_bullets", "structure_suggestions"]:
            opt[key] = ensure_list(opt.get(key))
        opt.setdefault("summary", "")
        data["resume_optimization"] = opt
    else:
        data["resume_optimization"] = None

    return data
