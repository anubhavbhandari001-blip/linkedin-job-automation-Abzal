import json

from resume.parser import extract_resume_text
from ai.resume_customizer import customize_resume
from resume.pdf_generator import generate_resume_pdf


resume_path = "../data/resume/resume.pdf"

resume_text = extract_resume_text(resume_path)


with open(
    "linkedin/data/sample_jobs.json",
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


job = jobs[0]


print("\nCustomizing resume with Gemini...\n")

customized_resume = customize_resume(
    resume_text,
    job
)


print("Generating PDF...\n")

pdf_path = generate_resume_pdf(
    customized_resume,
    job["job_title"]
)


print("\n========== RESUME GENERATED ==========\n")
print(f"PDF saved to: {pdf_path}")