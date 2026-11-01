"""
Core automation pipeline, extracted out of the old monolithic main.py.

This module has no input()/print() interactive prompts - it's pure
functions that either the CLI (main.py) or, eventually, an API
endpoint can call. This is what makes the dashboard's "controls"
phase possible later without another rewrite.

IMPORTANT FIX vs the original main.py:
    The original code imported `analyze_job` from ai.job_analyzer but
    never actually called it - `analysis` was referenced without ever
    being assigned, which would crash with a NameError the first time
    a valid job reached that point. `analyze_and_filter_jobs()` below
    actually calls analyze_job() for each candidate job and persists
    the match_score, fixing that.
"""

from config.settings import RESUME_PATH, MIN_MATCH_SCORE
from config.logger import get_logger

from resume.parser import extract_resume_text, extract_candidate_info

from linkedin.search import (
    start_browser,
    login_to_linkedin,
    search_linkedin_posts,
    extract_posts,
    filter_job_posts,
    generate_search_query,
)

from ai.job_analyzer import analyze_job
from gmail.draft import send_gmail_application

from database.submissions import (
    initialize_database,
    is_already_processed,
    save_submission,
    get_all_submissions,
)

log = get_logger(__name__)


# ============================================================
# CANDIDATE / RESUME
# ============================================================

def load_candidate(resume_path=None):
    """Reads the resume PDF and extracts the candidate's profile."""
    resume_path = resume_path or RESUME_PATH

    log.info("Reading candidate resume from %s", resume_path)
    resume_text = extract_resume_text(str(resume_path))
    candidate = extract_candidate_info(resume_text)

    log.info("Candidate: %s (target title: %s)", candidate.get("name"), candidate.get("job_title"))
    return resume_text, candidate


# ============================================================
# DISCOVERY
# ============================================================

def discover_jobs(driver, job_title):
    """
    Logs in, searches LinkedIn, and returns job posts that passed
    LinkedIn-side filtering (Full-Time, US, posted recently).
    """
    login_to_linkedin(driver)

    query = generate_search_query(job_title)
    log.info("Search query: %s", query)

    search_linkedin_posts(driver, query)
    posts = extract_posts(driver)
    log.info("Posts extracted: %s", len(posts))

    valid_jobs = filter_job_posts(posts, job_title)
    log.info("Valid job posts after filtering: %s", len(valid_jobs))

    return valid_jobs


# ============================================================
# ANALYSIS + ELIGIBILITY
# ============================================================

def analyze_and_filter_jobs(valid_jobs, resume_text):
    """
    For each valid job:
      1. Skip if missing recruiter email or post URL.
      2. Skip if already processed (SENT, or seen within the
         reconsideration window - see database/submissions.py).
      3. Record it as DISCOVERED.
      4. Run Gemini analysis to get a match score + recommendation.
      5. Record the ANALYZED result (with match_score persisted).
      6. If Gemini recommends APPLY and the score clears
         MIN_MATCH_SCORE, add it to the eligible list.

    Returns the list of eligible jobs, each annotated with an
    "analysis" key holding the full Gemini result.
    """
    eligible_jobs = []

    for index, job in enumerate(valid_jobs, start=1):
        job_title = job.get("job_title")
        company = job.get("company_name")
        log.info("[%s/%s] Processing: %s @ %s", index, len(valid_jobs), job_title, company)

        recruiter_email = job.get("recruiter_email")
        if not recruiter_email:
            log.info("SKIPPED (no recruiter email): %s", job_title)
            continue

        post_url = job.get("linkedin_post_url")
        if not post_url:
            log.info("SKIPPED (no LinkedIn post URL): %s", job_title)
            continue

        if is_already_processed(post_url):
            log.info("SKIPPED (already processed / within reconsideration window): %s", job_title)
            continue

        save_submission(job, status="DISCOVERED")

        try:
            analysis = analyze_job(resume_text, job)
        except Exception as error:
            log.error("Gemini analysis failed for '%s': %s", job_title, error)
            save_submission(job, status="ANALYSIS_FAILED")
            continue

        match_score = analysis.get("match_score", 0)
        recommendation = analysis.get("recommendation", "SKIP")

        save_submission(job, status="ANALYZED", match_score=match_score)

        if recommendation != "APPLY" or match_score < MIN_MATCH_SCORE:
            log.info(
                "SKIPPED (recommendation=%s, score=%s, min=%s): %s",
                recommendation, match_score, MIN_MATCH_SCORE, job_title,
            )
            save_submission(job, status="SKIPPED", match_score=match_score)
            continue

        log.info("ELIGIBLE (score=%s): %s", match_score, job_title)
        job_with_analysis = dict(job)
        job_with_analysis["analysis"] = analysis
        eligible_jobs.append(job_with_analysis)

    return eligible_jobs


# ============================================================
# APPLICATION SENDING
# ============================================================

def send_application(job, candidate, resume_pdf):
    """Sends the application email and records the outcome. Returns True/False."""
    try:
        result = send_gmail_application(job, candidate, resume_pdf)

        match_score = job.get("analysis", {}).get("match_score")
        save_submission(
            job,
            status="SENT",
            match_score=match_score,
            gmail_message_id=result.get("id"),
        )

        log.info(
            "SENT: %s @ %s -> %s (message id: %s)",
            job.get("job_title"), job.get("company_name"), job.get("recruiter_email"), result.get("id"),
        )
        return True

    except Exception as error:
        log.error("FAILED to send application for '%s': %s", job.get("job_title"), error)
        save_submission(job, status="FAILED", match_score=job.get("analysis", {}).get("match_score"))
        return False


def send_to_all_jobs(eligible_jobs, candidate, resume_pdf):
    successful = 0
    failed = 0

    for index, job in enumerate(eligible_jobs, start=1):
        log.info("[%s/%s] Sending application...", index, len(eligible_jobs))
        if send_application(job, candidate, resume_pdf):
            successful += 1
        else:
            failed += 1

    log.info("Send summary: %s successful, %s failed (of %s total)", successful, failed, len(eligible_jobs))
    return successful, failed


# ============================================================
# FULL RUN (discover -> analyze -> return eligible jobs)
# ============================================================

def run_discovery_pipeline(resume_path=None):
    """
    One full non-interactive pass: load candidate, open browser, log
    in, search, filter, analyze. Returns (candidate, eligible_jobs).
    The caller decides what to do with eligible_jobs (send all,
    send some, or just display them).
    """
    initialize_database()

    resume_text, candidate = load_candidate(resume_path)
    job_title = candidate.get("job_title")

    driver = start_browser()
    try:
        valid_jobs = discover_jobs(driver, job_title)
        eligible_jobs = analyze_and_filter_jobs(valid_jobs, resume_text)
        return candidate, eligible_jobs
    finally:
        driver.quit()
