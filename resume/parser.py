from pypdf import PdfReader
import re


def extract_resume_text(pdf_file) -> str:
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_resume_metadata(resume_text: str) -> dict:
    metadata = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "has_projects": False,
        "has_certifications": False,
        "sections": []
    }

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
    if email_match:
        metadata["email"] = email_match.group()

    phone_match = re.search(r'[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]', resume_text)
    if phone_match:
        metadata["phone"] = phone_match.group()

    section_keywords = [
        "experience", "education", "skills", "projects",
        "certifications", "summary", "objective", "achievements"
    ]
    for kw in section_keywords:
        if kw.lower() in resume_text.lower():
            metadata["sections"].append(kw.title())

    metadata["has_projects"] = "project" in resume_text.lower()
    metadata["has_certifications"] = "certif" in resume_text.lower()

    return metadata