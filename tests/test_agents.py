import pytest
from unittest.mock import MagicMock, patch

from agents.user_proxy import UserProxyAgent
from agents.reviewer import ReviewerAgent
from graph.state import create_initial_state


def test_user_proxy_intent_detection():
    """Verify User Proxy correctly categorizes a coding request."""

    with patch("agents.user_proxy.genai.configure"), patch("agents.user_proxy.genai.GenerativeModel") as MockModel:
        model_instance = MockModel.return_value
        mock_response = MagicMock()
        mock_response.text = '{"parsed_intent": "code", "requires_rag": true, "relevant_topics": ["fastapi"]}'
        model_instance.generate_content.return_value = mock_response

        agent = UserProxyAgent()
        agent.model = model_instance

        state = create_initial_state("Build a FastAPI app", "session_123")
        updated_state = agent.process(state)

        assert updated_state["parsed_intent"] == "code"
        assert updated_state["requires_rag"] is True


def test_reviewer_fail_on_low_score():
    """Verify Reviewer fails code that doesn't meet the score threshold."""

    with patch("agents.reviewer.genai.configure"), patch("agents.reviewer.genai.GenerativeModel") as MockModel:
        model_instance = MockModel.return_value
        mock_response = MagicMock()
        mock_response.text = '{"review_passed": false, "review_score": 65, "reviewer_feedback": "Too simple"}'
        model_instance.generate_content.return_value = mock_response

        agent = ReviewerAgent()
        agent.model = model_instance

        state = create_initial_state("test", "test")
        state["generated_code"] = "def faulty_func():\n    pass"

        updated_state = agent.act(state)

        assert updated_state["review_passed"] is False
        assert updated_state["review_score"] == 65
