from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError


# ============================================================
# GMAIL PERMISSIONS
# ============================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose"
]


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

CREDENTIALS_FILE = (
    BASE_DIR
    / "credentials"
    / "credentials.json"
)

TOKEN_FILE = (
    BASE_DIR
    / "credentials"
    / "token.json"
)


# ============================================================
# GET GMAIL CREDENTIALS
# ============================================================

def get_gmail_credentials():

    credentials = None

    # --------------------------------------------------------
    # Check whether saved token exists
    # --------------------------------------------------------

    if TOKEN_FILE.exists():

        print()
        print("Loading saved Gmail authentication token...")

        try:

            credentials = (
                Credentials.from_authorized_user_file(
                    str(TOKEN_FILE),
                    SCOPES
                )
            )

        except Exception as error:

            print(
                "Could not load saved Gmail token:"
            )
            print(error)

            credentials = None

    # --------------------------------------------------------
    # Token is already valid
    # --------------------------------------------------------

    if credentials and credentials.valid:

        print(
            "Gmail authentication is valid."
        )

        return credentials

    # --------------------------------------------------------
    # Try refreshing expired token
    # --------------------------------------------------------

    if (
        credentials
        and credentials.expired
        and credentials.refresh_token
    ):

        print()
        print(
            "Gmail access token expired."
        )

        print(
            "Attempting to refresh Gmail authentication..."
        )

        try:

            credentials.refresh(
                Request()
            )

            print(
                "Gmail token refreshed successfully."
            )

            TOKEN_FILE.write_text(
                credentials.to_json(),
                encoding="utf-8"
            )

            return credentials

        except RefreshError as error:

            print()
            print(
                "Saved Gmail refresh token is no longer valid."
            )
            print(
                "Starting fresh Gmail authentication..."
            )
            print()

            # Delete the invalid token.
            try:
                TOKEN_FILE.unlink()
                print(
                    "Invalid token.json deleted."
                )
            except Exception:
                pass

            credentials = None

        except Exception as error:

            print()
            print(
                "Unexpected Gmail token refresh error:"
            )
            print(error)
            print()
            
            credentials = None

    # --------------------------------------------------------
    # Fresh OAuth login
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("GMAIL AUTHENTICATION REQUIRED")
    print("=" * 60)
    print()

    print(
        "A browser window will open."
    )

    print(
        "Please sign in to the Gmail account"
    )

    print(
        "that should send the job applications."
    )

    print()

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        SCOPES
    )

    credentials = flow.run_local_server(
        port=0
    )

    # --------------------------------------------------------
    # Save new token
    # --------------------------------------------------------

    TOKEN_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    TOKEN_FILE.write_text(
        credentials.to_json(),
        encoding="utf-8"
    )

    print()
    print(
        "Gmail authentication completed successfully."
    )

    print(
        f"New token saved to: {TOKEN_FILE}"
    )

    print()

    return credentials