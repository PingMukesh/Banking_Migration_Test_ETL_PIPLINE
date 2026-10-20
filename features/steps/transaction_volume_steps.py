from decimal import Decimal

from behave import when, then
from sqlalchemy import text


def get_source_total_volume(context):
    result = context.source_conn.execute(
        text("SELECT COALESCE(SUM(amount), 0) FROM legacy_transactions")
    ).scalar_one()
    return Decimal(str(result))


def get_target_total_volume(context):
    result = context.target_conn.execute(
        text("SELECT COALESCE(SUM(AMOUNT), 0) FROM FACT_TRANSACTIONS")
    ).scalar_one()
    return Decimal(str(result))


def get_transaction_total(connection, table_name, type_column, status_column, transaction_type):
    result = connection.execute(
        text(
            f"SELECT COALESCE(SUM(amount), 0) FROM {table_name} "
            f"WHERE {type_column} = :transaction_type AND {status_column} = 'SUCCESS'"
        ),
        {"transaction_type": transaction_type},
    ).scalar_one()
    return Decimal(str(result))

@when('I reconcile total transaction financial volume between source and target')
def step_reconcile_volumes(context):
    context.source_volume = get_source_total_volume(context)
    context.target_volume = get_target_total_volume(context)

@then('the difference between source and target transaction volumes must be within tolerance {tolerance:f}')
def step_validate_tolerance(context, tolerance):
    actual_difference = abs(context.source_volume - context.target_volume)

    allowed_difference = Decimal(str(tolerance))

    assert actual_difference <= allowed_difference, \
        f"Reconciliation failed! Source: {context.source_volume}, Target: {context.target_volume}. " \
        f"Diff: {actual_difference} exceeds tolerance {tolerance}."


@when ('I reconcile total debit and credit amounts individually')
def step_reconcile_debit_credit(context):
    context.source_debits = get_transaction_total(
        context.source_conn, "legacy_transactions", "txn_type", "status", "DEBIT"
    )
    context.target_debits = get_transaction_total(
        context.target_conn, "FACT_TRANSACTIONS", "txn_type", "txn_status", "DEBIT"
    )
    context.source_credits = get_transaction_total(
        context.source_conn, "legacy_transactions", "txn_type", "status", "CREDIT"
    )
    context.target_credits = get_transaction_total(
        context.target_conn, "FACT_TRANSACTIONS", "txn_type", "txn_status", "CREDIT"
    )

@then('source total debits must match target total debits within tolerance {tolerance:f}')
def step_validate_debit_tolerance(context, tolerance):
    actual_difference = abs(context.source_debits - context.target_debits)
    allowed_difference = Decimal(str(tolerance))
    assert actual_difference <= allowed_difference, \
            f"Reconciliation failed! Source: {context.source_debits}, Target: {context.target_debits}. " \
            f"Diff: {actual_difference} exceeds tolerance {tolerance}."

@then('source total credits must match target total credits within tolerance {tolerance:f}')
def step_validate_credit_tolerance(context, tolerance):
    actual_difference = abs(context.source_credits - context.target_credits)
    allowed_difference = Decimal(str(tolerance))
    assert actual_difference <= allowed_difference, \
        f"Reconciliation failed! Source: {context.source_credits}, Target: {context.target_credits}. " \
        f"Diff: {actual_difference} exceeds tolerance {tolerance}."

@when('I check for AML flagged transactions in "{table_name}"')
def step_check_aml_flagged_transactions(context, table_name):
    context.unflagged_high_value_transactions = context.target_conn.execute(
        text(
            f"SELECT COUNT(*) FROM {table_name} "
            "WHERE AMOUNT > :threshold AND UPPER(AML_FLAG) <> 'Y'"
        ),
        {"threshold": 10000},
    ).scalar_one()


@then('all transactions with amount greater than 10000 must be flagged as AML')
def step_validate_aml_flags(context):
    assert context.unflagged_high_value_transactions == 0, (
        f"Found {context.unflagged_high_value_transactions} high-value transactions "
        "without an AML flag"
    )

