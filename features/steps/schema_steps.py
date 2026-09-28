"""
Schema Validation Step Definitions
"""

from behave import when, then
from sqlalchemy import text, inspect
try:
    from utils.excel_reader import ExternalDataReader
except ImportError:
    from bdd_automation.utils.excel_reader import ExternalDataReader


@when('I inspect the target database tables')
@when('inspect the tgt DB tables')
def step_inspect_target_tables(context):
    if context.target_engine.dialect.name == "oracle":
        res = context.target_conn.execute(text("SELECT table_name FROM user_tables")).fetchall()
        context.actual_tables = [r[0].upper() for r in res]
        context.act_tables = context.actual_tables
    else:
        inspector = inspect(context.target_engine)
        context.actual_tables = [t.upper() for t in inspector.get_table_names()]
        context.act_tables = context.actual_tables


@then('all tables defined in external schema "{schema_file}" must exist')
@then('all tables defined in the external Schema "{schema_file}" must exist')
def step_verify_all_tables_exist(context, schema_file):
    schema = ExternalDataReader.read_json_schema("expected_schema.json" if schema_file.lower() == "input" else schema_file)
    expected_tables = list(schema["tables"].keys())
    missing_tables = []
    act_tables = getattr(context, "actual_tables", getattr(context, "act_tables", []))
    for tbl in expected_tables:
        if tbl.upper() not in act_tables:
            missing_tables.append(tbl)
    assert len(missing_tables) == 0, f"Missing target tables in schema: {missing_tables}"


@then('table "{table_name}" must contain all required columns defined in "{schema_file}"')
@then('table "{table_name}" must contain all required columns defined in "{schema_file}".')
def step_verify_table_columns(context, table_name, schema_file):
    schema = ExternalDataReader.read_json_schema("expected_schema.json" if schema_file.lower() == "input" else schema_file)
    expected_cols = [c.upper() for c in schema["tables"][table_name.upper()]["required_columns"]]

    inspector = inspect(context.target_engine)
    cols = [c["name"].upper() for c in inspector.get_columns(table_name)]
    if not cols:
        cols = [c["name"].upper() for c in inspector.get_columns(table_name.lower())]

    missing_cols = [c for c in expected_cols if c not in cols]
    assert len(missing_cols) == 0, f"Table '{table_name}' is missing expected columns: {missing_cols}"


@then('mandatory columns in "{table_name}" must not have any NULL values: "{columns}"')
def step_mandatory_columns_not_null(context, table_name, columns):
    col_list = [c.strip() for c in columns.split(",")]
    conditions = " OR ".join([f"{col} IS NULL" for col in col_list])
    query = text(f"SELECT COUNT(*) FROM {table_name} WHERE {conditions}")
    null_count = context.target_conn.execute(query).scalar()
    assert null_count == 0, f"Found {null_count} rows with NULL in mandatory columns {col_list} in table '{table_name}'!"
