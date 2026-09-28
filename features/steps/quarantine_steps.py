"""
Dirty Data Quarantine Step Definitions
"""

from behave import when, then
from sqlalchemy import text


@when('I inspect the error quarantine table "{table_name}"')
def step_inspect_quarantine(context, table_name):
    query = text(f"SELECT SOURCE_TABLE, SOURCE_RECORD_KEY, REJECT_REASON FROM {table_name}")
    context.quarantine_rows = context.target_conn.execute(query).fetchall()


@then('dirty customer records with invalid email formats must be present in quarantine')
def step_assert_quarantined_emails(context):
    email_rejects = [
        r for r in context.quarantine_rows 
        if r[0] == "LEGACY_CUSTOMERS" and "INVALID_EMAIL_FORMAT" in r[2]
    ]
    assert len(email_rejects) >= 2, f"Expected at least 2 invalid email rejects, found {len(email_rejects)}"


@then('corrupted transaction status records must be present in quarantine')
def step_assert_quarantined_txns(context):
    txn_rejects = [
        r for r in context.quarantine_rows 
        if r[0] == "LEGACY_TRANSACTIONS" and "CORRUPTED_TXN_STATUS" in r[2]
    ]
    assert len(txn_rejects) >= 1, f"Expected corrupted transaction rejects, found {len(txn_rejects)}"


@then('no quarantined record key from "{source_table}" should be present in target table "{target_table}" column "{target_key_col}"')
def step_assert_quarantined_not_in_target(context, source_table, target_table, target_key_col):
    keys_query = text(f"""
        SELECT SOURCE_RECORD_KEY 
        FROM ETL_REJECTED_RECORDS 
        WHERE SOURCE_TABLE = '{source_table}'
    """)
    quarantined_raw_keys = context.target_conn.execute(keys_query).fetchall()
    
    extracted_keys = []
    for k in quarantined_raw_keys:
        raw = str(k[0])
        # If formatted as CUST_ID:1013 or TXN_ID:TXN-20240003
        if ":" in raw:
            extracted_keys.append(raw.split(":")[1].strip())
        else:
            extracted_keys.append(raw.strip())

    if not extracted_keys:
        return

    check_query = text(f"SELECT {target_key_col} FROM {target_table}")
    target_keys = [str(r[0]).strip() for r in context.target_conn.execute(check_query).fetchall()]

    leaked = set(extracted_keys).intersection(set(target_keys))
    assert len(leaked) == 0, f"Critical Data Leakage! Quarantined keys found in clean target table '{target_table}': {leaked}"
