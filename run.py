from Libraries.logger import get_logger
from Libraries.gmail_auth import gmail_authenticate
from Libraries.email_process import (
    process_emails,
    update_google_sheet,
    apply_label,
    get_labels,
)
import os
from dotenv import load_dotenv

logger = get_logger(__name__)

load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")


def run():
    service, _, _ = gmail_authenticate()

    OK, FAIL = get_labels(service)
    logger.info(f"Labels: {OK, FAIL}")

    email_data = process_emails(OK, FAIL)
    logger.info(f"Emails processados: {len(email_data)}")

    for msg_id, data in email_data:
        try:
            update_google_sheet(SHEET_ID, [data])
            apply_label(service, msg_id, OK)
        except Exception as e:
            logger.error(f"Erro ao inserir dados na planilha: {e}")
            apply_label(service, msg_id, FAIL)


run()
