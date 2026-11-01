import sqlite3
from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_DIR = (
    BASE_DIR
    / "data"
    / "database"
)

DATABASE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DATABASE_PATH = (
    DATABASE_DIR
    / "submissions.db"
)


# ============================================================
# CONNECT TO DATABASE
# ============================================================

def get_connection():

    return sqlite3.connect(
        DATABASE_PATH
    )


# ============================================================
# CREATE TABLE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            linkedin_post_url TEXT UNIQUE,

            recruiter_name TEXT,

            recruiter_email TEXT,

            company_name TEXT,

            job_title TEXT,

            location TEXT,

            employment_type TEXT,

            status TEXT,

            processed_at TEXT

        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# CHECK IF APPLICATION WAS ALREADY SENT WITHIN 48 HOURS
# ============================================================

def is_already_processed(
    linkedin_post_url
):

    if not linkedin_post_url:
        return False

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, status, processed_at
        FROM submissions
        WHERE linkedin_post_url = ?
        """,
        (
            linkedin_post_url.strip(),
        )
    )

    result = cursor.fetchone()

    connection.close()

    # --------------------------------------------------------
    # NO PREVIOUS RECORD
    # --------------------------------------------------------

    if result is None:

        print()
        print(
            "No previous record found for this "
            "LinkedIn post."
        )

        return False

    # --------------------------------------------------------
    # GET DATABASE INFORMATION
    # --------------------------------------------------------

    record_id = result[0]
    status = result[1]
    processed_at = result[2]

    print()
    print(
        f"Database record found: ID={record_id}"
    )

    print(
        f"Database status: {status}"
    )

    print(
        f"Last processed: {processed_at}"
    )

    # --------------------------------------------------------
    # ONLY SENT RECORDS ARE SUBJECT TO 48-HOUR CHECK
    # --------------------------------------------------------

    if status != "SENT":

        print()
        print(
            "This post has not been sent yet."
        )

        return False

    # --------------------------------------------------------
    # CHECK SENT TIME
    # --------------------------------------------------------

    if not processed_at:

        print()
        print(
            "Previous SENT record has no timestamp."
        )

        print(
            "Allowing this post to be processed."
        )

        return False

    try:

        sent_time = datetime.fromisoformat(
            processed_at
        )

        current_time = datetime.now()

        elapsed_time = (
            current_time - sent_time
        )

        elapsed_hours = (
            elapsed_time.total_seconds()
            / 3600
        )

    except Exception as error:

        print()
        print(
            "WARNING: Could not calculate "
            "48-hour sending window."
        )

        print(
            f"Error: {error}"
        )

        print(
            "Allowing this post to be processed."
        )

        return False

    # ========================================================
    # LESS THAN 48 HOURS
    # ========================================================

    if elapsed_hours < 48:

        remaining_hours = 48 - elapsed_hours

        print()
        print(
            "SKIPPED: This exact LinkedIn post "
            "was already sent within the last 48 hours."
        )

        print(
            f"Time since previous email: "
            f"{elapsed_hours:.1f} hours"
        )

        print(
            f"Time remaining before resend: "
            f"{remaining_hours:.1f} hours"
        )

        return True

    # ========================================================
    # 48 HOURS OR MORE
    # ========================================================

    print()
    print(
        "48-hour sending window has expired."
    )

    print(
        f"Time since previous email: "
        f"{elapsed_hours:.1f} hours"
    )

    print(
        "This post can be sent again."
    )

    return False

# ============================================================
# SAVE SUBMISSION
# ============================================================

def save_submission(
    job,
    status="DISCOVERED"
):

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Check whether the URL already exists
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM submissions
        WHERE linkedin_post_url = ?
        """,
        (
            job.get(
                "linkedin_post_url"
            ),
        )
    )

    existing_record = cursor.fetchone()

    # ========================================================
    # UPDATE EXISTING RECORD
    # ========================================================

    if existing_record:

        cursor.execute(
            """
            UPDATE submissions

            SET
                recruiter_name = ?,
                recruiter_email = ?,
                company_name = ?,
                job_title = ?,
                location = ?,
                employment_type = ?,
                status = ?,
                processed_at = ?

            WHERE linkedin_post_url = ?
            """,

            (
                job.get(
                    "recruiter_name"
                ),

                job.get(
                    "recruiter_email"
                ),

                job.get(
                    "company_name"
                ),

                job.get(
                    "job_title"
                ),

                job.get(
                    "location"
                ),

                job.get(
                    "employment_type"
                ),

                status,

                datetime.now().isoformat(),

                job.get(
                    "linkedin_post_url"
                )
            )
        )

    # ========================================================
    # INSERT NEW RECORD
    # ========================================================

    else:

        cursor.execute(
            """
            INSERT INTO submissions (

                linkedin_post_url,
                recruiter_name,
                recruiter_email,
                company_name,
                job_title,
                location,
                employment_type,
                status,
                processed_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (
                job.get(
                    "linkedin_post_url"
                ),

                job.get(
                    "recruiter_name"
                ),

                job.get(
                    "recruiter_email"
                ),

                job.get(
                    "company_name"
                ),

                job.get(
                    "job_title"
                ),

                job.get(
                    "location"
                ),

                job.get(
                    "employment_type"
                ),

                status,

                datetime.now().isoformat()
            )
        )

    connection.commit()

    connection.close()


# ============================================================
# GET ALL SUBMISSIONS
# ============================================================

def get_all_submissions():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            linkedin_post_url,
            recruiter_name,
            recruiter_email,
            company_name,
            job_title,
            location,
            employment_type,
            status,
            processed_at

        FROM submissions

        ORDER BY processed_at DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows


# ============================================================
# GET SUBMISSION BY URL
# ============================================================

def get_submission(
    linkedin_post_url
):

    if not linkedin_post_url:

        return None

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            linkedin_post_url,
            recruiter_name,
            recruiter_email,
            company_name,
            job_title,
            location,
            employment_type,
            status,
            processed_at

        FROM submissions

        WHERE linkedin_post_url = ?
        """,
        (
            linkedin_post_url,
        )
    )

    row = cursor.fetchone()

    connection.close()

    return row


# ============================================================
# DELETE SUBMISSION
# ============================================================

def delete_submission(
    linkedin_post_url
):

    if not linkedin_post_url:

        return False

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM submissions
        WHERE linkedin_post_url = ?
        """,
        (
            linkedin_post_url,
        )
    )

    deleted = cursor.rowcount > 0

    connection.commit()

    connection.close()

    return deleted


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "Initializing submission database..."
    )

    initialize_database()

    print()
    print(
        "Database ready."
    )

    print()
    print(
        "Database location:"
    )

    print(
        DATABASE_PATH
    )

    print()

    submissions = get_all_submissions()

    print(
        f"Total database records: "
        f"{len(submissions)}"
    )

    print()

    for row in submissions:

        print(
            f"ID: {row[0]} | "
            f"Job: {row[5]} | "
            f"Company: {row[4]} | "
            f"Email: {row[3]} | "
            f"Status: {row[8]}"
        )