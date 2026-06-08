import json
import re
import streamlit as st
from datetime import datetime

from resume.parser import extract_resume_text, extract_resume_metadata
from llm.gemini import get_llm, get_fast_llm
from prompts.prompts import (
    QUESTION_PROMPT,
    EVALUATION_PROMPT,
    HIRE_PROBABILITY_PROMPT,
    TOPIC_EXTRACTION_PROMPT
)
from ats.scorer import run_ats_analysis, get_score_label
from utils.helpers import parse_json_safe, score_color, score_label, hire_prob_color
from utils.report import generate_pdf_report

# ── Try importing voice modules (optional) ────────────────────────
try:
    from voice.tts import play_question_audio
    from voice.stt import transcribe_audio, evaluate_voice_answer
    from streamlit_mic_recorder import mic_recorder
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header { color: #666; font-size: 0.95rem; margin-bottom: 1.5rem; }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .score-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-green { background: #dcfce7; color: #166534; }
    .badge-orange { background: #fef3c7; color: #92400e; }
    .badge-red { background: #fee2e2; color: #991b1b; }
    .question-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.6rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .question-card:hover { border-color: #667eea; box-shadow: 0 2px 8px rgba(102,126,234,0.15); }
    .keyword-chip {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.78rem;
        margin: 2px;
    }
    .chip-matched { background: #dcfce7; color: #166534; }
    .chip-missing { background: #fee2e2; color: #991b1b; }
    .section-label {
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.5rem;
    }
    .stProgress > div > div > div > div { border-radius: 999px; }
    div[data-testid="stMetric"] { background: #f8fafc; border-radius: 10px; padding: 0.6rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
defaults = {
    "resume_text": "",
    "resume_metadata": {},
    "topics": [],
    "questions": [],
    "selected_q_idx": -1,
    "answer_history": [],
    "ats_result": {},
    "hire_result": {},
    "active_tab": "Resume",
    "voice_transcript": "",
    "company_role": "Software Engineer / Data Analyst",
    "company_type": "Product Startup"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎯 AI Interview Coach")
    st.markdown("---")

    st.markdown("**Target Role**")
    st.session_state.company_role = st.text_input(
        "Company / Role",
        value=st.session_state.company_role,
        placeholder="e.g. Google SDE Intern",
        label_visibility="collapsed"
    )

    st.session_state.company_type = st.selectbox(
        "Company Type",
        ["Product Startup", "FAANG / Big Tech", "MNC / Service", "Government / PSU", "Consulting"]
    )

    st.markdown("---")
    st.markdown("**Question Types**")
    q_types = {
        "Technical": st.checkbox("Technical", value=True),
        "Behavioral": st.checkbox("Behavioral", value=True),
        "DSA / CS Fundamentals": st.checkbox("DSA / CS Fundamentals", value=False),
        "HR / Culture": st.checkbox("HR / Culture", value=False),
        "Situational": st.checkbox("Situational", value=False),
    }
    selected_types = [k for k, v in q_types.items() if v]

    st.markdown("---")

    # Session stats
    if st.session_state.answer_history:
        scores = [h["score"] for h in st.session_state.answer_history]
        avg = sum(scores) / len(scores)
        st.markdown(f"**Session Stats**")
        st.markdown(f"- Practiced: **{len(scores)}** questions")
        st.markdown(f"- Avg Score: **{avg:.1f}/10**")
        st.markdown(f"- Best: **{max(scores)}/10**")

        if st.session_state.ats_result.get("ats_score"):
            st.markdown(f"- ATS Score: **{st.session_state.ats_result['ats_score']}/100**")

    st.markdown("---")

    # PDF Export
    if st.session_state.answer_history:
        if st.button("📄 Export PDF Report", use_container_width=True):
            with st.spinner("Generating report..."):
                pdf_bytes = generate_pdf_report(
                    candidate_name=st.session_state.resume_metadata.get("name", "Candidate"),
                    resume_summary=st.session_state.resume_text[:500],
                    questions_history=st.session_state.answer_history,
                    ats_result=st.session_state.ats_result,
                    hire_probability=st.session_state.hire_result
                )
            st.download_button(
                label="⬇️ Download Report",
                data=pdf_bytes,
                file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# ─────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-header">🎯 AI Interview Coach</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Resume Analysis · ATS Scoring · AI Interview Questions · Voice Practice · Hire Probability</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_resume, tab_ats, tab_questions, tab_practice, tab_voice, tab_analysis = st.tabs([
    "📄 Resume",
    "🔍 ATS Score",
    "❓ Questions",
    "✍️ Practice",
    "🎙️ Voice Mode",
    "📊 Analysis"
])


# ══════════════════════════════════════════════
# TAB 1: RESUME UPLOAD
# ══════════════════════════════════════════════
with tab_resume:
    st.subheader("Upload Your Resume")

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF)",
        type=["pdf"],
        help="Upload your resume in PDF format to get started"
    )

    if uploaded_file:
        with st.spinner("Extracting resume text..."):
            resume_text = extract_resume_text(uploaded_file)
            st.session_state.resume_text = resume_text
            st.session_state.resume_metadata = extract_resume_metadata(resume_text)

        st.success("✅ Resume uploaded successfully!")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Resume Preview**")
            st.text_area(
                "Content",
                resume_text,
                height=250,
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**Detected Sections**")
            for section in st.session_state.resume_metadata.get("sections", []):
                st.markdown(f"✓ {section}")

            st.markdown("**Contact Info**")
            if st.session_state.resume_metadata.get("email"):
                st.markdown(f"📧 {st.session_state.resume_metadata['email']}")
            if st.session_state.resume_metadata.get("phone"):
                st.markdown(f"📞 {st.session_state.resume_metadata['phone']}")

        st.markdown("---")

        # Topic extraction
        if st.button("🔍 Extract Skills & Generate Questions", use_container_width=True, type="primary"):
            with st.spinner("Analyzing resume and extracting topics..."):
                llm = get_fast_llm()
                topic_prompt = TOPIC_EXTRACTION_PROMPT.format(resume=resume_text)
                topic_resp = llm.invoke(topic_prompt)
                topics = parse_json_safe(topic_resp.content)
                st.session_state.topics = topics if isinstance(topics, list) else []

            with st.spinner("Generating tailored interview questions..."):
                llm = get_llm()
                q_prompt = QUESTION_PROMPT.format(
                    resume=resume_text,
                    company_role=st.session_state.company_role,
                    question_types=", ".join(selected_types) if selected_types else "Technical, Behavioral",
                    topics=", ".join(st.session_state.topics)
                )
                q_resp = llm.invoke(q_prompt)
                questions = parse_json_safe(q_resp.content)
                if isinstance(questions, list):
                    st.session_state.questions = questions
                    st.success(f"✅ Generated {len(questions)} questions! Go to the Questions tab.")
                else:
                    st.error("Failed to parse questions. Try again.")

    elif not st.session_state.resume_text:
        st.info("👆 Please upload your resume PDF to get started.")

    # Show topics if already extracted
    if st.session_state.topics:
        st.markdown("**Detected Skills**")
        chips_html = " ".join([
            f'<span class="keyword-chip chip-matched">{t}</span>'
            for t in st.session_state.topics
        ])
        st.markdown(chips_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2: ATS SCORE ANALYZER
# ══════════════════════════════════════════════
with tab_ats:
    st.subheader("🔍 ATS Score Analyzer")
    st.markdown("Paste a job description to see how well your resume matches.")

    if not st.session_state.resume_text:
        st.warning("⚠️ Please upload your resume in the Resume tab first.")
    else:
        job_desc = st.text_area(
            "Paste Job Description Here",
            height=200,
            placeholder="Paste the full job description from LinkedIn, Naukri, etc..."
        )

        if st.button("🚀 Analyze ATS Score", type="primary", use_container_width=True):
            if not job_desc.strip():
                st.error("Please paste a job description.")
            else:
                with st.spinner("Running ATS analysis... this takes 10-15 seconds"):
                    result = run_ats_analysis(st.session_state.resume_text, job_desc)
                    st.session_state.ats_result = result

        if st.session_state.ats_result:
            r = st.session_state.ats_result
            st.markdown("---")

            # ── Top metrics ──
            c1, c2, c3, c4 = st.columns(4)
            ats = r.get("ats_score", 0)
            hire = r.get("hire_probability", 0)

            c1.metric("ATS Score", f"{ats}/100", get_score_label(ats))
            c2.metric("Hire Probability", f"{hire}%",
                      "High" if hire >= 65 else "Medium" if hire >= 40 else "Low")
            c3.metric("Matched Keywords", len(r.get("matched_keywords", [])))
            c4.metric("Missing Keywords", len(r.get("missing_keywords", [])))

            st.markdown(f"**Verdict:** {r.get('verdict', '')}")

            # ── Section scores ──
            st.markdown("---")
            st.markdown("**Section-wise Scores**")
            section_scores = r.get("section_scores", {})
            if section_scores:
                cols = st.columns(len(section_scores))
                for col, (key, val) in zip(cols, section_scores.items()):
                    label = key.replace("_", " ").title()
                    col.markdown(f"**{label}**")
                    col.progress(int(val) / 100)
                    col.markdown(f"{val}%")

            # ── Keywords ──
            st.markdown("---")
            col_match, col_miss = st.columns(2)

            with col_match:
                st.markdown("**✅ Matched Keywords**")
                if r.get("matched_keywords"):
                    chips = " ".join([
                        f'<span class="keyword-chip chip-matched">{k}</span>'
                        for k in r["matched_keywords"]
                    ])
                    st.markdown(chips, unsafe_allow_html=True)

            with col_miss:
                st.markdown("**❌ Missing Keywords**")
                if r.get("missing_keywords"):
                    chips = " ".join([
                        f'<span class="keyword-chip chip-missing">{k}</span>'
                        for k in r["missing_keywords"]
                    ])
                    st.markdown(chips, unsafe_allow_html=True)

            # ── Bullet rewrites ──
            if r.get("bullet_rewrites"):
                st.markdown("---")
                st.markdown("**✏️ Suggested Bullet Point Rewrites**")
                for item in r["bullet_rewrites"]:
                    with st.expander(f"🔄 {item.get('original', '')[:60]}..."):
                        st.markdown(f"**Original:** {item.get('original', '')}")
                        st.markdown(f"**Improved:** ✨ {item.get('improved', '')}")

            # ── Recommendations ──
            if r.get("recommendations"):
                st.markdown("---")
                st.markdown("**💡 Recommendations**")
                for rec in r["recommendations"]:
                    st.markdown(f"→ {rec}")

            # ── Strengths and gaps ──
            col_s, col_g = st.columns(2)
            with col_s:
                if r.get("strengths"):
                    st.markdown("**💪 Strengths**")
                    for s in r["strengths"]:
                        st.markdown(f"✓ {s}")
            with col_g:
                if r.get("gaps"):
                    st.markdown("**⚠️ Gaps**")
                    for g in r["gaps"]:
                        st.markdown(f"• {g}")


# ══════════════════════════════════════════════
# TAB 3: QUESTIONS
# ══════════════════════════════════════════════
with tab_questions:
    st.subheader("Interview Questions")

    if not st.session_state.questions:
        st.info("📄 Upload your resume and click 'Extract Skills & Generate Questions' first.")
    else:
        st.markdown(f"Generated **{len(st.session_state.questions)}** questions for **{st.session_state.company_role}**")

        col_regen, col_space = st.columns([1, 4])
        with col_regen:
            if st.button("🔄 Regenerate"):
                with st.spinner("Regenerating..."):
                    llm = get_llm()
                    q_prompt = QUESTION_PROMPT.format(
                        resume=st.session_state.resume_text,
                        company_role=st.session_state.company_role,
                        question_types=", ".join(selected_types) if selected_types else "Technical, Behavioral",
                        topics=", ".join(st.session_state.topics)
                    )
                    q_resp = llm.invoke(q_prompt)
                    questions = parse_json_safe(q_resp.content)
                    if isinstance(questions, list):
                        st.session_state.questions = questions
                    st.rerun()

        st.markdown("---")

        for i, q in enumerate(st.session_state.questions):
            diff = q.get("difficulty", "medium")
            diff_color = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "🟡")

            with st.container():
                col_q, col_btn = st.columns([5, 1])
                with col_q:
                    st.markdown(
                        f"**Q{i+1}.** [{q.get('type','').upper()}] {diff_color} "
                        f"`{q.get('topic','')}`"
                    )
                    st.markdown(q.get("question", ""))
                with col_btn:
                    if st.button("Practice →", key=f"prac_{i}"):
                        st.session_state.selected_q_idx = i
                        st.info("Go to the Practice tab to answer this question!")

                st.markdown("---")


# ══════════════════════════════════════════════
# TAB 4: PRACTICE (TEXT)
# ══════════════════════════════════════════════
with tab_practice:
    st.subheader("✍️ Practice — Text Mode")

    if not st.session_state.questions:
        st.info("Generate questions first from the Resume tab.")
    else:
        # Question selector
        q_options = [
            f"Q{i+1}: {q['question'][:60]}..."
            for i, q in enumerate(st.session_state.questions)
        ]
        selected_idx = st.selectbox(
            "Select Question",
            range(len(q_options)),
            format_func=lambda i: q_options[i],
            index=max(0, st.session_state.selected_q_idx)
        )
        st.session_state.selected_q_idx = selected_idx

        current_q = st.session_state.questions[selected_idx]

        # Show question
        st.markdown("**Question:**")
        st.info(current_q["question"])

        # Timer hint
        st.caption(
            f"Type: {current_q.get('type','').title()} | "
            f"Difficulty: {current_q.get('difficulty','medium').title()} | "
            f"Topic: {current_q.get('topic','')}"
        )

        # Answer input
        answer = st.text_area(
            "Your Answer",
            height=180,
            placeholder="Write your answer here. For behavioral questions, use STAR: Situation → Task → Action → Result",
            key=f"ans_{selected_idx}"
        )

        col1, col2 = st.columns([1, 4])
        with col1:
            evaluate = st.button("🤖 Evaluate", type="primary", use_container_width=True)

        if evaluate:
            if not answer.strip():
                st.error("Please write an answer before evaluating.")
            else:
                with st.spinner("Evaluating your answer..."):
                    llm = get_llm()
                    eval_prompt = EVALUATION_PROMPT.format(
                        question=current_q["question"],
                        question_type=current_q.get("type", "technical"),
                        answer=answer
                    )
                    eval_resp = llm.invoke(eval_prompt)
                    evaluation = parse_json_safe(eval_resp.content)

                if evaluation:
                    score = evaluation.get("score", 0)

                    # Store in history
                    st.session_state.answer_history.append({
                        "question": current_q["question"],
                        "type": current_q.get("type", ""),
                        "topic": current_q.get("topic", ""),
                        "answer": answer,
                        "score": score,
                        "strengths": evaluation.get("strengths", ""),
                        "weaknesses": evaluation.get("weaknesses", ""),
                        "improved_answer": evaluation.get("improved_answer", ""),
                        "timestamp": datetime.now().strftime("%H:%M")
                    })

                    # Display evaluation
                    st.markdown("---")
                    st.markdown("### Evaluation Result")

                    m1, m2, m3 = st.columns(3)
                    m1.metric("Score", f"{score}/10", score_label(score))
                    m2.metric("Verdict", evaluation.get("verdict", "")[:30])
                    m3.metric("Keywords Used", len(evaluation.get("keywords_used", [])))

                    col_s, col_w = st.columns(2)
                    with col_s:
                        st.markdown("**✅ Strengths**")
                        st.success(evaluation.get("strengths", ""))
                    with col_w:
                        st.markdown("**⚠️ Weaknesses**")
                        st.warning(evaluation.get("weaknesses", ""))

                    st.markdown("**💡 Improved Answer**")
                    st.info(evaluation.get("improved_answer", ""))

                    # STAR check for behavioral
                    star = evaluation.get("star_check", {})
                    if star.get("applicable"):
                        st.markdown("**⭐ STAR Method Check**")
                        s_col, t_col, a_col, r_col = st.columns(4)
                        s_col.markdown(f"{'' if star.get('situation') else '❌'} Situation")
                        t_col.markdown(f"{'' if star.get('task') else '❌'} Task")
                        a_col.markdown(f"{'' if star.get('action') else '❌'} Action")
                        r_col.markdown(f"{'' if star.get('result') else '❌'} Result")
                        if star.get("feedback"):
                            st.caption(star["feedback"])

                    # Missing keywords
                    if evaluation.get("keywords_missing"):
                        st.markdown("** Keywords You Missed**")
                        chips = " ".join([
                            f'<span class="keyword-chip chip-missing">{k}</span>'
                            for k in evaluation["keywords_missing"]
                        ])
                        st.markdown(chips, unsafe_allow_html=True)
                else:
                    st.error("Could not parse evaluation. Try again.")


# ══════════════════════════════════════════════
# TAB 5: VOICE MODE
# ══════════════════════════════════════════════
with tab_voice:
    st.subheader(" Voice Interview Mode")

    if not VOICE_AVAILABLE:
        st.warning(
            "Voice mode requires extra packages. Run:\n\n"
            "```\npip install gtts SpeechRecognition streamlit-mic-recorder\n```\n\n"
            "Then restart the app."
        )
    elif not st.session_state.questions:
        st.info("Generate questions first from the Resume tab.")
    else:
        st.markdown("Hear the question spoken aloud, record your voice answer, get instant feedback.")

        q_options_voice = [
            f"Q{i+1}: {q['question'][:55]}..."
            for i, q in enumerate(st.session_state.questions)
        ]
        voice_q_idx = st.selectbox(
            "Select Question",
            range(len(q_options_voice)),
            format_func=lambda i: q_options_voice[i],
            key="voice_q_sel"
        )
        voice_q = st.session_state.questions[voice_q_idx]

        st.markdown("**Question:**")
        st.info(voice_q["question"])

        # TTS — play question
        if st.button(" Hear Question Aloud"):
            with st.spinner("Generating audio..."):
                play_question_audio(voice_q["question"])

        st.markdown("---")

        # STT — record answer
        st.markdown("**Record Your Answer:**")
        audio_data = mic_recorder(
            start_prompt=" Start Recording",
            stop_prompt=" Stop Recording",
            key="voice_recorder"
        )

        if audio_data and audio_data.get("bytes"):
            with st.spinner("Transcribing your answer..."):
                transcript = transcribe_audio(audio_data["bytes"])
                st.session_state.voice_transcript = transcript

        if st.session_state.voice_transcript:
            st.markdown("**Transcript:**")
            st.text_area(
                "Transcribed Answer",
                st.session_state.voice_transcript,
                height=100,
                key="transcript_display"
            )

            if st.button("⚡ Quick Evaluate", type="primary"):
                with st.spinner("Evaluating..."):
                    v_eval = evaluate_voice_answer(
                        voice_q["question"],
                        st.session_state.voice_transcript
                    )

                st.metric("Score", f"{v_eval.get('score', 0)}/10", v_eval.get("one_line_verdict", ""))
                c1, c2 = st.columns(2)
                c1.success(f" {v_eval.get('top_strength', '')}")
                c2.warning(f" {v_eval.get('top_improvement', '')}")
                if v_eval.get("follow_up_question"):
                    st.markdown(f"**Follow-up:** _{v_eval['follow_up_question']}_")


# ══════════════════════════════════════════════
# TAB 6: ANALYSIS — HIRE PROBABILITY
# ══════════════════════════════════════════════
with tab_analysis:
    st.subheader(" Session Analysis & Hire Probability")

    if not st.session_state.answer_history:
        st.info("Practice at least one question to see your analysis.")
    else:
        history = st.session_state.answer_history
        scores = [h["score"] for h in history]
        avg = sum(scores) / len(scores)

        # ── Top stats ──
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Score", f"{avg:.1f}/10")
        c2.metric("Practiced", len(history))
        c3.metric("Best Score", f"{max(scores)}/10")
        c4.metric("Scored 7+", f"{len([s for s in scores if s >= 7])}/{len(scores)}")

        st.markdown("---")

        # ── Hire probability ──
        col_hp, col_btn = st.columns([3, 1])
        with col_btn:
            generate_hp = st.button(" Calculate Hire Probability", type="primary")

        if generate_hp:
            weak_areas = [h["topic"] for h in history if h["score"] < 6]
            with st.spinner("Calculating your hire probability..."):
                llm = get_fast_llm()
                hp_prompt = HIRE_PROBABILITY_PROMPT.format(
                    resume=st.session_state.resume_text,
                    role=st.session_state.company_role,
                    company_type=st.session_state.company_type,
                    questions_practiced=len(history),
                    avg_score=round(avg, 1),
                    weak_areas=", ".join(weak_areas) if weak_areas else "None identified"
                )
                hp_resp = llm.invoke(hp_prompt)
                hp_result = parse_json_safe(hp_resp.content)
                if hp_result:
                    st.session_state.hire_result = hp_result

        if st.session_state.hire_result:
            hp = st.session_state.hire_result
            prob = hp.get("hire_probability", 0)

            st.markdown("###  Hire Probability Report")

            # Big probability display
            prob_color = hire_prob_color(prob)
            st.markdown(
                f"<h1 style='text-align:center; color:{'#22c55e' if prob>=65 else '#f59e0b' if prob>=40 else '#ef4444'}'>"
                f"{prob}% Hire Probability</h1>",
                unsafe_allow_html=True
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Overall Grade", hp.get("overall_grade", "N/A"))
            c2.metric("Resume Strength", f"{hp.get('resume_strength', 0)}%")
            c3.metric("Interview Strength", f"{hp.get('interview_strength', 0)}%")
            c4.metric("Technical Strength", f"{hp.get('technical_strength', 0)}%")

            st.markdown(f"**{hp.get('readiness_level', '')}** — {hp.get('summary', '')}")

            col_str, col_gap = st.columns(2)
            with col_str:
                st.markdown("** Top Strengths**")
                for s in hp.get("top_strengths", []):
                    st.markdown(f"✓ {s}")
            with col_gap:
                st.markdown("** Critical Gaps**")
                for g in hp.get("critical_gaps", []):
                    st.markdown(f"• {g}")

            # 30-day plan
            st.markdown("---")
            st.markdown("** Your 30-Day Improvement Plan**")
            for step in hp.get("30_day_plan", []):
                st.markdown(f"→ {step}")

            # Recommended companies
            col_comp, col_roles = st.columns(2)
            with col_comp:
                if hp.get("recommended_companies"):
                    st.markdown("** Target Companies**")
                    for c in hp["recommended_companies"]:
                        st.markdown(f"• {c}")
            with col_roles:
                if hp.get("roles_to_target"):
                    st.markdown("** Target Roles**")
                    for r in hp["roles_to_target"]:
                        st.markdown(f"• {r}")

        st.markdown("---")
        st.markdown("** Question History**")

        for i, h in enumerate(history):
            sc = h["score"]
            badge = "badge-green" if sc >= 7 else "badge-orange" if sc >= 5 else "badge-red"
            with st.expander(
                f"Q{i+1} [{h.get('type','').upper()}] — Score: {sc}/10 — {h.get('topic','')}",
                expanded=False
            ):
                st.markdown(f"**Question:** {h['question']}")
                st.markdown(f"**Your Answer:** {h['answer'][:300]}{'...' if len(h['answer'])>300 else ''}")
                col_s, col_w = st.columns(2)
                col_s.success(f" {h.get('strengths','')}")
                col_w.warning(f" {h.get('weaknesses','')}")
                if h.get("improved_answer"):
                    st.info(f" {h['improved_answer']}")