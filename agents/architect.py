from __future__ import annotations

import logging
import re
from typing import Dict, List

import google.generativeai as genai

from config import settings
from graph.state import AgentState
from prompts.architect_prompt import ARCHITECT_PROMPT_TEMPLATE, ARCHITECT_SYSTEM_PROMPT
from rag.vectorstore import VectorStore
from agents.base_agent import gemini_retry_strategy

logger = logging.getLogger(__name__)


class ArchitectAgent:
    """Designs solution blueprints grounded in RAG context."""

    def __init__(self, vectorstore: VectorStore, model_name: str = "gemini-3.1-flash-lite-preview") -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.vectorstore = vectorstore
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=ARCHITECT_SYSTEM_PROMPT,
        )

    @gemini_retry_strategy  # <--- Add this decorator here
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Architect: Designing solution...")

        rag_result = {"context": "", "sources": []}
        if state.get("requires_rag"):
            rag_result = self.vectorstore.query(
                topics=state.get("relevant_topics", []),
                query_text=state.get("clarified_query", ""),
            )

        state["rag_context"] = rag_result.get("context", "") or "No relevant documentation found."
        state["rag_sources"] = rag_result.get("sources", [])

        prompt = ARCHITECT_PROMPT_TEMPLATE.format(
            clarified_query=state.get("clarified_query", state.get("user_query", "")),
            intent=state.get("parsed_intent", "general"),
            difficulty_level=state.get("difficulty_level", "intermediate"),
            programming_language=state.get("programming_language", "unknown"),
            rag_context=state.get("rag_context", ""),
            rag_sources=", ".join(state.get("rag_sources", [])),
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.2},
            )
            plan_text = response.text or ""

            state["architecture_plan"] = plan_text
            state["implementation_steps"] = self._extract_implementation_steps(plan_text)

            tech_match = re.search(r"## 📦 Recommended Tech Stack\n(.*?)\n##", plan_text, re.DOTALL)
            if tech_match:
                state["tech_stack_recommendation"] = tech_match.group(1).strip()

            state.setdefault("agents_involved", []).append("architect")
            state["activeAgent"] = "architect"  # For frontend visualization
            logger.info("Architect: Design complete.")

        except Exception as exc: 
            # ADD THIS: Re-raise the error so the decorator can retry!
            if "429" in str(exc) or "quota" in str(exc).lower():
                raise exc
                
            logger.error("Architect error: %s", exc)
            state.setdefault("agents_involved", []).append("architect_error")

        return state

    def _extract_implementation_steps(self, plan_text: str) -> List[str]:
        """Parse the 'Implementation Steps' section from markdown."""

        steps: List[str] = []
        match = re.search(r"## 📋 Implementation Steps\n(.*?)(?:\n##|$)", plan_text, re.DOTALL)
        if match:
            section = match.group(1).strip()
            raw_steps = re.split(r"\n\d+\.\s+", "\n" + section)
            steps = [s.strip() for s in raw_steps if s.strip()]
        return steps
