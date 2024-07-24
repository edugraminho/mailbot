import re
import os
from datetime import datetime
from Libraries.gmail_auth import gmail_authenticate
from Libraries.logger import get_logger

logger = get_logger(__name__)


def extract_data(subject, sender):
    id_pattern = r"ID (\d+)"
    prazo_pattern = r"PRAZO: (\d{2}/\d{2}/\d{4})"
    solicitacao_pattern = r"PRAZO: \d{2}/\d{2}/\d{4} - (.*?) -"
    partes_pattern = r"- ([^-]+) X ([^-]+) -"
    processo_pattern = r"PROC (\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4})"
    comarca_pattern = r"- ([^-]+/[A-Z]{2})$"

    id_match = re.search(id_pattern, subject)
    prazo_match = re.search(prazo_pattern, subject)
    solicitacao_match = re.search(solicitacao_pattern, subject)
    partes_match = re.search(partes_pattern, subject)
    processo_match = re.search(processo_pattern, subject)
    comarca_match = re.search(comarca_pattern, subject)

    if not (id_match and processo_match):
        return None

    comarca = comarca_match.group(1).strip()
    estado = comarca.split("/")[-1]

    sender_name_pattern = r"^(.*) <.*>$"
    sender_name_match = re.match(sender_name_pattern, sender)
    sender_name = sender_name_match.group(1).strip() if sender_name_match else sender

    extracted_data = {
        "DATA DA SOLICITAÇÃO": datetime.now().strftime("%d/%m/%Y"),
        "CLIENTE": sender_name,
        "ADV/SOLICITANTE": None,
        "PRAZO": datetime.strptime(prazo_match.group(1), "%d/%m/%Y").strftime(
            "%d/%m/%Y"
        ),
        "ID": id_match.group(1),
        "SOLICITACAO": solicitacao_match.group(1).strip(),
        "COMARCA": comarca,
        "ESTADO": estado,
        "ORGAO": None,
        "PROCESSO": processo_match.group(1),
        "PARTE_1": partes_match.group(1).strip(),
        "PARTE_2": partes_match.group(2).strip(),
        "TELEFONE": None,
        "AGENDA": None,
        "OBSERVACAO": None,
        "COLIGADO": None,
        "VALOR CLIENTE": None,
        "VALOR COLIGADO": None,
    }
    return extracted_data


def process_emails():
    service, _, _ = gmail_authenticate()

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
        msg_id = message["id"]
        msg = service.users().messages().get(userId="me", id=msg_id).execute()
        subject = ""
        sender = ""
        for header in msg["payload"]["headers"]:
            if header["name"] == "Subject":
                subject = header["value"]
            elif header["name"] == "From":
                sender = header["value"]
        data = extract_data(subject, sender)
        if data:
            email_data.append((msg_id, data))

    with open(history_file, "w") as file:
        file.write(current_history_id)

    return service, email_data


def update_google_sheet(sheet_id, email_data):
    _, service, _ = gmail_authenticate()
    range_name = "ABRAZ - ALV E DESP!A2"

    # Verifica se email_data não está vazio e filtra valores None
    if not email_data:
        logger.info("Nenhum dado de e-mail processado.")
        return

    # Cria a lista de valores ignorando itens None
    values = [
        [
            data["DATA DA SOLICITAÇÃO"],
            data["CLIENTE"],
            data["ADV/SOLICITANTE"],
            data["PRAZO"] if data["PRAZO"] else None,
            data["ID"],
            data["COMARCA"],
            data["ESTADO"],
            data["ORGAO"],
            data["PROCESSO"],
            data["PARTE_1"],
            data["PARTE_2"],
            data["SOLICITACAO"],
            data["TELEFONE"],
            data["AGENDA"],
            data["OBSERVACAO"],
            data["COLIGADO"],
            data["VALOR CLIENTE"],
            data["VALOR COLIGADO"],
        ]
        for data in email_data
        if data
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


def create_label_if_not_exists(service, label_name):
    # Verifica se a label já existe
    labels = service.users().labels().list(userId="me").execute()
    label_id = None
    for label in labels["labels"]:
        if label["name"] == label_name:
            label_id = label["id"]
            break

    # Se a label não existir, cria uma nova
    if not label_id:
        label = {
            "messageListVisibility": "show",
            "name": label_name,
            "labelListVisibility": "labelShow",
        }
        created_label = (
            service.users().labels().create(userId="me", body=label).execute()
        )
        label_id = created_label["id"]

    return label_id


def apply_label(service, msg_id, label_id):
    service.users().messages().modify(
        userId="me", id=msg_id, body={"addLabelIds": [label_id]}
    ).execute()
