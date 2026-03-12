from __future__ import annotations

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.reviewer import ReviewerAgent
from agents.teacher import TeacherAgent
from agents.user_proxy import UserProxyAgent
from api import routes
from graph.workflow import AgentWorkflow

app = FastAPI(title="Agentic AI Developer Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    workflow = AgentWorkflow()
    routes.workflow = workflow


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(routes.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
