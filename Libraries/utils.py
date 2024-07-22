from datetime import datetime
from Variables.config import FULL_DATE_FORMAT, DATE_NOW


def convert_date_to_timestamp(date: str) -> int:
    timestamp = datetime.strptime(date, FULL_DATE_FORMAT).timestamp()
    return int(timestamp)
