"""
BDD Test Runner Class File for Banking ETL Migration QA Validation
===================================================================
A modular Object-Oriented Test Runner class to configure, filter by tags,
execute BDD scenarios, and optionally trigger the ETL Migration Pipeline.

Usage Options:
--------------
1. Set the tag directly inside this file in `BDDTestRunner.TAGS`:
       TAGS = "@smoke"
   and run:
       python bdd_automation/test_runner.py

2. Pass the tag dynamically from command line:
       python bdd_automation/test_runner.py --tags @schema
       python bdd_automation/test_runner.py --tags @reconciliation
       python bdd_automation/test_runner.py --tags @transformation
       python bdd_automation/test_runner.py --tags @pii
       python bdd_automation/test_runner.py --tags @financial
       python bdd_automation/test_runner.py --tags @quarantine
       python bdd_automation/test_runner.py --tags @kafka
       python bdd_automation/test_runner.py --tags "@smoke and not @kafka"

3. Run Full Pipeline (Trigger ETL Migration -> Run BDD QA Validation):
       python bdd_automation/test_runner.py --pipeline --tags @smoke

4. Programmatic OOP Usage from any Python script:
       from bdd_automation.test_runner import BDDTestRunner
       runner = BDDTestRunner(tags="@financial")
       runner.run()
"""

import sys
import time
import argparse
from pathlib import Path

# Ensure workspace root and bdd_automation directory are in sys.path
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
for path in [str(ROOT_DIR), str(BASE_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Configure UTF-8 for Windows terminals
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Optional, List
from behave.__main__ import main as behave_main
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True, legacy_windows=False)


class BDDTestRunner:
    """
    Object-Oriented Runner for Behave BDD QA Test Execution.
    --------------------------------------------------------
    Attributes can be configured directly in code or overridden via constructor/CLI.
    """

    # =========================================================================
    # 🏷️ CONFIGURE YOUR TARGET TAG HERE:
    # Options:
    #   "@smoke"          -> High-priority smoke tests (Schema, Counts, PII, Balances)
    #   "@regression"     -> Complete test regression across all 7 features
    #   "@schema"         -> Table structures, columns, and NOT NULL checks
    #   "@reconciliation" -> Source vs Target row count & financial equations
    #   "@transformation" -> Business rules, code mappings, and PII regex
    #   "@pii"            -> Tax ID / SSN data masking verification
    #   "@financial"      -> Arithmetic ledger equations & debit/credit totals
    #   "@quarantine"     -> Defective email/status routing & zero data leakage
    #   "@kafka"          -> Real-time event streaming & SLA latency
    #   "" (empty string) -> Run ALL scenarios without tag filtering
    # =========================================================================
    TAGS: str = "@smoke"

    # Directory Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    FEATURES_DIR: Path = BASE_DIR / "features"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    JUNIT_DIR: Path = REPORTS_DIR / "junit"

    # Pipeline pre-execution flag
    RUN_PIPELINE_FIRST: bool = False

    def __init__(
        self,
        tags: Optional[str] = None,
        feature: Optional[str] = None,
        run_pipeline: bool = False,
        junit: bool = True,
        dry_run: bool = False,
    ):
        """
        Initialize the BDD Test Runner.

        :param tags: Tag expression to filter scenarios (e.g. '@schema', '@pii').
                     If None, uses class default `TAGS`.
        :param feature: Specific feature file name (e.g. '01_schema_structure_validation.feature').
        :param run_pipeline: Set True to trigger the ETL migration before running tests.
        :param junit: Set True to generate JUnit XML reports for CI/CD pipelines.
        :param dry_run: Set True to parse steps without executing them.
        """
        raw_tags = tags if tags is not None else self.TAGS
        if raw_tags and isinstance(raw_tags, str):
            cleaned = raw_tags.strip()
            if cleaned and not cleaned.startswith("@") and not cleaned.startswith("not ") and not cleaned.startswith("("):
                cleaned = f"@{cleaned}"
            self.tags = cleaned
        else:
            self.tags = raw_tags

        self.feature = feature
        self.run_pipeline = run_pipeline or self.RUN_PIPELINE_FIRST
        self.junit = junit
        self.dry_run = dry_run

        # Ensure output report folders exist
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.JUNIT_DIR.mkdir(parents=True, exist_ok=True)

    def trigger_etl_migration(self) -> bool:
        """
        Executes the Core Banking ETL Migration Pipeline before testing.
        Refreshes Target Oracle 23c tables and populates dimensional models.
        """
        console.print(Panel(
            "[bold yellow]STEP 1: TRIGGERING ETL MIGRATION PIPELINE[/bold yellow]\n"
            "Extracting from Legacy Core Banking -> Transforming -> Loading to Oracle 23c Target",
            border_style="yellow"
        ))
        try:
            # Dynamically import and execute migration pipeline
            from banking.etl.migration_pipeline import BankingETLPipeline
            start_t = time.time()
            pipeline = BankingETLPipeline()
            pipeline.run()
            elapsed = time.time() - start_t
            console.print(f"[bold green][SUCCESS] ETL Migration completed successfully in {elapsed:.2f}s[/bold green]\n")
            return True
        except Exception as e:
            console.print(f"[bold red][FAILED] ETL Migration Failed: {e}[/bold red]")
            return False


    def check_database_health(self) -> bool:
        """Verifies database connectivity to Target database."""
        try:
            try:
                from config.db_manager import get_db_manager
                db = get_db_manager()
                target_conn = db.get_target_engine()
            except Exception:
                from bdd_automation.config.db_manager import get_db
                db = get_db()
                target_conn = db.get_target_connection()
            from sqlalchemy import text
            with target_conn as conn:
                dialect = conn.dialect.name
                query = "SELECT 1 FROM DUAL" if dialect == "oracle" else "SELECT 1"
                res = conn.execute(text(query)).scalar()
            return res == 1
        except Exception as e:
            console.print(f"[bold red]Database Health Check Failed: {e}[/bold red]")
            return False


    def build_behave_args(self) -> List[str]:
        """Constructs the CLI argument list for the Behave runner."""
        args: List[str] = []

        # Target feature path
        if self.feature:
            feat_path = self.FEATURES_DIR / self.feature
            if not feat_path.exists():
                raise FileNotFoundError(f"Feature file not found: {feat_path}")
            args.append(str(feat_path))
        else:
            args.append(str(self.FEATURES_DIR))

        # Tag filter
        if self.tags and self.tags.strip():
            args.extend(["--tags", self.tags.strip()])

        # JUnit XML reports for Jenkins / CI/CD
        if self.junit:
            args.extend(["--junit", "--junit-directory", str(self.JUNIT_DIR)])

        # Dry-run
        if self.dry_run:
            args.append("--dry-run")

        return args

    def display_banner(self):
        """Displays execution information banner."""
        tag_display = self.tags if self.tags else "ALL SCENARIOS (No Filter)"
        pipeline_status = "ENABLED (Run Migration First)" if self.run_pipeline else "DISABLED (Test Against Existing Target)"

        console.print(Panel.fit(
            f"[bold cyan]BANKING ETL MIGRATION - BDD QA AUTOMATION RUNNER[/bold cyan]\n"
            f"[bold white]Target Database :[/bold white] Oracle 23c Free ([cyan]localhost:1521/FREEPDB1[/cyan])\n"
            f"[bold white]Active Tag Filter:[/bold white] [bold magenta]{tag_display}[/bold magenta]\n"
            f"[bold white]ETL Pipeline Pre-Run:[/bold white] {pipeline_status}\n"
            f"[bold white]JUnit Reports   :[/bold white] [dim]{self.JUNIT_DIR}[/dim]",
            border_style="cyan"
        ))

    def run(self) -> int:
        """
        Executes the BDD test suite.
        :return: 0 if all tests passed, non-zero exit code on failure.
        """
        self.display_banner()

        # Step 1: Health Check
        if not self.check_database_health():
            console.print("[bold red]Aborting: Cannot reach Target Database![/bold red]")
            return 1

        # Step 2: Optional Migration Pipeline Execution
        if self.run_pipeline:
            success = self.trigger_etl_migration()
            if not success:
                console.print("[bold red]Aborting: ETL Pipeline failed. Cannot proceed with QA validation.[/bold red]")
                return 1

        # Step 3: Run Behave Suite
        console.print(f"[bold green]STEP 2: RUNNING BDD TEST SCENARIOS WITH TAG: {self.tags or 'ALL'}[/bold green]\n")
        behave_args = self.build_behave_args()

        start_time = time.time()
        exit_code = behave_main(behave_args)
        duration = time.time() - start_time

        # Step 4: Summary Table
        self.display_summary(exit_code, duration)
        return exit_code

    def display_summary(self, exit_code: int, duration: float):
        """Displays a clean summary table of execution."""
        status_text = "[bold green]PASSED[/bold green]" if exit_code == 0 else "[bold red]FAILED[/bold red]"
        
        table = Table(title="BDD Test Execution Summary", border_style="cyan")
        table.add_column("Parameter", style="bold white")
        table.add_column("Value", style="cyan")

        table.add_row("Execution Status", status_text)
        table.add_row("Tags Filter", self.tags or "ALL")
        table.add_row("Execution Time", f"{duration:.3f} seconds")
        table.add_row("JUnit XML Reports", str(self.JUNIT_DIR))

        console.print("\n")
        console.print(table)

    @classmethod
    def list_available_tags(cls):
        """Displays all available tags in the framework with descriptions."""
        table = Table(title="Available BDD QA Framework Tags", border_style="magenta")
        table.add_column("Tag Name", style="bold magenta")
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("CLI Example", style="yellow")

        tags_info = [
            ("@smoke", "Smoke Test", "Quick sanity check covering Schema, Counts, PII, and Balances", "python bdd_automation/test_runner.py --tags @smoke"),
            ("@regression", "Full Regression", "Executes entire QA test suite across all 7 features", "python bdd_automation/test_runner.py --tags @regression"),
            ("@schema", "DDL & Schema", "Validates tables, columns, data types, and NOT NULL checks", "python bdd_automation/test_runner.py --tags @schema"),
            ("@reconciliation", "Data Reconciliation", "Source vs Target row count parity and reconciliation equation", "python bdd_automation/test_runner.py --tags @reconciliation"),
            ("@integrity", "Keys & Constraints", "Surrogate keys, Natural keys uniqueness, and Foreign key integrity", "python bdd_automation/test_runner.py --tags @integrity"),
            ("@transformation", "Business Transformations", "Excel data-driven code translation (Status, AccountType, Delinquency)", "python bdd_automation/test_runner.py --tags @transformation"),
            ("@pii", "Data Protection", "Validates SSN/Tax ID masking (***-**-XXXX) and regex pattern", "python bdd_automation/test_runner.py --tags @pii"),
            ("@financial", "Financial Ledger", "Validates ledger balance equation: OPEN + CR - DR = CLOSE", "python bdd_automation/test_runner.py --tags @financial"),
            ("@quarantine", "Error Quarantine", "Validates malformed email/status diversion with zero data leakage", "python bdd_automation/test_runner.py --tags @quarantine"),
            ("@kafka", "Streaming Real-Time", "Validates real-time event ingestion to Oracle and AML SLA", "python bdd_automation/test_runner.py --tags @kafka"),
        ]

        for tag, cat, desc, eg in tags_info:
            table.add_row(tag, cat, desc, eg)

        console.print(table)


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Banking ETL Migration - BDD QA Automation Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PowerShell Note:
  In Windows PowerShell, '@' is a reserved splatting operator.
  To avoid PowerShell eating unquoted tags, use any of these formats:
    1. Omit the '@' sign:        --tags smoke   (Runner will automatically add '@')
    2. Wrap tag in quotes:       --tags "@smoke"
    3. Use '=' assignment:       --tags=@smoke
    4. Direct positional arg:    python bdd_automation/test_runner.py smoke
        """
    )
    parser.add_argument(
        "tag_positional",
        nargs="?",
        default=None,
        help="Optional positional tag name (e.g. smoke, schema, reconciliation)"
    )
    parser.add_argument(
        "--tags", "-t",
        type=str,
        nargs="?",
        const="",
        default=None,
        help="Tag expression to filter scenarios (e.g. 'smoke', '@smoke', '@schema')"
    )
    parser.add_argument(
        "--pipeline", "-p",
        action="store_true",
        help="Run ETL Migration Pipeline first before running BDD tests"
    )
    parser.add_argument(
        "--feature", "-f",
        type=str,
        default=None,
        help="Specific feature file to execute (e.g. '01_schema_structure_validation.feature')"
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Parse scenarios without executing step logic"
    )
    parser.add_argument(
        "--list-tags", "-l",
        action="store_true",
        help="Display all available framework tags and descriptions"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.list_tags:
        BDDTestRunner.list_available_tags()
        sys.exit(0)

    # Determine tag from flag or positional argument
    selected_tag = args.tags if args.tags is not None else args.tag_positional

    # If user ran in PowerShell: --tags @smoke (PowerShell swallowed @smoke leaving empty string)
    if selected_tag == "" and args.tag_positional is None:
        console.print(Panel(
            "[bold yellow]PowerShell Notice:[/bold yellow] In PowerShell, '@' is a reserved operator, so [cyan]@smoke[/cyan] was parsed as empty.\n"
            "Automatically defaulting to [bold magenta]@smoke[/bold magenta].\n"
            "In future runs, you can also use: [green]--tags smoke[/green] or [green]--tags \"@smoke\"[/green] or [green]--tags=@smoke[/green]",
            border_style="yellow"
        ))
        selected_tag = "@smoke"

    # Instantiate the Runner class
    runner = BDDTestRunner(
        tags=selected_tag,
        feature=args.feature,
        run_pipeline=args.pipeline,
        dry_run=args.dry_run,
    )

    exit_code = runner.run()
    sys.exit(exit_code)

