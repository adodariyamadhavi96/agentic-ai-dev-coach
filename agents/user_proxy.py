from __future__ import annotations

import json
import logging
from typing import Dict, Any

import google.generativeai as genai

from config import settings
from graph.state import AgentState
from prompts.user_proxy_prompt import (
    INTENT_CLASSIFICATION_RULES,
    USER_PROXY_PROMPT_TEMPLATE,
    USER_PROXY_SYSTEM_PROMPT,
)
from agents.base_agent import gemini_retry_strategy

logger = logging.getLogger(__name__)


class UserProxyAgent:
    """Intake specialist that clarifies the query and extracts RAG topics."""

    def __init__(self, model_name: str = "gemini-3.1-flash-lite-preview") -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=f"{USER_PROXY_SYSTEM_PROMPT}\n\nIntent Rules:\n{INTENT_CLASSIFICATION_RULES}",
        )

    @gemini_retry_strategy  # <--- CRITICAL: You must add this decorator here!
    def process(self, state: AgentState) -> AgentState:
        """Process the user query to detect intent and clarify requirements."""

        logger.info("UserProxy: Processing query: %s", state.get("user_query"))

        conversation_history = "No previous history."
        prompt = USER_PROXY_PROMPT_TEMPLATE.format(
            user_query=state.get("user_query", ""),
            conversation_history=conversation_history,
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
            )
            data: Dict = json.loads(response.text)

            state["parsed_intent"] = data.get("parsed_intent", "general")
            state["clarified_query"] = data.get("clarified_query", state.get("user_query", ""))
            state["programming_language"] = data.get("programming_language", "unknown")
            state["difficulty_level"] = data.get("difficulty_level", "intermediate")
            state["requires_rag"] = data.get("requires_rag", False)
            state["relevant_topics"] = data.get("relevant_topics", [])

            state.setdefault("agents_involved", []).append("user_proxy")
            state["activeAgent"] = "user_proxy"  # For frontend visualization
            logger.info("UserProxy: Intent detected as %s", state.get("parsed_intent"))

        except Exception as exc: 
            # RE-RAISE 429s so gemini_retry_strategy can see them and trigger a retry
            if "429" in str(exc) or "quota" in str(exc).lower():
                raise exc
                
            logger.error("UserProxy error: %s", exc)
            state["parsed_intent"] = "general"
            state["clarified_query"] = state.get("user_query", "")
            state.setdefault("agents_involved", []).append("user_proxy_error")

        return state
