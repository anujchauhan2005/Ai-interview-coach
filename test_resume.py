from resume.parser import extract_resume_text

pdf_path = "resume.pdf"

with open(pdf_path, "rb") as file:
    text = extract_resume_text(file)

print(text)