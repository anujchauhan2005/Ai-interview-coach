import os
import tempfile
from gtts import gTTS
import streamlit as st


def text_to_speech(text: str) -> str:
    tts = gTTS(text=text, lang="en", slow=False)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp.name)
    return tmp.name


def play_question_audio(question_text: str):
    audio_path = text_to_speech(question_text)
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3")
    os.unlink(audio_path)