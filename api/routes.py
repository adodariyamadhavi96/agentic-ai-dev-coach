import json
import os
import zipfile
import uuid
from datetime import datetime
from io import BytesIO
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse, Response

# --- CRITICAL FIX: Add this import ---
from pydantic import BaseModel 

router = APIRouter(prefix="/api")
workflow = None 

# --- REQUEST MODEL FOR SWAGGER ---
class CoachRequest(BaseModel):
    user_query: str
    difficulty_level: str = "Intermediate" 

# Global variable to hold the latest result for the download button
latest_session_result = {}

@router.post("/ask")
async def ask_coach(request: CoachRequest): 
    global latest_session_result
    # Use the model attributes directly
    query = request.user_query
    expertise = request.difficulty_level
    
    # Execute workflow
    result = workflow.run(user_query=query, thread_id="web_session", difficulty_level=expertise)
    
    # Store in memory for immediate download access
    latest_session_result = result
    
    # --- INDIVIDUAL FILE STORAGE ---
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save a unique timestamped file for record-keeping
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"result_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, "w") as f:
        json.dump({"query": query, "result": result}, f, indent=4)
        
    return result

@router.get("/download")
async def download_code():
    global latest_session_result

    def _unwrap_payload(obj: dict) -> dict:
        """Support shapes from /api/ask and saved history files."""
        if not obj or not isinstance(obj, dict):
            return {}
        # history files: { query, result: {...} }
        if isinstance(obj.get("result"), dict):
            obj = obj["result"]
        # workflow state: { final_response: {...} }
        if isinstance(obj.get("final_response"), dict):
            obj = obj["final_response"]
        return obj if isinstance(obj, dict) else {}

    def _load_latest_saved_result() -> dict:
        """Fallback if server memory was cleared/restarted."""
        output_dir = "output"
        if not os.path.exists(output_dir):
            return {}
        candidates = [
            os.path.join(output_dir, f)
            for f in os.listdir(output_dir)
            if f.startswith("result_") and f.endswith(".json")
        ]
        if not candidates:
            return {}
        latest_path = max(candidates, key=lambda p: os.path.getmtime(p))
        try:
            with open(latest_path, "r") as f:
                return json.load(f) or {}
        except Exception:
            return {}

    # Prefer in-memory latest result; otherwise use latest saved file
    container = latest_session_result if latest_session_result else _load_latest_saved_result()
    raw = _unwrap_payload(container)

    if not raw:
        raise HTTPException(status_code=404, detail="No active project data to download")

    code = raw.get("final_code") or raw.get("generated_code") or raw.get("code") or ""
    lang = raw.get("code_language") or "py"
    arch = raw.get("architecture_plan") or "No architecture plan provided."
    coach = raw.get("full_explanation") or raw.get("explanation") or raw.get("summary") or "No coach walkthrough provided."

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr(f"generated_code.{lang}", code)
        zip_file.writestr("architecture.md", arch)
        zip_file.writestr("coach.md", coach)

    return Response(
        zip_buffer.getvalue(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment;filename=project.zip"}
    )

@router.get("/stream")
async def stream_coach(query: str, session_id: str | None = None):
    sid = session_id or str(uuid.uuid4())

    async def event_generator():
        async for chunk in workflow.graph.astream(
            {"user_query": query},
            config={"configurable": {"thread_id": sid}},
            stream_mode="updates",
        ):
            if chunk:
                agent_name = list(chunk.keys())[0]
                data = {"agent": agent_name, "status": "processing"}
                yield f"data: {json.dumps(data)}\n\n"
    
    # --- FIX: Ensure the generator is returned ---
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/history")
async def get_history_list():
    """Scans output folder to list previous projects."""
    output_dir = "output"
    if not os.path.exists(output_dir): return []
    
    files = []
    for f in os.listdir(output_dir):
        if f.endswith(".json"):
            path = os.path.join(output_dir, f)
            try:
                with open(path, "r") as file:
                    data = json.load(file)
                    # Extract timestamp from filename
                    files.append({"file": f, "query": data.get("query", f), "time": f[7:22]})
            except Exception: continue
    return sorted(files, key=lambda x: x['time'], reverse=True)

@router.get("/history/{filename}")
async def get_history_detail(filename: str):
    """Fetches a specific past result."""
    path = os.path.join("output", filename)
    if not os.path.exists(path): raise HTTPException(404)
    with open(path, "r") as f: return json.load(f)