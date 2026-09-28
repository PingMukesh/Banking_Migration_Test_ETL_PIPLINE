"""
Reconciliation and Row Count Step Definitions
"""

from behave import when, then
from sqlalchemy import text


@when('I reconcile row counts between source "{src_table}" and target "{tgt_table}"')
def step_reconcile_counts(context, src_table, tgt_table):
    src_cnt = context.source_conn.execute(text(f"SELECT COUNT(*) FROM {src_table}")).scalar()
    tgt_cnt = context.target_conn.execute(text(f"SELECT COUNT(*) FROM {tgt_table}")).scalar()
    context.src_count = src_cnt
    context.tgt_count = tgt_cnt
    context.last_comparison = (src_table, tgt_table)


@then('the row counts must match exactly')
def step_assert_row_counts_match(context):
    src_tbl, tgt_tbl = context.last_comparison
    assert context.src_count == context.tgt_count, (
        f"Row count mismatch! Source '{src_tbl}': {context.src_count}, Target '{tgt_tbl}': {context.tgt_count}"
    )


@when('I evaluate the customer reconciliation equation')
def step_eval_customer_equation(context):
    context.source_cust = context.source_conn.execute(text("SELECT COUNT(*) FROM LEGACY_CUSTOMERS")).scalar()
    context.target_cust = context.target_conn.execute(text("SELECT COUNT(*) FROM DIM_CUSTOMER")).scalar()
    context.quarantine_cust = context.target_conn.execute(text(
        "SELECT COUNT(*) FROM ETL_REJECTED_RECORDS WHERE SOURCE_TABLE = 'LEGACY_CUSTOMERS'"
    )).scalar()


@then('source customer rows must equal target DIM_CUSTOMER rows plus quarantined rows')
def step_assert_customer_equation(context):
    expected_source = context.target_cust + context.quarantine_cust
    assert context.source_cust == expected_source, (
        f"Reconciliation Equation Failed! Source Customers: {context.source_cust} != "
        f"Target ({context.target_cust}) + Quarantine ({context.quarantine_cust}) = {expected_source}"
    )


@when('I evaluate the transaction reconciliation equation')
def step_eval_txn_equation(context):
    context.src_txns = context.source_conn.execute(text("SELECT COUNT(*) FROM LEGACY_TRANSACTIONS")).scalar()
    context.tgt_txns = context.target_conn.execute(text("SELECT COUNT(*) FROM FACT_TRANSACTIONS WHERE TXN_ID NOT LIKE 'TXN-KAFKA-%'")).scalar()
    context.quar_txns = context.target_conn.execute(text(
        "SELECT COUNT(*) FROM ETL_REJECTED_RECORDS WHERE SOURCE_TABLE = 'LEGACY_TRANSACTIONS'"
    )).scalar()
    # Orphan transactions (accounts tied to quarantined customers 1013, 1027)
    context.orphan_txns = context.source_conn.execute(text("""
        SELECT COUNT(*) FROM LEGACY_TRANSACTIONS 
        WHERE ACCT_NO IN (
            SELECT ACCT_NO FROM LEGACY_ACCOUNTS WHERE CUST_ID IN (1013, 1027)
        ) AND STATUS_CODE = 'SUCCESS'
    """)).scalar()


@then('source transaction rows must equal target FACT_TRANSACTIONS rows plus quarantined rows plus orphan rows')
def step_assert_txn_equation(context):
    reconciled_sum = context.tgt_txns + context.quar_txns + context.orphan_txns
    assert context.src_txns == reconciled_sum, (
        f"Transaction Reconciliation Equation Failed! Source ({context.src_txns}) != "
        f"Target ({context.tgt_txns}) + Quarantined ({context.quar_txns}) + Excluded Orphans ({context.orphan_txns}) = {reconciled_sum}"
    )
