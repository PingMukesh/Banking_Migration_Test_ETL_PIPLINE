"""
Local SQLite Database Setup Script
Generates data/target_fallback.db and data/source_fallback.db
Enables 100% Docker-free and serverless local test execution.
"""
import sqlite3
from pathlib import Path
from datetime import datetime, date

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TARGET_DB_PATH = DATA_DIR / "target_fallback.db"
SOURCE_DB_PATH = DATA_DIR / "source_fallback.db"


def setup_target_database():
    print(f"Setting up target database at: {TARGET_DB_PATH}")
    conn = sqlite3.connect(TARGET_DB_PATH)
    cur = conn.cursor()

    # Drop existing tables
    tables = [
        "FACT_TRANSACTIONS",
        "FACT_LOAN_PORTFOLIO",
        "DAILY_BALANCE_SUMMARY",
        "ETL_REJECTED_RECORDS",
        "DIM_ACCOUNT",
        "DIM_CUSTOMER",
        "DIM_BRANCH",
    ]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")

    # 1. DIM_BRANCH
    cur.execute("""
    CREATE TABLE DIM_BRANCH (
        BRANCH_SK INTEGER PRIMARY KEY AUTOINCREMENT,
        BRANCH_CODE TEXT NOT NULL UNIQUE,
        BRANCH_NAME TEXT NOT NULL,
        REGION TEXT NOT NULL,
        POSTAL_CODE TEXT,
        SWIFT_BIC TEXT DEFAULT 'OCIBUS33XXX',
        CREATED_TIMESTAMP TEXT NOT NULL
    )
    """)

    # 2. DIM_CUSTOMER
    cur.execute("""
    CREATE TABLE DIM_CUSTOMER (
        CUSTOMER_SK INTEGER PRIMARY KEY AUTOINCREMENT,
        CUSTOMER_ID INTEGER NOT NULL,
        FULL_NAME TEXT NOT NULL,
        MASKED_TAX_ID TEXT NOT NULL,
        EMAIL TEXT,
        PHONE_STANDARDIZED TEXT,
        STATUS TEXT NOT NULL,
        KYC_STATUS TEXT NOT NULL,
        CREDIT_SCORE INTEGER,
        DATE_OF_BIRTH TEXT,
        CITY TEXT,
        STATE_PROV TEXT,
        START_DATE TEXT NOT NULL,
        END_DATE TEXT,
        IS_CURRENT TEXT DEFAULT 'Y' NOT NULL,
        DW_INSERT_DATE TEXT NOT NULL
    )
    """)

    # 3. DIM_ACCOUNT
    cur.execute("""
    CREATE TABLE DIM_ACCOUNT (
        ACCOUNT_SK INTEGER PRIMARY KEY AUTOINCREMENT,
        ACCOUNT_NUMBER TEXT NOT NULL UNIQUE,
        CUSTOMER_SK INTEGER NOT NULL,
        BRANCH_SK INTEGER NOT NULL,
        ACCOUNT_TYPE TEXT NOT NULL,
        CURRENCY_CODE TEXT DEFAULT 'USD' NOT NULL,
        CURRENT_BALANCE REAL NOT NULL,
        INTEREST_RATE REAL NOT NULL,
        STATUS TEXT NOT NULL,
        OPEN_DATE TEXT NOT NULL,
        OVERDRAFT_LIMIT REAL DEFAULT 0.0 NOT NULL,
        DW_INSERT_DATE TEXT NOT NULL,
        FOREIGN KEY (CUSTOMER_SK) REFERENCES DIM_CUSTOMER (CUSTOMER_SK),
        FOREIGN KEY (BRANCH_SK) REFERENCES DIM_BRANCH (BRANCH_SK)
    )
    """)

    # 4. FACT_TRANSACTIONS
    cur.execute("""
    CREATE TABLE FACT_TRANSACTIONS (
        TXN_SK INTEGER PRIMARY KEY AUTOINCREMENT,
        TXN_ID TEXT NOT NULL UNIQUE,
        ACCOUNT_SK INTEGER NOT NULL,
        TXN_TIMESTAMP TEXT NOT NULL,
        TXN_TYPE TEXT NOT NULL,
        CHANNEL TEXT NOT NULL,
        AMOUNT REAL NOT NULL,
        BALANCE_AFTER_TXN REAL NOT NULL,
        AML_FLAG TEXT DEFAULT 'N' NOT NULL,
        TXN_STATUS TEXT DEFAULT 'SUCCESS' NOT NULL,
        DW_INSERT_DATE TEXT NOT NULL,
        FOREIGN KEY (ACCOUNT_SK) REFERENCES DIM_ACCOUNT (ACCOUNT_SK)
    )
    """)

    # 5. FACT_LOAN_PORTFOLIO
    cur.execute("""
    CREATE TABLE FACT_LOAN_PORTFOLIO (
        LOAN_SK INTEGER PRIMARY KEY AUTOINCREMENT,
        LOAN_ID TEXT NOT NULL UNIQUE,
        ACCOUNT_SK INTEGER NOT NULL,
        CUSTOMER_SK INTEGER NOT NULL,
        LOAN_PRODUCT TEXT NOT NULL,
        PRINCIPAL_AMOUNT REAL NOT NULL,
        OUTSTANDING_BALANCE REAL NOT NULL,
        INTEREST_RATE REAL NOT NULL,
        MONTHLY_EMI REAL NOT NULL,
        TENURE_MONTHS INTEGER NOT NULL,
        DISBURSEMENT_DATE TEXT NOT NULL,
        DELINQUENCY_STATUS TEXT NOT NULL,
        DW_INSERT_DATE TEXT NOT NULL,
        FOREIGN KEY (ACCOUNT_SK) REFERENCES DIM_ACCOUNT (ACCOUNT_SK),
        FOREIGN KEY (CUSTOMER_SK) REFERENCES DIM_CUSTOMER (CUSTOMER_SK)
    )
    """)

    # 6. DAILY_BALANCE_SUMMARY
    cur.execute("""
    CREATE TABLE DAILY_BALANCE_SUMMARY (
        SUMMARY_SK INTEGER PRIMARY KEY AUTOINCREMENT,
        SNAPSHOT_DATE TEXT NOT NULL,
        ACCOUNT_SK INTEGER NOT NULL,
        OPENING_BALANCE REAL NOT NULL,
        TOTAL_DEBIT_AMOUNT REAL DEFAULT 0.0 NOT NULL,
        TOTAL_CREDIT_AMOUNT REAL DEFAULT 0.0 NOT NULL,
        CLOSING_BALANCE REAL NOT NULL,
        TOTAL_TXN_COUNT INTEGER DEFAULT 0 NOT NULL,
        RECONCILIATION_STATUS TEXT DEFAULT 'BALANCED' NOT NULL,
        DW_INSERT_DATE TEXT NOT NULL,
        FOREIGN KEY (ACCOUNT_SK) REFERENCES DIM_ACCOUNT (ACCOUNT_SK)
    )
    """)

    # 7. ETL_REJECTED_RECORDS
    cur.execute("""
    CREATE TABLE ETL_REJECTED_RECORDS (
        REJECT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        SOURCE_TABLE TEXT NOT NULL,
        SOURCE_RECORD_KEY TEXT NOT NULL,
        REJECT_REASON TEXT NOT NULL,
        RAW_RECORD_PAYLOAD TEXT NOT NULL,
        QUARANTINE_TIMESTAMP TEXT NOT NULL
    )
    """)

    # Seed Sample Data
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Branches
    branches = [
        ("BR001", "Downtown Main Branch", "North", "10001", "OCIBUS33XXX", now_str),
        ("BR002", "Westside Commercial", "West", "90001", "OCIBUS33XXX", now_str),
        ("BR003", "Metro Financial Hub", "East", "30301", "OCIBUS33XXX", now_str),
    ]
    cur.executemany(
        "INSERT INTO DIM_BRANCH (BRANCH_CODE, BRANCH_NAME, REGION, POSTAL_CODE, SWIFT_BIC, CREATED_TIMESTAMP) VALUES (?, ?, ?, ?, ?, ?)",
        branches,
    )

    # Customers
    customers = [
        (101, "Alice Morgan", "***-**-4581", "alice@example.com", "+1-555-0101", "ACTIVE", "VERIFIED", 740, "1985-04-12", "New York", "NY", "2020-01-15", None, "Y", now_str),
        (102, "Bob Vance", "***-**-9231", "bob@example.com", "+1-555-0102", "ACTIVE", "VERIFIED", 680, "1978-09-23", "Scranton", "PA", "2019-06-10", None, "Y", now_str),
        (103, "Charlie Davis", "***-**-1192", "charlie@example.com", "+1-555-0103", "ACTIVE", "VERIFIED", 810, "1992-11-05", "Austin", "TX", "2021-03-20", None, "Y", now_str),
    ]
    cur.executemany(
        "INSERT INTO DIM_CUSTOMER (CUSTOMER_ID, FULL_NAME, MASKED_TAX_ID, EMAIL, PHONE_STANDARDIZED, STATUS, KYC_STATUS, CREDIT_SCORE, DATE_OF_BIRTH, CITY, STATE_PROV, START_DATE, END_DATE, IS_CURRENT, DW_INSERT_DATE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        customers,
    )

    # Accounts
    accounts = [
        ("ACC10001", 1, 1, "SAVINGS", "USD", 15400.50, 3.25, "ACTIVE", "2020-01-15", 0.0, now_str),
        ("ACC10002", 1, 1, "CHECKING", "USD", 4200.00, 0.50, "ACTIVE", "2020-01-15", 500.0, now_str),
        ("ACC10003", 2, 2, "CHECKING", "USD", 8900.25, 0.50, "ACTIVE", "2019-06-10", 1000.0, now_str),
        ("ACC10004", 3, 3, "MONEY_MARKET", "USD", 35000.00, 4.10, "ACTIVE", "2021-03-20", 0.0, now_str),
    ]
    cur.executemany(
        "INSERT INTO DIM_ACCOUNT (ACCOUNT_NUMBER, CUSTOMER_SK, BRANCH_SK, ACCOUNT_TYPE, CURRENCY_CODE, CURRENT_BALANCE, INTEREST_RATE, STATUS, OPEN_DATE, OVERDRAFT_LIMIT, DW_INSERT_DATE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        accounts,
    )

    # Fact Loan Portfolio
    loans = [
        ("LN9001", 1, 1, "MORTGAGE", 250000.00, 210000.00, 4.5, 1266.71, 360, "2020-02-01", "CURRENT", now_str),
        ("LN9002", 3, 2, "AUTO_LOAN", 35000.00, 18500.00, 5.2, 663.85, 60, "2021-05-15", "CURRENT", now_str),
    ]
    cur.executemany(
        "INSERT INTO FACT_LOAN_PORTFOLIO (LOAN_ID, ACCOUNT_SK, CUSTOMER_SK, LOAN_PRODUCT, PRINCIPAL_AMOUNT, OUTSTANDING_BALANCE, INTEREST_RATE, MONTHLY_EMI, TENURE_MONTHS, DISBURSEMENT_DATE, DELINQUENCY_STATUS, DW_INSERT_DATE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        loans,
    )

    # Daily Balance Summary
    summaries = [
        (date.today().strftime("%Y-%m-%d"), 1, 15000.00, 100.0, 500.50, 15400.50, 2, "BALANCED", now_str),
        (date.today().strftime("%Y-%m-%d"), 2, 4000.00, 50.0, 250.00, 4200.00, 3, "BALANCED", now_str),
    ]
    cur.executemany(
        "INSERT INTO DAILY_BALANCE_SUMMARY (SNAPSHOT_DATE, ACCOUNT_SK, OPENING_BALANCE, TOTAL_DEBIT_AMOUNT, TOTAL_CREDIT_AMOUNT, CLOSING_BALANCE, TOTAL_TXN_COUNT, RECONCILIATION_STATUS, DW_INSERT_DATE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        summaries,
    )

    # Rejected Records
    rejects = [
        ("RAW_CUSTOMERS", "CUST_9999", "INVALID_TAX_ID", '{"id": 9999, "tax_id": "INVALID"}', now_str)
    ]
    cur.executemany(
        "INSERT INTO ETL_REJECTED_RECORDS (SOURCE_TABLE, SOURCE_RECORD_KEY, REJECT_REASON, RAW_RECORD_PAYLOAD, QUARANTINE_TIMESTAMP) VALUES (?, ?, ?, ?, ?)",
        rejects,
    )

    conn.commit()
    conn.close()
    print("Target SQLite DB created and seeded successfully.")


def setup_source_database():
    print(f"Setting up source database at: {SOURCE_DB_PATH}")
    conn = sqlite3.connect(SOURCE_DB_PATH)
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS source_customers")
    cur.execute("""
    CREATE TABLE source_customers (
        cust_id INTEGER PRIMARY KEY,
        name TEXT,
        tax_id TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    cur.execute("DROP TABLE IF EXISTS source_accounts")
    cur.execute("""
    CREATE TABLE source_accounts (
        acct_no TEXT PRIMARY KEY,
        cust_id INTEGER,
        type TEXT,
        balance REAL,
        status TEXT
    )
    """)

    cur.execute("INSERT INTO source_customers VALUES (101, 'Alice Morgan', '999-11-4581', 'A', '2020-01-15')")
    cur.execute("INSERT INTO source_customers VALUES (102, 'Bob Vance', '999-22-9231', 'A', '2019-06-10')")
    cur.execute("INSERT INTO source_accounts VALUES ('ACC10001', 101, 'SAVINGS', 15400.50, 'OPEN')")
    cur.execute("INSERT INTO source_accounts VALUES ('ACC10002', 101, 'CHECKING', 4200.00, 'OPEN')")

    conn.commit()
    conn.close()
    print("Source SQLite DB created and seeded successfully.")


if __name__ == "__main__":
    setup_target_database()
    setup_source_database()
    print("\nDatabase initialization complete! You can now run tests with: python runner.py")
