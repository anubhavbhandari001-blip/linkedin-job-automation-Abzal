from gmail.auth import get_gmail_credentials


print("\nStarting Gmail authentication...\n")


credentials = get_gmail_credentials()


if credentials and credentials.valid:

    print("Gmail authentication successful!")

else:

    print("Gmail authentication failed.")