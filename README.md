# Banking Migration ETL Pipeline Validation Framework

A robust, enterprise-grade BDD test automation framework for validating **Banking ETL Migrations** (Legacy MySQL/On-Prem Source to Target Oracle Data Warehouse) built with Python, Behave, SQLAlchemy, Pandas, and Rich.

> **Zero Docker Requirement**: This entire test suite runs directly on **localhost** using built-in SQLite fallback or native local database installations. No Docker containers are needed!

---

## Quick Start

### 1. Set Up Environment
```bash
python -m venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r req.txt
```

### 2. Initialize Local Data (100% Docker-Free)
```bash
python scripts/setup_local_sqlite.py
```

### 3. Run the Tests
```bash
python runner.py
```

---

## Detailed Documentation

For full setup details, database options, configuration, and execution flags, refer to:
📖 **[SETUP_AND_RUN.md](SETUP_AND_RUN.md)**

---

## Key Highlights

- **BDD Feature Specifications**: Gherkin scenarios defined in `features/`.
- **Flexible Database Support**: Seamless execution against native Oracle/MySQL or instant zero-dependency SQLite.
- **Automated Fallback**: Gracefully falls back to local SQLite if native database services are offline.
- **Rich Reporting**: Beautiful terminal feedback and structured logging in `reports/logs/`.
