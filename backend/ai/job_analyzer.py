import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# LOAD GEMINI
# ============================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )

client = genai.Client(
    api_key=api_key
)


# ============================================================
# ANALYZE JOB
# ============================================================

def analyze_job(resume_text, job):

    job_title = job.get(
        "job_title",
        "Not specified"
    )

    company = job.get(
        "company_name",
        "Not specified"
    )

    location = job.get(
        "location",
        job.get(
            "job_location",
            "Not specified"
        )
    )

    employment_type = job.get(
        "employment_type",
        "Not specified"
    )

    experience_required = job.get(
        "experience_required",
        "Not specified"
    )

    skills_required = job.get(
        "skills_required",
        []
    )

    job_description = job.get(
        "job_description",
        ""
    )

    # ========================================================
    # GEMINI PROMPT
    # ========================================================

    prompt = f"""
You are a job screening assistant for an automated job application system.

Your job is to determine whether this job is RELEVANT enough for the
candidate to apply.

IMPORTANT:

The goal is NOT to find a perfect resume-to-job match.

The goal is to identify potentially suitable job opportunities.

Therefore:

- Do NOT reject a job just because the candidate is missing some skills.
- Do NOT require the candidate to match every technology.
- Do NOT require an exact keyword match between the resume and job.
- Do NOT reject a job because the job description contains additional
  technologies that are not listed on the resume.
- Missing skills are NORMAL.
- A candidate can still APPLY when they meet only part of the requirements.
- Prefer APPLY over SKIP when the job is reasonably relevant.

============================================================
WHEN TO RECOMMEND APPLY
============================================================

Recommend APPLY when the job is generally related to the candidate's
background, skills, education, projects, or target role.

Examples:

- Backend Developer
- Frontend Developer
- Full Stack Developer
- Software Developer
- Software Engineer
- Python Developer
- Java Developer
- Web Developer
- Junior Software Engineer
- Entry-Level Software Engineer
- Graduate Software Engineer
- Associate Software Engineer
- Application Developer
- API Developer
- similar software/IT development roles

A job does NOT need to match the resume perfectly.

For example:

If the job requires:

Python, Django, React, AWS, Docker, PostgreSQL

and the resume contains:

Python, React, JavaScript

the recommendation can still be APPLY.

The missing technologies should be listed under missing_skills.

============================================================
WHEN TO RECOMMEND SKIP
============================================================

Recommend SKIP ONLY when the job is clearly unsuitable or unrelated.

Examples:

- Sales
- Marketing
- HR
- Recruiter
- Accounting
- Finance
- Legal
- Healthcare
- Mechanical Engineering
- Civil Engineering
- Electrical Engineering
- Customer Service
- Administrative roles
- Data-entry-only roles
- Truck/vehicle driving
- jobs requiring a completely different profession

Also recommend SKIP if the position is clearly senior/executive and
the candidate obviously cannot meet the fundamental experience requirement.

Do NOT SKIP simply because:

- some skills are missing
- the candidate lacks one framework
- the candidate lacks one programming language
- the candidate lacks cloud experience
- the candidate lacks a database mentioned in the job
- the candidate lacks a tool mentioned in the job
- the job description is long
- the job description contains many technologies
- the candidate has fewer skills than the job description
- the job title is slightly different from the candidate's target role

============================================================
EXPERIENCE RULE
============================================================

Experience mismatch alone should NOT automatically cause SKIP.

If a job asks for:

"2-3 years experience"

but the candidate is a student or junior candidate, still evaluate
the overall relevance.

Only use experience as a strong reason for SKIP when the position is
clearly senior, managerial, lead, architect, principal, director, etc.

Examples of clearly senior roles:

- Senior Software Engineer
- Lead Developer
- Engineering Manager
- Software Architect
- Principal Engineer
- Director of Engineering

============================================================
SKILL MATCHING
============================================================

Only list a skill under matching_skills if it is actually supported by
the candidate resume.

NEVER invent skills.

However, missing skills should NOT automatically cause SKIP.

The purpose of missing_skills is to show what the candidate may need to
learn, NOT to reject the job.

============================================================
MATCH SCORE
============================================================

Calculate a reasonable match score from 0 to 100.

The score should represent overall relevance.

Suggested interpretation:

80-100:
Very strong match.

60-79:
Good potential match.

40-59:
Moderate match but still potentially worth applying.

20-39:
Weak match.

0-19:
Clearly unrelated.

IMPORTANT:

A score below 60 does NOT automatically mean SKIP.

Only recommend SKIP when the job is clearly unrelated or fundamentally
incompatible.

============================================================
FINAL DECISION RULE
============================================================

When uncertain between APPLY and SKIP:

CHOOSE APPLY if the job is plausibly related to the candidate's
software/IT development background.

The system should favor finding opportunities rather than eliminating
potential opportunities.

============================================================
CANDIDATE RESUME
============================================================

{resume_text}


============================================================
JOB INFORMATION
============================================================

Job Title:
{job_title}

Company:
{company}

Location:
{location}

Employment Type:
{employment_type}

Experience Required:
{experience_required}

Required Skills:
{", ".join(skills_required)}

Complete Job Description:
{job_description}


============================================================
RETURN ONLY JSON
============================================================

Do not return explanations outside the JSON object.
"""


    # ========================================================
    # JSON SCHEMA
    # ========================================================

    schema = {

        "type": "object",

        "properties": {

            "job_title": {
                "type": "string"
            },

            "company": {
                "type": "string"
            },

            "required_skills": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },

            "matching_skills": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },

            "missing_skills": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },

            "experience_required": {
                "type": "string"
            },

            "candidate_meets_experience": {
                "type": "boolean"
            },

            "location": {
                "type": "string"
            },

            "employment_type": {
                "type": "string"
            },

            "match_score": {
                "type": "integer"
            },

            "recommendation": {
                "type": "string",
                "enum": [
                    "APPLY",
                    "SKIP"
                ]
            }
        },

        "required": [

            "job_title",
            "company",
            "required_skills",
            "matching_skills",
            "missing_skills",
            "experience_required",
            "candidate_meets_experience",
            "location",
            "employment_type",
            "match_score",
            "recommendation"
        ]
    }


        # ========================================================
    # GEMINI REQUEST
    # ========================================================

    try:

        response = client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema=schema
            )
        )

    except Exception as error:

        error_text = str(error)

        # ----------------------------------------------------
        # GEMINI QUOTA ERROR
        # ----------------------------------------------------

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):

            print()
            print("=" * 60)
            print("GEMINI API QUOTA EXCEEDED")
            print("=" * 60)
            print()
            print(
                "Gemini cannot analyze this job because "
                "the API quota has been exhausted."
            )
            print()
            print(
                "This is an API quota problem, not a "
                "LinkedIn or scraper error."
            )
            print()
            print("AI DECISION: APPLY")
            print("Reason: Gemini API quota exceeded.")
            print("Continuing to the application stage.")
            print()

            return {
                "recommendation": "APPLY",
                "match_score": 1,
                "job_title": job_title,
                "company": company,
                "required_skills": skills_required,
                "matching_skills": [],
                "missing_skills": [],
                "experience_required": experience_required,
                "candidate_meets_experience": False,
                "location": location,
                "employment_type": employment_type
            }

        # ----------------------------------------------------
        # OTHER GEMINI ERROR
        # ----------------------------------------------------

        print()
        print("AI ANALYSIS FAILED")
        print(f"Error: {error}")

        raise


    # ========================================================
    # PARSE RESPONSE
    # ========================================================

    try:

        result = json.loads(
            response.text
        )

        return result

    except json.JSONDecodeError as error:

        print()
        print(
            "Gemini returned invalid JSON."
        )

        print(
            response.text
        )

        raise error