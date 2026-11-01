from gmail.draft import send_gmail_application


# ============================================================
# TEST JOB
# ============================================================

job = {

    "recruiter_name": "Test Recruiter",

    # IMPORTANT:
    # Put YOUR OWN Gmail address here for testing.
    "recruiter_email": "bhandari.anubhav07@gmail.com",

    "job_title": "Frontend Developer",

    "linkedin_post_url":
        "https://www.linkedin.com/",

    "job_description":
        "Frontend Developer position requiring React, "
        "JavaScript, HTML, CSS and Git."
}


# ============================================================
# TEST CANDIDATE
# ============================================================

candidate = {

    "name": "Anubhav Bhandari",

    "email": "anubhav.bhandari001@gmail.com",

    "phone": "9999999999",

    "linkedin": "https://www.linkedin.com/",

    "location": "New Delhi, India",

    "work_authorization": "India",

    "availability": "Immediate",

    "experience": "Fresher",

    "expected_salary": "As per company standards"
}


# ============================================================
# ORIGINAL RESUME
# ============================================================

resume_pdf = (
    "../data/resume/resume.pdf"
)


# ============================================================
# SEND EMAIL
# ============================================================

print()
print("=" * 50)
print("SENDING TEST EMAIL")
print("=" * 50)
print()

result = send_gmail_application(
    job,
    candidate,
    resume_pdf
)


print()
print("EMAIL SENT SUCCESSFULLY")
print()

print(
    "Gmail Message ID:",
    result.get("id")
)

print()
print(
    "Check the recipient Gmail inbox."
)