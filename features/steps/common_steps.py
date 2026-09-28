from behave import given, when, then
from sqlalchemy import text


@given('ETL Migration has completed')
def step_migration_completed(context):

    count = context.target_conn.execute(
        text("SELECT count(*) FROM DIM_CUSTOMER")
    ).scalar_one()
    assert count > 0, "ETL Migration has not completed. DIM_CUSTOMER table is empty."

