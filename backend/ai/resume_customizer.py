import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found in .env")

client = genai.Client(api_key=api_key)


def customize_resume(resume_text, job):

    prompt = f"""
You are an expert technical resume writer.

Customize the candidate's resume for the job description below.

STRICT TRUTHFULNESS RULES:

1. Never invent experience.
2. Never invent employment.
3. Never invent projects.
4. Never invent certifications.
5. Never invent education.
6. Never invent skills that are not present in the original resume.
7. Do not change dates.
8. Do not change the candidate's name or contact information.
9. Do not claim the candidate has professional experience if the resume does not say so.
10. You may reorganize existing information.
11. You may emphasize skills that are relevant to the job.
12. You may rewrite project descriptions to better emphasize existing relevant technologies.
13. Keep the resume ATS-friendly.
14. Use clear professional language.
15. Do not use tables, graphics, emojis, or unusual formatting.

ORIGINAL RESUME:

{resume_text}


JOB DESCRIPTION:

Job Title:
{job["job_title"]}

Company:
{job["company_name"]}

Required Skills:
{", ".join(job["skills_required"])}

Experience Required:
{job["experience_required"]}

Complete Job Description:
{job["job_description"]}


Return ONLY valid JSON using this structure:

{{
    "name": "",
    "job_title": "",
    "email": "",
    "phone": "",
    "linkedin": "",
    "github": "",
    "professional_summary": "",
    "skills": [],
    "education": [],
    "projects": [],
    "certifications": []
}}
"""

    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "job_title": {"type": "string"},
            "email": {"type": "string"},
            "phone": {"type": "string"},
            "linkedin": {"type": "string"},
            "github": {"type": "string"},
            "professional_summary": {"type": "string"},
            "skills": {
                "type": "array",
                "items": {"type": "string"}
            },
            "education": {
                "type": "array",
                "items": {"type": "string"}
            },
            "projects": {
                "type": "array",
                "items": {"type": "string"}
            },
            "certifications": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": [
            "name",
            "job_title",
            "email",
            "phone",
            "linkedin",
            "github",
            "professional_summary",
            "skills",
            "education",
            "projects",
            "certifications"
        ]
    }

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
            response_schema=schema
        )
    )

    return json.loads(response.text)