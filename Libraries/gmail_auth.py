import os.path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from Libraries.logger import get_logger

logger = get_logger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def gmail_authenticate():
    """Autentica o usuário e retorna o serviço da API do Gmail."""
    creds = None
    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "wb") as token:
            token.write(creds.to_json().encode())
    service_gmail = build("gmail", "v1", credentials=creds)
    service_sheet = build("sheets", "v4", credentials=creds)
    service_drive = build("drive", "v3", credentials=creds)

    return service_gmail, service_sheet, service_drive


def list_sheets():
    _, _, service_drive = gmail_authenticate()

    results = (
        service_drive.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    for sheet in items:
        logger.info("=================================================================")
        logger.info(sheet)
