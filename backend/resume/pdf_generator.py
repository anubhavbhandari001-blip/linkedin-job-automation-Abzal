from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.units import mm


BASE_DIR = Path(__file__).resolve().parent.parent.parent

OUTPUT_DIR = BASE_DIR / "data" / "customized_resumes"

def generate_resume_pdf(resume_data, job_title):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    safe_title = (
        job_title
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
    )

    output_path = OUTPUT_DIR / f"customized_{safe_title}.pdf"

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=13 * mm,
        bottomMargin=13 * mm
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "Name",
        parent=styles["Title"],
        fontSize=20,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        "Contact",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=11,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=10.5,
        leading=13,
        spaceBefore=7,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=8.7,
        leading=11.5,
        spaceAfter=2
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-5
    )

    story = []

    # Name
    story.append(
        Paragraph(
            resume_data["name"],
            name_style
        )
    )

    # Contact information
    contact = (
        f'{resume_data["job_title"]} | '
        f'{resume_data["email"]} | '
        f'{resume_data["phone"]}<br/>'
        f'{resume_data["linkedin"]} | '
        f'{resume_data["github"]}'
    )

    story.append(
        Paragraph(
            contact,
            contact_style
        )
    )

    # Summary
    story.append(
        Paragraph(
            "PROFESSIONAL SUMMARY",
            heading_style
        )
    )

    story.append(
        Paragraph(
            resume_data["professional_summary"],
            body_style
        )
    )

    # Skills
    story.append(
        Paragraph(
            "TECHNICAL SKILLS",
            heading_style
        )
    )

    for skill in resume_data["skills"]:
        story.append(
            Paragraph(
                f"• {skill}",
                bullet_style
            )
        )

    # Education
    story.append(
        Paragraph(
            "EDUCATION",
            heading_style
        )
    )

    for education in resume_data["education"]:
        story.append(
            Paragraph(
                f"• {education}",
                bullet_style
            )
        )

    # Projects
    story.append(
        Paragraph(
            "PROJECTS",
            heading_style
        )
    )

    for project in resume_data["projects"]:
        story.append(
            Paragraph(
                f"• {project}",
                bullet_style
            )
        )

    # Certifications
    if resume_data["certifications"]:

        story.append(
            Paragraph(
                "CERTIFICATIONS",
                heading_style
            )
        )

        for certification in resume_data["certifications"]:
            story.append(
                Paragraph(
                    f"• {certification}",
                    bullet_style
                )
            )

    document.build(story)

    return output_path