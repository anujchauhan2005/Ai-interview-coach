import json
import re
from llm.gemini import get_fast_llm
from prompts.prompts import ATS_PROMPT


def run_ats_analysis(resume_text: str, job_description: str) -> dict:
    llm = get_fast_llm()
    prompt = ATS_PROMPT.format(
        resume=resume_text,
        job_description=job_description
    )
    response = llm.invoke(prompt)
    raw = response.content.strip()
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "ats_score": 0,
            "hire_probability": 0,
            "verdict": "Could not parse. Try again.",
            "matched_keywords": [],
            "missing_keywords": [],
            "section_scores": {},
            "strengths": [],
            "gaps": [],
            "bullet_rewrites": [],
            "recommendations": []
        }


def get_score_label(score: int) -> str:
    if score >= 80:
        return "Excellent Match"
    elif score >= 65:
        return "Good Match"
    elif score >= 50:
        return "Average Match"
    elif score >= 35:
        return "Weak Match"
    else:
        return "Poor Match"