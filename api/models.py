from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_query: str = Field(..., min_length=5, description="The developer's question or code snippet")
    session_id: Optional[str] = Field(None, description="Unique ID for conversation memory")
    difficulty_level: str = Field("intermediate", description="beginner, intermediate, or advanced")


class CoachResponse(BaseModel):
    session_id: str
    summary: str
    architecture_plan: str
    final_code: str
    code_language: str
    dependencies: List[str]
    review_score: int
    review_loops: int
    agents_used: List[str]
    execution_time_seconds: float
