import time
import asyncio
import pdb
from Libraries.logger import get_logger
from Libraries.email_process import process_emails, update_google_sheet
import os



logger = get_logger(__name__)

SHEET_ID = os.getenv("SHEET_ID")

def run():
    initial_time = time.time()

    email_data = process_emails()

    logger.info(f"Emails processados: {len(email_data)}")
    logger.info(email_data)

    update_google_sheet(SHEET_ID, email_data)

    actual_time = time.time()
    exec_time = actual_time - initial_time
    # logger.info(f"Tempo de execução: {exec_time:.2f} segundos")


run()
