import pytest
from unittest.mock import MagicMock

from graph.state import create_initial_state
from graph.workflow import AgentWorkflow


@pytest.fixture
def mock_workflow():
    wf = AgentWorkflow()

    # Mock agents to avoid external calls
    for attr in ["user_proxy", "architect", "coder", "reviewer", "teacher"]:
        agent = MagicMock()
        agent.process = MagicMock(side_effect=lambda s: s)
        agent.act = agent.process
        setattr(wf, attr, agent)

    wf.graph = wf._build_graph()
    return wf


def test_full_workflow_path(mock_workflow):
    initial_state = create_initial_state("How do I use FastAPI?", "test_session")

    # Reviewer passes immediately
    mock_workflow.reviewer.process.side_effect = lambda s: {**s, "review_passed": True, "agents_involved": s.get("agents_involved", []) + ["reviewer"]}
    mock_workflow.reviewer.act = mock_workflow.reviewer.process

    final_state = mock_workflow.graph.invoke(initial_state, config={"configurable": {"thread_id": "test"}})

    assert "reviewer" in final_state.get("agents_involved", [])
    assert final_state.get("review_passed") is True
    assert final_state.get("review_loops_count", 0) == 0
