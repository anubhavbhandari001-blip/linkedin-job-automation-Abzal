from playwright.sync_api import sync_playwright
from pathlib import Path


SESSION_PATH = Path("../credentials/linkedin_session")


def start_linkedin_session():

    SESSION_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_PATH),
            headless=False
        )

        # Use the page that Chromium already opened
        page = context.pages[0]

        page.goto(
            "https://in.linkedin.com/",
            wait_until="domcontentloaded"
        )

        print("\nLinkedIn has been opened.")
        print("Log in manually if LinkedIn asks you to.")
        print("Complete any verification required by LinkedIn.")

        input("\nAfter you are logged in, press ENTER here...")

        context.close()


if __name__ == "__main__":
    start_linkedin_session()