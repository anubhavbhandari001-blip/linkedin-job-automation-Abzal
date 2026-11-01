import json

from resume.parser import extract_resume_text
from ai.resume_customizer import customize_resume


resume_path = "../data/resume/resume.pdf"

resume_text = extract_resume_text(resume_path)


with open(
    "linkedin/data/sample_jobs.json",
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


job = jobs[0]


print("\nCustomizing resume...\n")


result = customize_resume(
    resume_text,
    job
)


print("\n========== CUSTOMIZED RESUME ==========\n")

print(json.dumps(
    result,
    indent=4
))