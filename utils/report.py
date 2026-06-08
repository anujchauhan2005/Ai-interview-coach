from fpdf import FPDF
import tempfile
import os
from datetime import datetime


class InterviewReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(30, 30, 30)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "AI Interview Coach - Session Report",
                  ln=True, fill=True, align="C")
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10,
                  f"Generated on {datetime.now().strftime('%d %b %Y %H:%M')}",
                  align="C")


def generate_pdf_report(candidate_name, resume_summary,
                        questions_history, ats_result, hire_probability) -> bytes:
    pdf = InterviewReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Candidate: {candidate_name or 'N/A'}", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, f"Date: {datetime.now().strftime('%d %B %Y')}", ln=True)
    pdf.ln(4)

    if questions_history:
        avg = sum(q["score"] for q in questions_history) / len(questions_history)
        best = max(q["score"] for q in questions_history)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, "Session Summary", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(60, 7, f"Questions Practiced: {len(questions_history)}")
        pdf.cell(60, 7, f"Average Score: {avg:.1f}/10")
        pdf.cell(60, 7, f"Best Score: {best}/10", ln=True)
        pdf.ln(4)

    if ats_result and ats_result.get("ats_score"):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, "ATS Analysis", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"ATS Score: {ats_result['ats_score']}/100", ln=True)
        pdf.cell(0, 6,
                 f"Hire Probability: {ats_result.get('hire_probability', 'N/A')}%",
                 ln=True)
        if ats_result.get("missing_keywords"):
            pdf.cell(0, 6,
                     f"Missing Keywords: {', '.join(ats_result['missing_keywords'][:8])}",
                     ln=True)
        pdf.ln(4)

    if hire_probability and hire_probability.get("hire_probability"):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, "Hire Probability Report", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6,
                 f"Hire Probability: {hire_probability['hire_probability']}%",
                 ln=True)
        pdf.cell(0, 6,
                 f"Overall Grade: {hire_probability.get('overall_grade', 'N/A')}",
                 ln=True)
        summary = hire_probability.get("summary", "")
        if summary:
            pdf.multi_cell(0, 6, f"Summary: {summary}")
        pdf.ln(4)

    if questions_history:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, "Question-wise Performance", ln=True, fill=True)
        pdf.ln(2)
        for i, item in enumerate(questions_history):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(30, 30, 30)
            q_text = f"Q{i+1}: {item['question'][:100]}..."
            pdf.multi_cell(0, 6, q_text)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(0, 6, f"Score: {item['score']}/10", ln=True)
            if item.get("strengths"):
                pdf.multi_cell(0, 5, f"Strengths: {item['strengths'][:200]}")
            if item.get("weaknesses"):
                pdf.multi_cell(0, 5, f"Improve: {item['weaknesses'][:200]}")
            pdf.ln(3)

    if hire_probability and hire_probability.get("30_day_plan"):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, "30-Day Improvement Plan", ln=True, fill=True)
        pdf.set_font("Helvetica", "", 10)
        for step in hire_probability["30_day_plan"]:
            pdf.multi_cell(0, 6, f"- {step}")
            pdf.ln(1)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)
    with open(tmp.name, "rb") as f:
        pdf_bytes = f.read()
    os.unlink(tmp.name)
    return pdf_bytes