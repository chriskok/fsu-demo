from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import json
from datetime import datetime

from backend.models import SessionState, SimulationAction, ActionResponse, SessionResults
from backend.scenarios import get_initial_team_state, process_action, get_available_tasks
from backend.scoring import calculate_final_scores

app = FastAPI(title="EF Assessment MVP", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# In-memory session storage (use Redis/DB in production)
sessions: Dict[str, SessionState] = {}

@app.get("/")
async def read_root():
    return FileResponse("frontend/index.html")

@app.post("/api/session/start")
async def start_session() -> Dict[str, str]:
    session_id = str(uuid.uuid4())
    sessions[session_id] = SessionState(
        session_id=session_id,
        phase="meet_team",
        team_members=get_initial_team_state(),
        actions=[],
        start_time=datetime.now(),
        phase_start_time=datetime.now(),
        available_tasks=get_available_tasks()
    )
    return {"session_id": session_id}

@app.get("/api/session/{session_id}/state")
async def get_session_state(session_id: str) -> SessionState:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.post("/api/session/{session_id}/action")
async def submit_action(session_id: str, action: SimulationAction) -> ActionResponse:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    response = process_action(session, action)
    
    # Update session with action and response
    session.actions.append(action)
    session.team_members = response.updated_team_state
    
    # Check for phase transitions
    elapsed_minutes = (datetime.now() - session.phase_start_time).seconds / 60
    
    if session.phase == "meet_team" and elapsed_minutes >= 2:
        session.phase = "delegate_tasks"
        session.phase_start_time = datetime.now()
    elif session.phase == "delegate_tasks" and elapsed_minutes >= 5:
        session.phase = "navigate_conflicts"
        session.phase_start_time = datetime.now()
    elif session.phase == "navigate_conflicts" and elapsed_minutes >= 3:
        session.phase = "completed"
    
    sessions[session_id] = session
    return response

@app.get("/api/session/{session_id}/results")
async def get_session_results(session_id: str) -> SessionResults:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session.phase != "completed":
        raise HTTPException(status_code=400, detail="Session not completed yet")
    
    scores = calculate_final_scores(session)
    return SessionResults(
        session_id=session_id,
        competency_scores=scores,
        total_duration=(datetime.now() - session.start_time).seconds / 60,
        actions_taken=len(session.actions)
    )