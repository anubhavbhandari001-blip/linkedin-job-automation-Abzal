# ============================================================
# EXTRACT EMAIL
# ============================================================

def extract_email(text):

    if not text:
        return None

    email_pattern = (
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    )

    match = re.search(
        email_pattern,
        text
    )

    if match:

        return match.group(0)

    return None