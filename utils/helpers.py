import json
import re
import streamlit as st


def parse_json_safe(raw_text: str):
    cleaned = re.sub(r"```json|```", "", raw_text).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None


def score_color(score: int) -> str:
    if score >= 7:
        return "#22c55e"
    elif score >= 5:
        return "#f59e0b"
    else:
        return "#ef4444"


def score_label(score: int) -> str:
    if score >= 9:
        return "Excellent"
    elif score >= 7:
        return "Good"
    elif score >= 5:
        return "Average"
    elif score >= 3:
        return "Below Average"
    else:
        return "Needs Work"


def hire_prob_color(prob: int) -> str:
    if prob >= 70:
        return "green"
    elif prob >= 45:
        return "orange"
    else:
        return "red"


def extract_topics_from_llm(resume_text: str) -> list:
    from llm.gemini import get_fast_llm
    from prompts.prompts import TOPIC_EXTRACTION_PROMPT
    llm = get_fast_llm()
    prompt = TOPIC_EXTRACTION_PROMPT.format(resume=resume_text)
    response = llm.invoke(prompt)
    result = parse_json_safe(response.content)
    if isinstance(result, list):
        return result
    return []