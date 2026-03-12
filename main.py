from __future__ import annotations

import os
import argparse

# Force Google SDK to use stable v1 endpoints
os.environ["GOOGLE_API_USE_V1"] = "true"

from rich.console import Console

from config import settings
from graph.state import AgentState, create_initial_state
from graph.workflow import AgentWorkflow

console = Console()


def run_query(query: str) -> AgentState:
    workflow = AgentWorkflow()
    app = workflow.graph

    thread_id = "cli_test_session"
    config = {"configurable": {"thread_id": thread_id}}

    return app.invoke({"user_query": query}, config=config)


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Developer Coach CLI")
    parser.add_argument("-q", "--query", required=True, help="Developer request to solve")
    args = parser.parse_args()

    console.rule("AI Developer Coach")
    result = run_query(args.query)

    console.print("[bold green]Plan[/bold green]")
    console.print(result.get("architecture_plan") or "(no plan generated)")

    console.print("\n[bold cyan]Approved Code[/bold cyan]")
    console.print(result.get("generated_code") or "(no code produced)")

    explanation = result.get("teaching_explanation", "")
    console.print("\n[bold yellow]Explanation[/bold yellow]")
    console.print(explanation or "(no explanation)")


if __name__ == "__main__":
    main()
