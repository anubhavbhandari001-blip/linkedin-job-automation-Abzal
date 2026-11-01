import json
from pathlib import Path

from gmail.draft import create_gmail_draft


BASE_DIR = Path(__file__).resolve().parent.parent.parent


candidate = {
    "name": "Anubhav Bhandari",
    "email": "your_email@gmail.com",
    "phone": "+91 XXXXXXXXXX",
    "linkedin": "https://www.linkedin.com/in/your-profile",
    "location": "New Delhi, India",
    "work_authorization": "India",
    "availability": "Immediate",
    "experience": "Fresher",
    "expected_salary": "As per company standards"
}

with open(
    "linkedin/data/sample_jobs.json",
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


job = jobs[0]


resume_pdf = (
    BASE_DIR
    / "data"
    / "customized_resumes"
    / "customized_Frontend_Developer.pdf"
)

print("\nCreating Gmail draft...\n")


draft = create_gmail_draft(
    job,
    candidate,
    resume_pdf
)


print("\n========== GMAIL DRAFT CREATED ==========\n")

print("Draft ID:", draft["id"])
print("Draft created successfully!")