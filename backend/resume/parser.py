import pymupdf
from pathlib import Path
import re


def extract_resume_text(pdf_path):
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"Resume not found: {pdf_path}")

    document = pymupdf.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text


def extract_email(text):
    pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    match = re.search(pattern, text)

    return match.group() if match else None


def extract_phone(text):
    pattern = r'\+?\d[\d\s\-]{9,}\d'
    match = re.search(pattern, text)

    return match.group().strip() if match else None


def extract_linkedin(text):
    pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\-]+'
    match = re.search(pattern, text, re.IGNORECASE)

    return match.group() if match else None


def extract_github(text):
    pattern = r'(?:https?://)?(?:www\.)?github\.com/[\w\-]+'
    match = re.search(pattern, text, re.IGNORECASE)

    return match.group() if match else None


def extract_job_title(text):
    job_titles = [
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Software Developer",
        "Software Engineer",
        "Java Developer",
        "Python Developer",
        "React Developer",
        ".NET Developer",
        "Web Developer"
    ]

    text_lower = text.lower()

    for title in job_titles:
        if title.lower() in text_lower:
            return title

    return None


def extract_candidate_info(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    candidate = {
        "name": None,
        "job_title": extract_job_title(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text)
    }

    if lines:
        candidate["name"] = lines[0]

    return candidate


if __name__ == "__main__":

    resume_path = "../data/resume/resume.pdf"

    resume_text = extract_resume_text(resume_path)

    candidate = extract_candidate_info(resume_text)

    print("\n========== CANDIDATE INFORMATION ==========\n")

    for key, value in candidate.items():
        print(f"{key.title()}: {value}")