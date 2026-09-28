import pandas as pd
import json
from pathlib import Path


base_dir = Path(__file__).resolve().parent.parent
data_dir = base_dir / "data"


class ExternalDataReader:

    _cache = {}

    @classmethod
    def read_excel_sheet(cls, file_name: str, sheet_name: str) -> pd.DataFrame:
        file_path = data_dir / file_name if not Path(file_name).is_absolute() else Path(file_name)

        if not file_path.exists():
            raise FileNotFoundError(f"External file not found: {file_path}")

        cache_key = f"{file_path}::{sheet_name}"
        if cache_key in cls._cache:
            return cls._cache[cache_key].copy()

        df = pd.read_excel(file_path, sheet_name=sheet_name)
        cls._cache[cache_key] = df
        return df.copy()

    @classmethod
    def read_json_schema(cls, file_name: str) -> dict:
        file_path = data_dir / file_name if not Path(file_name).is_absolute() else Path(file_name)

        if not file_path.exists():
            raise FileNotFoundError(f"Json Schema file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def read_excel_mappping(cls, file_name: str, sheet_name: str) -> dict:
        df = cls.read_excel_sheet(file_name, sheet_name)

        if len(df.columns) < 2:
            raise ValueError(f"Sheet '{sheet_name}', in {file_name} must contains at least 2 columns")

        key_col = df.columns[0]
        val_col = df.columns[1]

        return dict(zip(df[key_col].astype(str).str.strip(), df[val_col].astype(str).str.strip()))

    @classmethod
    def Read_csv_threshold(cls, file_name: str) -> dict:
        file_path = data_dir / file_name if not Path(file_name).is_absolute() else Path(file_name)

        if not file_path.exists():
            raise FileNotFoundError(f"CSV Threshold file not found: {file_path}")

        df = pd.read_csv(file_path)
        return dict(zip(df["RULE_NAME"].astype(str), df["THRESHOLD_VALUE"]))

    read_csv_thresholds = Read_csv_threshold
    read_excel_mapping = read_excel_mappping
