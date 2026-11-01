import json

from pathlib import Path

from linkedin.search import (
    is_within_24_hours,
    is_us_location,
    is_target_job
)


BASE_DIR = Path(
    __file__
).resolve().parent.parent.parent


DATA_FILE = (
    BASE_DIR
    / "data"
    / "linkedin_jobs.json"
)


def load_test_jobs():

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def filter_test_jobs(
    jobs,
    target_title
):

    valid_jobs = []

    print()
    print("=" * 60)
    print("LINKEDIN JOB FILTERING")
    print("=" * 60)

    for job in jobs:

        print()
        print(
            f"Checking: "
            f"{job['job_title']}"
        )

        # Target role
        if not is_target_job(
            job,
            target_title
        ):

            print(
                "SKIPPED: Not target role"
            )

            continue

        # 24 hours
        if not is_within_24_hours(
            job["posted_time"]
        ):

            print(
                "SKIPPED: Older than 24 hours"
            )

            continue

        # US
        if not is_us_location(
            job["location"]
        ):

            print(
                "SKIPPED: Not a US job"
            )

            continue

        # Full time
        if (
            "full" not in
            job["employment_type"].lower()
        ):

            print(
                "SKIPPED: Not Full-Time"
            )

            continue

        # Email
        if not job.get(
            "recruiter_email"
        ):

            print(
                "SKIPPED: No recruiter email"
            )

            continue

        print(
            "VALID JOB"
        )

        valid_jobs.append(job)

    return valid_jobs

if __name__ == "__main__":

    jobs = load_test_jobs()

    valid_jobs = filter_test_jobs(
        jobs,
        "Frontend Developer"
    )

    print()
    print("=" * 60)
    print(
        f"VALID JOBS: {len(valid_jobs)}"
    )
    print("=" * 60)