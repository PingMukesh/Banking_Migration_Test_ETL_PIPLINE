import os 
import configparser
from pathlib import Path
from sqlalchemy import*

from utils.logger import logger

BASE_DIR = Path(__file__).resolve().parent.parent
Root_DIR = BASE_DIR.parent
CONFIG_FILE = BASE_DIR / "config" / "config.ini"

config = configparser.ConfigParser()
if CONFIG_FILE.exists():
    config.read(CONFIG_FILE)


def build_oracle_url():
    if os.getenv("TARGET_ORCALE_URL"):
        return os.getenv("TARGET_ORCALE_URL")

    host = config.get("DATABASE.TARGET","host", fallback="localhost")
    port = config.get("DATABASE.TARGET","port", fallback="1521")
    service_name = config.get("DATABASE.TARGET","service_name", fallback="orcl")
    username = config.get("DATABASE.TARGET","username", fallback="user")
    password = config.get("DATABASE.TARGET","password", fallback="password")
    return f"oracle+oracledb://{username}:{password}@{host}:{port}/?service_name={service_name}"


def build_source_url():
    if os.getenv("SOURCE_LEGACY_URL"):
        return os.getenv("SOURCE_LEGACY_URL")

    host = config.get("DATABASE.SOURCE","host", fallback="localhost")
    port = config.get("DATABASE.SOURCE","port", fallback="3306")
    db = config.get("DATABASE.SOURCE","database", fallback="legacy_banking")
    username = config.get("DATABASE.SOURCE","username", fallback="root")
    password = config.get("DATABASE.SOURCE","password", fallback="root")
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db}"


def build_sqlite_url(section, default_path):
    configured_path = config.get(section, "fallback_sqlite", fallback="").strip()
    sqlite_path = Path(configured_path) if configured_path else Path(default_path)
    if not sqlite_path.is_absolute():
        sqlite_path = BASE_DIR / sqlite_path
    if not sqlite_path.parent.exists():
        sqlite_path = Path(default_path)
    return f"sqlite:///{sqlite_path}"


class DBManager:

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
       self.source_engine = self._init_Source_engine()
       self.target_engine = self._init_Target_engine()


    @classmethod
    def _init_Source_engine(self):
        mysql_url = build_source_url()

        try:
            eng = create_engine(mysql_url, echo=False)

            with eng.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Successfully connected to the source database.")
                return eng

        except Exception as e:
            logger.warning(f"Could not connect to source database ({e}), falling back to SQLite.")
            sqlite_url = build_sqlite_url(
                "DATABASE.SOURCE", BASE_DIR / "data" / "source_fallback.db"
            )
            return create_engine(sqlite_url, echo=False)

    def _init_Target_engine(self):
        oracle_url = build_oracle_url()

        try:
            eng = create_engine(oracle_url, echo=False)

            with eng.connect() as conn:
                conn.execute(text("SELECT 1 from dual"))
                logger.info("Successfully connected to the Target database.")
                return eng

        except Exception as e:
            logger.warning(f"Could not connect to target database ({e}), falling back to SQLite.")
            sqlite_url = build_sqlite_url(
                "DATABASE.TARGET", BASE_DIR / "data" / "target_fallback.db"
            )
            return create_engine(sqlite_url, echo=False)



    def get_source_engine(self):
        return self.source_engine.connect()

    def get_target_engine(self):
        return self.target_engine.connect()






def get_db_manager():
    return DBManager.get_instance()

    

