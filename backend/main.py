from pathlib import Path

from resume.parser import (
    extract_resume_text
)

from linkedin.search import (
    start_browser,
    login_to_linkedin,
    search_linkedin_posts,
    extract_posts,
    filter_job_posts,
    generate_search_query
)

from ai.job_analyzer import analyze_job

from gmail.draft import send_gmail_application

from database.submissions import (
    initialize_database,
    is_already_processed,
    save_submission,
    get_all_submissions
)
import time
import random

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RESUME_PATH = (
    BASE_DIR
    / "data"
    / "resume"
    / "resume.pdf"
)

LINKEDIN_PAGE_FILE = (
    BASE_DIR
    / "data"
    / "linkedin_page.txt"
)


# ============================================================
# LOAD CORRECT LINKEDIN RECRUITER NAMES
# ============================================================

def load_linkedin_recruiter_names():

    recruiter_map = {}

    if not LINKEDIN_PAGE_FILE.exists():

        print()
        print(
            "WARNING: linkedin_page.txt was not found."
        )
        print(
            f"Expected file: {LINKEDIN_PAGE_FILE}"
        )

        return recruiter_map

    try:

        with open(
            LINKEDIN_PAGE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read()

        # ----------------------------------------------------
        # Split saved posts
        # ----------------------------------------------------

        blocks = content.split(
            "=" * 70
        )

        for block in blocks:

            recruiter_name = None
            post_url = None

            for line in block.splitlines():

                line = line.strip()

                # ------------------------------------------------
                # RECRUITER
                # ------------------------------------------------

                if line.startswith(
                    "RECRUITER:"
                ):

                    recruiter_name = (
                        line[
                            len("RECRUITER:")
                        :].strip()
                    )

                # ------------------------------------------------
                # URL
                # ------------------------------------------------

                elif line.startswith(
                    "URL:"
                ):

                    post_url = (
                        line[
                            len("URL:")
                        :].strip()
                    )

            # ----------------------------------------------------
            # Save URL -> recruiter mapping
            # ----------------------------------------------------

            if (
                recruiter_name
                and recruiter_name.lower()
                not in [
                    "none",
                    "null"
                ]
                and post_url
                and post_url.lower()
                not in [
                    "none",
                    "null"
                ]
            ):

                recruiter_map[
                    post_url
                ] = recruiter_name

        print()
        print(
            f"Loaded {len(recruiter_map)} "
            f"LinkedIn recruiter names from "
            f"linkedin_page.txt."
        )

    except Exception as error:

        print()
        print(
            "WARNING: Could not read "
            "linkedin_page.txt."
        )

        print(
            f"Error: {error}"
        )

    return recruiter_map


# ============================================================
# DISPLAY APPLICATION OPTIONS
# ============================================================

def display_application_options(eligible_jobs):

    print()
    print("=" * 70)
    print("       JOBS AVAILABLE FOR APPLICATION")
    print("=" * 70)
    print()

    if not eligible_jobs:

        print(
            "No jobs are currently available for application."
        )

        print()

        return

    for index, job in enumerate(
        eligible_jobs,
        start=1
    ):

        print(
            f"========== JOB {index} =========="
        )

        print(
            f"Job Title: "
            f"{job.get('job_title')}"
        )

        print(
            f"Company: "
            f"{job.get('company_name')}"
        )

        print(
            f"Recruiter: "
            f"{job.get('recruiter_name')}"
        )

        print(
            f"Email: "
            f"{job.get('recruiter_email')}"
        )

        print(
            f"Location: "
            f"{job.get('location')}"
        )

        print(
            f"Employment: "
            f"{job.get('employment_type')}"
        )

        print(
            f"Posted: "
            f"{job.get('posted_time')}"
        )

        print(
            f"LinkedIn URL: "
            f"{job.get('linkedin_post_url')}"
        )

        print()


# ============================================================
# SEND APPLICATION TO ONE JOB
# ============================================================

def send_application(
    job,
    candidate,
    resume_pdf
):

    print()
    print("=" * 70)
    print("       SENDING APPLICATION")
    print("=" * 70)
    print()

    print(
        f"Recruiter: "
        f"{job.get('recruiter_name')}"
    )

    print(
        f"Email: "
        f"{job.get('recruiter_email')}"
    )

    print(
        f"Job: "
        f"{job.get('job_title')}"
    )

    print(
        f"Company: "
        f"{job.get('company_name')}"
    )

    print(
        f"LinkedIn URL: "
        f"{job.get('linkedin_post_url')}"
    )

    print()

    try:

        result = send_gmail_application(
            job,
            candidate,
            resume_pdf
        )

        print()
        print(
            "APPLICATION EMAIL SENT SUCCESSFULLY"
        )

        print()

        print(
            f"Recipient: "
            f"{job.get('recruiter_email')}"
        )

        print(
            f"Job: "
            f"{job.get('job_title')}"
        )

        print(
            f"Company: "
            f"{job.get('company_name')}"
        )

        print(
            f"Message ID: "
            f"{result.get('id')}"
        )

        print()

        save_submission(
            job,
            status="SENT"
        )

        print(
            "Database status: SENT"
        )

        return True

    except Exception as error:

        print()
        print(
            "FAILED TO SEND APPLICATION"
        )

        print(
            f"Error: {error}"
        )

        print()

        return False


# ============================================================
# SEND TO ALL JOBS
# ============================================================

def send_to_all_jobs(
    eligible_jobs,
    candidate,
    resume_pdf
):

    print()
    print("=" * 70)
    print("       SENDING APPLICATIONS TO ALL")
    print("=" * 70)
    print()

    total_jobs = len(
        eligible_jobs
    )

    successful = 0
    failed = 0

    for index, job in enumerate(
        eligible_jobs,
        start=1
    ):

        print()
        print(
            f"[{index}/{total_jobs}] "
            f"Processing application..."
        )

        # ----------------------------------------------------
        # SEND APPLICATION
        # ----------------------------------------------------

        success = send_application(
            job,
            candidate,
            resume_pdf
        )

        if success:

            successful += 1

        else:

            failed += 1

        # ----------------------------------------------------
        # RANDOM DELAY BEFORE NEXT EMAIL
        # ----------------------------------------------------

        if index < total_jobs:

            delay = random.randint(
                15,
                60
            )

            print()
            print(
                f"Waiting {delay} seconds "
                f"before the next application..."
            )

            time.sleep(
                delay
            )

    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print()
    print("=" * 70)
    print("       EMAIL SENDING SUMMARY")
    print("=" * 70)
    print()

    print(
        f"Total applications: {total_jobs}"
    )

    print(
        f"Successfully sent: {successful}"
    )

    print(
        f"Failed: {failed}"
    )

    print()


# ============================================================
# SEND TO SPECIFIC JOB
# ============================================================

def send_to_specific_job(
    eligible_jobs,
    candidate,
    resume_pdf
):

    if not eligible_jobs:

        print()
        print(
            "There are no eligible jobs."
        )

        return

    display_application_options(
        eligible_jobs
    )

    while True:

        print(
            "Enter the job number you want "
            "to apply to."
        )

        print(
            "Enter 0 to return to the main menu."
        )

        try:

            choice = int(
                input(
                    "Job number: "
                )
            )

        except ValueError:

            print()
            print(
                "Invalid input. "
                "Please enter a number."
            )
            print()

            continue

        if choice == 0:

            print()
            print(
                "Returning to main menu..."
            )

            return

        if choice < 1 or choice > len(
            eligible_jobs
        ):

            print()
            print(
                "Invalid job number."
            )

            print(
                f"Please choose between "
                f"1 and {len(eligible_jobs)}."
            )

            print()

            continue

        selected_job = eligible_jobs[
            choice - 1
        ]

        print()
        print("=" * 70)
        print("       SELECTED JOB")
        print("=" * 70)
        print()

        print(
            f"Job Title: "
            f"{selected_job.get('job_title')}"
        )

        print(
            f"Company: "
            f"{selected_job.get('company_name')}"
        )

        print(
            f"Recruiter: "
            f"{selected_job.get('recruiter_name')}"
        )

        print(
            f"Email: "
            f"{selected_job.get('recruiter_email')}"
        )

        print(
            f"LinkedIn URL: "
            f"{selected_job.get('linkedin_post_url')}"
        )

        print()

        while True:

            confirmation = input(
                "Send application to this recruiter? "
                "(y/n): "
            ).strip().lower()

            if confirmation == "y":

                send_application(
                    selected_job,
                    candidate,
                    resume_pdf
                )

                return

            if confirmation == "n":

                print()
                print(
                    "Application cancelled."
                )

                return

            print(
                "Please enter y or n."
            )


# # ============================================================
# # ANALYZE JOB WITH AI
# # ============================================================


# ============================================================
# ANALYZE JOB WITH AI
# ============================================================

def analyze_single_job(
    job,
    candidate
):

    try:

        # ----------------------------------------------------
        # GET RESUME TEXT
        # ----------------------------------------------------

        resume_text = candidate.get(
            "resume_text",
            ""
        )

        # ----------------------------------------------------
        # RUN GEMINI ANALYSIS
        # ----------------------------------------------------

        analysis = analyze_job(
            job,
            candidate
        )

        # ----------------------------------------------------
        # VALIDATE RESPONSE
        # ----------------------------------------------------

        if not isinstance(
            analysis,
            dict
        ):

            print()
            print(
                "AI returned an unexpected response."
            )

            # AI did not provide a valid score.
            # Allow the job to continue.
            return {
                "recommendation": "APPLY",
                "skip_reason": "",
                "match_score": 1
            }

        # ----------------------------------------------------
        # GET ANALYSIS VALUES
        # ----------------------------------------------------

        job_title = analysis.get(
            "job_title",
            job.get("job_title", "Unknown")
        )

        company = analysis.get(
            "company",
            job.get("company_name", "Unknown")
        )

        required_skills = analysis.get(
            "required_skills",
            []
        )

        matching_skills = analysis.get(
            "matching_skills",
            []
        )

        missing_skills = analysis.get(
            "missing_skills",
            []
        )

        experience_required = analysis.get(
            "experience_required",
            ""
        )

        candidate_meets_experience = analysis.get(
            "candidate_meets_experience",
            False
        )

        location = analysis.get(
            "location",
            job.get("location", "")
        )

        employment_type = analysis.get(
            "employment_type",
            job.get("employment_type", "")
        )

        match_score = analysis.get(
            "match_score",
            0
        )

        # ----------------------------------------------------
        # NORMALIZE MATCH SCORE
        # ----------------------------------------------------

        try:

            match_score = int(
                float(match_score)
            )

        except (
            ValueError,
            TypeError
        ):

            match_score = 0

        # ----------------------------------------------------
        # FORCE RECOMMENDATION BASED ONLY ON SCORE
        # ----------------------------------------------------
        #
        # SCORE 0  -> SKIP
        # SCORE 1+ -> APPLY
        #
        # Gemini's original recommendation is ignored.
        # ----------------------------------------------------

        if match_score == 0:

            recommendation = "SKIP"

        else:

            recommendation = "APPLY"

        # ----------------------------------------------------
        # SAVE NORMALIZED VALUES
        # ----------------------------------------------------

        analysis["recommendation"] = (
            recommendation
        )

        analysis["match_score"] = (
            match_score
        )

        # ----------------------------------------------------
        # SAVE ANALYSIS TO JOB
        # ----------------------------------------------------

        job["ai_analysis"] = analysis

        # ====================================================
        # DISPLAY AI ANALYSIS
        # ====================================================

        print()
        print("=" * 60)
        print("AI JOB ANALYSIS")
        print("=" * 60)
        print()

        print(
            f"Job Title: {job_title}"
        )

        print(
            f"Company: {company}"
        )

        print(
            f"Match Score: {match_score}/100"
        )

        print(
            f"Experience Required: "
            f"{experience_required}"
        )

        print(
            f"Candidate Meets Experience: "
            f"{candidate_meets_experience}"
        )

        print(
            f"Location: {location}"
        )

        print(
            f"Employment Type: "
            f"{employment_type}"
        )

        print()

        # ----------------------------------------------------
        # REQUIRED SKILLS
        # ----------------------------------------------------

        print(
            "Required Skills:"
        )

        if required_skills:

            for skill in required_skills:

                print(
                    f"  - {skill}"
                )

        else:

            print(
                "  None identified"
            )

        print()

        # ----------------------------------------------------
        # MATCHING SKILLS
        # ----------------------------------------------------

        print(
            "Matching Skills:"
        )

        if matching_skills:

            for skill in matching_skills:

                print(
                    f"  + {skill}"
                )

        else:

            print(
                "  None"
            )

        print()

        # ----------------------------------------------------
        # MISSING SKILLS
        # ----------------------------------------------------

        print(
            "Missing Skills:"
        )

        if missing_skills:

            for skill in missing_skills:

                print(
                    f"  - {skill}"
                )

        else:

            print(
                "  None"
            )

        print()

        # ----------------------------------------------------
        # RECOMMENDATION
        # ----------------------------------------------------

        print(
            f"AI Recommendation: "
            f"{recommendation}"
        )

        # ----------------------------------------------------
        # AI DECISION
        # ----------------------------------------------------

        print()

        if match_score == 0:

            print(
                "AI DECISION: SKIP"
            )

            print(
                "Reason: Match score is 0/100."
            )

        else:

            print(
                "AI DECISION: APPLY"
            )

            print(
                f"Match score: "
                f"{match_score}/100"
            )

        print()

        print("=" * 60)

        return analysis

    except Exception as error:

        error_text = str(
            error
        )

        print()
        print("=" * 60)
        print("AI ANALYSIS FAILED")
        print("=" * 60)
        print()

        print(
            f"Error: {error}"
        )

        # ----------------------------------------------------
        # GEMINI QUOTA / RATE LIMIT ERROR
        # ----------------------------------------------------
        #
        # DO NOT SKIP THE JOB.
        #
        # This is an API availability problem,
        # NOT a match score of 0.
        # ----------------------------------------------------

        if (
            "429" in error_text
            or
            "RESOURCE_EXHAUSTED" in error_text
            or
            "quota" in error_text.lower()
        ):

            print()
            print(
                "Gemini API quota/rate limit "
                "has been reached."
            )

            print(
                "This is NOT an AI recommendation."
            )

            print(
                "Allowing the job to continue "
                "to the application stage."
            )

            return {
                "recommendation": "APPLY",
                "skip_reason": "",
                "match_score": 1
            }

        # ----------------------------------------------------
        # GEMINI 503 / TEMPORARY UNAVAILABLE
        # ----------------------------------------------------
        #
        # Example:
        # 503 UNAVAILABLE
        # This model is currently experiencing
        # high demand.
        #
        # DO NOT SKIP THE JOB.
        # ----------------------------------------------------

        if (
            "503" in error_text
            or
            "UNAVAILABLE" in error_text
            or
            "high demand" in error_text.lower()
        ):

            print()
            print(
                "Gemini model is temporarily "
                "unavailable."
            )

            print(
                "This is NOT an AI recommendation."
            )

            print(
                "Allowing the job to continue "
                "to the application stage."
            )

            return {
                "recommendation": "APPLY",
                "skip_reason": "",
                "match_score": 1
            }

        # ----------------------------------------------------
        # OTHER AI ERROR
        # ----------------------------------------------------
        #
        # Any other Gemini/API failure should also
        # NOT block the application.
        # ----------------------------------------------------

        print()
        print(
            "Gemini AI analysis failed temporarily."
        )

        print(
            "The error is NOT treated as a "
            "match score of 0."
        )

        print(
            "Allowing this job to continue "
            "to the application stage."
        )

        return {
            "recommendation": "APPLY",
            "skip_reason": "",
            "match_score": 1
        }

# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("        LINKEDIN JOB AUTOMATION")
    print("=" * 60)
    print()

    # ========================================================
    # INITIALIZE DATABASE
    # ========================================================

    print(
        "Initializing database..."
    )

    initialize_database()

    print(
        "Database ready."
    )

    print()

    # ========================================================
    # LOAD RESUME
    # ========================================================

    print(
        "Reading candidate resume..."
    )

    resume_text = extract_resume_text(
        str(RESUME_PATH)
    )

    print(
        f"Resume text extracted: {len(resume_text)} characters"
    )

    # ========================================================
    # CANDIDATE PROFILE
    # ========================================================

    candidate = {

        "name": "ABZAL RAHIMA KOWSAR MOHAMMAD",

        "email": "abzal.mod@gmail.com",

        "phone": "5515800701",

        "location": "Newark",

        "relocation": "Yes",

        "visa_status": (
            "STEM OPT valid till 02/14/2027"
        ),

        "linkedin": (
            "https://www.linkedin.com/in/abzal-m-15609a332"
        ),

        "applied_role": "Business Analyst",

        "total_experience": "4 Years",

        "relevant_experience": "3+ Years",

        "availability": "Immediately",

        "interview_availability": "ASAP",

        "address": (
            "111 Mulberry Street, Newark, 07102"
        )
    }
    # ========================================================
    # GET JOB SEARCH QUERY FROM USER
    # ========================================================

    print()
    print("=" * 60)
    print("        JOB SEARCH")
    print("=" * 60)
    print()

    job_title = input(
        "Enter the job title you want to search for: "
    ).strip()

    if not job_title:

        print()
        print(
            "Job title cannot be empty."
        )

        return

    print()
    print(
        f"Searching for: {job_title}"
    )

    print()

    # ========================================================
    # START LINKEDIN
    # ========================================================

    driver = start_browser()

    try:

        login_to_linkedin(
            driver
        )

        # ----------------------------------------------------
        # GENERATE SEARCH QUERY
        # ----------------------------------------------------

        query = generate_search_query(
            job_title
        )

        print()
        print("=" * 60)
        print("LINKEDIN SEARCH QUERY")
        print("=" * 60)

        print(
            query
        )

        print()

        # ----------------------------------------------------
        # SEARCH LINKEDIN POSTS
        # ----------------------------------------------------

        search_linkedin_posts(
            driver,
            query
        )

        # ----------------------------------------------------
        # EXTRACT POSTS
        # ----------------------------------------------------

        posts = extract_posts(
            driver
        )

        print()

        print(
            f"Posts extracted: "
            f"{len(posts)}"
        )

        # ----------------------------------------------------
        # FILTER JOB POSTS
        # ----------------------------------------------------

        valid_jobs = filter_job_posts(
            posts,
            job_title
        )

        # ====================================================
        # RESTORE CORRECT LINKEDIN POST AUTHOR NAMES
        # ====================================================

        recruiter_name_map = (
            load_linkedin_recruiter_names()
        )

        print()

        print(
            "=" * 60
        )

        print(
            "RESTORING LINKEDIN POST AUTHORS"
        )

        print(
            "=" * 60
        )

        restored_count = 0

        for job in valid_jobs:

            post_url = (
                job.get(
                    "linkedin_post_url"
                )
            )

            if not post_url:
                continue

            # ------------------------------------------------
            # Direct URL match
            # ------------------------------------------------

            correct_name = (
                recruiter_name_map.get(
                    post_url
                )
            )

            # ------------------------------------------------
            # If URL formatting differs slightly,
            # compare cleaned versions.
            # ------------------------------------------------

            if not correct_name:

                normalized_job_url = (
                    post_url.strip().rstrip("/")
                )

                for saved_url, saved_name in (
                    recruiter_name_map.items()
                ):

                    normalized_saved_url = (
                        saved_url.strip().rstrip("/")
                    )

                    if (
                        normalized_job_url
                        == normalized_saved_url
                    ):

                        correct_name = saved_name
                        break

            # ------------------------------------------------
            # Update recruiter name
            # ------------------------------------------------

            if correct_name:

                job["recruiter_name"] = (
                    correct_name
                )

                restored_count += 1

                print()

                print(
                    "Correct LinkedIn recruiter "
                    "name restored:"
                )

                print(
                    f"Recruiter: {correct_name}"
                )

                print(
                    f"URL: {post_url}"
                )

        print()

        print(
            f"Recruiter names restored: "
            f"{restored_count}/{len(valid_jobs)}"
        )

        print()

        print("=" * 60)
        print("VALID JOBS")
        print("=" * 60)

        print(
            f"Valid jobs: "
            f"{len(valid_jobs)}"
        )

        print()

        # ====================================================
        # ELIGIBLE JOBS FOR APPLICATION
        # ====================================================

        eligible_jobs = []

        # ====================================================
        # PROCESS EACH JOB
        # ====================================================

        for index, job in enumerate(
            valid_jobs,
            start=1
        ):

            print()
            print("=" * 60)

            print(
                f"PROCESSING JOB {index}"
            )

            print("=" * 60)

            print(
                f"Job Title: "
                f"{job.get('job_title')}"
            )

            print(
                f"Company: "
                f"{job.get('company_name')}"
            )

            print(
                f"Recruiter: "
                f"{job.get('recruiter_name')}"
            )

            print(
                f"Email: "
                f"{job.get('recruiter_email')}"
            )

            print(
                f"Location: "
                f"{job.get('location')}"
            )

            print(
                f"Posted: "
                f"{job.get('posted_time')}"
            )

            print(
                f"LinkedIn URL: "
                f"{job.get('linkedin_post_url')}"
            )

            # ------------------------------------------------
            # CHECK RECRUITER EMAIL
            # ------------------------------------------------

            recruiter_email = (
                job.get("recruiter_email")
            )

            if not recruiter_email:

                print()
                print(
                    "SKIPPED: Recruiter email "
                    "is missing."
                )

                continue

            # ------------------------------------------------
            # CHECK LINKEDIN URL
            # ------------------------------------------------

            post_url = (
                job.get("linkedin_post_url")
            )

            if not post_url:

                print()
                print(
                    "SKIPPED: LinkedIn post URL "
                    "is missing."
                )

                continue

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            if is_already_processed(
                post_url
            ):

                print()
                print(
                    "SKIPPED: This job has "
                    "already been processed."
                )

                continue

            print()
            print(
                "Duplicate check: PASSED"
            )

            # ------------------------------------------------
            # SAVE DISCOVERED JOB
            # ------------------------------------------------

            try:

                save_submission(
                    job,
                    status="DISCOVERED"
                )

                print(
                    "Database status: DISCOVERED"
                )

            except Exception as error:

                print(
                    f"Database save warning: "
                    f"{error}"
                )

            # ------------------------------------------------
            # AI ANALYSIS
            # ------------------------------------------------

            analysis = analyze_single_job(
                job,
                candidate
            )

            # ------------------------------------------------
            # CHECK AI RECOMMENDATION
            # ------------------------------------------------

            recommendation = (
                analysis.get(
                    "recommendation",
                    "SKIP"
                )
            )

            recommendation = str(
                recommendation
            ).strip().upper()

            if recommendation != "APPLY":

                print()
                print(
                    "Gemini recommendation: "
                    f"{recommendation}"
                )

                print(
                    "Skipping this job."
                )

                continue

            # ------------------------------------------------
            # GEMINI APPROVED
            # ------------------------------------------------

            print()
            print(
                "Gemini recommendation: APPLY"
            )

            print(
                "Adding job to application list..."
            )

            eligible_jobs.append(
                job
            )

        # ====================================================
        # SHOW APPLICATION JOBS
        # ====================================================

        print()
        print("=" * 70)
        print("       APPLICATION SELECTION")
        print("=" * 70)
        print()

        print(
            f"Jobs eligible for application: "
            f"{len(eligible_jobs)}"
        )

        print()

        if eligible_jobs:

            display_application_options(
                eligible_jobs
            )

        else:

            print(
                "No jobs passed all application checks."
            )

            print(
                "There are no emails to send."
            )

            print()

        # ====================================================
        # APPLICATION MENU
        # ====================================================

        while True:

            print()
            print("=" * 70)
            print("             WHAT DO YOU WANT TO DO?")
            print("=" * 70)
            print()

            print(
                "1. Send email to ALL recruiters"
            )

            print(
                "2. Send email to a SPECIFIC job recruiter"
            )

            print(
                "3. Close browser"
            )

            print()

            choice = input(
                "Enter your choice (1/2/3): "
            ).strip()

            # =================================================
            # OPTION 1
            # =================================================

            if choice == "1":

                if not eligible_jobs:

                    print()
                    print(
                        "No eligible jobs available."
                    )

                    print(
                        "Nothing will be sent."
                    )

                    continue

                print()

                print(
                    f"You are about to send "
                    f"{len(eligible_jobs)} application(s)."
                )

                confirmation = input(
                    "Continue? (y/n): "
                ).strip().lower()

                if confirmation != "y":

                    print()
                    print(
                        "Sending cancelled."
                    )

                    continue

                send_to_all_jobs(
                    eligible_jobs,
                    candidate,
                    str(RESUME_PATH)
                )

                break

            # =================================================
            # OPTION 2
            # =================================================

            elif choice == "2":

                if not eligible_jobs:

                    print()
                    print(
                        "No eligible jobs available."
                    )

                    continue

                send_to_specific_job(
                    eligible_jobs,
                    candidate,
                    str(RESUME_PATH)
                )

                break

            # =================================================
            # OPTION 3
            # =================================================

            elif choice == "3":

                print()
                print(
                    "No further applications will be sent."
                )

                print(
                    "Closing browser..."
                )

                break

            # =================================================
            # INVALID OPTION
            # =================================================

            else:

                print()
                print(
                    "Invalid choice."
                )

                print(
                    "Please enter 1, 2, or 3."
                )

        # ====================================================
        # FINAL SUMMARY
        # ====================================================

        

        print()

        print("=" * 60)
        print("AUTOMATION COMPLETED")
        print("=" * 60)

        print()

        input(
            "Press ENTER to close LinkedIn..."
        )

    finally:

        driver.quit()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()