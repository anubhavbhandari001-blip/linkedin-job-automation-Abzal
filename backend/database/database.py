import sqlite3
from pathlib import Path


DATABASE_PATH = Path("../../data/submissions.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linkedin_post_url TEXT UNIQUE NOT NULL,
        recruiter_name TEXT,
        recruiter_email TEXT,
        company_name TEXT,
        job_title TEXT,
        status TEXT,
        match_score INTEGER,
        resume_path TEXT,
        gmail_draft_id TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    connection.commit()
    connection.close()


def is_already_processed(linkedin_post_url):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM submissions
        WHERE linkedin_post_url = ?
        """,
        (linkedin_post_url,)
    )

    result = cursor.fetchone()

    connection.close()

    return result is not None


def update_submission(
    linkedin_post_url,
    status=None,
    match_score=None,
    resume_path=None,
    gmail_draft_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE submissions
        SET
            status = COALESCE(?, status),
            match_score = COALESCE(?, match_score),
            resume_path = COALESCE(?, resume_path),
            gmail_draft_id = COALESCE(?, gmail_draft_id)
        WHERE linkedin_post_url = ?
        """,
        (
            status,
            match_score,
            str(resume_path) if resume_path else None,
            gmail_draft_id,
            linkedin_post_url
        )
    )

    connection.commit()
    connection.close()


def save_submission(
    job,
    status="DISCOVERED",
    match_score=None,
    resume_path=None,
    gmail_draft_id=None
):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO submissions (
                linkedin_post_url,
                recruiter_name,
                recruiter_email,
                company_name,
                job_title,
                status,
                match_score,
                resume_path,
                gmail_draft_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job["linkedin_post_url"],
                job["recruiter_name"],
                job["recruiter_email"],
                job["company_name"],
                job["job_title"],
                status,
                match_score,
                str(resume_path) if resume_path else None,
                gmail_draft_id
            )
        )

        connection.commit()

    except sqlite3.IntegrityError:

        print("Job already exists in database.")

    finally:

        connection.close()


if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully.")