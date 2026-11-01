# ============================================================
# LINKEDIN JOB FILTERS
# ============================================================


# ============================================================
# CHECK RECENT POST
# ============================================================

def is_recent(job):

    return (
        job.get(
            "posted_hours_ago",
            999
        ) <= 24
    )


# ============================================================
# CHECK FULL-TIME
# ============================================================

def is_full_time(job):

    return (
        job.get(
            "employment_type",
            ""
        )
        .strip()
        .lower()
        in [
            "full-time",
            "full time",
            "fulltime"
        ]
    )


# ============================================================
# CHECK UNITED STATES JOB
# ============================================================

def is_us_job(job):

    location = (
        job.get(
            "location",
            ""
        )
        .strip()
        .lower()
    )

    if not location:

        return False


    us_locations = [

        # ----------------------------------------------------
        # Country
        # ----------------------------------------------------

        "united states",
        "usa",
        "u.s.",
        "u.s.a.",


        # ----------------------------------------------------
        # States
        # ----------------------------------------------------

        "alabama",
        "alaska",
        "arizona",
        "arkansas",
        "california",
        "colorado",
        "connecticut",
        "delaware",
        "florida",
        "georgia",
        "hawaii",
        "idaho",
        "illinois",
        "indiana",
        "iowa",
        "kansas",
        "kentucky",
        "louisiana",
        "maine",
        "maryland",
        "massachusetts",
        "michigan",
        "minnesota",
        "mississippi",
        "missouri",
        "montana",
        "nebraska",
        "nevada",
        "new hampshire",
        "new jersey",
        "new mexico",
        "new york",
        "north carolina",
        "north dakota",
        "ohio",
        "oklahoma",
        "oregon",
        "pennsylvania",
        "rhode island",
        "south carolina",
        "south dakota",
        "tennessee",
        "texas",
        "utah",
        "vermont",
        "virginia",
        "washington",
        "west virginia",
        "wisconsin",
        "wyoming",


        # ----------------------------------------------------
        # Common US cities
        # ----------------------------------------------------

        "new york city",
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
        "washington dc",
        "washington, dc",
        "philadelphia",
        "portland",
        "san jose",
        "charlotte",
        "baltimore",
        "detroit",
        "minneapolis",
        "las vegas",
        "salt lake city",
        "orlando",
        "tampa",
        "nashville",
        "raleigh",
        "pittsburgh",
        "cleveland",
        "columbus",
        "cincinnati",
        "st louis",
        "kansas city",
        "indianapolis",
        "newark",
        "jersey city",
        "sacramento",
        "san antonio",
        "fort worth",
        "jacksonville"
    ]


    for us_location in us_locations:

        if us_location in location:

            return True


    return False


# ============================================================
# CHECK RECRUITER EMAIL
# ============================================================

def has_recruiter_email(job):

    email = job.get(
        "recruiter_email"
    )

    return (
        email is not None
        and "@" in email
        and "." in email.split("@")[-1]
    )


# ============================================================
# CHECK JOB DESCRIPTION
# ============================================================

def has_valid_job_description(job):

    description = job.get(
        "job_description",
        ""
    )

    if not description:

        return False

    return (
        len(
            description.strip()
        ) >= 50
    )


# ============================================================
# EMAIL CHECK
# ============================================================

def can_send_email(job):

    email = job.get(
        "recruiter_email"
    )

    return (
        email is not None
        and "@" in email
        and "." in email.split("@")[-1]
    )


# ============================================================
# MAIN FILTER
# ============================================================

def passes_filters(job):


    # --------------------------------------------------------
    # UNITED STATES
    # --------------------------------------------------------

    if not is_us_job(job):

        return False


    # --------------------------------------------------------
    # FULL-TIME
    # --------------------------------------------------------

    if not is_full_time(job):

        return False


    # --------------------------------------------------------
    # JOB DESCRIPTION
    # --------------------------------------------------------

    if not has_valid_job_description(job):

        return False


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # DO NOT REQUIRE RECRUITER EMAIL HERE.
    #
    # Email discovery happens before the final
    # application stage.
    #
    # --------------------------------------------------------

    return True