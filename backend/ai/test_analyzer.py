import json

from resume.parser import (
    extract_resume_text
)

from ai.job_analyzer import analyze_job


resume_path = "../data/resume/resume.pdf"

resume_text = extract_resume_text(resume_path)


with open(
    "linkedin/data/sample_jobs.json",
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


job = jobs[0]


print("\nAnalyzing job...\n")


result = analyze_job(
    resume_text,
    job
)


print("\n========== AI JOB ANALYSIS ==========\n")

print(json.dumps(
    result,
    indent=4
))