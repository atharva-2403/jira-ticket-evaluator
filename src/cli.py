import argparse
import sys
import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
from src.agent import Agent
from src.schemas import EvaluationResult

def main():
    parser = argparse.ArgumentParser(description="Jira-PR Compliance Evaluator")
    parser.add_argument("--ticket", required=True, help="Jira Ticket ID or path to ticket JSON")
    parser.add_argument("--pr", required=True, help="GitHub PR URL or path to PR JSON")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of table")
    
    args = parser.parse_args()
    console = Console()
    
    rprint(Panel.fit("[bold blue]Jira Ticket Evaluator[/bold blue]\n[italic]Analyzing PR against Requirements...[/italic]"))
    
    try:
        agent = Agent()
        result = agent.evaluate_pr(args.ticket, args.pr)
        
        if args.json:
            print(result.model_dump_json(indent=2))
        else:
            display_report(result, console)
            
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        import traceback
        # logger.error(traceback.format_exc())
        sys.exit(1)

def display_report(result: EvaluationResult, console: Console):
    # Overall Summary
    status_color = "green" if result.overall == "Pass" else "yellow" if result.overall == "Partial" else "red"
    console.print(f"\n[bold]Overall Verdict:[/bold] [{status_color}]{result.overall}[/{status_color}]")
    console.print(f"[bold]Ticket:[/bold] {result.ticket_id}")
    console.print(f"[bold]PR:[/bold] {result.pr_url}\n")
    
    # Requirements Table
    table = Table(title="Requirement Evaluation", show_header=True, header_style="bold magenta")
    table.add_column("Requirement", style="dim", width=40)
    table.add_column("Verdict", justify="center")
    table.add_column("Confidence", justify="right")
    table.add_column("Evidence")
    
    for req in result.requirements:
        v_color = "green" if req.verdict == "Pass" else "yellow" if req.verdict == "Partial" else "red"
        table.add_row(
            req.requirement,
            f"[{v_color}]{req.verdict}[/{v_color}]",
            f"{req.confidence:.2f}",
            req.evidence
        )
    
    console.print(table)
    console.print(f"\n[dim]Evaluated at: {result.evaluated_at}[/dim]")

if __name__ == "__main__":
    main()
