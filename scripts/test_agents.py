from __future__ import annotations

import sys

import pytest
from rich.console import Console

from config import settings
from graph.state import AgentState
from graph.workflow import AgentWorkflow


if "pytest" in sys.modules:
    pytest.skip("script is for manual runs, not a test", allow_module_level=True)

console = Console()


def main() -> None:
    console.rule("Agent Smoke Test")
    workflow = AgentWorkflow(max_loops=settings.MAX_REVIEW_LOOPS)
    app = workflow.graph
    result: AgentState = app.invoke(AgentState(query="Show me a Python hello world"))

    console.print("[bold green]Plan:[/bold green]", result.plan)
    console.print("[bold cyan]Approved Code:[/bold cyan]\n", result.approved_code)
    console.print("[bold yellow]Explanation:[/bold yellow]\n", getattr(result, "explanation", ""))


if __name__ == "__main__":
    main()
