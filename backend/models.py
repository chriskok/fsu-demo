from pydantic import BaseModel
from typing import Dict, List, Optional, Literal
from datetime import datetime
from enum import Enum

class MoodState(str, Enum):
    HAPPY = "happy"
    NEUTRAL = "neutral"
    FRUSTRATED = "frustrated"

class TeamMember(BaseModel):
    name: str
    role: str
    description: str
    mood: MoodState = MoodState.NEUTRAL
    workload: int = 0  # 0-100 scale
    skills: List[str]
    personality_traits: Dict[str, int]  # trait_name: strength (1-10)
    trigger_points: List[str]
    current_tasks: List[str] = []

class SimulationAction(BaseModel):
    type: Literal["delegate_task", "send_message", "address_conflict", "ask_question"]
    target_member: Optional[str] = None
    task_id: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict] = None

class ActionResponse(BaseModel):
    success: bool
    message: str
    team_member_reaction: Optional[str] = None
    mood_change: Optional[MoodState] = None
    updated_team_state: Dict[str, TeamMember]
    consequences: List[str] = []

class SessionState(BaseModel):
    session_id: str
    phase: Literal["meet_team", "delegate_tasks", "navigate_conflicts", "completed"]
    team_members: Dict[str, TeamMember]
    actions: List[SimulationAction] = []
    start_time: datetime
    phase_start_time: datetime
    available_tasks: List[Dict] = []

class CompetencyScore(BaseModel):
    name: str
    score: int  # 0-100
    feedback: str
    evidence: List[str]

class SessionResults(BaseModel):
    session_id: str
    competency_scores: Dict[str, CompetencyScore]
    total_duration: float  # minutes
    actions_taken: int
    overall_rating: str  # "Excellent", "Good", "Needs Improvement"