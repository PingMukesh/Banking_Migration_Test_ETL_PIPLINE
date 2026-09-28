"""
External Test Data Generator
-----------------------------
Generates validation artifacts for BDD data-driven testing:
1. test_mapping_rules.xlsx (Excel with multiple validation sheets)
2. expected_schema.json (JSON schema definitions)
3. validation_thresholds.csv (Boundary and business rule thresholds)
"""

import json
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_excel_mapping_rules():
    file_path = DATA_DIR / "test_mapping_rules.xlsx"
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        # Sheet 1: Customer Status Mapping
        df_status = pd.DataFrame([
            {"LegacyCode": "A", "ExpectedTargetStatus": "ACTIVE", "Description": "Active Account Holder"},
            {"LegacyCode": "I", "ExpectedTargetStatus": "INACTIVE", "Description": "Inactive Customer"},
            {"LegacyCode": "S", "ExpectedTargetStatus": "SUSPENDED", "Description": "Suspended for Review"},
            {"LegacyCode": "D", "ExpectedTargetStatus": "DECEASED", "Description": "Deceased Status"}
        ])
        df_status.to_excel(writer, sheet_name="StatusMapping", index=False)

        # Sheet 2: Account Type Mapping
        df_acct_type = pd.DataFrame([
            {"LegacyCode": "SAV", "ExpectedTargetType": "SAVINGS"},
            {"LegacyCode": "CHK", "ExpectedTargetType": "CHECKING"},
            {"LegacyCode": "MMA", "ExpectedTargetType": "MONEY_MARKET"},
            {"LegacyCode": "LON", "ExpectedTargetType": "LOAN"},
            {"LegacyCode": "CD", "ExpectedTargetType": "CERTIFICATE_OF_DEPOSIT"}
        ])
        df_acct_type.to_excel(writer, sheet_name="AccountTypeMapping", index=False)

        # Sheet 3: Delinquency Status Mapping
        df_delinq = pd.DataFrame([
            {"LegacyBucket": "00", "ExpectedTargetStatus": "PERFORMING"},
            {"LegacyBucket": "30", "ExpectedTargetStatus": "WATCHLIST_30_DPD"},
            {"LegacyBucket": "60", "ExpectedTargetStatus": "SUBSTANDARD_60_DPD"},
            {"LegacyBucket": "90", "ExpectedTargetStatus": "NPA_90_PLUS_DPD"}
        ])
        df_delinq.to_excel(writer, sheet_name="DelinquencyMapping", index=False)

        # Sheet 4: Channel Normalization Mapping
        df_channel = pd.DataFrame([
            {"LegacyChannel": "ATM", "ExpectedTargetChannel": "ATM"},
            {"LegacyChannel": "NET", "ExpectedTargetChannel": "ONLINE_BANKING"},
            {"LegacyChannel": "UPI", "ExpectedTargetChannel": "UPI"},
            {"LegacyChannel": "POS", "ExpectedTargetChannel": "POS"},
            {"LegacyChannel": "BRN", "ExpectedTargetChannel": "BRANCH"}
        ])
        df_channel.to_excel(writer, sheet_name="ChannelMapping", index=False)

    print(f"Generated: {file_path}")


def generate_json_schema():
    file_path = DATA_DIR / "expected_schema.json"
    schema = {
        "tables": {
            "DIM_BRANCH": {
                "primary_key": "BRANCH_SK",
                "natural_key": "BRANCH_CODE",
                "required_columns": ["BRANCH_SK", "BRANCH_CODE", "BRANCH_NAME", "REGION", "SWIFT_BIC"]
            },
            "DIM_CUSTOMER": {
                "primary_key": "CUSTOMER_SK",
                "natural_key": "CUSTOMER_ID",
                "required_columns": [
                    "CUSTOMER_SK", "CUSTOMER_ID", "FULL_NAME", "MASKED_TAX_ID",
                    "STATUS", "KYC_STATUS", "START_DATE", "IS_CURRENT"
                ]
            },
            "DIM_ACCOUNT": {
                "primary_key": "ACCOUNT_SK",
                "natural_key": "ACCOUNT_NUMBER",
                "required_columns": [
                    "ACCOUNT_SK", "ACCOUNT_NUMBER", "CUSTOMER_SK", "BRANCH_SK",
                    "ACCOUNT_TYPE", "CURRENCY_CODE", "CURRENT_BALANCE", "STATUS"
                ]
            },
            "FACT_TRANSACTIONS": {
                "primary_key": "TXN_SK",
                "natural_key": "TXN_ID",
                "required_columns": [
                    "TXN_SK", "TXN_ID", "ACCOUNT_SK", "TXN_TIMESTAMP",
                    "TXN_TYPE", "CHANNEL", "AMOUNT", "BALANCE_AFTER_TXN", "AML_FLAG"
                ]
            },
            "FACT_LOAN_PORTFOLIO": {
                "primary_key": "LOAN_SK",
                "natural_key": "LOAN_ID",
                "required_columns": [
                    "LOAN_SK", "LOAN_ID", "ACCOUNT_SK", "CUSTOMER_SK",
                    "PRINCIPAL_AMOUNT", "OUTSTANDING_BALANCE", "DELINQUENCY_STATUS"
                ]
            },
            "DAILY_BALANCE_SUMMARY": {
                "primary_key": "SUMMARY_SK",
                "required_columns": [
                    "SUMMARY_SK", "SNAPSHOT_DATE", "ACCOUNT_SK", "OPENING_BALANCE",
                    "TOTAL_DEBIT_AMOUNT", "TOTAL_CREDIT_AMOUNT", "CLOSING_BALANCE", "RECONCILIATION_STATUS"
                ]
            },
            "ETL_REJECTED_RECORDS": {
                "primary_key": "REJECT_ID",
                "required_columns": [
                    "REJECT_ID", "SOURCE_TABLE", "SOURCE_RECORD_KEY", "REJECT_REASON", "RAW_RECORD_PAYLOAD"
                ]
            }
        }
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)
    print(f"Generated: {file_path}")


def generate_csv_thresholds():
    file_path = DATA_DIR / "validation_thresholds.csv"
    data = [
        {"RULE_NAME": "AML_TRANSACTION_THRESHOLD", "THRESHOLD_VALUE": 10000.00, "DATA_TYPE": "FLOAT"},
        {"RULE_NAME": "MIN_CREDIT_SCORE", "THRESHOLD_VALUE": 300, "DATA_TYPE": "INT"},
        {"RULE_NAME": "MAX_CREDIT_SCORE", "THRESHOLD_VALUE": 850, "DATA_TYPE": "INT"},
        {"RULE_NAME": "DEFAULT_CURRENCY", "THRESHOLD_VALUE": "USD", "DATA_TYPE": "STRING"},
        {"RULE_NAME": "DEFAULT_SWIFT_BIC", "THRESHOLD_VALUE": "OCIBUS33XXX", "DATA_TYPE": "STRING"},
        {"RULE_NAME": "MAX_LOAN_TENURE_MONTHS", "THRESHOLD_VALUE": 360, "DATA_TYPE": "INT"}
    ]
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    print(f"Generated: {file_path}")


def main():
    generate_excel_mapping_rules()
    generate_json_schema()
    generate_csv_thresholds()
    print("All external validation test data files created successfully!")


if __name__ == "__main__":
    main()
