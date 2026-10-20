from behave import given, when, then
from sqlalchemy import text, inspect

@when('I Verify the arithmetic Balance in "{table_name}"')
def step_verify_arithmetic_balance(context, table_name):
    query = text(f"""Select opening_balance,
        total_debit_amount,total_credit_amount,closing_balance,
        account_sk,snapshot_date
        from {table_name}""")

    context.account_balances = context.target_conn.execute(query).fetchall()

@then("the formula opening_balance + credit - debit = Closing_balance must true for all Accounts")
def step_verify_balance_formula(context):

    mismatches = []
    for row in context.account_balances:
        open_b = float(row[0])
        dr = float(row[1])
        cr = float(row[2])
        cb = float(row[3])
        calculated_cb = round(open_b + cr - dr, 2)

        if abs(calculated_cb - cb) > 0.05:
            mismatches.append(
                {
                    "account_sk": row[4],
                    "snapshot_date": row[5],
                    "opening_balance": open_b,
                    "total_debit_amount": dr,
                    "total_credit_amount": cr,
                    "closing_balance": cb,
                    "calculated_closing_balance": calculated_cb,
                }
            )

    assert len(mismatches) == 0, f"Balance formula mismatches found: {mismatches}"   



