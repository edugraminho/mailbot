from Libraries.logger import get_logger
from Libraries.email_process import (
    process_emails,
    update_google_sheet,
    create_label_if_not_exists,
    apply_label,
)
import os
from dotenv import load_dotenv

logger = get_logger(__name__)

load_dotenv()
SHEET_ID = os.getenv("SHEET_ID")


def run():
    service, email_data = process_emails()
    logger.info(f"Emails processados: {len(email_data)}")

    label_inseridos_id = create_label_if_not_exists(service, "OK")
    label_falha_id = create_label_if_not_exists(service, "FAIL")

    for msg_id, data in email_data:
        try:
            update_google_sheet(SHEET_ID, [data])
            apply_label(service, msg_id, label_inseridos_id)
        except Exception as e:
            logger.error(f"Erro ao inserir dados na planilha: {e}")
            apply_label(service, msg_id, label_falha_id)


run()
