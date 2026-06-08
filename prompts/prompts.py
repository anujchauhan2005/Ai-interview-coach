QUESTION_PROMPT = """
You are a senior technical interviewer at a top tech company.

Candidate Resume:
{resume}

Knowledge Base:
- DSA: Arrays, LinkedLists, Trees, Graphs, Dynamic Programming, Sorting, Searching, HashMaps, Stacks, Queues
- OS: Processes, Threads, Deadlock, Memory Management, Scheduling
- DBMS: Normalization, Indexing, ACID Properties, Joins, Transactions
- Computer Networks: OSI Model, TCP/IP, DNS, HTTP/HTTPS, REST
- OOP: Encapsulation, Inheritance, Polymorphism, Abstraction, SOLID
- Machine Learning: Supervised/Unsupervised, Bias-Variance, Overfitting, Model Evaluation

Company/Role Target: {company_role}
Question Types Requested: {question_types}
Focus Topics: {topics}

Generate exactly 7 interview questions tailored to this specific candidate.
Return ONLY a valid JSON array, no markdown, no extra text:
[
  {{"id": 1, "type": "technical", "difficulty": "medium", "topic": "SQL", "question": "..."}},
  {{"id": 2, "type": "behavioral", "difficulty": "easy", "topic": "Teamwork", "question": "..."}}
]
"""

EVALUATION_PROMPT = """
You are a strict but constructive interviewer evaluating a candidate's answer.

Question: {question}
Question Type: {question_type}
Candidate Answer: {answer}

Return ONLY a valid JSON object, no markdown:
{{
  "score": 7,
  "verdict": "Good answer with room for improvement",
  "strengths": "- Clear explanation\\n- Mentioned real use case",
  "weaknesses": "- Did not mention time complexity\\n- No example given",
  "improved_answer": "A concise 4-5 sentence model answer here",
  "star_check": {{
    "applicable": true,
    "situation": true,
    "task": true,
    "action": false,
    "result": false,
    "feedback": "You described the situation well but missed concrete actions and results."
  }},
  "keywords_used": ["indexing", "query optimization"],
  "keywords_missing": ["B-tree", "cardinality", "composite index"]
}}
"""

ATS_PROMPT = """
You are an ATS (Applicant Tracking System) and HR expert.

Resume Text:
{resume}

Job Description:
{job_description}

Perform a deep ATS analysis. Return ONLY a valid JSON object, no markdown:
{{
  "ats_score": 72,
  "hire_probability": 65,
  "verdict": "Strong candidate with skill gaps",
  "matched_keywords": ["Python", "SQL", "Data Analysis"],
  "missing_keywords": ["Spark", "Airflow", "AWS"],
  "section_scores": {{
    "skills_match": 80,
    "experience_match": 60,
    "education_match": 90,
    "formatting_score": 85,
    "keyword_density": 70
  }},
  "strengths": [
    "Strong technical skills aligned with JD",
    "Relevant internship experience"
  ],
  "gaps": [
    "Missing cloud platform experience",
    "No mention of big data tools"
  ],
  "bullet_rewrites": [
    {{
      "original": "Analyzed customer data using Python",
      "improved": "Analyzed 100K+ customer records using Python (Pandas, NumPy), identifying churn patterns that reduced attrition by 15%"
    }}
  ],
  "recommendations": [
    "Add AWS or GCP certification",
    "Quantify all bullet points with numbers"
  ]
}}
"""

HIRE_PROBABILITY_PROMPT = """
You are a senior recruiter and hiring manager.

Candidate Resume:
{resume}

Target Role: {role}
Company Type: {company_type}
Questions Practiced: {questions_practiced}
Average Score: {avg_score}/10
Weak Areas: {weak_areas}

Return ONLY a valid JSON object, no markdown:
{{
  "hire_probability": 68,
  "overall_grade": "B+",
  "readiness_level": "Interview Ready",
  "resume_strength": 75,
  "interview_strength": 60,
  "technical_strength": 70,
  "communication_strength": 65,
  "summary": "Strong technical foundation. Needs to improve articulation of impact.",
  "top_strengths": [
    "Relevant internship experience",
    "Strong SQL and Python skills"
  ],
  "critical_gaps": [
    "System design knowledge needs depth",
    "Behavioral answers lack STAR structure"
  ],
  "30_day_plan": [
    "Day 1-7: Practice 2 DSA problems daily on LeetCode",
    "Day 8-14: Study system design basics",
    "Day 15-21: Mock interviews on Pramp",
    "Day 22-30: Apply to target companies"
  ],
  "recommended_companies": ["Flipkart", "Swiggy", "Zomato", "Razorpay"],
  "roles_to_target": ["Data Analyst", "Junior Data Scientist"]
}}
"""

TOPIC_EXTRACTION_PROMPT = """
From this resume, extract 8-10 key technical skill/topic tags.
Examples: "SQL", "Python", "Machine Learning", "Power BI"

Resume:
{resume}

Return ONLY a JSON array of strings, no markdown, no extra text:
["SQL", "Python", "Machine Learning"]
"""

VOICE_EVAL_PROMPT = """
You are an interviewer. The candidate just spoke their answer aloud.

Question: {question}
Transcribed Answer: {answer}

Return ONLY valid JSON, no markdown:
{{
  "score": 6,
  "one_line_verdict": "Good start, needs more technical depth",
  "top_strength": "Clear communication and structured response",
  "top_improvement": "Add specific numbers and technical terms",
  "follow_up_question": "Can you elaborate on how you handled edge cases?"
}}
"""