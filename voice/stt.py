import json
import re
import speech_recognition as sr
import tempfile
import os
from llm.gemini import get_fast_llm
from prompts.prompts import VOICE_EVAL_PROMPT


def transcribe_audio(audio_bytes: bytes) -> str:
    recognizer = sr.Recognizer()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"[Error: {e}]"
    finally:
        os.unlink(tmp_path)


def evaluate_voice_answer(question: str, transcribed_answer: str) -> dict:
    llm = get_fast_llm()
    prompt = VOICE_EVAL_PROMPT.format(
        question=question,
        answer=transcribed_answer
    )
    response = llm.invoke(prompt)
    raw = re.sub(r"```json|```", "", response.content).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "score": 0,
            "one_line_verdict": "Could not evaluate. Try again.",
            "top_strength": "",
            "top_improvement": "",
            "follow_up_question": ""
        }