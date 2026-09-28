# Banking ETL Migration Test Pipeline - Localhost Setup & Test Execution Guide

This document provides complete instructions for setting up the test data and executing the ETL validation test suite on **localhost without requiring any Docker containers**.

---

## 1. Architecture & Overview

The **Banking ETL Migration Test Pipeline** is a BDD (Behavior-Driven Development) test automation framework built using:
- **Behave** (Gherkin BDD syntax)
- **SQLAlchemy & PyMySQL / OracleDB** (Database abstraction and connectivity)
- **SQLite** (Zero-dependency local database engine for fast, serverless local testing)
- **Pandas & OpenPyXL** (Data comparison and validation against external schemas and rules)
- **Rich** (Terminal output and formatted test runner reports)

```
   ┌────────────────────────────────────────────────────────────┐
   │                       BDD Test Suite                       │
   │               (features/Schema_validation.feature)         │
   └─────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
   ┌────────────────────────────────────────────────────────────┐
   │                    runner.py (CLI / Behave)                │
   └─────────────────────────────┬──────────────────────────────┘
                                 │
                                 ▼
   ┌────────────────────────────────────────────────────────────┐
   │             DBManager (config/db_manager.py)               │
   │  Attempts connection to Local Oracle / MySQL               │
   │  Auto-falls back to local SQLite if native DB is absent    │
   └───────────────┬────────────────────────────┬───────────────┘
                   │ (Native Localhost DB)      │ (Zero-install Fallback)
                   ▼                            ▼
       ┌───────────────────────┐   ┌───────────────────────────┐
       │ Localhost Oracle/MySQL│   │ Local SQLite Databases    │
       │ (Port 1521 / 3306)    │   │ (data/*.db - 100% local)  │
       │ (No Docker Needed)    │   │ (No Server / Docker Req)  │
       └───────────────────────┘   └───────────────────────────┘
```

---

## 2. Prerequisites

Everything runs directly on your local machine:
- **Python**: Version 3.10, 3.11, or 3.12 installed on your machine.
- **Git**: Installed for version control.
- **No Docker**: Docker Desktop or Docker containers are **NOT** required.

---

## 3. Environment Setup

### Step 3.1: Clone the Repository
```bash
git clone https://github.com/PingMukesh/Banking_Migration_Test_ETL_PIPLINE.git
cd Banking_Migration_Test_ETL_PIPLINE
```

### Step 3.2: Create and Activate a Virtual Environment

**On Windows (PowerShell / CMD):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3.3: Install Dependencies
```bash
pip install -r req.txt
```

Verified packages installed from `req.txt`:
- `behave >= 1.2.0`
- `pandas >= 2.0.0`
- `openpyxl >= 3.0.0`
- `sqlalchemy >= 2.0.0`
- `pymysql >= 1.0.0`
- `oracledb >= 2.0.0`
- `rich >= 13.0.0`

---

## 4. Data Setup Options (100% Localhost - No Docker)

Choose one of the two local setup options below:

### Option A: Zero-Dependency Local SQLite (Recommended & Instant)

This option requires **zero database installation** and works immediately out-of-the-box. The framework includes an automated seeder script that provisions local SQLite databases inside the `data/` directory.

#### Run the local SQLite setup script:
```bash
python scripts/setup_local_sqlite.py
```

This creates and seeds:
1. `data/target_fallback.db`:
   - `DIM_BRANCH` (Branches dimension table)
   - `DIM_CUSTOMER` (Customer dimension table)
   - `DIM_ACCOUNT` (Account dimension table)
   - `FACT_TRANSACTIONS` (Transactions fact table)
   - `FACT_LOAN_PORTFOLIO` (Loan portfolio fact table)
   - `DAILY_BALANCE_SUMMARY` (Daily balance summary table)
   - `ETL_REJECTED_RECORDS` (Quarantine / rejection table)
2. `data/source_fallback.db`:
   - Legacy source database tables (`source_customers`, `source_accounts`).

> **Note**: Whenever the test suite runs and cannot connect to an external Oracle/MySQL server, it **automatically falls back to SQLite** seamlessly.

---

### Option B: Native Localhost Oracle Setup (Optional)

If you have a native Oracle Database (such as Oracle 23ai Free or Oracle 21c XE) installed directly on your Windows/Linux machine:

1. Open **SQL*Plus** or your preferred SQL editor on localhost:
   ```bash
   sqlplus system/YourPassword@localhost:1521/FREEPDB1
   ```
2. Execute the provided DDL schema script:
   ```sql
   @scripts/oracle_schema_setup.sql
   ```
3. Update `config/config.ini` with your local Oracle credentials:
   ```ini
   [DATABASE.TARGET]
   host = localhost
   port = 1521
   service_name = FREEPDB1
   username = system
   password = YourPassword
   driver = oracle+oracledb
   fallback_sqlite = data/target_fallback.db
   ```

---

### Option C: Native Localhost MySQL Setup (Optional)

If you have a native MySQL Community Server installed directly on your localhost:

1. Connect to MySQL via terminal or MySQL Workbench:
   ```bash
   mysql -u root -p < scripts/mysql_schema_setup.sql
   ```
   Or inside the MySQL CLI:
   ```sql
   source scripts/mysql_schema_setup.sql;
   ```
2. Update `config/config.ini` with your local MySQL password:
   ```ini
   [DATABASE.SOURCE]
   host = localhost
   port = 3306
   database = legacy_banking
   username = root
   password = YourPassword
   driver = mysql+pymysql
   fallback_sqlite = data/source_fallback.db
   ```

---

## 5. Configuration Settings

The configuration file is located at `config/config.ini`:

```ini
[ENVIROMENT]
current_env = QA

[DATABASE.SOURCE]
host = localhost
port = 3306
database = legacy_banking
username = root
password = root
driver = mysql+pymysql
fallback_sqlite = data/source_fallback.db

[DATABASE.TARGET]
host = localhost
port = 1521
service_name = FREEPDB1
username = system
password = MyPassword123
driver = oracle+oracledb
fallback_sqlite = data/target_fallback.db
```

### Environment Variable Overrides (Optional)
You can override configuration settings without modifying `config.ini`:
- `TARGET_ORCALE_URL`: Target database SQLAlchemy URL (e.g. `sqlite:///data/target_fallback.db`)
- `SOURCE_LEGACY_URL`: Source database SQLAlchemy URL (e.g. `sqlite:///data/source_fallback.db`)

Example (run purely against SQLite):
```powershell
$env:TARGET_ORCALE_URL = "sqlite:///data/target_fallback.db"
python runner.py
```

---

## 6. How to Run Tests

### 6.1 Run the Full Test Suite
Run the custom formatted test runner:
```bash
python runner.py
```

### 6.2 Run by Tag
Filter and execute scenarios with specific BDD tags:
```bash
python runner.py --tags @Schema
```

### 6.3 Run a Specific Feature File
```bash
python runner.py --features features/Schema_validation.feature
```

### 6.4 Run Directly with Behave CLI
```bash
behave features/Schema_validation.feature
```

---

## 7. Test Scenarios Covered

The test suite validates target data warehouse schema integrity:

| # | Scenario | Description |
|---|---|---|
| 1 | Target Tables Existence | Verifies all required tables defined in `expected_schema.json` exist in the target database. |
| 2 | `DIM_BRANCH` Columns | Verifies mandatory columns: `BRANCH_SK`, `BRANCH_CODE`, `BRANCH_NAME`, `REGION`, `SWIFT_BIC`. |
| 3 | `DIM_CUSTOMER` Columns | Verifies mandatory columns: `CUSTOMER_SK`, `CUSTOMER_ID`, `FULL_NAME`, `MASKED_TAX_ID`, `STATUS`, `KYC_STATUS`, `START_DATE`, `IS_CURRENT`. |
| 4 | `DIM_ACCOUNT` Columns | Verifies mandatory columns: `ACCOUNT_SK`, `ACCOUNT_NUMBER`, `CUSTOMER_SK`, `BRANCH_SK`, `ACCOUNT_TYPE`, `CURRENCY_CODE`, `CURRENT_BALANCE`, `STATUS`. |
| 5 | `FACT_LOAN_PORTFOLIO` Columns | Verifies mandatory columns: `LOAN_SK`, `LOAN_ID`, `ACCOUNT_SK`, `CUSTOMER_SK`, `PRINCIPAL_AMOUNT`, `OUTSTANDING_BALANCE`, `DELINQUENCY_STATUS`. |
| 6 | `FACT_TRANSACTIONS` Columns | Verifies mandatory columns: `TXN_SK`, `TXN_ID`, `ACCOUNT_SK`, `TXN_TIMESTAMP`, `TXN_TYPE`, `CHANNEL`, `AMOUNT`, `BALANCE_AFTER_TXN`, `AML_FLAG`. |
| 7 | `DAILY_BALANCE_SUMMARY` Columns | Verifies mandatory columns: `SUMMARY_SK`, `SNAPSHOT_DATE`, `ACCOUNT_SK`, `OPENING_BALANCE`, `TOTAL_DEBIT_AMOUNT`, `TOTAL_CREDIT_AMOUNT`, `CLOSING_BALANCE`, `RECONCILIATION_STATUS`. |
| 8 | `ETL_REJECTED_RECORDS` Columns | Verifies quarantine columns: `REJECT_ID`, `SOURCE_TABLE`, `SOURCE_RECORD_KEY`, `REJECT_REASON`, `RAW_RECORD_PAYLOAD`. |

---

## 8. Reports & Logs

- **Console Output**: Live Rich terminal output showing execution progress and scenario results.
- **Log Files**: Execution logs are stored in:
  ```
  reports/logs/bb_test_execution.log
  ```
  The log captures:
  - Database connection handshakes and fallback events
  - Pre-test and post-test data cleanup activities
  - Scenario start and completion logs
  - Connection disposal details

---

## 9. Project Directory Structure

```
Banking_Migration_Test_ETL_PIPLINE/
│
├── config/
│   ├── config.ini                   # Local DB connection configuration
│   └── db_manager.py                # Database connection factory & auto-fallback
│
├── data/
│   ├── expected_schema.json         # Master schema definition for target tables
│   ├── source_fallback.db           # Local SQLite source database
│   ├── target_fallback.db           # Local SQLite target database
│   ├── test_mapping_rules.xlsx      # Business rule mappings (status, delinquency)
│   └── validation_thresholds.csv    # Threshold limits (AML amounts, credit scores)
│
├── features/
│   ├── Schema_validation.feature    # Gherkin BDD feature specifications
│   ├── environment.py               # Behave hooks (before_all, after_all, etc.)
│   └── steps/
│       ├── common_steps.py          # Shared precondition steps
│       └── schema_steps.py          # Schema inspection and validation logic
│
├── reports/
│   └── logs/
│       └── bb_test_execution.log    # Execution log output
│
├── scripts/
│   ├── mysql_schema_setup.sql       # Native MySQL legacy source DDL creation script
│   ├── oracle_schema_setup.sql      # Native Oracle DDL creation script
│   └── setup_local_sqlite.py        # Local SQLite database setup & seeder
│
├── utils/
│   ├── data_compartor.py            # DataFrame comparison helper
│   ├── excel_reader.py              # External schema & mapping rules reader
│   └── logger.py                    # Consolidated logging handler
│
├── .gitignore                       # Git ignore file
├── req.txt                          # Python dependencies
├── runner.py                        # Test runner script
├── README.md                        # Project introduction
└── SETUP_AND_RUN.md                 # Setup and execution guide
```

---

## 10. Troubleshooting

- **"Access denied for user 'root'@'localhost'"**:
  - The framework will automatically log a warning and fall back to `data/source_fallback.db`. This is expected behavior when a local MySQL instance is not running or has different credentials.
- **Target database fallback**:
  - If Oracle is not installed or running, the framework falls back to `data/target_fallback.db`. Tests will run and pass 100% on SQLite.
- **Resetting Test Data**:
  - If you need a clean state, simply run:
    ```bash
    python scripts/setup_local_sqlite.py
    ```
