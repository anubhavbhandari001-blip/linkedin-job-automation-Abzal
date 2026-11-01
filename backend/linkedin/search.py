
from pathlib import Path
import time
import re
from urllib.parse import quote

import pyperclip

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from resume.parser import (
    extract_resume_text,
    extract_candidate_info
)

from linkedin.post_parser import parse_job_post


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

RESUME_PATH = (
    BASE_DIR
    / "data"
    / "resume"
    / "resume.pdf"
)


# ============================================================
# CHROME PROFILE
#
# IMPORTANT:
# We use a persistent Chrome profile so LinkedIn login
# is remembered between program runs.
# ============================================================

CHROME_PROFILE_DIR = (
    BASE_DIR
    / "data"
    / "chrome_profile"
)


# ============================================================
# SEARCH QUERY
# ============================================================

# ============================================================
# SEARCH QUERY
# ============================================================

def generate_search_query(job_title):

    job_title = str(
        job_title
    ).strip()

    if not job_title:

        raise ValueError(
            "Job title cannot be empty."
        )

    query = (
        f'"{job_title}" '
        '"United States" '
        '-C2C '
        '-Hotlist '

    )

    return query


# ============================================================
# START CHROME
# ============================================================

def start_browser():

    options = Options()

    options.add_argument("--start-maximized")

    # Persistent Chrome profile.
    #
    # LinkedIn cookies/session are stored here.
    # After the first successful login, future runs should
    # normally stay logged in.

    CHROME_PROFILE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    options.add_argument(
        f"--user-data-dir={CHROME_PROFILE_DIR}"
    )

    # Clipboard permission.

    options.add_experimental_option(
        "prefs",
        {
            "profile.default_content_setting_values.clipboard": 1
        }
    )

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_window_size(
        1400,
        1000
    )

    return driver


# ============================================================
# CHECK WHETHER LINKEDIN LOGIN IS REQUIRED
# ============================================================

def is_linkedin_logged_in(driver):

    current_url = driver.current_url.lower()

    # Login pages.

    if "/login" in current_url:
        return False

    if "/signup" in current_url:
        return False

    # Check for common LinkedIn logged-in elements.

    selectors = [
        "img.global-nav__me-photo",
        "button.global-nav__primary-link",
        "nav.global-nav",
        "input[placeholder*='Search']",
        "input[placeholder*='search']",
        ".global-nav__me"
    ]

    for selector in selectors:

        try:

            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in elements:

                try:

                    if element.is_displayed():
                        return True

                except Exception:
                    continue

        except Exception:
            continue

    # If we are already on a LinkedIn page other than login,
    # give LinkedIn a little more time to render.

    if "linkedin.com" in current_url:

        try:

            body_text = driver.find_element(
                By.TAG_NAME,
                "body"
            ).text.lower()

            if (
                "home" in body_text
                and "sign in" not in body_text
            ):
                return True

        except Exception:
            pass

    return False


# ============================================================
# LOGIN TO LINKEDIN
#
# First run:
#   User logs in manually.
#
# Later runs:
#   Persistent Chrome profile reuses the session.
# ============================================================

def login_to_linkedin(driver):

    print()
    print("=" * 60)
    print("LINKEDIN LOGIN")
    print("=" * 60)
    print()

    print("Opening LinkedIn...")

    driver.get(
        "https://www.linkedin.com/"
    )

    try:
        WebDriverWait(
            driver,
            15
        ).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )
    except Exception:
        pass

    time.sleep(3)

    # --------------------------------------------------------
    # Already logged in?
    # --------------------------------------------------------

    if is_linkedin_logged_in(driver):

        print()
        print("Existing LinkedIn session detected.")
        print("Automatic login successful.")
        print()

        return True

    # --------------------------------------------------------
    # First-time login.
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("FIRST-TIME LINKEDIN LOGIN")
    print("=" * 60)
    print()

    print(
        "No saved LinkedIn session was detected."
    )

    print()

    print(
        "Please log in to LinkedIn ONCE in the browser."
    )

    print(
        "Complete any security verification if LinkedIn"
    )

    print(
        "requests it."
    )

    print()

    input(
        "Press ENTER after LinkedIn login is complete..."
    )

    print()

    # Verify login after manual login.

    if is_linkedin_logged_in(driver):

        print(
            "LinkedIn login successful."
        )

        print(
            "Your session has been saved in:"
        )

        print(
            CHROME_PROFILE_DIR
        )

        print()

        return True

    print()
    print(
        "WARNING: LinkedIn login could not be verified."
    )
    print()

    return False


# ============================================================
# SEARCH LINKEDIN POSTS
#
# IMPORTANT:
#
# The 24-hour filter is applied BY LINKEDIN.
#
# We do NOT use Python to reject old posts.
# ============================================================

def search_linkedin_posts(
    driver,
    query
):

    print()
    print("=" * 60)
    print("SEARCHING LINKEDIN POSTS")
    print("=" * 60)
    print()

    print("Query:")
    print(query)
    print()

    encoded_query = quote(
        query
    )

    # ========================================================
    # LINKEDIN NATIVE FILTER
    #
    # datePosted=["past-24h"]
    #
    # This is the important part.
    # ========================================================

    search_url = (
        "https://www.linkedin.com/search/results/content/"
        "?keywords="
        + encoded_query
        + "&origin=FACETED_SEARCH"
        + '&datePosted=%5B%22past-24h%22%5D'
    )

    print(
        "Opening LinkedIn Posts search..."
    )

    print()

    print(
        "LINKEDIN NATIVE FILTER:"
    )

    print(
        "Past 24 hours"
    )

    print()

    print(
        "Search URL:"
    )

    print(
        search_url
    )

    print()

    driver.get(
        search_url
    )

    try:

        WebDriverWait(
            driver,
            20
        ).until(
            lambda d: (
                "search/results/content"
                in d.current_url
            )
        )

    except Exception:

        print(
            "WARNING: Search URL verification timed out."
        )

    # Give LinkedIn time to load the filtered results.

    time.sleep(8)

    print()
    print(
        "Current URL:"
    )
    print(
        driver.current_url
    )

    print()

    print(
        "LinkedIn Posts page opened."
    )

    print(
        "LinkedIn is responsible for the Past 24 hours filter."
    )

    print()

    return driver.current_url


# ============================================================
# NORMALIZE POSTED TIME
#
# This is now ONLY informational.
# It does NOT determine whether a post is accepted.
# ============================================================

def normalize_posted_time(value):

    if not value:
        return None

    value = value.lower().strip()

    value = value.replace(
        "\u00a0",
        " "
    )

    value = value.replace(
        "ago",
        ""
    ).strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# ============================================================
# IS WITHIN 24 HOURS
#
# INFORMATIONAL ONLY.
#
# LinkedIn itself performs the actual filtering.
# ============================================================

def is_within_24_hours(posted_time):

    if not posted_time:
        return False

    value = normalize_posted_time(
        posted_time
    )

    if not value:
        return False

    compact_match = re.fullmatch(
        r"(\d+)\s*([mhdw])",
        value
    )

    if compact_match:

        number = int(
            compact_match.group(1)
        )

        unit = compact_match.group(2)

        if unit == "m":
            return number <= 24 * 60

        if unit == "h":
            return number <= 24

        return False

    text_match = re.fullmatch(
        r"(\d+)\s+"
        r"(minute|minutes|hour|hours|day|days|week|weeks)",
        value
    )

    if text_match:

        number = int(
            text_match.group(1)
        )

        unit = text_match.group(2)

        if unit in [
            "minute",
            "minutes"
        ]:
            return number <= 24 * 60

        if unit in [
            "hour",
            "hours"
        ]:
            return number <= 24

        return False

    return False


# ============================================================
# EXTRACT POSTED TIME
# ============================================================

def extract_posted_time(
    element,
    text
):

    # --------------------------------------------------------
    # METHOD 1: <time>
    # --------------------------------------------------------

    try:

        time_elements = element.find_elements(
            By.TAG_NAME,
            "time"
        )

        for time_element in time_elements:

            try:

                visible_text = (
                    time_element.text.strip()
                )

                if visible_text:
                    return visible_text

            except Exception:
                pass

            try:

                datetime_value = (
                    time_element.get_attribute(
                        "datetime"
                    )
                )

                if datetime_value:
                    return datetime_value

            except Exception:
                pass

    except Exception:
        pass

    # --------------------------------------------------------
    # METHOD 2: LINE BY LINE
    # --------------------------------------------------------

    lines = text.splitlines()

    for line in lines:

        value = line.strip().lower()

        if not value:
            continue

        if re.fullmatch(
            r"\d+\s*[mhdw]",
            value
        ):
            return line.strip()

        if re.fullmatch(
            r"\d+\s+"
            r"(minute|minutes|hour|hours|day|days|week|weeks)"
            r"(\s+ago)?",
            value
        ):
            return line.strip()

    # --------------------------------------------------------
    # METHOD 3: ENTIRE TEXT
    # --------------------------------------------------------

    compact_match = re.search(
        r"\b\d+\s*[mhdw]\b",
        text.lower()
    )

    if compact_match:
        return compact_match.group(0)

    text_match = re.search(
        r"\b\d+\s+"
        r"(minute|minutes|hour|hours|day|days|week|weeks)"
        r"(\s+ago)?\b",
        text.lower()
    )

    if text_match:
        return text_match.group(0)

    return None


# ============================================================
# EXPAND POST
# ============================================================

def expand_post_with_driver(
    driver,
    element
):

    xpaths = [
        ".//*[normalize-space(text())='… more']",
        ".//*[normalize-space(text())='... more']",
        ".//*[normalize-space(text())='more']",
    ]

    original_text = ""

    try:
        original_text = element.text.strip()
    except Exception:
        pass

    for xpath in xpaths:

        try:

            buttons = element.find_elements(
                By.XPATH,
                xpath
            )

            for button in buttons:

                try:

                    if not button.is_displayed():
                        continue

                    print(
                        "Found post expansion button."
                    )

                    driver.execute_script(
                        """
                        arguments[0].scrollIntoView({
                            block: 'center'
                        });
                        """,
                        button
                    )

                    time.sleep(0.5)

                    try:
                        button.click()

                    except Exception:

                        driver.execute_script(
                            "arguments[0].click();",
                            button
                        )

                    print(
                        "Clicked post expansion button."
                    )

                    # ------------------------------------------------
                    # Wait for LinkedIn to actually update the post.
                    # ------------------------------------------------

                    try:

                        WebDriverWait(
                            driver,
                            5
                        ).until(
                            lambda d:
                            element.text.strip()
                            != original_text
                        )

                        print(
                            "Expanded content detected."
                        )

                    except Exception:

                        # Even if the text did not visibly change,
                        # give LinkedIn extra time to render it.
                        print(
                            "Waiting additional time "
                            "for LinkedIn content..."
                        )

                        time.sleep(2)

                    return True

                except Exception as error:

                    print(
                        "Expansion attempt failed:",
                        error
                    )

                    continue

        except Exception:

            continue

    return False


# ============================================================
# EXTRACT EMAIL
# ============================================================

def extract_email_from_text(text):

    if not text:
        return None

    # Normalize common invisible/Unicode characters
    cleaned_text = (
        text
        .replace("\u00a0", " ")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
    )

    # Standard email pattern
    email_pattern = (
        r"\b[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@"
        r"[A-Za-z0-9-]+"
        r"(?:\.[A-Za-z0-9-]+)+\b"
    )

    matches = re.findall(
        email_pattern,
        cleaned_text
    )

    if not matches:
        return None

    for email in matches:
        email = email.strip(
            ".,;:()[]{}<>\"'"
        )

        # Basic validation
        if (
            "@" in email
            and "." in email.split("@")[-1]
        ):
            return email

    return None


# ============================================================
# VALIDATE LINKEDIN POST URL
# ============================================================

def is_valid_linkedin_post_url(url):

    if not url:
        return False

    url = url.strip()

    patterns = [

        r"^https?://(?:www\.)?linkedin\.com/"
        r"(?:feed/update/|posts/)",

        r"^https?://lnkd\.in/"

    ]

    for pattern in patterns:

        if re.match(
            pattern,
            url,
            re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# CLEAR CLIPBOARD
# ============================================================

def clear_clipboard():

    try:

        pyperclip.copy("")

        time.sleep(0.3)

        return True

    except Exception as error:

        print(
            "Could not clear clipboard:",
            error
        )

        return False


# ============================================================
# READ BROWSER CLIPBOARD
# ============================================================

def read_browser_clipboard(driver):

    try:

        value = driver.execute_async_script(
            """
            const done = arguments[arguments.length - 1];

            if (
                navigator.clipboard &&
                navigator.clipboard.readText
            ) {

                navigator.clipboard.readText()
                    .then(
                        text => done(text || "")
                    )
                    .catch(
                        () => done("")
                    );

            } else {

                done("");

            }
            """
        )

        return (
            value or ""
        ).strip()

    except Exception as error:

        print(
            "Browser clipboard read failed:",
            error
        )

        return ""


# ============================================================
# FIND THREE-DOT BUTTON
#
# IMPORTANT:
#
# We DO NOT require the Follow button.
#
# LinkedIn's top-right control normally has:
#
# aria-label =
# Open control menu for post by <person>
#
# That is our preferred selector.
# ============================================================

def find_three_dot_buttons(
    driver,
    element
):

    candidates = []

    seen = set()

    # --------------------------------------------------------
    # METHOD 1:
    # Exact LinkedIn aria-label.
    # --------------------------------------------------------

    xpaths = [

        ".//button[contains("
        "translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'open control menu for post by'"
        ")]",

        ".//*[@role='button' and contains("
        "translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'open control menu for post by'"
        ")]",

        ".//button[contains("
        "translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'more actions'"
        ")]",

        ".//*[@role='button' and contains("
        "translate(@aria-label,"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'more actions'"
        ")]"

    ]

    for xpath in xpaths:

        try:

            buttons = element.find_elements(
                By.XPATH,
                xpath
            )

            for button in buttons:

                try:

                    if not button.is_displayed():
                        continue

                    if button.id in seen:
                        continue

                    seen.add(
                        button.id
                    )

                    candidates.append(
                        button
                    )

                except Exception:
                    continue

        except Exception:
            continue

    if candidates:

        print(
            f"Found {len(candidates)} top-right menu button(s) "
            f"using LinkedIn aria-label."
        )

        return candidates

    # --------------------------------------------------------
    # METHOD 2:
    # Search ALL buttons.
    #
    # We specifically look at aria-label/title.
    # --------------------------------------------------------

    try:

        buttons = element.find_elements(
            By.XPATH,
            ".//button | .//*[@role='button']"
        )

        print(
            f"Inspecting {len(buttons)} button(s) "
            f"inside post..."
        )

        for button in buttons:

            try:

                if not button.is_displayed():
                    continue

                label = (
                    button.get_attribute(
                        "aria-label"
                    )
                    or ""
                ).strip()

                title = (
                    button.get_attribute(
                        "title"
                    )
                    or ""
                ).strip()

                combined = (
                    label + " " + title
                ).lower()

                if (
                    "open control menu" in combined
                    or "more actions" in combined
                ):

                    if button.id not in seen:

                        seen.add(
                            button.id
                        )

                        candidates.append(
                            button
                        )

            except Exception:
                continue

    except Exception as error:

        print(
            "Button inspection failed:",
            error
        )

    if candidates:

        print(
            f"Found {len(candidates)} top-right "
            f"menu button(s)."
        )

        return candidates

    # --------------------------------------------------------
    # METHOD 3:
    # Position-based fallback.
    #
    # This prevents accidentally clicking Like.
    #
    # We find the upper portion of the post and choose
    # buttons toward the RIGHT side.
    # --------------------------------------------------------

    try:

        buttons = element.find_elements(
            By.XPATH,
            ".//button"
        )

        element_rect = element.rect

        post_x = element_rect.get(
            "x",
            0
        )

        post_y = element_rect.get(
            "y",
            0
        )

        post_width = element_rect.get(
            "width",
            0
        )

        post_height = element_rect.get(
            "height",
            0
        )

        print(
            "Using top-right positional fallback..."
        )

        positional = []

        for button in buttons:

            try:

                if not button.is_displayed():
                    continue

                rect = button.rect

                x = rect.get(
                    "x",
                    0
                )

                y = rect.get(
                    "y",
                    0
                )

                width = rect.get(
                    "width",
                    0
                )

                height = rect.get(
                    "height",
                    0
                )

                # Ignore buttons below the upper 35% of post.

                relative_y = (
                    y - post_y
                )

                if post_height > 0:

                    if relative_y > (
                        post_height * 0.35
                    ):
                        continue

                # Ignore tiny/invisible elements.

                if width < 20 or height < 20:
                    continue

                # Right side of post.

                relative_x = (
                    x - post_x
                )

                if post_width > 0:

                    if relative_x < (
                        post_width * 0.65
                    ):
                        continue

                positional.append(
                    (
                        x,
                        y,
                        button
                    )
                )

            except Exception:
                continue

        positional.sort(
            key=lambda item: (
                item[1],
                -item[0]
            )
        )

        for x, y, button in positional:

            if button.id not in seen:

                seen.add(
                    button.id
                )

                candidates.append(
                    button
                )

    except Exception as error:

        print(
            "Position fallback failed:",
            error
        )

    return candidates


# ============================================================
# FIND COPY LINK TO POST
# ============================================================

def find_copy_link_button(driver):

    copy_xpaths = [

        "//*[normalize-space(.)='Copy link to post']",

        "//*[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'copy link to post'"
        ")]",

        "//*[@aria-label='Copy link to post']",

        "//*[@data-control-name='copy_link']"

    ]

    for xpath in copy_xpaths:

        try:

            candidates = driver.find_elements(
                By.XPATH,
                xpath
            )

            for candidate in candidates:

                try:

                    if (
                        candidate.is_displayed()
                        and candidate.is_enabled()
                    ):

                        return candidate

                except Exception:
                    continue

        except Exception:
            continue

    return None


# ============================================================
# GET POST URL
#
# MAIN URL EXTRACTION FUNCTION
#
# Flow:
#
# 1. Find top-right menu
# 2. Click
# 3. Wait for Copy link to post
# 4. Click Copy
# 5. Wait
# 6. Read clipboard
# 7. Retry if necessary
# ============================================================

def get_post_url_from_share(
    driver,
    element
):

    print(
        "Attempting: three dots -> Copy link to post..."
    )

    # --------------------------------------------------------
    # Give the post time to finish rendering.
    # --------------------------------------------------------

    time.sleep(1.5)

    # --------------------------------------------------------
    # Find top-right menu buttons.
    # --------------------------------------------------------

    menu_buttons = find_three_dot_buttons(
        driver,
        element
    )

    if not menu_buttons:

        print(
            "Three-dot More Actions button was not found."
        )

        return None

    print(
        f"Final three-dot candidates: "
        f"{len(menu_buttons)}"
    )

    # --------------------------------------------------------
    # Try candidates one at a time.
    # --------------------------------------------------------

    for attempt, menu_button in enumerate(
        menu_buttons,
        start=1
    ):

        print()
        print(
            f"Trying top-right button "
            f"{attempt}/{len(menu_buttons)}..."
        )

        try:

            # ------------------------------------------------
            # Scroll button into center.
            # ------------------------------------------------

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center',
                    inline: 'center'
                });
                """,
                menu_button
            )

            time.sleep(1)

            # ------------------------------------------------
            # Clear clipboard BEFORE clicking.
            # ------------------------------------------------

            clear_clipboard()

            # ------------------------------------------------
            # Click three-dot button.
            # ------------------------------------------------

            try:

                menu_button.click()

            except Exception:

                driver.execute_script(
                    "arguments[0].click();",
                    menu_button
                )

            print(
                "Three-dot button clicked."
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # LinkedIn sometimes takes several seconds to
            # render the menu.
            # ------------------------------------------------

            print(
                "Waiting for 'Copy link to post'..."
            )

            copy_button = None

            try:

                copy_button = WebDriverWait(
                    driver,
                    10
                ).until(
                    lambda d: find_copy_link_button(d)
                )

            except Exception:

                print(
                    "'Copy link to post' did not appear "
                    "within 10 seconds."
                )

            # ------------------------------------------------
            # If not found, wait another 3 seconds.
            # ------------------------------------------------

            if not copy_button:

                time.sleep(3)

                copy_button = (
                    find_copy_link_button(
                        driver
                    )
                )

            if not copy_button:

                print(
                    "Copy link button still not found."
                )

                try:

                    ActionChains(
                        driver
                    ).send_keys(
                        "\ue00c"
                    ).perform()

                except Exception:
                    pass

                time.sleep(1)

                continue

            print(
                "'Copy link to post' found."
            )

            # ------------------------------------------------
            # Scroll Copy button into view.
            # ------------------------------------------------

            try:

                driver.execute_script(
                    """
                    arguments[0].scrollIntoView({
                        block: 'center'
                    });
                    """,
                    copy_button
                )

                time.sleep(0.5)

            except Exception:
                pass

            # ------------------------------------------------
            # Click Copy.
            # ------------------------------------------------

            try:

                copy_button.click()

            except Exception:

                driver.execute_script(
                    "arguments[0].click();",
                    copy_button
                )

            print(
                "'Copy link to post' clicked."
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Give Windows + Chrome + LinkedIn time to
            # update the clipboard.
            # ------------------------------------------------

            print(
                "Waiting for LinkedIn to copy the URL..."
            )

            time.sleep(2)

            # ------------------------------------------------
            # Try clipboard multiple times.
            # ------------------------------------------------

            for clipboard_attempt in range(
                1,
                6
            ):

                print(
                    f"Checking clipboard "
                    f"({clipboard_attempt}/5)..."
                )

                # Browser clipboard.

                copied_url = (
                    read_browser_clipboard(
                        driver
                    )
                )

                if is_valid_linkedin_post_url(
                    copied_url
                ):

                    print()
                    print(
                        "COPY LINK SUCCESSFUL:"
                    )
                    print(
                        copied_url
                    )

                    return copied_url

                # Windows clipboard.

                try:

                    copied_url = (
                        pyperclip.paste()
                        or ""
                    ).strip()

                except Exception:

                    copied_url = ""

                if is_valid_linkedin_post_url(
                    copied_url
                ):

                    print()
                    print(
                        "COPY LINK SUCCESSFUL:"
                    )
                    print(
                        copied_url
                    )

                    return copied_url

                # Give clipboard more time.

                time.sleep(1)

            print(
                "Clipboard did not contain a valid "
                "LinkedIn post URL."
            )

            # ------------------------------------------------
            # Close menu before retrying.
            # ------------------------------------------------

            try:

                ActionChains(
                    driver
                ).send_keys(
                    "\ue00c"
                ).perform()

            except Exception:
                pass

            time.sleep(1)

        except Exception as error:

            print(
                "Three-dot processing failed:",
                error
            )

            try:

                ActionChains(
                    driver
                ).send_keys(
                    "\ue00c"
                ).perform()

            except Exception:
                pass

            time.sleep(1)

    print(
        "Could not obtain Copy link to post URL "
        "from three-dot menu."
    )

    return None


# ============================================================
# FALLBACK: URL FROM POST HTML
# ============================================================

def get_url_from_post_html(
    element
):

    try:

        html = element.get_attribute(
            "outerHTML"
        )

        if not html:
            return None

        patterns = [

            r'https?://(?:www\.)?linkedin\.com/'
            r'(?:posts/|feed/update/)[^"\'<>\s]+',

            r'https?://lnkd\.in/[^"\'<>\s]+'

        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                html,
                re.IGNORECASE
            )

            if match:

                url = match.group(
                    0
                )

                if is_valid_linkedin_post_url(
                    url
                ):

                    return url

    except Exception:
        pass

    return None


# ============================================================
# FALLBACK: ACTIVITY URN
# ============================================================

def get_url_from_activity_urn(
    element
):

    try:

        html = element.get_attribute(
            "outerHTML"
        )

        if not html:
            return None

        match = re.search(
            r'urn:li:activity:\d+',
            html
        )

        if match:

            activity_id = (
                match.group(0)
            )

            return (
                "https://www.linkedin.com/"
                "feed/update/"
                + activity_id
                + "/"
            )

    except Exception:
        pass

    return None


# ============================================================
# FIND POST CONTAINERS
# ============================================================

def find_post_containers(
    driver
):

    elements = []

    seen_ids = set()

    selectors = [

        "div.feed-shared-update-v2",

        "div[data-urn*='urn:li:activity']",

        "div[data-urn*='urn:li:ugcPost']",

        "article"

    ]

    print()
    print("=" * 60)
    print("SEARCHING FOR LINKEDIN POST CONTAINERS")
    print("=" * 60)

    for selector in selectors:

        try:

            found = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            print()
            print(
                f"Selector: {selector}"
            )

            print(
                f"Found: {len(found)}"
            )

            for element in found:

                try:

                    text = element.text.strip()

                    if len(text) < 150:
                        continue

                    element_id = element.id

                    if element_id in seen_ids:
                        continue

                    seen_ids.add(
                        element_id
                    )

                    elements.append(
                        element
                    )

                except Exception:
                    continue

        except Exception as error:

            print(
                f"Selector failed: {error}"
            )

    # --------------------------------------------------------
    # Feed marker fallback.
    # --------------------------------------------------------

    if not elements:

        print()
        print(
            "Trying Feed post marker extraction..."
        )

        try:

            markers = driver.find_elements(
                By.XPATH,
                "//*[normalize-space(text())='Feed post']"
            )

            print(
                f"Feed post markers: {len(markers)}"
            )

            for marker in markers:

                try:

                    current = marker
                    candidate = None

                    for level in range(
                        1,
                        15
                    ):

                        try:

                            current = (
                                current.find_element(
                                    By.XPATH,
                                    "./.."
                                )
                            )

                        except Exception:
                            break

                        try:

                            text = (
                                current.text.strip()
                            )

                        except Exception:
                            continue

                        if not text:
                            continue

                        if (
                            200 <= len(text) <= 15000
                            and (
                                "Follow" in text
                                or "… more" in text
                                or "... more" in text
                            )
                        ):

                            candidate = current

                            if len(text) >= 500:
                                break

                    if candidate:

                        element_id = (
                            candidate.id
                        )

                        if element_id not in seen_ids:

                            seen_ids.add(
                                element_id
                            )

                            elements.append(
                                candidate
                            )

                except Exception:
                    continue

        except Exception as error:

            print(
                "Feed marker extraction failed:",
                error
            )

    # --------------------------------------------------------
    # Share-button fallback.
    # --------------------------------------------------------

    if not elements:

        print()
        print(
            "Trying Share-button based extraction..."
        )

        try:

            share_buttons = driver.find_elements(
                By.XPATH,
                "//button[contains("
                "translate(@aria-label,"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),"
                "'share'"
                ")]"
            )

            print(
                f"Share buttons found: "
                f"{len(share_buttons)}"
            )

            for button in share_buttons:

                try:

                    current = button
                    candidate = None

                    for level in range(
                        1,
                        15
                    ):

                        try:

                            current = (
                                current.find_element(
                                    By.XPATH,
                                    "./.."
                                )
                            )

                        except Exception:
                            break

                        try:

                            text = (
                                current.text.strip()
                            )

                        except Exception:
                            continue

                        if (
                            200 <= len(text) <= 15000
                            and (
                                "Follow" in text
                                or "Feed post" in text
                                or "more" in text.lower()
                            )
                        ):

                            candidate = current

                            if len(text) >= 500:
                                break

                    if candidate:

                        element_id = (
                            candidate.id
                        )

                        if element_id not in seen_ids:

                            seen_ids.add(
                                element_id
                            )

                            elements.append(
                                candidate
                            )

                except Exception:
                    continue

        except Exception as error:

            print(
                "Share-button extraction failed:",
                error
            )

    print()
    print(
        "Post containers found: "
        f"{len(elements)}"
    )

    return elements


# ============================================================
# EXTRACT POSTS
# ============================================================

def extract_posts(
    driver
):

    print()
    print("=" * 60)
    print("EXTRACTING LINKEDIN POSTS")
    print("=" * 60)
    print()

    time.sleep(5)

    print(
        "Loading LinkedIn posts..."
    )

    # ========================================================
    # SCROLL
    # ========================================================

    previous_height = 0

    for i in range(30):

        driver.execute_script(
            """
            window.scrollTo(
                0,
                document.body.scrollHeight
            );
            """
        )

        time.sleep(2)

        current_height = (
            driver.execute_script(
                "return document.body.scrollHeight;"
            )
        )

        print(
            f"Scrolling LinkedIn... "
            f"{i + 1}/30"
        )

        if current_height == previous_height:
            break

        previous_height = current_height

    driver.execute_script(
        "window.scrollTo(0, 0);"
    )

    time.sleep(2)

    # ========================================================
    # DEBUG
    # ========================================================

    print()
    print("=" * 70)
    print("LINKEDIN PAGE DEBUG")
    print("=" * 70)

    print()
    print(
        "Current URL:"
    )
    print(
        driver.current_url
    )

    print()
    print(
        "Page title:"
    )
    print(
        driver.title
    )

    print()
    print(
        "Page source length:"
    )
    print(
        len(driver.page_source)
    )

    try:

        body_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text

        print()
        print(
            "Body text length:"
        )
        print(
            len(body_text)
        )

        print()
        print(
            "FIRST 3000 CHARACTERS:"
        )

        print(
            "-" * 70
        )

        print(
            body_text[:3000]
        )

        print(
            "-" * 70
        )

    except Exception as error:

        print(
            "Could not read body:",
            error
        )

    # ========================================================
    # SAVE DEBUG HTML
    # ========================================================

    debug_html = (
        BASE_DIR
        / "data"
        / "linkedin_debug.html"
    )

    debug_html.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        debug_html,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            driver.page_source
        )

    print()
    print(
        "Debug HTML saved to:"
    )
    print(
        debug_html
    )

    # ========================================================
    # FIND POSTS
    # ========================================================

    unique_elements = (
        find_post_containers(
            driver
        )
    )

    print()
    print("=" * 60)
    print("POST CONTAINER DETECTION")
    print("=" * 60)

    print(
        f"Unique post containers found: "
        f"{len(unique_elements)}"
    )

    # ========================================================
    # EXTRACT
    # ========================================================

    posts = []

    seen_text = set()

    for index, element in enumerate(
    unique_elements,
    start=1
    ):

        try:

            # =================================================
            # 1. SCROLL POST INTO VIEW
            # =================================================

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                element
            )

            time.sleep(1)

            # =================================================
            # 2. EXPAND POST FIRST
            # =================================================

            print()
            print("=" * 70)
            print(
                f"EXTRACTING POST {index}"
            )
            print("=" * 70)

            print(
                "Step 1: Expanding post..."
            )

            expanded = expand_post_with_driver(
                driver,
                element
            )

            if expanded:
                print(
                    "Post expanded successfully."
                )
            else:
                print(
                    "Post did not require expansion "
                    "or expansion button was not found."
                )

            # =================================================
            # 3. WAIT FOR LINKEDIN TO FINISH RENDERING
            # =================================================

            print(
                "Step 2: Waiting for expanded content..."
            )

            time.sleep(2)

            # =================================================
            # 4. READ TEXT AFTER EXPANSION
            # =================================================

            print(
                "Step 3: Reading final post text..."
            )

            text = element.text.strip()

            if not text:
                print(
                    "Post has no text. Skipping."
                )
                continue

            # =================================================
            # 5. EXTRACT EMAIL ONLY NOW
            # =================================================

            print(
                "Step 4: Searching expanded post for email..."
            )

            recruiter_email = extract_email_from_text(
                text
            )

            print(
                f"Email found AFTER expansion: "
                f"{recruiter_email}"
            )

            # =================================================
            # 5A. REQUIRE EMAIL
            # =================================================
            #
            # If an email was found:
            #   Continue processing the post.
            #
            # If no email was found:
            #   Skip this post immediately and move
            #   to the next LinkedIn post.
            # =================================================

            if not recruiter_email:

                print()
                print(
                    "NO EMAIL FOUND."
                )

                print(
                    "Skipping this post and moving "
                    "to the next post."
                )

                continue

            print()
            print(
                f"EMAIL FOUND: {recruiter_email}"
            )

            # =================================================
            # 6. DUPLICATE CHECK
            # =================================================

            # =================================================
            # 6. DUPLICATE CHECK
            # =================================================

            normalized_text = re.sub(
                r"\s+",
                " ",
                text
            ).strip()

            if normalized_text in seen_text:
                print(
                    "Duplicate post. Skipping."
                )
                continue

            seen_text.add(
                normalized_text
            )

            # =================================================
            # 7. POSTED TIME
            # =================================================

            posted_time = extract_posted_time(
                element,
                text
            )

            # =================================================
            # 8. RECRUITER NAME
            # =================================================

            recruiter_name = None

            lines = [
                line.strip()
                for line in text.splitlines()
                if line.strip()
            ]

            for line_index, line in enumerate(
                lines[:25]
            ):

                if line == "Feed post":

                    if line_index > 0:

                        possible_name = (
                            lines[line_index - 1]
                        )

                        if (
                            possible_name
                            and possible_name
                            not in [
                                "Follow",
                                "More",
                                "… more",
                                "... more"
                            ]
                        ):
                            recruiter_name = possible_name

                    break

            # =================================================
            # 9. FALLBACK RECRUITER NAME
            # =================================================

            if not recruiter_name:

                for line in lines[:20]:

                    if line in [
                        "Feed post",
                        "Follow",
                        "More",
                        "… more",
                        "... more"
                    ]:
                        continue

                    lower = line.lower()

                    if any(
                        keyword in lower
                        for keyword in [
                            "developer",
                            "engineer",
                            "recruiter",
                            "hiring",
                            "full-time",
                            "full time"
                        ]
                    ):
                        continue

                    if " • " in line:
                        continue

                    if len(line) < 100:
                        recruiter_name = line
                        break

            # =================================================
            # 9. FALLBACK RECRUITER NAME
            # =================================================

            if not recruiter_name:

                for line in lines[:20]:

                    if line in [
                        "Feed post",
                        "Follow",
                        "More",
                        "… more",
                        "... more"
                    ]:
                        continue

                    lower = line.lower()

                    if any(
                        keyword in lower
                        for keyword in [
                            "developer",
                            "engineer",
                            "recruiter",
                            "hiring",
                            "full-time",
                            "full time"
                        ]
                    ):
                        continue

                    if " • " in line:
                        continue

                    if len(line) < 100:
                        recruiter_name = line
                        break

            # =================================================
            # DISPLAY
            # =================================================

            # =================================================
            # DISPLAY
            # =================================================

            print()
            print("=" * 70)
            print(
                f"POST {index} EXTRACTED"
            )
            print("=" * 70)

            print(
                f"Recruiter: "
                f"{recruiter_name}"
            )

            print(
                f"Email found: "
                f"{recruiter_email}"
            )

            print(
                f"Posted: "
                f"{posted_time}"
            )

            # =================================================
            # GET URL
            # =================================================

            post_url = (
                get_post_url_from_share(
                    driver,
                    element
                )
            )

            # ------------------------------------------------
            # HTML FALLBACK
            # ------------------------------------------------

            if not post_url:

                print()
                print(
                    "Copy-link method failed."
                )

                print(
                    "Trying post HTML fallback..."
                )

                post_url = (
                    get_url_from_post_html(
                        element
                    )
                )

                if post_url:

                    print(
                        "HTML fallback URL found:"
                    )

                    print(
                        post_url
                    )

            # ------------------------------------------------
            # ACTIVITY URN FALLBACK
            # ------------------------------------------------

            if not post_url:

                print(
                    "Trying activity URN fallback..."
                )

                post_url = (
                    get_url_from_activity_urn(
                        element
                    )
                )

                if post_url:

                    print(
                        "Activity URN fallback URL:"
                    )

                    print(
                        post_url
                    )

            # =================================================
            # FINAL URL
            # =================================================

            if post_url:

                post_url = post_url.strip()

                print()
                print(
                    "FINAL LINKEDIN POST URL:"
                )
                print(
                    post_url
                )

            else:

                print()
                print(
                    "WARNING: Could not obtain "
                    "a LinkedIn post URL."
                )

            # =================================================
            # SAVE
            # =================================================

            post = {

                "post_number":
                    index,

                "text":
                    text,

                "linkedin_post_url":
                    post_url,

                "posted_time":
                    posted_time,

                "recruiter_name":
                    recruiter_name,

                "recruiter_email":
                    recruiter_email
            }

            posts.append(
                post
            )

            # =================================================
            # DISPLAY
            # =================================================

            print()
            print(
                f"POST {len(posts)} EXTRACTED"
            )

            print()

            print(
                f"Recruiter/Author: "
                f"{recruiter_name}"
            )

            print(
                f"Email: "
                f"{recruiter_email}"
            )

            print(
                f"Posted: "
                f"{posted_time}"
            )

            print(
                f"LinkedIn URL: "
                f"{post_url}"
            )

            print()

            print(
                text[:1500]
            )

            print()

        except Exception as error:

            print()
            print(
                f"Could not extract post "
                f"{index}:"
            )

            print(
                error
            )

    # ========================================================
    # SAVE DEBUG FILE
    # ========================================================

    debug_file = (
        BASE_DIR
        / "data"
        / "linkedin_page.txt"
    )

    debug_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        debug_file,
        "w",
        encoding="utf-8"
    ) as file:

        for post in posts:

            file.write(
                "\n"
                + "=" * 70
                + "\n"
            )

            file.write(
                f"POST {post['post_number']}\n"
            )

            file.write(
                f"RECRUITER: "
                f"{post.get('recruiter_name')}\n"
            )

            file.write(
                f"EMAIL: "
                f"{post.get('recruiter_email')}\n"
            )

            file.write(
                f"URL: "
                f"{post.get('linkedin_post_url')}\n"
            )

            file.write(
                f"POSTED: "
                f"{post.get('posted_time')}\n"
            )

            file.write(
                "=" * 70
                + "\n"
            )

            file.write(
                post["text"]
            )

            file.write(
                "\n"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("=" * 60)
    print("LINKEDIN EXTRACTION RESULT")
    print("=" * 60)

    print()

    print(
        f"Posts extracted: "
        f"{len(posts)}"
    )

    urls_found = sum(
        1
        for post in posts
        if post.get(
            "linkedin_post_url"
        )
    )

    print(
        f"LinkedIn URLs found: "
        f"{urls_found}/{len(posts)}"
    )

    print()

    print(
        "24-hour filtering:"
    )

    print(
        "LINKEDIN NATIVE FILTER - PAST 24 HOURS"
    )

    print()

    print(
        "Saved extracted posts to:"
    )

    print(
        debug_file
    )

    print()

    return posts


# ============================================================
# DISPLAY POSTS
# ============================================================

def display_posts(
    posts
):

    print()
    print("=" * 60)
    print("LINKEDIN POSTS")
    print("=" * 60)

    if not posts:

        print()
        print(
            "No posts were extracted."
        )

        print()

        return

    for post in posts:

        print()

        print(
            f"========== POST "
            f"{post['post_number']} =========="
        )

        print(
            f"Recruiter: "
            f"{post.get('recruiter_name')}"
        )

        print(
            f"Email: "
            f"{post.get('recruiter_email')}"
        )

        print(
            f"Posted: "
            f"{post.get('posted_time')}"
        )

        print(
            f"URL: "
            f"{post.get('linkedin_post_url')}"
        )

        print()

        print(
            post["text"]
        )

        print()


# ============================================================
# FILTER AND PARSE POSTS
#
# IMPORTANT:
#
# There is NO Python 24-hour rejection here.
#
# LinkedIn already filtered the search results.
# ============================================================

def filter_job_posts(
    posts,
    candidate_job_title
):

    valid_jobs = []

    print()
    print("=" * 60)
    print("FILTERING LINKEDIN POSTS")
    print("=" * 60)

    print()

    for post in posts:

        posted_time = post.get(
            "posted_time"
        )

        # ====================================================
        # NO PYTHON AGE FILTER
        #
        # LinkedIn already applied:
        #
        # Past 24 hours
        #
        # through:
        #
        # datePosted=["past-24h"]
        # ====================================================

        print(
            f"Post {post['post_number']}: "
            f"LinkedIn Past-24h result "
            f"({posted_time})"
        )

        # ====================================================
        # PARSE JOB
        # ====================================================

        result = parse_job_post(
            post["text"],
            candidate_job_title
        )

        # ====================================================
        # PRESERVE LINKEDIN DATA
        # ====================================================

        result["linkedin_post_url"] = (
            post.get(
                "linkedin_post_url"
            )
        )

        result["posted_time"] = (
            posted_time
        )


        # =================================================
        # PRESERVE EMAIL FROM LINKEDIN POST
        # =================================================

        post_email = post.get("recruiter_email")
        parser_email = result.get("recruiter_email")

        print(
            f"Parser email: {parser_email}"
        )

        print(
            f"Post extracted email: {post_email}"
        )

        # Prefer the email extracted directly from the
        # LinkedIn post because it came from the actual
        # expanded post text.
        if post_email:
            result["recruiter_email"] = post_email
        elif parser_email:
            result["recruiter_email"] = parser_email
        else:
            result["recruiter_email"] = None

        print(
            f"Final recruiter email: "
            f"{result.get('recruiter_email')}"
        )

        # ====================================================
        # PRESERVE RECRUITER
        # ====================================================

        result["recruiter_name"] = (
            result.get(
                "recruiter_name"
            )
            or
            post.get(
                "recruiter_name"
            )
        )

        # ====================================================
        # VALIDATION
        # ====================================================

        if not result.get(
            "valid",
            False
        ):

            print(
                f"Post {post['post_number']}: SKIPPED"
            )

            print(
                f"Reason: "
                f"{result.get('skip_reason')}"
            )

            print()

            continue

        # ====================================================
        # VALID JOB
        # ====================================================

        print(
            f"Post {post['post_number']}: VALID JOB"
        )

        print(
            f"Recruiter: "
            f"{result.get('recruiter_name')}"
        )

        print(
            f"Email: "
            f"{result.get('recruiter_email')}"
        )

        print(
            f"Job Title: "
            f"{result.get('job_title')}"
        )

        print(
            f"Company: "
            f"{result.get('company_name')}"
        )

        print(
            f"Location: "
            f"{result.get('location')}"
        )

        print(
            f"Posted: "
            f"{posted_time}"
        )

        print(
            f"LinkedIn URL: "
            f"{result.get('linkedin_post_url')}"
        )

        print()

        valid_jobs.append(
            result
        )

    return valid_jobs


# ============================================================
# DISPLAY VALID JOBS
# ============================================================

def display_valid_jobs(
    valid_jobs
):

    print()
    print("=" * 60)
    print("VALID JOBS")
    print("=" * 60)

    print()

    print(
        f"Valid jobs found: "
        f"{len(valid_jobs)}"
    )

    for index, job in enumerate(
        valid_jobs,
        start=1
    ):

        print()

        print(
            f"========== JOB {index} =========="
        )

        print(
            f"Recruiter: "
            f"{job.get('recruiter_name')}"
        )

        print(
            f"Email: "
            f"{job.get('recruiter_email')}"
        )

        print(
            f"Company: "
            f"{job.get('company_name')}"
        )

        print(
            f"Job Title: "
            f"{job.get('job_title')}"
        )

        print(
            f"Experience: "
            f"{job.get('experience_required')}"
        )

        print(
            f"Location: "
            f"{job.get('location')}"
        )

        print(
            f"Employment: "
            f"{job.get('employment_type')}"
        )

        print(
            f"Posted: "
            f"{job.get('posted_time')}"
        )

        print(
            f"LinkedIn URL: "
            f"{job.get('linkedin_post_url')}"
        )

        print()

        print(
            "Job Description:"
        )

        print(
            job.get(
                "job_description"
            )
        )

        print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("LINKEDIN JOB AUTOMATION")
    print("=" * 60)

    print()

    # --------------------------------------------------------
    # READ RESUME
    # --------------------------------------------------------

    print(
        "Reading candidate resume..."
    )

    resume_text = extract_resume_text(
        str(RESUME_PATH)
    )

    candidate = extract_candidate_info(
        resume_text
    )

    job_title = candidate.get(
        "job_title"
    )

    print()

    print(
        f"Candidate Job Title: "
        f"{job_title}"
    )

    # --------------------------------------------------------
    # QUERY
    # --------------------------------------------------------

    query = generate_search_query(
        job_title
    )

    print()

    print("=" * 60)
    print("SEARCH QUERY")
    print("=" * 60)

    print(
        query
    )

    print()

    # --------------------------------------------------------
    # BROWSER
    # --------------------------------------------------------

    driver = start_browser()

    try:

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        logged_in = login_to_linkedin(
            driver
        )

        if not logged_in:

            print()
            print(
                "LinkedIn login failed."
            )

            input(
                "Press ENTER to close..."
            )

            raise SystemExit

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        search_linkedin_posts(
            driver,
            query
        )

        # ----------------------------------------------------
        # EXTRACT
        # ----------------------------------------------------

        posts = extract_posts(
            driver
        )

        print()

        print(
            f"Posts extracted: "
            f"{len(posts)}"
        )

        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        display_posts(
            posts
        )

        # ----------------------------------------------------
        # FILTER
        # ----------------------------------------------------

        valid_jobs = filter_job_posts(
            posts,
            job_title
        )

        # ----------------------------------------------------
        # DISPLAY VALID JOBS
        # ----------------------------------------------------

        display_valid_jobs(
            valid_jobs
        )

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        print()

        print("=" * 60)
        print(
            "LINKEDIN SEARCH COMPLETED"
        )
        print("=" * 60)

        print()

        print(
            f"Total posts extracted: "
            f"{len(posts)}"
        )

        print(
            f"Valid jobs found: "
            f"{len(valid_jobs)}"
        )

        print()

        print(
            "24-hour filter:"
        )

        print(
            "LINKEDIN NATIVE - PAST 24 HOURS"
        )

        print()

        input(
            "Press ENTER to close the browser..."
        )

    finally:

        driver.quit()
