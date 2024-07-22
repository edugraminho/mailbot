import re
import os
from datetime import datetime
import pandas as pd
from Libraries.gmail_auth import gmail_authenticate, list_sheets
from Libraries.logger import get_logger

logger = get_logger(__name__)

# If modifying these SCOPES, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def extract_data(subject, sender):
    id_pattern = r"ID (\d+)"
    prazo_pattern = r"PRAZO: (\d{2}/\d{2}/\d{4})"
    solicitacao_pattern = r"- (.*?) -"
    partes_pattern = r"- ([^-]+) X ([^-]+) -"
    processo_pattern = r"PROC (\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4})"
    comarca_pattern = r"- ([^-]+)$"

    id_match = re.search(id_pattern, subject)
    prazo_match = re.search(prazo_pattern, subject)
    solicitacao_match = re.search(solicitacao_pattern, subject)
    partes_match = re.search(partes_pattern, subject)
    processo_match = re.search(processo_pattern, subject)
    comarca_match = re.search(comarca_pattern, subject)

    extracted_data = {
        "ID": id_match.group(1) if id_match else None,
        "DATA DA SOLICITAÇÃO": datetime.now().strftime("%d/%m/%Y"),
        "CLIENTE": sender,
        "PRAZO": (
            datetime.strptime(prazo_match.group(1), "%d/%m/%Y") if prazo_match else None
        ),
        "SOLICITACAO": (
            solicitacao_match.group(1).strip() if solicitacao_match else None
        ),
        "PARTE_1": partes_match.group(1).strip() if partes_match else None,
        "PARTE_2": partes_match.group(2).strip() if partes_match else None,
        "PROCESSO": processo_match.group(1) if processo_match else None,
        "COMARCA": comarca_match.group(1).strip() if comarca_match else None,
    }
    return extracted_data


def process_emails():
    service, _, _ = gmail_authenticate()

    # Load the last historyId from a file
    history_file = "last_history_id.txt"
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            last_history_id = file.read().strip()
    else:
        last_history_id = None

    # Get the latest historyId
    profile = service.users().getProfile(userId="me").execute()
    current_history_id = profile["historyId"]

    # If no last_history_id, initialize the first batch of emails
    if last_history_id is None:
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=10)
            .execute()
        )
    else:
        results = (
            service.users()
            .history()
            .list(userId="me", startHistoryId=last_history_id, labelId="INBOX")
            .execute()
        )

    messages = results.get("messages", [])

    email_data = []
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        subject = ""
        sender = ""
        for header in msg["payload"]["headers"]:
            if header["name"] == "Subject":
                subject = header["value"]
            elif header["name"] == "From":
                sender = header["value"]
        data = extract_data(subject, sender)
        email_data.append(data)

    # Save the current historyId to a file
    with open(history_file, "w") as file:
        file.write(current_history_id)

    return email_data


def update_google_sheet(sheet_id, email_data):
    _, service, _ = gmail_authenticate()
    list_sheets()

    range_name = "ABRAZ - ALV E DESP!A2"

    values = [
        [
            data["ID"],
            data["DATA DA SOLICITAÇÃO"],
            data["CLIENTE"],
            data["PRAZO"].strftime("%d/%m/%Y") if data["PRAZO"] else None,
            data["SOLICITACAO"],
            data["PARTE_1"],
            data["PARTE_2"],
            data["PROCESSO"],
            data["COMARCA"],
        ]
        for data in email_data
    ]

    body = {"values": values}

    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body,
        )
        .execute()
    )

    logger.info(f"{result.get('updates').get('updatedCells')} cells updated.")
