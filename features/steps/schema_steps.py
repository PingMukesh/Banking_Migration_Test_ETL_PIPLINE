from behave import when, then
from sqlalchemy import text, inspect
from utils.excel_reader import ExternalDataReader


@when('inspect the tgt DB tables')
def step_inspect_tgt_tables(context):
    context.act_tables = []
    if context.target_engine.dialect.name == "oracle":
        res = context.target_conn.execute(text("select table_name from user_tables")).fetchall()
        context.act_tables = [r[0].upper() for r in res]
    else:
        inspector = inspect(context.target_engine)
        for t in inspector.get_table_names():
            context.act_tables.append(t.upper())


@then('all tables defined in the external Schema "{Schema_file}" must exist')
def step_verify_all_tables_exist(context, Schema_file):
    schema = context.expected_schema
    expected_tables = list(schema["tables"].keys())
    missing_tables = []

    for table in expected_tables:
        if table.upper() not in context.act_tables:
            missing_tables.append(table)
    assert len(missing_tables) == 0, f"Missing tables in target DB: {missing_tables}"


@then('table "{table_name}" must contain all required columns defined in "{Schema_file}".')
def step_verify_required_columns(context, table_name, Schema_file):
    table_schema = context.expected_schema["tables"].get(table_name.upper())
    assert table_schema is not None, f"Table is not defined in schema: {table_name}"

    actual_columns = {
        column["name"].upper()
        for column in inspect(context.target_engine).get_columns(table_name)
    }
    required_columns = {
        column.upper() for column in table_schema["required_columns"]
    }
    missing_columns = sorted(required_columns - actual_columns)
    assert not missing_columns, (
        f"Missing required columns in {table_name}: {missing_columns}"
    )

