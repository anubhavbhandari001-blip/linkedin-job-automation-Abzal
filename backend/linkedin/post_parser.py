import re


# ============================================================
# CHECK IF POST IS A HIRING POST
# ============================================================

def is_hiring_post(text):

    if not text:
        return False

    text_lower = text.lower()

    hiring_keywords = [
        "we're hiring",
        "we are hiring",
        "hiring",
        "job opening",
        "job openings",
        "open position",
        "open positions",
        "looking for",
        "vacancy",
        "vacancies",
        "recruiting",
        "recruitment",
        "immediate opening",
        "career opportunity",
        "sourcing talent",
        "submit your cv",
        "submit your resume",
        "send your resume",
        "send resume",
        "send your cv",
        "apply now",
        "applications are open",
    ]

    for keyword in hiring_keywords:

        if keyword in text_lower:
            return True

    return False


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = text.lower()

    # Normalize dash characters
    text = text.replace("-", " ")
    text = text.replace("–", " ")
    text = text.replace("—", " ")

    # Normalize slash
    text = text.replace("/", " ")

    # Replace punctuation
    text = re.sub(
        r"[^a-z0-9+#.\s]",
        " ",
        text
    )

    # Remove duplicate spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# GENERATE JOB TITLE VARIATIONS
# ============================================================

def get_job_title_variations(candidate_job_title):

    if not candidate_job_title:
        return []

    title = candidate_job_title.lower().strip()

    variations = set()

    variations.add(title)

    # --------------------------------------------------------
    # FRONTEND
    # --------------------------------------------------------

    if (
        "frontend developer" in title
        or "front end developer" in title
        or "front-end developer" in title
    ):

        variations.update([
            "frontend developer",
            "front end developer",
            "front-end developer",
            "frontend engineer",
            "front end engineer",
            "front-end engineer",
            "frontend",
            "front end",
            "front-end",
        ])

    # --------------------------------------------------------
    # BACKEND
    # --------------------------------------------------------

    if (
        "backend developer" in title
        or "back end developer" in title
        or "back-end developer" in title
    ):

        variations.update([
            "backend developer",
            "back end developer",
            "back-end developer",
            "backend engineer",
            "back end engineer",
            "back-end engineer",
            "backend",
            "back end",
            "back-end",
        ])

    # --------------------------------------------------------
    # FULL STACK
    # --------------------------------------------------------

    if "full stack" in title:

        variations.update([
            "full stack developer",
            "full-stack developer",
            "fullstack developer",
            "full stack engineer",
            "full-stack engineer",
            "fullstack engineer",
            "full stack",
        ])

    # --------------------------------------------------------
    # SOFTWARE DEVELOPER
    # --------------------------------------------------------

    if "software developer" in title:

        variations.update([
            "software developer",
            "software engineer",
            "developer",
        ])

    # --------------------------------------------------------
    # REACT
    # --------------------------------------------------------

    if "react" in title:

        variations.update([
            "react developer",
            "react engineer",
            "react.js developer",
            "reactjs developer",
        ])

    return list(variations)


# ============================================================
# CHECK JOB TITLE
# ============================================================

def contains_job_title(
    text,
    candidate_job_title
):

    if not text or not candidate_job_title:
        return False

    text_normalized = normalize_text(text)

    variations = get_job_title_variations(
        candidate_job_title
    )

    for variation in variations:

        variation_normalized = normalize_text(
            variation
        )

        if variation_normalized in text_normalized:
            return True

    return False


# # ============================================================
# # CHECK FULL-TIME
# # ============================================================

# def is_full_time(text):

#     if not text:
#         return False

#     text_lower = text.lower()

#     keywords = [
#         "full-time",
#         "full time",
#         "fulltime",
#     ]

#     for keyword in keywords:

#         if keyword in text_lower:
#             return True

#     # W2 employment
#     if re.search(
#         r"\bw2\b",
#         text_lower
#     ):
#         return True

#     return False


# ============================================================
# EXTRACT EMAIL
# ============================================================

def extract_email(text):

    if not text:
        return None

    email_pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}"
    )

    matches = re.findall(
        email_pattern,
        text
    )

    if not matches:
        return None

    for email in matches:

        email = email.strip(
            ".,;:()[]{}<>"
        )

        if email:
            return email

    return None


# ============================================================
# EXTRACT RECRUITER NAME
# ============================================================

def extract_recruiter_name(text):

    if not text:
        return None

    # --------------------------------------------------------
    # LOOK FOR EXPLICIT RECRUITER / CONTACT NAME
    # --------------------------------------------------------

    patterns = [

        r"recruiter\s*:\s*([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",

        r"recruiter\s*-\s*([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",

        r"contact\s*:\s*([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",

        r"contact\s*-\s*([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",

        r"recruiter\s+([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",

        r"contact\s+([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            if name and "@" not in name:
                return name

    # --------------------------------------------------------
    # LOOK FOR:
    #
    # Send your resume to John Smith
    # Submit your CV to John Smith
    # --------------------------------------------------------

    patterns = [

        r"send\s+(?:your\s+)?(?:resume|cv)\s+to\s+([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",

        r"submit\s+(?:your\s+)?(?:resume|cv)\s+to\s+([A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){0,3})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            if name and "@" not in name:
                return name

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # DO NOT USE LINKEDIN POST AUTHOR AS RECRUITER
    # --------------------------------------------------------

    return None



# ============================================================
# EXTRACT JOB TITLE
# ============================================================

def extract_job_title(
    text,
    candidate_job_title
):

    if not text:
        return candidate_job_title

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    candidate_lower = (
        candidate_job_title.lower()
        if candidate_job_title
        else ""
    )

    # --------------------------------------------------------
    # Direct candidate title
    # --------------------------------------------------------

    for line in lines:

        lower = line.lower()

        if candidate_lower and candidate_lower in lower:

            return candidate_job_title

    # --------------------------------------------------------
    # Frontend
    # --------------------------------------------------------

    frontend_keywords = [
        "frontend developer",
        "front end developer",
        "front-end developer",
        "frontend engineer",
        "front end engineer",
        "front-end engineer",
    ]

    for line in lines:

        lower = line.lower()

        for keyword in frontend_keywords:

            if keyword in lower:

                return "Frontend Developer"

    # --------------------------------------------------------
    # Backend
    # --------------------------------------------------------

    backend_keywords = [
        "backend developer",
        "back end developer",
        "back-end developer",
        "backend engineer",
        "back end engineer",
        "back-end engineer",
    ]

    for line in lines:

        lower = line.lower()

        for keyword in backend_keywords:

            if keyword in lower:

                return "Backend Developer"

    # --------------------------------------------------------
    # Full Stack
    # --------------------------------------------------------

    for line in lines:

        lower = line.lower()

        if (
            "full stack developer" in lower
            or "full-stack developer" in lower
            or "fullstack developer" in lower
        ):

            return "Full Stack Developer"

    # --------------------------------------------------------
    # Software
    # --------------------------------------------------------

    for line in lines:

        lower = line.lower()

        if "software developer" in lower:
            return "Software Developer"

        if "software engineer" in lower:
            return "Software Engineer"

    # --------------------------------------------------------
    # React
    # --------------------------------------------------------

    for line in lines:

        lower = line.lower()

        if (
            "react developer" in lower
            or "react.js developer" in lower
            or "reactjs developer" in lower
        ):

            return "React Developer"

    return candidate_job_title


# ============================================================
# EXTRACT EXPERIENCE
# ============================================================

def extract_experience(text):

    if not text:
        return None

    patterns = [

        # 2-5 years
        r"\b\d+\s*[-–]\s*\d+\s*(?:years?|months?)\b",

        # 2 years experience
        r"\b\d+\s*(?:years?|months?)\s*(?:of\s*)?experience\b",

        # Freshers
        r"\bfreshers?\b",

        r"\bfresher\b",

        # Entry level
        r"\bentry[- ]level\b",

        # Common ranges
        r"\b0\s*[-–]\s*2\s*years?\b",

        r"\b1\s*[-–]\s*3\s*years?\b",

        r"\b2\s*[-–]\s*5\s*years?\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(0)

    return None


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(text):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------------
    # Explicit location
    # --------------------------------------------------------

    location_keywords = [
        "location:",
        "based in:",
        "work location:",
        "job location:",
    ]

    for line in lines:

        lower = line.lower()

        for keyword in location_keywords:

            if keyword in lower:

                return line.split(
                    ":",
                    1
                )[-1].strip()

    # --------------------------------------------------------
    # Remote / Hybrid / On-site
    # --------------------------------------------------------

    for line in lines:

        lower = line.lower()

        if (
            "remote" in lower
            or "hybrid" in lower
            or "on-site" in lower
            or "onsite" in lower
        ):

            # Prefer lines containing US information
            if (
                "united states" in lower
                or "usa" in lower
                or "u.s." in lower
            ):

                return line

    # --------------------------------------------------------
    # US indicators
    # --------------------------------------------------------

    us_indicators = [

        "united states",
        "usa",
        "u.s.",
        "u.s.a.",

        "new york",
        "nyc",
        "california",
        "texas",
        "florida",
        "washington",
        "illinois",
        "massachusetts",
        "virginia",
        "maryland",
        "colorado",
        "arizona",
        "georgia",
        "pennsylvania",
        "ohio",
        "michigan",
        "oregon",
        "nevada",
        "new jersey",
        "north carolina",
        "south carolina",
        "minnesota",
        "tennessee",
        "indiana",
        "missouri",
        "wisconsin",

        "san francisco",
        "los angeles",
        "seattle",
        "chicago",
        "boston",
        "austin",
        "dallas",
        "houston",
        "atlanta",
        "miami",
        "denver",
        "phoenix",
        "san diego",
        "philadelphia",
        "portland",
        "san jose",
        "charlotte",
        "baltimore",
        "detroit",
        "minneapolis",
        "las vegas",
    ]

    for line in lines:

        lower = line.lower()

        for indicator in us_indicators:

            if indicator in lower:

                return line

    # --------------------------------------------------------
    # Remote fallback
    # --------------------------------------------------------

    for line in lines:

        if "remote" in line.lower():

            return line

    return None


# ============================================================
# CHECK US LOCATION
# ============================================================

def is_us_location(location):

    if not location:
        return False

    location_lower = location.lower()

    us_indicators = [

        "united states",
        "usa",
        "u.s.",
        "u.s.a.",

        "new york",
        "nyc",
        "san francisco",
        "los angeles",
        "seattle",
        "chicago",
        "boston",
        "austin",
        "dallas",
        "houston",
        "atlanta",
        "miami",
        "denver",
        "phoenix",
        "san diego",
        "philadelphia",
        "portland",
        "san jose",
        "charlotte",
        "baltimore",
        "detroit",
        "minneapolis",
        "las vegas",

        "california",
        "texas",
        "florida",
        "washington",
        "illinois",
        "massachusetts",
        "virginia",
        "maryland",
        "colorado",
        "arizona",
        "georgia",
        "pennsylvania",
        "ohio",
        "michigan",
        "oregon",
        "nevada",
        "new jersey",
        "north carolina",
        "south carolina",
        "minnesota",
        "tennessee",
        "indiana",
        "missouri",
        "wisconsin",
    ]

    for indicator in us_indicators:

        if indicator in location_lower:
            return True

    return False


# ============================================================
# EXTRACT COMPANY
# ============================================================

def extract_company(text):

    if not text:
        return None

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------------
    # Explicit company field
    # --------------------------------------------------------

    for line in lines:

        match = re.search(
            r"company\s*:\s*(.+)",
            line,
            re.IGNORECASE
        )

        if match:

            company = match.group(1).strip()

            if company:
                return company

    # --------------------------------------------------------
    # "at COMPANY"
    # --------------------------------------------------------

    match = re.search(
        r"\bat\s+([A-Z][A-Za-z0-9&.,' -]{2,80})",
        text
    )

    if match:

        company = match.group(1).strip()

        # Remove common trailing text
        company = re.split(
            r"\s+(?:is|are|hiring|recruiting)\b",
            company,
            flags=re.IGNORECASE
        )[0].strip()

        return company

    # --------------------------------------------------------
    # COMPANY IS RECRUITING / HIRING
    # --------------------------------------------------------

    match = re.search(
        r"\b([A-Z][A-Za-z0-9&.,' -]{2,80})"
        r"\s+is\s+(?:recruiting|hiring)\b",
        text,
        re.IGNORECASE
    )

    if match:

        return match.group(1).strip()

    return None


# ============================================================
# EXTRACT POSTED TIME
# ============================================================

def extract_posted_hours(text):

    if not text:
        return 999

    text_lower = text.lower()

    # --------------------------------------------------------
    # Minutes
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d+)\s*m\b",
        text_lower
    )

    if match:
        return int(match.group(1)) / 60

    # --------------------------------------------------------
    # Hours
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d+)\s*h\b",
        text_lower
    )

    if match:
        return int(match.group(1))

    # --------------------------------------------------------
    # Days
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d+)\s*d\b",
        text_lower
    )

    if match:
        return int(match.group(1)) * 24

    # --------------------------------------------------------
    # Weeks
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d+)\s*w\b",
        text_lower
    )

    if match:
        return int(match.group(1)) * 7 * 24

    # --------------------------------------------------------
    # Full words
    # --------------------------------------------------------

    match = re.search(
        r"\b(\d+)\s+minutes?\b",
        text_lower
    )

    if match:
        return int(match.group(1)) / 60

    match = re.search(
        r"\b(\d+)\s+hours?\b",
        text_lower
    )

    if match:
        return int(match.group(1))

    match = re.search(
        r"\b(\d+)\s+days?\b",
        text_lower
    )

    if match:
        return int(match.group(1)) * 24

    match = re.search(
        r"\b(\d+)\s+weeks?\b",
        text_lower
    )

    if match:
        return int(match.group(1)) * 7 * 24

    return 999


# ============================================================
# MAIN PARSER
# ============================================================

def parse_job_post(
    text,
    candidate_job_title
):

    result = {

        "is_hiring_post": False,

        "recruiter_name": None,

        "recruiter_email": None,

        "company_name": None,

        "job_title": None,

        "job_description": (
            text.strip()
            if text
            else ""
        ),

        "skills_required": [],

        "experience_required": None,

        "location": None,

        "is_us_job": False,

        "employment_type": None,

        "posted_time": None,

        "posted_hours_ago": 999,

        "linkedin_post_url": None,

        "valid": False,

        "skip_reason": None,
    }

    # ========================================================
    # HIRING POST
    # ========================================================

    if not is_hiring_post(text):

        result["skip_reason"] = (
            "Not a hiring/recruitment post"
        )

        return result

    result["is_hiring_post"] = True

    # ========================================================
    # JOB TITLE
    # ========================================================

    # ========================================================
    # JOB TITLE
    # ========================================================

    # The job title is already controlled by the
    # LinkedIn search query.
    #
    # Do NOT reject the post if the title is not
    # explicitly found inside the post description.

    result["job_title"] = extract_job_title(
        text,
        candidate_job_title
    )

    # # ========================================================
    # # FULL-TIME
    # # ========================================================

    # if not is_full_time(text):

    #     result["skip_reason"] = (
    #         "Not a Full-Time opportunity"
    #     )

    #     return result

    # result["employment_type"] = "Full-Time"

    # ========================================================
    # RECRUITER
    # ========================================================

    result["recruiter_name"] = (
        extract_recruiter_name(text)
    )

    # ========================================================
    # EMAIL
    # ========================================================

    result["recruiter_email"] = (
        extract_email(text)
    )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    result["experience_required"] = (
        extract_experience(text)
    )

    # ========================================================
    # LOCATION
    # ========================================================

    result["location"] = (
        extract_location(text)
    )

    result["is_us_job"] = (
        is_us_location(
            result["location"]
        )
    )

    # ========================================================
    # POSTED TIME
    # ========================================================

    result["posted_hours_ago"] = (
        extract_posted_hours(text)
    )

    # Keep a readable posted time
    if result["posted_hours_ago"] != 999:

        hours = result["posted_hours_ago"]

        if hours < 1:

            result["posted_time"] = (
                f"{int(hours * 60)}m"
            )

        elif hours < 24:

            result["posted_time"] = (
                f"{int(hours)}h"
            )

        elif hours < 168:

            result["posted_time"] = (
                f"{int(hours / 24)}d"
            )

        else:

            result["posted_time"] = (
                f"{int(hours / 168)}w"
            )

    # ========================================================
    # COMPANY
    # ========================================================

    result["company_name"] = (
        extract_company(text)
    )

    # ========================================================
    # DESCRIPTION LENGTH
    # ========================================================

    if len(
        result["job_description"]
    ) < 150:

        result["skip_reason"] = (
            "Job description is too short"
        )

        return result

    # ========================================================
    # VALID
    # ========================================================

    result["valid"] = True

    return result