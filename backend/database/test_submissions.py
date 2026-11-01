from database.submissions import (
    initialize_database,
    is_already_processed,
    save_submission,
    get_all_submissions
)


initialize_database()


job = {

    "linkedin_post_url":
        "https://www.linkedin.com/posts/test-job-123",

    "recruiter_name":
        "Test Recruiter",

    "recruiter_email":
        "recruiter@example.com",

    "company_name":
        "Example Technologies",

    "job_title":
        "Frontend Developer",

    "location":
        "New Delhi",

    "employment_type":
        "Full-Time"
}


print()
print(
    "Checking before saving..."
)

print(
    is_already_processed(
        job["linkedin_post_url"]
    )
)


print()
print(
    "Saving submission..."
)

save_submission(
    job,
    status="processed"
)


print()
print(
    "Checking after saving..."
)

print(
    is_already_processed(
        job["linkedin_post_url"]
    )
)


print()
print(
    "========== SUBMISSIONS =========="
)

for row in get_all_submissions():

    print(row)