import json

from database.database import (
    initialize_database,
    is_already_processed,
    save_submission
)


initialize_database()


with open(
    "linkedin/data/sample_jobs.json",
    "r",
    encoding="utf-8"
) as file:

    jobs = json.load(file)


job = jobs[0]

url = job["linkedin_post_url"]


print("\n========== FIRST CHECK ==========\n")

if is_already_processed(url):

    print("Job already processed.")

else:

    print("Job is new.")
    save_submission(job)

print("\n========== SECOND CHECK ==========\n")

if is_already_processed(url):

    print("Duplicate detected — SKIP")

else:

    print("Job is new.")
    