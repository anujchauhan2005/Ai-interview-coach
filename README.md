 
#  AI Interview Coach

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)


**An end-to-end AI-powered interview preparation tool that reads your resume,
generates personalized questions, evaluates your answers, and tells you your hire probability.**

[Features](#-features) • [Demo](#-demo) • [Tech Stack](#-tech-stack) • [Setup](#-setup) • [Project Structure](#-project-structure) • [How It Works](#-how-it-works)

</div>

---

##  What is this project?

Most interview prep tools give generic questions.
**AI Interview Coach** reads YOUR resume and generates questions based on YOUR skills, YOUR projects, and YOUR experience.

Then it evaluates your answers like a real interviewer — giving you a score, pointing out weaknesses, checking your STAR method, and showing you a better answer.

It also tells you your **Hire Probability %** based on your resume + interview performance combined.

---

##  Features

| Feature | Description |
|---|---|
|  **Resume Parser** | Upload PDF resume — app extracts all text and skills automatically |
|  **ATS Score Analyzer** | Paste any job description — get keyword match %, missing skills, and bullet point rewrites |
|  **AI Question Generator** | Generates 7 personalized questions based on your resume, role, and selected topics |
|  **Answer Evaluator** | Score out of 10, strengths, weaknesses, improved answer, STAR method check |
|  **Voice Interview Mode** | Hear questions spoken aloud, record your answer, get instant feedback |
|  **Hire Probability** | Calculates realistic hire % with overall grade, 30-day improvement plan |
|  **PDF Report Export** | Download complete session report with all scores and feedback |

---

##  Demo

### Resume Tab — Upload and extract skills
> Upload your PDF resume → app auto-detects skills like Python, SQL, Power BI and generates questions tailored to YOU

### ATS Score Tab — Compare with job description
> Paste any LinkedIn/Naukri job description → get ATS score, missing keywords, and improved bullet points

### Practice Tab — Answer and get evaluated
> Type your answer → AI scores it 1-10, checks STAR method, shows keywords you missed

### Voice Mode — Speak your answer
> Hear the question aloud → record your voice answer → get instant feedback

### Analysis Tab — See your hire probability
> After practicing → get realistic hire % with grade, strengths, gaps, and 30-day plan

---

## 🛠️ Tech Stack

### Core
| Technology | Purpose |
|---|---|
| **Python 3.12** | Core programming language |
| **Streamlit** | Web UI framework — 6 tabs, sidebar, session state |
| **LangChain** | LLM orchestration — unified interface for any AI model |
| **Google Gemini 2.0 Flash** | Primary LLM for question generation and evaluation |
| **Groq (Llama 3.1 8B)** | Backup LLM — 14,400 free requests/day |

### AI & NLP
| Technology | Purpose |
|---|---|
| **Prompt Engineering** | 6 custom prompts for questions, evaluation, ATS, hire probability |
| **RAG (Retrieval Augmented Generation)** | Knowledge base injection for DSA, DBMS, OS, CN topics |
| **JSON Structured Output** | All LLM responses parsed as structured JSON |

### Resume & Voice
| Technology | Purpose |
|---|---|
| **pypdf** | PDF text extraction from uploaded resume |
| **gTTS (Google TTS)** | Convert interview questions to speech (free) |
| **SpeechRecognition** | Convert voice answers to text (Google STT, free) |
| **streamlit-mic-recorder** | Browser microphone capture |

### Utilities
| Technology | Purpose |
|---|---|
| **fpdf2** | Generate PDF session reports |
| **python-dotenv** | Secure API key management via .env file |
| **regex (re)** | Email/phone extraction, JSON cleanup |

---

##  Setup

### Prerequisites
- Python 3.10 or higher
- A free Gemini API key OR a free Groq API key

### Step 1 — Clone the repository
```bash
git clone https://github.com/anujchauhan2005/Ai-interview-coach.git
cd Ai-interview-coach
```

### Step 2 — Create virtual environment
```bash
python -m venv .venv
```

**Activate it:**
- Windows: `.venv\Scripts\activate`
- Mac/Linux: `source .venv/bin/activate`

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Get your free API key

**Option A — Google Gemini (free):**
1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key

**Option B — Groq (more free requests):**
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up free → Create API Key
3. Copy the key
4. In `llm/gemini.py` change to Groq (see note in file)

### Step 5 — Create `.env` file
Create a file named `.env` in the project root:
```
GOOGLE_API_KEY=paste_your_gemini_key_here
```

### Step 6 — Run the app
```bash
streamlit run app.py
```

App opens at **http://localhost:8501** 🎉

---

##  Project Structure

```
Ai-interview-coach/
│
├── app.py                  ← Main Streamlit app (6 tabs, all UI)
├── requirements.txt        ← All dependencies
├── .env                    ← API keys (not pushed to GitHub)
│
├── resume/
│   └── parser.py           ← PDF text extraction + metadata (pypdf)
│
├── llm/
│   └── gemini.py           ← LLM setup (get_llm, get_fast_llm)
│
├── prompts/
│   └── prompts.py          ← 6 prompt templates for all features
│
├── ats/
│   └── scorer.py           ← ATS scoring logic
│
├── voice/
│   ├── tts.py              ← Text to speech (gTTS)
│   └── stt.py              ← Speech to text (SpeechRecognition)
│
├── utils/
│   ├── helpers.py          ← parse_json_safe, score_label, etc.
│   └── report.py           ← PDF report generation (fpdf2)
│
└── knowledge_base/
    ├── dsa.txt             ← DSA concepts for RAG
    ├── dbms.txt            ← Database concepts for RAG
    ├── os.txt              ← Operating Systems for RAG
    ├── cn.txt              ← Computer Networks for RAG
    └── aptitude.txt        ← HR and aptitude questions for RAG
```

---

##  How It Works

```
User uploads PDF Resume
         │
         ▼
resume/parser.py
[pypdf extracts all text]
         │
         ▼
LLM extracts skill tags
[Python, SQL, Power BI...]
         │
         ▼
QUESTION_PROMPT + Resume + Knowledge Base
[LangChain sends to Gemini/Groq]
         │
         ▼
7 Personalized Interview Questions (JSON)
         │
         ▼
User types/speaks answer
         │
         ▼
EVALUATION_PROMPT → LLM
[Score 1-10, STAR check, keywords]
         │
         ▼
ATS_PROMPT + Job Description
[Keyword match, bullet rewrites]
         │
         ▼
HIRE_PROBABILITY_PROMPT
[%, grade, 30-day plan]
         │
         ▼
utils/report.py → PDF Export
[Full session report download]
```

---

##  The 6 Prompt Templates

| Prompt | What it does |
|---|---|
| `QUESTION_PROMPT` | Generates 7 tailored questions using resume + CS knowledge base |
| `EVALUATION_PROMPT` | Scores answer 1-10 with STAR check and keyword analysis |
| `ATS_PROMPT` | Compares resume to job description, gives match % and rewrites |
| `HIRE_PROBABILITY_PROMPT` | Calculates hire % based on resume + interview performance |
| `TOPIC_EXTRACTION_PROMPT` | Extracts skill tags from resume (Python, SQL, etc.) |
| `VOICE_EVAL_PROMPT` | Quick evaluation for voice-recorded answers |

---

##  Free API Limits

| Provider | Model | Free Requests |
|---|---|---|
| Google Gemini | gemini-2.0-flash | 200/day |
| Google Gemini | gemini-1.5-flash | 1,500/day |
| Groq | llama-3.1-8b-instant | 14,400/day |

> **Tip:** If you hit Gemini limits, switch to Groq in `llm/gemini.py` — takes 2 minutes.

---

##  Troubleshooting

**ImportError on startup:**
```bash
Remove-Item -Recurse -Force *\__pycache__ -ErrorAction SilentlyContinue
streamlit run app.py
```

**429 Quota exceeded error:**
Switch to Groq in `llm/gemini.py`:
```python
from langchain_groq import ChatGroq
# Change model to:
return ChatGroq(model="llama-3.1-8b-instant", groq_api_key=GROQ_API_KEY)
```

**Voice mode not working:**
```bash
pip install gtts SpeechRecognition streamlit-mic-recorder
```

---

##  Future Improvements

- [ ] ChromaDB/FAISS for proper vector-based RAG
- [ ] User authentication + PostgreSQL for session history
- [ ] Streaming LLM responses (token by token)
- [ ] Whisper API for better offline speech recognition
- [ ] Deploy on Streamlit Cloud / Hugging Face Spaces
- [ ] Company-specific question modes (Google, Amazon, etc.)

---

##  Author

**Anuj Chauhan**
- GitHub: [@anujchauhan2005](https://github.com/anujchauhan2005)
- Project: [AI Interview Coach](https://github.com/anujchauhan2005/Ai-interview-coach)

---

##  License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

MIT License means: Use it, modify it, share it — just keep the author's name. 

---

<div align="center">

**If this project helped you, please give it a  on GitHub!**

*Built with  using Python, LangChain, and Google Gemini*

</div>
