import re

import PyPDF2


STOP_WORDS = {
    "the", "and", "for", "with", "are", "was", "were",
    "been", "being", "have", "has", "had", "will", "would",
    "could", "should", "may", "might", "can", "shall",
    "this", "that", "these", "those", "from", "into",
    "about", "between", "through", "during", "before", "after",
    "above", "below", "not", "but", "also", "very", "just",
    "than", "then", "only", "own", "same", "other",
}


def allowed_file(filename, allowed_extensions=None):
    if allowed_extensions is None:
        allowed_extensions = {"pdf"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def extract_resume_text(student):
    """to build searchable text from a student's skills, experience, and uploaded PDF resume."""
    parts = []
    if student.skills:
        parts.append(student.skills)
    if student.experience:
        parts.append(student.experience)
    if student.resume_path:
        try:
            with open(student.resume_path, "rb") as f:
                for page in PyPDF2.PdfReader(f).pages:
                    text = page.extract_text()
                    if text:
                        parts.append(text)
        except Exception:
            pass
    return " ".join(parts)


def compute_ats_score(resume_text, job_description):
    """Simple keyword-matching ATS score (0-100%).
    Compares words in resume_text against keywords from the job_description."""
    if not resume_text or not job_description:
        return 0.0

    resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
    jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower()))
    jd_keywords = jd_words - STOP_WORDS

    if not jd_keywords:
        return 0.0

    matched = resume_words & jd_keywords
    score = (len(matched) / len(jd_keywords)) * 100
    return round(min(score, 100.0), 1)
