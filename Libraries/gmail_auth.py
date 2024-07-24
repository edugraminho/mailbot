import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from Libraries.logger import get_logger

logger = get_logger(__name__)

# Se modificar esse SCOPES, delete o token.json
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
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
