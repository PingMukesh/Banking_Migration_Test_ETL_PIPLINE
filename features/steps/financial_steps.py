"""
Financial Balance and Volume Reconciliation Step Definitions
"""

from behave import when, then
from sqlalchemy import text


@when('I verify the arithmetic balance rollup in "{table_name}"')
def step_fetch_balance_summaries(context, table_name):
    query = text(f"""
        SELECT 
            OPENING_BALANCE, 
            TOTAL_DEBIT_AMOUNT, 
            TOTAL_CREDIT_AMOUNT, 
            CLOSING_BALANCE, 
            ACCOUNT_SK, 
            SNAPSHOT_DATE 
        FROM {table_name}
    """)
    context.balance_rows = context.target_conn.execute(query).fetchall()


@then('the equation OPENING_BALANCE + CREDIT - DEBIT = CLOSING_BALANCE must hold true for all accounts')
def step_assert_balance_equation(context):
    mismatches = []
    for row in context.balance_rows:
        open_b = float(row[0])
        dr = float(row[1])
        cr = float(row[2])
        close_b = float(row[3])
        calculated_close = round(open_b + cr - dr, 2)
        if abs(calculated_close - close_b) > 0.05:
            mismatches.append(f"Acct {row[4]} on {row[5]}: Expected {calculated_close}, Got {close_b}")

    assert len(mismatches) == 0, f"Balance arithmetic discrepancies found: {mismatches[:5]}"


@when('I reconcile total transaction financial volume between source and target')
def step_fetch_total_volumes(context):
    src_query = text("""
        SELECT ROUND(SUM(AMOUNT), 2)
        FROM LEGACY_TRANSACTIONS
        WHERE STATUS_CODE = 'SUCCESS'
          AND ACCT_NO IN (SELECT ACCT_NO FROM LEGACY_ACCOUNTS WHERE CUST_ID NOT IN (1013, 1027))
    """)
    tgt_query = text("SELECT ROUND(SUM(AMOUNT), 2) FROM FACT_TRANSACTIONS WHERE TXN_ID NOT LIKE 'TXN-KAFKA-%'")
    context.src_vol = float(context.source_conn.execute(src_query).scalar())
    context.tgt_vol = float(context.target_conn.execute(tgt_query).scalar())


@then('the difference between source and target transaction volumes must be within tolerance {tolerance:f}')
def step_assert_volume_tolerance(context, tolerance):
    diff = round(abs(context.src_vol - context.tgt_vol), 2)
    assert diff <= tolerance, (
        f"Financial Volume Discrepancy! Source: ${context.src_vol}, Target: ${context.tgt_vol}, Diff: ${diff} > tolerance ${tolerance}"
    )


@when('I reconcile total debit and credit amounts individually')
def step_fetch_dr_cr_totals(context):
    context.src_dr = float(context.source_conn.execute(text("""
        SELECT ROUND(SUM(AMOUNT), 2) FROM LEGACY_TRANSACTIONS 
        WHERE TXN_TYPE = 'DR' AND STATUS_CODE = 'SUCCESS'
          AND ACCT_NO IN (SELECT ACCT_NO FROM LEGACY_ACCOUNTS WHERE CUST_ID NOT IN (1013, 1027))
    """)).scalar())

    context.tgt_dr = float(context.target_conn.execute(text("""
        SELECT ROUND(SUM(AMOUNT), 2) FROM FACT_TRANSACTIONS WHERE TXN_TYPE = 'DEBIT' AND TXN_ID NOT LIKE 'TXN-KAFKA-%'
    """)).scalar())

    context.src_cr = float(context.source_conn.execute(text("""
        SELECT ROUND(SUM(AMOUNT), 2) FROM LEGACY_TRANSACTIONS 
        WHERE TXN_TYPE = 'CR' AND STATUS_CODE = 'SUCCESS'
          AND ACCT_NO IN (SELECT ACCT_NO FROM LEGACY_ACCOUNTS WHERE CUST_ID NOT IN (1013, 1027))
    """)).scalar())

    context.tgt_cr = float(context.target_conn.execute(text("""
        SELECT ROUND(SUM(AMOUNT), 2) FROM FACT_TRANSACTIONS WHERE TXN_TYPE = 'CREDIT' AND TXN_ID NOT LIKE 'TXN-KAFKA-%'
    """)).scalar())


@then('source total debits must match target total debits within tolerance {tolerance:f}')
def step_assert_dr_match(context, tolerance):
    diff = round(abs(context.src_dr - context.tgt_dr), 2)
    assert diff <= tolerance, f"Debit Sum Discrepancy! Source: {context.src_dr}, Target: {context.tgt_dr}, Diff: {diff}"


@then('source total credits must match target total credits within tolerance {tolerance:f}')
def step_assert_cr_match(context, tolerance):
    diff = round(abs(context.src_cr - context.tgt_cr), 2)
    assert diff <= tolerance, f"Credit Sum Discrepancy! Source: {context.src_cr}, Target: {context.tgt_cr}, Diff: {diff}"
