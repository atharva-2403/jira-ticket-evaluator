import argparse
import sys
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from src.agent import run_evaluation

def main():
    parser = argparse.ArgumentParser(
        description="Jira Ticket Evaluator: Automatically verify PR compliance."
    )
    parser.add_argument("--ticket", required=True, help="Jira Ticket ID (e.g., PROJ-123)")
    parser.add_argument("--pr", required=True, help="GitHub Pull Request URL")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of a table")

    args = parser.parse_args()
    console = Console()

    if not args.json:
        console.print(Panel.fit(
            "[bold blue]Jira Ticket Evaluator[/bold blue]\n[italic]Analyzing PR compliance with Jira requirements...[/italic]",
            border_style="blue"
        ))

    try:
        result = run_evaluation(args.ticket, args.pr)
        
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            _display_verdict_table(result, console)
            
    except Exception as e:
        console.print(f"\n[bold red]Error during evaluation:[/bold red] {str(e)}")
        sys.exit(1)

def _display_verdict_table(result, console):
    # Overall Status
    status_colors = {"Pass": "green", "Partial": "yellow", "Fail": "red"}
    color = status_colors.get(result.overall, "white")
    
    console.print(f"\n[bold]Ticket:[/bold] {result.ticket_id}")
    console.print(f"[bold]PR URL:[/bold] {result.pr_url}")
    console.print(f"[bold]Overall Verdict:[/bold] [{color}]{result.overall.upper()}[/{color}]\n")

    # Detailed Table
    table = Table(title="Requirement Compliance Breakdown", box=box.ROUNDED)
    table.add_column("Requirement", style="cyan", no_wrap=False)
    table.add_column("Verdict", justify="center")
    table.add_column("Confidence", justify="right")
    table.add_column("Evidence", style="dim")

    for req in result.requirements:
        v_color = status_colors.get(req.verdict, "white")
        table.add_row(
            req.requirement,
            f"[{v_color}]{req.verdict}[/{v_color}]",
            f"{req.confidence:.2f}",
            req.evidence
        )

    console.print(table)
    
    if result.test_results:
        console.print(f"\n[bold]Automated Test Results:[/bold] {len(result.test_results)} tests executed.")
    
    console.print(f"\n[dim]Evaluated at: {result.evaluated_at}[/dim]")

if __name__ == "__main__":
    main()
