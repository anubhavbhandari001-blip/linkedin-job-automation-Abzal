import json

from linkedin.filters import passes_filters


with open("linkedin/data/sample_jobs.json", "r", encoding="utf-8") as file:
    jobs = json.load(file)


print("\n========== JOB FILTER RESULTS ==========\n")

for job in jobs:

    result = passes_filters(job)

    print(f"Job: {job['job_title']}")
    print(f"Company: {job['company_name']}")
    print(f"Employment: {job['employment_type']}")
    print(f"Posted: {job['posted_hours_ago']} hours ago")
    print(f"Result: {'PROCESS' if result else 'SKIP'}")
    print("-" * 50)