import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from pathlib import Path
from behave.__main__ import main as behave_main


console = Console(force_terminal=True, legacy_windows=False)
base_dir = Path(__file__).resolve().parent
FEATURES_dir = base_dir / "features"


def parser_args():
    parser = argparse.ArgumentParser(description="Run BAnking ETL Migration Tests")
    parser.add_argument("--tags", "-t", type = str, default = None, help = "Run tests with specific tags(E.g: @tag1,@tag2)")
    parser.add_argument("--features", "-f", type = str, default = None, help = "Path to features directory")
    return parser.parse_args()




def main():

    args = parser_args()

    console.print(Panel.fit("[bold Cyan] BAnking ETL Migration - Test Runner [/bold Cyan]"
                            , border_style = "cyan"))

    behave_args = ([str(FEATURES_dir)])


    if args.features:
        feat_path = Path(args.features)
        if not feat_path.is_absolute():
            feat_path = base_dir / feat_path
        if feat_path.exists():
            behave_args = ([str(feat_path)])
        else:
            console.print(f"[bold red] Features path  or file does not exist: {feat_path} [/bold red]")
            sys.exit(1)

    if args.tags:
        behave_args.extend(["--tags", args.tags])


    result = behave_main(behave_args)
    sys.exit(result)


if __name__ == "__main__":
    main()

    