"""
Common Step Definitions for BDD Framework
"""

from behave import given, when, then
from sqlalchemy import text


@given('the ETL migration has completed successfully')
@given('ETL Migration has completed')
def step_migration_ready(context):
    # Verify target tables have records
    count = context.target_conn.execute(text("SELECT COUNT(*) FROM DIM_CUSTOMER")).scalar()
    assert count > 0, "Target tables are empty. Please run ETL migration first."


@given('target table "{table_name}" is loaded')
@then('target table "{table_name}" is loaded')
def step_target_table_loaded(context, table_name):
    query = text(f"SELECT COUNT(*) FROM {table_name}")
    count = context.target_conn.execute(query).scalar()
    assert count > 0, f"Target table '{table_name}' is empty!"


@then('table "{table_name}" must have at least {min_count:d} records')
def step_table_min_count(context, table_name, min_count):
    query = text(f"SELECT COUNT(*) FROM {table_name}")
    count = context.target_conn.execute(query).scalar()
    assert count >= min_count, f"Table '{table_name}' has only {count} rows, expected at least {min_count}."


@then('table "{table_name}" must not contain any duplicate rows by natural key "{key_column}"')
def step_no_duplicates_by_key(context, table_name, key_column):
    query = text(f"""
        SELECT {key_column}, COUNT(*) 
        FROM {table_name} 
        GROUP BY {key_column} 
        HAVING COUNT(*) > 1
    """)
    duplicates = context.target_conn.execute(query).fetchall()
    assert len(duplicates) == 0, f"Duplicate natural keys found in '{table_name}': {duplicates[:5]}"
