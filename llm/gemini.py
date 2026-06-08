import os
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def get_llm(temperature: float = 0.7):
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY,
        temperature=temperature
    )


def get_fast_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=GROQ_API_KEY,
        temperature=0.2
    )


def invoke_with_retry(llm, prompt, retries=3, wait=30):
    for attempt in range(retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                if attempt < retries - 1:
                    time.sleep(wait)
                else:
                    raise e
            else:
                raise e