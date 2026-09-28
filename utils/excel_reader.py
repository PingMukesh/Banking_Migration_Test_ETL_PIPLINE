"""
External Test Data Reader Utility
----------------------------------
Reads Excel (.xlsx), CSV, and JSON external validation files.
"""

import json
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class ExternalDataReader:
    _cache = {}

    @classmethod
    def read_excel_sheet(cls, file_name: str, sheet_name: str) -> pd.DataFrame:
        """Read a sheet from an Excel file into a pandas DataFrame."""
        file_path = DATA_DIR / file_name if not Path(file_name).is_absolute() else Path(file_name)
        if not file_path.exists():
            raise FileNotFoundError(f"External validation file not found: {file_path}")

        cache_key = f"{file_path}::{sheet_name}"
        if cache_key in cls._cache:
            return cls._cache[cache_key].copy()

        df = pd.read_excel(file_path, sheet_name=sheet_name)
        cls._cache[cache_key] = df
        return df.copy()

    @classmethod
    def read_excel_mapping(cls, file_name: str, sheet_name: str) -> dict:
        """Read 2-column Excel sheet as a lookup dictionary {key: value}."""
        df = cls.read_excel_sheet(file_name, sheet_name)
        if len(df.columns) < 2:
            raise ValueError(f"Sheet '{sheet_name}' in {file_name} must contain at least 2 columns for key-value mapping.")
        key_col = df.columns[0]
        val_col = df.columns[1]
        return dict(zip(df[key_col].astype(str).str.strip(), df[val_col].astype(str).str.strip()))

    @classmethod
    def read_json_schema(cls, file_name: str) -> dict:
        """Read a JSON schema definition file."""
        file_path = DATA_DIR / file_name if not Path(file_name).is_absolute() else Path(file_name)
        if not file_path.exists():
            raise FileNotFoundError(f"JSON schema file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def read_csv_thresholds(cls, file_name: str) -> dict:
        """Read CSV key-value thresholds file."""
        file_path = DATA_DIR / file_name if not Path(file_name).is_absolute() else Path(file_name)
        if not file_path.exists():
            raise FileNotFoundError(f"CSV thresholds file not found: {file_path}")

        df = pd.read_csv(file_path)
        return dict(zip(df["RULE_NAME"].astype(str), df["THRESHOLD_VALUE"]))

    # Backward-compatible aliases
    Read_csv_threshold = read_csv_thresholds
    read_excel_mappping = read_excel_mapping
