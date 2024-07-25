import re
from datetime import datetime
from Libraries.gmail_auth import gmail_authenticate
from Libraries.logger import get_logger

logger = get_logger(__name__)


def extract_data(subject, sender):
    id = re.search(r"ID (\d+)", subject)
    prazo = re.search(r"PRAZO: (\d{2}/\d{2}/\d{4})", subject)
    solicitacao = re.search(r"PRAZO: \d{2}/\d{2}/\d{4} - (.*?) -", subject)
    partes = re.search(r"- ([^-]+) X ([^-]+) -", subject)
    processo = re.search(r"PROC (\d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4})", subject)
    comarca = re.search(r"- ([^-]+/[A-Z]{2})$", subject)
    orgao = re.search(r"PROC \d{7}-\d{2}.\d{4}.\d{1}.\d{2}.\d{4} – (.*?) -", subject)

    if not (id and processo):
        return None

    comarca = comarca.group(1).strip().split("/")[0]
    estado = comarca.split("/")[-1]

    sender_name = re.match(r"^(.*) <.*>$", sender)
    sender_name = sender_name.group(1).strip() if sender_name else sender[1:-1]

    extracted_data = {
        "DATA DA SOLICITAÇÃO": datetime.now().strftime("%d/%m/%Y"),
        "CLIENTE": sender_name,
        "ADV/SOLICITANTE": None,
        "PRAZO": (
            datetime.strptime(prazo.group(1), "%d/%m/%Y").strftime("%d/%m/%Y")
            if prazo
            else None
        ),
        "ID": id.group(1),
        "SOLICITACAO": (solicitacao.group(1).strip() if solicitacao else None),
        "COMARCA": comarca,
        "ESTADO": estado,
        "ORGAO": orgao.group(1).strip() if orgao else None,
        "PROCESSO": processo.group(1),
        "PARTE_1": partes.group(1).strip() if partes else None,
        "PARTE_2": partes.group(2).strip() if partes else None,
        "TELEFONE": None,
        "AGENDA": None,
        "OBSERVACAO": None,
        "COLIGADO": None,
        "VALOR CLIENTE": None,
        "VALOR COLIGADO": None,
    }
    return extracted_data


def process_emails(ok_label, fail_label):
    service, _, _ = gmail_authenticate()

    messages_to_process = []

    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=30)
        .execute()
    )
    messages = results.get("messages", [])

    for message in messages:
        msg_id = message["id"]
        msg = service.users().messages().get(userId="me", id=msg_id).execute()
        labels = msg.get("labelIds", [])

        if ok_label not in labels and fail_label not in labels:
            messages_to_process.append(msg_id)

    logger.info(f"Numero total de emails: {len(messages_to_process)}")

    email_data = []
    for msg_id in messages_to_process:
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

    return email_data


def update_google_sheet(sheet_id, email_data):
    _, service, _ = gmail_authenticate()
    range_name = "ABRAZ - ALV E DESP!A2"

    if not email_data:
        logger.info("Nenhum dado de e-mail processado.")
        return

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


def apply_label(service, msg_id, label_id):
    service.users().messages().modify(
        userId="me", id=msg_id, body={"addLabelIds": [label_id]}
    ).execute()


def get_labels(service):
    labels = service.users().labels().list(userId="me").execute()

    ok_label = None
    fail_label = None

    for label in labels["labels"]:
        if label["name"] == "OK":
            ok_label = label["id"]
        elif label["name"] == "FAIL":
            fail_label = label["id"]

    return ok_label, fail_label
