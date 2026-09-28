"""
Transformation and Business Rules Step Definitions (External Data-Driven)
"""

import re
from behave import given, when, then
from sqlalchemy import text
try:
    from utils.excel_reader import ExternalDataReader
except ImportError:
    from bdd_automation.utils.excel_reader import ExternalDataReader


@then('all records in "{table_name}" column "{column_name}" must match pattern "{pattern}"')
def step_assert_pattern_match(context, table_name, column_name, pattern):
    query = text(f"SELECT {column_name} FROM {table_name}")
    rows = context.target_conn.execute(query).fetchall()
    compiled_pattern = re.compile(pattern)
    violations = [str(r[0]) for r in rows if not compiled_pattern.match(str(r[0]))]
    assert len(violations) == 0, f"Found {len(violations)} non-matching records for pattern '{pattern}': {violations[:5]}"


@then('no raw unmasked Tax IDs or SSNs should exist in "{table_name}"')
def step_assert_no_raw_ssn(context, table_name):
    query = text(f"SELECT MASKED_TAX_ID FROM {table_name} WHERE MASKED_TAX_ID NOT LIKE '***-**-%'")
    unmasked = context.target_conn.execute(query).fetchall()
    assert len(unmasked) == 0, f"Found {len(unmasked)} unmasked PII records: {unmasked[:5]}"


@given('external mapping rules are loaded from Excel "{file_name}" sheet "{sheet_name}"')
def step_load_external_rules(context, file_name, sheet_name):
    context.excel_mappings = ExternalDataReader.read_excel_mapping(file_name, sheet_name)
    assert len(context.excel_mappings) > 0, f"Failed to load rules from sheet '{sheet_name}' in {file_name}"


@then('all legacy customer statuses must match expected target statuses from Excel')
def step_validate_status_mapping_from_excel(context):
    src_rows = context.source_conn.execute(text("SELECT CUST_ID, CUST_STATUS FROM LEGACY_CUSTOMERS")).fetchall()
    src_map = {r[0]: str(r[1]).strip() for r in src_rows}

    tgt_rows = context.target_conn.execute(text("SELECT CUSTOMER_ID, STATUS FROM DIM_CUSTOMER")).fetchall()
    tgt_map = {r[0]: str(r[1]).strip() for r in tgt_rows}

    mismatches = []
    for cust_id, target_status in tgt_map.items():
        legacy_code = src_map.get(cust_id)
        if legacy_code:
            expected = context.excel_mappings.get(legacy_code)
            if target_status != expected:
                mismatches.append(f"Cust {cust_id}: Legacy code '{legacy_code}' mapped to '{target_status}', expected '{expected}'")

    assert len(mismatches) == 0, f"Status translation errors found: {mismatches[:5]}"


@then('all legacy account types must match expected target types from Excel')
def step_validate_account_type_from_excel(context):
    src_rows = context.source_conn.execute(text("SELECT ACCT_NO, ACCT_TYPE FROM LEGACY_ACCOUNTS")).fetchall()
    src_map = {str(r[0]).strip(): str(r[1]).strip() for r in src_rows}

    tgt_rows = context.target_conn.execute(text("SELECT ACCOUNT_NUMBER, ACCOUNT_TYPE FROM DIM_ACCOUNT")).fetchall()
    tgt_map = {str(r[0]).strip(): str(r[1]).strip() for r in tgt_rows}

    mismatches = []
    for acct_no, target_type in tgt_map.items():
        legacy_type = src_map.get(acct_no)
        if legacy_type:
            expected = context.excel_mappings.get(legacy_type)
            if target_type != expected:
                mismatches.append(f"Acct {acct_no}: Legacy type '{legacy_type}' mapped to '{target_type}', expected '{expected}'")

    assert len(mismatches) == 0, f"Account type translation errors found: {mismatches[:5]}"


@then('all legacy loan delinquency buckets must match expected target statuses from Excel')
def step_validate_delinquency_from_excel(context):
    src_rows = context.source_conn.execute(text("SELECT LOAN_ID, DELINQUENCY_BUCKET FROM LEGACY_LOANS")).fetchall()
    src_map = {str(r[0]).strip(): str(r[1]).strip() for r in src_rows}

    tgt_rows = context.target_conn.execute(text("SELECT LOAN_ID, DELINQUENCY_STATUS FROM FACT_LOAN_PORTFOLIO")).fetchall()
    tgt_map = {str(r[0]).strip(): str(r[1]).strip() for r in tgt_rows}

    mismatches = []
    for loan_id, target_delinq in tgt_map.items():
        legacy_bucket = src_map.get(loan_id)
        if legacy_bucket:
            expected = context.excel_mappings.get(legacy_bucket)
            if target_delinq != expected:
                mismatches.append(f"Loan {loan_id}: Bucket '{legacy_bucket}' mapped to '{target_delinq}', expected '{expected}'")

    assert len(mismatches) == 0, f"Delinquency bucket translation errors found: {mismatches[:5]}"


@then('all transactions with amount greater than or equal to {threshold:f} must have AML_FLAG set to "{expected_flag}"')
def step_verify_aml_high_values(context, threshold, expected_flag):
    query = text(f"""
        SELECT COUNT(*) FROM FACT_TRANSACTIONS 
        WHERE AMOUNT >= {threshold} AND AML_FLAG != '{expected_flag}'
    """)
    violations = context.target_conn.execute(query).scalar()
    assert violations == 0, f"Found {violations} transactions >= ${threshold} without AML_FLAG = '{expected_flag}'!"


@then('no transaction with amount less than {threshold:f} should have AML_FLAG set to "{flag}"')
def step_verify_aml_low_values(context, threshold, flag):
    query = text(f"""
        SELECT COUNT(*) FROM FACT_TRANSACTIONS 
        WHERE AMOUNT < {threshold} AND AML_FLAG = '{flag}'
    """)
    false_positives = context.target_conn.execute(query).scalar()
    assert false_positives == 0, f"Found {false_positives} false-positive AML flags under ${threshold} threshold!"
