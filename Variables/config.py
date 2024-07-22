from pathlib import Path, PurePath
import os
from datetime import datetime, timedelta

# ====================== DIRETÓRIOS LOCAIS e DATAS ======================
ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
DATA_DIRECTORY = os.path.join(ROOT, "Data")
SESSION_DIRECTORY = os.path.join(ROOT, "Session")
CURRENT_DAY = datetime.now().strftime("%d/%m")
FULL_DATE_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_NOW = datetime.now().strftime(FULL_DATE_FORMAT)
