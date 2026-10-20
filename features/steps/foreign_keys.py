from behave import given,when, then
from sqlalchemy import table, text


@given('target table "{table_name}" is loaded')
def step_target_table_loaded(context, table_name):
    result = context.target_conn.execute(
        text(f"SELECT COUNT(*) FROM {table_name}")
    ).scalar_one()
    assert result > 0, f"Target table {table_name} is empty."

@then('target table "{table_name}" is loaded')
def step_target_table_loaded(context, table_name):
    result = context.target_conn.execute(
        text(f"SELECT COUNT(*) FROM {table_name}")
    ).scalar_one()
    assert result > 0, f"Target table {table_name} is empty."

@then('table "{table_name}" must have at least 230 records')
def step_table_must_have_records(context, table_name):
    result = context.target_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
    assert result >= 230, f"Target table {table_name} does not have atleast 230 records."


@then('table "{table_name}" must have at least 1400 records')
def step_table_must_have_records(context, table_name):
    result = context.target_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
    assert result>=1400, f"Target table {table_name} does not have at least 1400 records"

@then('table "{table_name}" must have at least 70 records')
def step_table_must_have_records(context,table_name):
    result = context.target_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
    assert result>=70, f"Target table {table_name} does not have atleast 70 records"


@then('table "{table_name}" must not contain any duplicate rows by natural key "{natural_key}"')
def step_table_must_not_have_duplicates(context, table_name, natural_key):
    result = context.target_conn.execute(text(f"SELECT COUNT({natural_key}) - COUNT(DISTINCT {natural_key}) FROM {table_name}")).scalar_one()
    assert result == 0, f"Target table {table_name} contains duplicate rows by natural key {natural_key}."
