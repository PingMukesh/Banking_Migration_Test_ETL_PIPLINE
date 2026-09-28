import logging
import sys
from pathlib import Path

log_dir = Path(__file__).resolve().parent.parent / "reports" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)


logger = logging.getLogger("ETL_BDD_QA")
logger.setLevel(logging.INFO)



if not logger.handlers:

    #Console Handler

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    #File Handler

    fh = logging.FileHandler(log_dir / "bb_test_execution.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    
