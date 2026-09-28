"""
Master BDD Test Execution Runner & Reporting CLI
------------------------------------------------
Usage:
    python run_bdd_tests.py                  # Run all features
    python run_bdd_tests.py --tags=@pii      # Run specific tag
    python run_bdd_tests.py --tags=@schema   # Run schema tests
"""

import sys
import argparse
from pathlib import Path
from behave.__main__ import main as behave_main
from rich.console import Console
from rich.panel import Panel

console = Console(force_terminal=True, legacy_windows=False)
BASE_DIR = Path(__file__).resolve().parent
FEATURES_DIR = BASE_DIR / "features"


def parse_args():
    parser = argparse.ArgumentParser(description="Banking ETL Migration BDD Automation Runner")
    parser.add_argument("--tags", "-t", type=str, default=None, help="Filter scenarios by tag (e.g. @pii, @reconciliation)")
    parser.add_argument("--feature", "-f", type=str, default=None, help="Specific feature file to execute")
    return parser.parse_args()


def main():
    args = parse_args()

    console.print(Panel.fit(
        "[bold cyan]BANKING ETL MIGRATION - BDD QA AUTOMATION TEST SUITE[/bold cyan]\n"
        "[bold white]Framework: Python + Behave (Gherkin) + External Excel Validation[/bold white]",
        border_style="cyan"
    ))

    behave_args = [str(FEATURES_DIR)]

    if args.feature:
        feat_path = FEATURES_DIR / args.feature
        if feat_path.exists():
            behave_args = [str(feat_path)]
        else:
            console.print(f"[bold red]Feature file not found: {feat_path}[/bold red]")
            sys.exit(1)

    if args.tags:
        behave_args.extend(["--tags", args.tags])

    # Run Behave
    result = behave_main(behave_args)
    sys.exit(result)


if __name__ == "__main__":
    main()
