from typing import Dict, List
from backend.models import TeamMember, MoodState, SimulationAction, ActionResponse
import random

def get_initial_team_state() -> Dict[str, TeamMember]:
    """Initialize the three team members with their personalities and traits."""
    return {
        "alex": TeamMember(
            name="Alex",
            role="Developer",
            description="Brilliant but disorganized",
            mood=MoodState.NEUTRAL,
            workload=30,
            skills=["Python", "JavaScript", "Problem Solving", "Innovation"],
            personality_traits={
                "creativity": 9,
                "organization": 3,
                "technical_skill": 8,
                "communication": 5,
                "stress_tolerance": 6
            },
            trigger_points=["micromanagement", "tight_deadlines", "unclear_requirements"],
            current_tasks=[]
        ),
        "jordan": TeamMember(
            name="Jordan",
            role="Designer",
            description="Detail-oriented but anxious",
            mood=MoodState.NEUTRAL,
            workload=25,
            skills=["UI/UX Design", "Attention to Detail", "User Research", "Prototyping"],
            personality_traits={
                "creativity": 7,
                "organization": 8,
                "attention_to_detail": 9,
                "confidence": 4,
                "stress_tolerance": 5
            },
            trigger_points=["public_criticism", "rushed_feedback", "unclear_expectations"],
            current_tasks=[]
        ),
        "sam": TeamMember(
            name="Sam",
            role="Marketing",
            description="Driven but impatient",
            mood=MoodState.NEUTRAL,
            workload=40,
            skills=["Marketing Strategy", "Communication", "Leadership", "Results Focus"],
            personality_traits={
                "drive": 9,
                "patience": 3,
                "communication": 8,
                "results_focus": 9,
                "collaboration": 6
            },
            trigger_points=["long_meetings", "indecision", "slow_progress"],
            current_tasks=[]
        )
    }

def get_available_tasks() -> List[Dict]:
    """Get the list of tasks that need to be delegated."""
    return [
        {
            "id": "create_mockups",
            "name": "Create UI Mockups",
            "description": "Design initial user interface mockups for the new feature",
            "estimated_hours": 8,
            "skills_required": ["UI/UX Design", "Prototyping"],
            "urgency": "medium",
            "best_fit": "jordan"
        },
        {
            "id": "backend_api",
            "name": "Develop Backend API",
            "description": "Build the REST API endpoints for data management",
            "estimated_hours": 12,
            "skills_required": ["Python", "API Development"],
            "urgency": "high",
            "best_fit": "alex"
        },
        {
            "id": "market_research",
            "name": "Conduct Market Research",
            "description": "Research competitor features and user needs",
            "estimated_hours": 6,
            "skills_required": ["Marketing Strategy", "User Research"],
            "urgency": "low",
            "best_fit": "sam"
        },
        {
            "id": "user_testing",
            "name": "Plan User Testing",
            "description": "Design and coordinate user testing sessions",
            "estimated_hours": 4,
            "skills_required": ["User Research", "Communication"],
            "urgency": "medium",
            "best_fit": "jordan"
        },
        {
            "id": "integration_testing",
            "name": "Integration Testing",
            "description": "Test API integration with frontend components",
            "estimated_hours": 6,
            "skills_required": ["JavaScript", "Problem Solving"],
            "urgency": "high",
            "best_fit": "alex"
        }
    ]

def process_action(session_state, action: SimulationAction) -> ActionResponse:
    """Process a user action and return the team's response."""
    team_members = session_state.team_members.copy()
    
    if action.type == "delegate_task":
        return handle_task_delegation(team_members, action)
    elif action.type == "send_message":
        return handle_message(team_members, action)
    elif action.type == "address_conflict":
        return handle_conflict_resolution(team_members, action)
    elif action.type == "ask_question":
        return handle_question(team_members, action)
    
    return ActionResponse(
        success=False,
        message="Unknown action type",
        updated_team_state=team_members
    )

def handle_task_delegation(team_members: Dict[str, TeamMember], action: SimulationAction) -> ActionResponse:
    """Handle task delegation to team members."""
    target = action.target_member
    task_id = action.task_id
    
    if not target or target not in team_members:
        return ActionResponse(
            success=False,
            message="Invalid team member selected",
            updated_team_state=team_members
        )
    
    member = team_members[target]
    tasks = get_available_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    
    if not task:
        return ActionResponse(
            success=False,
            message="Invalid task selected",
            updated_team_state=team_members
        )
    
    # Check if task is a good fit
    is_good_fit = task["best_fit"] == target
    skill_match = any(skill in member.skills for skill in task["skills_required"])
    
    # Update member state
    member.current_tasks.append(task["name"])
    member.workload += task["estimated_hours"]
    
    # Determine reaction based on fit and current mood
    if is_good_fit and skill_match:
        if member.workload < 50:
            member.mood = MoodState.HAPPY
            reaction = f"{member.name} seems excited about this task - it's right in their wheelhouse!"
        else:
            reaction = f"{member.name} appreciates the good fit but looks concerned about their workload."
    else:
        if member.workload > 40:
            member.mood = MoodState.FRUSTRATED
            reaction = f"{member.name} looks overwhelmed - this task doesn't match their skills and they're already busy."
        else:
            reaction = f"{member.name} seems uncertain but willing to try."
    
    team_members[target] = member
    
    return ActionResponse(
        success=True,
        message=f"Task '{task['name']}' delegated to {member.name}",
        team_member_reaction=reaction,
        mood_change=member.mood,
        updated_team_state=team_members,
        consequences=generate_consequences(member, task, is_good_fit)
    )

def handle_message(team_members: Dict[str, TeamMember], action: SimulationAction) -> ActionResponse:
    """Handle sending a message to a team member."""
    target = action.target_member
    message = action.message or ""
    
    if not target or target not in team_members:
        return ActionResponse(
            success=False,
            message="Invalid team member selected",
            updated_team_state=team_members
        )
    
    member = team_members[target]
    
    # Simple sentiment analysis for message tone
    positive_words = ["great", "excellent", "appreciate", "thank", "good", "well done"]
    encouraging_words = ["support", "help", "confident", "believe", "capable"]
    
    is_positive = any(word in message.lower() for word in positive_words)
    is_encouraging = any(word in message.lower() for word in encouraging_words)
    
    if is_positive or is_encouraging:
        if member.mood == MoodState.FRUSTRATED:
            member.mood = MoodState.NEUTRAL
        elif member.mood == MoodState.NEUTRAL:
            member.mood = MoodState.HAPPY
        reaction = f"{member.name} smiles and seems more motivated."
    else:
        reaction = f"{member.name} nods politely but seems unchanged."
    
    team_members[target] = member
    
    return ActionResponse(
        success=True,
        message=f"Message sent to {member.name}",
        team_member_reaction=reaction,
        mood_change=member.mood,
        updated_team_state=team_members
    )

def handle_conflict_resolution(team_members: Dict[str, TeamMember], action: SimulationAction) -> ActionResponse:
    """Handle conflict resolution between team members."""
    # Simulate a conflict between Sam and Jordan
    sam = team_members["sam"]
    jordan = team_members["jordan"]
    
    approach = action.data.get("approach", "neutral") if action.data else "neutral"
    
    if approach == "address_both":
        sam.mood = MoodState.NEUTRAL
        jordan.mood = MoodState.NEUTRAL
        reaction = "Both Sam and Jordan seem relieved that you're addressing the tension directly."
    elif approach == "private_meetings":
        sam.mood = MoodState.HAPPY
        jordan.mood = MoodState.HAPPY
        reaction = "Sam and Jordan appreciate the private approach - they both seem more comfortable."
    else:
        reaction = "The tension between Sam and Jordan remains unresolved."
    
    team_members["sam"] = sam
    team_members["jordan"] = jordan
    
    return ActionResponse(
        success=True,
        message="Conflict resolution attempted",
        team_member_reaction=reaction,
        updated_team_state=team_members
    )

def handle_question(team_members: Dict[str, TeamMember], action: SimulationAction) -> ActionResponse:
    """Handle asking a question to a team member."""
    target = action.target_member
    
    if not target or target not in team_members:
        return ActionResponse(
            success=False,
            message="Invalid team member selected",
            updated_team_state=team_members
        )
    
    member = team_members[target]
    
    # Generate contextual responses based on member personality
    responses = {
        "alex": [
            "I think we should focus on the technical architecture first.",
            "I've been working on some ideas - want to see my sketches?",
            "This reminds me of a similar project I worked on last year."
        ],
        "jordan": [
            "I'd like to do some user research before we finalize the design.",
            "I'm a bit worried about the timeline - can we discuss the priorities?",
            "I want to make sure we get the details right."
        ],
        "sam": [
            "We need to move fast on this - the market window is closing.",
            "What's our go-to-market strategy for this feature?",
            "I can help coordinate with the stakeholders."
        ]
    }
    
    reaction = random.choice(responses.get(target, ["I'll need to think about that."]))
    
    return ActionResponse(
        success=True,
        message=f"Question asked to {member.name}",
        team_member_reaction=reaction,
        updated_team_state=team_members
    )

def generate_consequences(member: TeamMember, task: Dict, is_good_fit: bool) -> List[str]:
    """Generate consequences based on task delegation decisions."""
    consequences = []
    
    if not is_good_fit:
        consequences.append(f"{member.name} may struggle with this task due to skill mismatch")
    
    if member.workload > 60:
        consequences.append(f"{member.name} is becoming overloaded and may burn out")
    
    if member.mood == MoodState.FRUSTRATED:
        consequences.append(f"{member.name}'s frustration may affect team morale")
    
    return consequences