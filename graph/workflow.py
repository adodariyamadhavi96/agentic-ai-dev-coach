from __future__ import annotations

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from agents.teacher import TeacherAgent
from agents.user_proxy import UserProxyAgent
from graph.router import (
    route_after_architect,
    route_after_reviewer,
    route_after_user_proxy,
)
from graph.state import AgentState, create_initial_state
from rag.vectorstore import VectorStore


class AgentWorkflow:
    def __init__(self) -> None:
        vectorstore = VectorStore()

        self.user_proxy = UserProxyAgent()
        self.architect = ArchitectAgent(vectorstore)
        self.coder = CoderAgent()
        self.reviewer = ReviewerAgent()
        self.teacher = TeacherAgent()

        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("user_proxy", self.user_proxy.process)
        workflow.add_node("architect", self.architect.act)
        workflow.add_node("coder", self.coder.act)
        workflow.add_node("reviewer", self.reviewer.act)
        workflow.add_node("teacher", self.teacher.act)

        workflow.add_edge(START, "user_proxy")

        workflow.add_conditional_edges(
            "user_proxy",
            route_after_user_proxy,
            {"architect": "architect"},
        )

        workflow.add_conditional_edges(
            "architect",
            route_after_architect,
            {"coder": "coder", "teacher": "teacher"},
        )

        workflow.add_edge("coder", "reviewer")

        workflow.add_conditional_edges(
            "reviewer",
            route_after_reviewer,
            {"coder": "coder", "teacher": "teacher"},
        )

        workflow.add_edge("teacher", END)

        return workflow.compile(checkpointer=self.memory)

    def run(self, user_query: str, thread_id: str, difficulty_level: str | None = None):
        initial_state = create_initial_state(user_query, thread_id)
        if difficulty_level:
            initial_state["difficulty_level"] = difficulty_level
        config = {"configurable": {"thread_id": thread_id}}
        final_state = self.graph.invoke(initial_state, config=config)
        return final_state.get("final_response", final_state)
