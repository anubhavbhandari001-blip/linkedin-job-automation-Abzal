import base64
import re
import random

from email.message import EmailMessage
from pathlib import Path

from googleapiclient.discovery import build

from gmail.auth import get_gmail_credentials


# ============================================================
# CLEAN RECRUITER NAME
# ============================================================

def clean_recruiter_name(name):

    if not name:
        return "Hiring Team"

    name = str(name).strip()

    # --------------------------------------------------------
    # Remove LinkedIn connection information
    # Example:
    # John Smith • 3rd+
    # --------------------------------------------------------

    name = re.sub(
        r"\s*[•|]\s*.*$",
        "",
        name
    ).strip()

    # --------------------------------------------------------
    # Invalid recruiter-name patterns
    # --------------------------------------------------------

    invalid_patterns = [

        "c2c",
        "w2",
        "direct client",
        "implementation partner",
        "implementation partners",
        "all over usa",
        "all over us",
        "all over canada",

        "positions",
        "job positions",
        "remote positions",

        "we are hiring",
        "we're hiring",
        "we’re hiring",

        "hiring",
        "jobs in",
        "job opportunity",

        "recruiter",
        "recruitment",
        "staffing",
        "staffing specialist",
        "talent acquisition",

        "career",
        "careers",
        "vacancies",
        "vacancy"
    ]

    lower_name = name.lower()

    for pattern in invalid_patterns:

        if pattern in lower_name:
            return "Hiring Team"

    # --------------------------------------------------------
    # Reject email addresses
    # --------------------------------------------------------

    if "@" in name:
        return "Hiring Team"

    # --------------------------------------------------------
    # Reject URLs
    # --------------------------------------------------------

    if (
        "http://" in lower_name
        or "https://" in lower_name
        or "www." in lower_name
    ):
        return "Hiring Team"

    # --------------------------------------------------------
    # Reject excessively long names
    # --------------------------------------------------------

    if len(name) > 60:
        return "Hiring Team"

    # --------------------------------------------------------
    # Reject too many words
    # --------------------------------------------------------

    if len(name.split()) > 5:
        return "Hiring Team"

    # --------------------------------------------------------
    # Reject obvious job-description text
    # --------------------------------------------------------

    job_words = [

        "developer",
        "engineer",
        "software",
        "full stack",
        "frontend",
        "backend",

        "apply",
        "position",
        "opportunity",

        "usa",
        "canada"
    ]

    if any(
        word in lower_name
        for word in job_words
    ):
        return "Hiring Team"

    return name


# ============================================================
# CLEAN LINKEDIN JOB DESCRIPTION
# ============================================================

def clean_job_description(text):

    if not text:
        return "Job description not available."

    lines = text.splitlines()

    cleaned_lines = []

    # ========================================================
    # CLEAN EACH LINE
    # ========================================================

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # ----------------------------------------------------
        # Convert markdown image links
        # [📋](https://fonts.gstatic.com/...)
        # -> 📋
        # ----------------------------------------------------

        line = re.sub(
            r"\[([^\]]+)\]\(https?://[^)]+\)",
            r"\1",
            line
        )

        # ----------------------------------------------------
        # Convert mailto markdown links
        # [email](mailto:email)
        # -> email
        # ----------------------------------------------------

        line = re.sub(
            r"\[([^\]]+)\]\(mailto:[^)]+\)",
            r"\1",
            line
        )

        # ----------------------------------------------------
        # Convert any remaining markdown links
        # ----------------------------------------------------

        line = re.sub(
            r"\[([^\]]+)\]\([^)]+\)",
            r"\1",
            line
        )

        # ----------------------------------------------------
        # Remove escaped @
        # ----------------------------------------------------

        line = line.replace(
            r"\@",
            "@"
        )

        cleaned_lines.append(line)

    # ========================================================
    # FIND START OF REAL JOB DESCRIPTION
    # ========================================================

    start_keywords = [

        "immediate hiring",
        "we are hiring",
        "we're hiring",
        "we’re hiring",

        "hiring:",
        "hiring ",

        "urgent hiring",

        "job opportunity",
        "exciting opportunity",
        "immediate opportunity",

        "now hiring",

        "open positions",
        "multiple openings",

        "career opportunity",

        "we are looking for",
        "we're looking for",
        "we’re looking for",

        "looking for",

        "position:",
        "positions:"
    ]

    start_index = None

    for index, line in enumerate(cleaned_lines):

        lower = line.lower().strip()

        if any(
            keyword in lower
            for keyword in start_keywords
        ):

            start_index = index
            break

    # ========================================================
    # REMOVE LINKEDIN HEADER
    # ========================================================

    if start_index is not None:

        job_lines = cleaned_lines[start_index:]

    else:

        job_lines = []

        for line in cleaned_lines:

            lower = line.lower().strip()

            if lower in [
                "feed post",
                "follow",
                "more",
                "… more",
                "... more"
            ]:
                continue

            job_lines.append(line)

    # ========================================================
    # REMOVE LINKEDIN UI
    # ========================================================

    final_lines = []

    for line in job_lines:

        lower = line.lower().strip()

        if lower in [
            "feed post",
            "follow",
            "more",
            "… more",
            "... more"
        ]:
            continue

        final_lines.append(line)

    # ========================================================
    # REMOVE HOW TO APPLY SECTION
    # ========================================================

    result_lines = []

    for line in final_lines:

        lower = line.lower().strip()

        # ----------------------------------------------------
        # Stop completely when application instructions begin
        # ----------------------------------------------------

        if (
            "how to apply" in lower
            or lower == "how to apply:"
            or lower == "application process"
            or lower.startswith("how to apply:")
        ):

            break

        result_lines.append(line)

    # ========================================================
    # REMOVE HASHTAGS
    # ========================================================

    hashtag_cleaned = []

    for line in result_lines:

        # ----------------------------------------------------
        # Remove entire hashtag-only lines
        # ----------------------------------------------------

        if re.fullmatch(
            r"(?:\s*#[A-Za-z0-9_]+\s*)+",
            line
        ):
            continue

        # ----------------------------------------------------
        # Remove hashtags inside normal lines
        # ----------------------------------------------------

        line = re.sub(
            r"\s*#[A-Za-z0-9_]+",
            "",
            line
        ).strip()

        if line:
            hashtag_cleaned.append(line)

    # ========================================================
    # REMOVE LINKEDIN REACTION NUMBERS
    # ========================================================

    while hashtag_cleaned:

        last_line = hashtag_cleaned[-1].strip()

        if re.fullmatch(
            r"\d+",
            last_line
        ):
            hashtag_cleaned.pop()

        else:
            break

    # ========================================================
    # REMOVE LINKEDIN IMAGE URL ARTIFACTS
    # ========================================================

    final_cleaned = []

    for line in hashtag_cleaned:

        if (
            "fonts.gstatic.com" in line
            or "gstatic.com/s/e/notoemoji" in line
        ):
            continue

        final_cleaned.append(line)

    # ========================================================
    # BUILD FINAL DESCRIPTION
    # ========================================================

    result = "\n\n".join(
        final_cleaned
    ).strip()

    # ========================================================
    # FINAL CLEANUP
    # ========================================================

    result = result.replace(
        r"\@",
        "@"
    )

    # Remove excessive blank lines

    result = re.sub(
        r"\n{3,}",
        "\n\n",
        result
    )

    # ========================================================
    # FALLBACK
    # ========================================================

    if not result:
        return "Job description not available."

    return result


# ============================================================
# SEND GMAIL APPLICATION
# ============================================================

def send_gmail_application(
    job,
    candidate,
    resume_pdf_path
):

    # --------------------------------------------------------
    # GET GMAIL CREDENTIALS
    # --------------------------------------------------------

    credentials = get_gmail_credentials()

    gmail_service = build(
        "gmail",
        "v1",
        credentials=credentials
    )

    # ========================================================
    # JOB INFORMATION
    # ========================================================

    recruiter_name = clean_recruiter_name(
        job.get("recruiter_name")
    )

    recruiter_email = (
        job.get("recruiter_email")
    )

    job_title = (
        job.get("job_title")
        or "the position"
    )

    company_name = (
        job.get("company_name")
        or ""
    )

    linkedin_post_url = (
        job.get("linkedin_post_url")
    )

    raw_job_description = (
        job.get("job_description")
        or ""
    )

    # ========================================================
    # CLEAN JOB DESCRIPTION
    # ========================================================

    job_description = clean_job_description(
        raw_job_description
    )

    # ========================================================
    # VALIDATE RECRUITER EMAIL
    # ========================================================

    if not recruiter_email:

        raise ValueError(
            "Recruiter email is missing."
        )

    # ========================================================
    # VALIDATE LINKEDIN URL
    # ========================================================

    if not linkedin_post_url:

        raise ValueError(
            "LinkedIn post URL is missing."
        )

    # ========================================================
    # CANDIDATE DETAILS
    # ========================================================

    candidate_name = (
        candidate.get("name") or ""
    )

    candidate_email = (
        candidate.get("email") or ""
    )

    candidate_phone = (
        candidate.get("phone") or ""
    )

    candidate_location = (
        candidate.get("location") or ""
    )

    candidate_relocation = (
        candidate.get("relocation") or ""
    )

    candidate_visa_status = (
        candidate.get("visa_status") or ""
    )

    candidate_linkedin = (
        candidate.get("linkedin") or ""
    )

    candidate_applied_role = (
        candidate.get("applied_role") or job_title
    )

    candidate_total_experience = (
        candidate.get("total_experience") or ""
    )

    candidate_availability = (
        candidate.get("availability") or ""
    )

    candidate_rate = (
        candidate.get("rate_compensation") or ""
    )

    # ========================================================
    # BUILD SUBMISSION DETAILS
    # ========================================================

    submission_fields = [

        ("Candidate Name", candidate_name),

        ("Applied Role", candidate_applied_role),

        ("Total Experience", candidate_total_experience),

        ("Phone / Contact", candidate_phone),

        ("Email Address", candidate_email),

        ("Current Location", candidate_location),

        ("Relocation", candidate_relocation),

        ("Work Authorization", candidate_visa_status),

        ("Availability", candidate_availability),

        ("Rate / Compensation", candidate_rate),

        ("LinkedIn Profile", candidate_linkedin),
    ]

    submission_details = []

    for label, value in submission_fields:

        if value:

            submission_details.append(
                f"• {label}: {value}"
            )

    submission_profile = "\n".join(
        submission_details
    )
    # ========================================================
    # CREATE EMAIL
    # ========================================================

    message = EmailMessage()

    # --------------------------------------------------------
    # TO
    # --------------------------------------------------------

    message["To"] = recruiter_email

    # --------------------------------------------------------
    # CC
    # --------------------------------------------------------

    cc_addresses = [
        "joyal@jpitstaffing.com",
        "abzal.mod@gmail.com"
    ]

    cc_addresses = [
        email.strip()
        for email in cc_addresses
        if email and email.strip()
    ]

    if cc_addresses:
        message["Cc"] = ", ".join(cc_addresses)

    # --------------------------------------------------------
    # BCC
    # --------------------------------------------------------

    message["Bcc"] = (
        "kim@jpitstaffing.com"
    )

    # ========================================================
    # SUBJECT
    # ========================================================

    message["Subject"] = (
        f"Submission for {job_title} - "
        f"{candidate_name}"
    )


        # ============================================================
    # EMAIL BODY
    # ============================================================

    body = f"""Dear {recruiter_name},

I hope you are doing well.

I came across your LinkedIn post regarding the {job_title} opportunity"""

    if company_name:
        body += f" at {company_name}"

    body += """ and would like to express my interest in the position.

Please find my submission details below for your review:

--- SUBMISSION DETAILS ---
    """

    # ============================================================
    # ADD SUBMISSION DETAILS
    # ============================================================

    if submission_profile:

        body += (
            submission_profile
            + "\n"
        )

    # ============================================================
    # CLOSING
    # ============================================================

    body += """
I have attached my updated resume for your review. I would welcome the opportunity to discuss how my skills and experience could contribute to this position.

Thank you for your time and consideration.

Best Regards,

    """

    # ============================================================
    # CANDIDATE CONTACT
    # ============================================================

    if candidate_name:
        body += candidate_name + "\n"

    if candidate_email:
        body += candidate_email + "\n"

    if candidate_phone:
        body += candidate_phone + "\n"

    # ============================================================
    # LINKEDIN JOB POST
    # ============================================================

    body += f"""

--- LINKEDIN JOB POST ---
    {linkedin_post_url}

    """

    # ============================================================
    # JOB DESCRIPTION
    # ============================================================

    body += f"""--- JOB DESCRIPTION ---

    {job_description}
    """



    # ========================================================
    # SET EMAIL CONTENT
    # ========================================================

    message.set_content(
        body
    )

    # ========================================================
    # ATTACH RESUME
    # ========================================================

    resume_path = Path(
        resume_pdf_path
    )

    if not resume_path.exists():

        raise FileNotFoundError(
            f"Resume not found: {resume_path}"
        )

    with open(
        resume_path,
        "rb"
    ) as file:

        resume_data = file.read()

    # ========================================================
    # RANDOM RESUME FILENAME
    # ========================================================

    random_number = random.randint(
        100,
        999
    )

    resume_filename = (
        f"Resume_{random_number}.pdf"
    )

    message.add_attachment(

        resume_data,

        maintype="application",

        subtype="pdf",

        filename=resume_filename
    )

    # ========================================================
    # ENCODE GMAIL MESSAGE
    # ========================================================

    encoded_message = (
        base64.urlsafe_b64encode(
            message.as_bytes()
        )
        .decode()
    )

    gmail_body = {
        "raw": encoded_message
    }

    # ========================================================
    # SEND EMAIL
    # ========================================================

    result = (
        gmail_service
        .users()
        .messages()
        .send(
            userId="me",
            body=gmail_body
        )
        .execute()
    )

    # ========================================================
    # RETURN RESULT
    # ========================================================

    return result
