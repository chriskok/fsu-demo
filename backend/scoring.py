from typing import Dict, List
from backend.models import SessionState, CompetencyScore, MoodState
import statistics

def calculate_final_scores(session: SessionState) -> Dict[str, CompetencyScore]:
    """Calculate NACE competency scores based on user actions during the simulation."""
    
    scores = {}
    
    # Critical Thinking - Task assignment logic and priority decisions
    scores["critical_thinking"] = assess_critical_thinking(session)
    
    # Communication - Message clarity and active listening
    scores["communication"] = assess_communication(session)
    
    # Teamwork - Inclusion balance and conflict resolution
    scores["teamwork"] = assess_teamwork(session)
    
    # Leadership - Decision timing and team morale management
    scores["leadership"] = assess_leadership(session)
    
    # Professionalism - Response consistency and time management
    scores["professionalism"] = assess_professionalism(session)
    
    # Equity & Inclusion - Ensuring all voices heard
    scores["equity_inclusion"] = assess_equity_inclusion(session)
    
    return scores

def assess_critical_thinking(session: SessionState) -> CompetencyScore:
    """Assess critical thinking based on task delegation decisions."""
    score = 50  # Base score
    evidence = []
    
    task_actions = [a for a in session.actions if a.type == "delegate_task"]
    
    # Check for logical task assignments
    from backend.scenarios import get_available_tasks
    available_tasks = {task["id"]: task for task in get_available_tasks()}
    
    good_assignments = 0
    total_assignments = len(task_actions)
    
    for action in task_actions:
        if action.task_id in available_tasks:
            task = available_tasks[action.task_id]
            if task["best_fit"] == action.target_member:
                good_assignments += 1
                score += 10
                evidence.append(f"Assigned {task['name']} to {action.target_member} (good skill match)")
            else:
                score -= 5
                evidence.append(f"Assigned {task['name']} to {action.target_member} (skill mismatch)")
    
    # Bonus for considering workload balance
    member_workloads = []
    for member in session.team_members.values():
        member_workloads.append(member.workload)
    
    if member_workloads and statistics.stdev(member_workloads) < 15:
        score += 15
        evidence.append("Maintained balanced workload distribution")
    
    score = max(0, min(100, score))
    
    feedback = generate_critical_thinking_feedback(score, good_assignments, total_assignments)
    
    return CompetencyScore(
        name="Critical Thinking",
        score=score,
        feedback=feedback,
        evidence=evidence
    )

def assess_communication(session: SessionState) -> CompetencyScore:
    """Assess communication based on messages sent and questions asked."""
    score = 50
    evidence = []
    
    message_actions = [a for a in session.actions if a.type == "send_message"]
    question_actions = [a for a in session.actions if a.type == "ask_question"]
    
    # Points for active communication
    score += min(20, len(message_actions) * 5)
    score += min(15, len(question_actions) * 7)
    
    if message_actions:
        evidence.append(f"Sent {len(message_actions)} messages to team members")
    if question_actions:
        evidence.append(f"Asked {len(question_actions)} questions to gather input")
    
    # Check for balanced communication (not favoring one person)
    communication_targets = {}
    for action in message_actions + question_actions:
        if action.target_member:
            communication_targets[action.target_member] = communication_targets.get(action.target_member, 0) + 1
    
    if len(communication_targets) >= 2:
        score += 10
        evidence.append("Communicated with multiple team members")
    
    score = max(0, min(100, score))
    
    feedback = generate_communication_feedback(score, len(message_actions), len(question_actions))
    
    return CompetencyScore(
        name="Communication",
        score=score,
        feedback=feedback,
        evidence=evidence
    )

def assess_teamwork(session: SessionState) -> CompetencyScore:
    """Assess teamwork based on conflict resolution and team inclusion."""
    score = 50
    evidence = []
    
    conflict_actions = [a for a in session.actions if a.type == "address_conflict"]
    
    # Points for addressing conflicts
    if conflict_actions:
        score += 20
        evidence.append("Proactively addressed team conflicts")
    
    # Check team mood at end
    happy_members = sum(1 for m in session.team_members.values() if m.mood == MoodState.HAPPY)
    frustrated_members = sum(1 for m in session.team_members.values() if m.mood == MoodState.FRUSTRATED)
    
    score += happy_members * 10
    score -= frustrated_members * 15
    
    if happy_members > 0:
        evidence.append(f"{happy_members} team members ended in positive mood")
    if frustrated_members > 0:
        evidence.append(f"{frustrated_members} team members ended frustrated")
    
    # Check for inclusive task distribution
    members_with_tasks = sum(1 for m in session.team_members.values() if m.current_tasks)
    if members_with_tasks >= 2:
        score += 10
        evidence.append("Distributed tasks across multiple team members")
    
    score = max(0, min(100, score))
    
    feedback = generate_teamwork_feedback(score, len(conflict_actions), happy_members, frustrated_members)
    
    return CompetencyScore(
        name="Teamwork",
        score=score,
        feedback=feedback,
        evidence=evidence
    )

def assess_leadership(session: SessionState) -> CompetencyScore:
    """Assess leadership based on decision timing and team management."""
    score = 50
    evidence = []
    
    total_actions = len(session.actions)
    
    # Points for taking action
    if total_actions >= 5:
        score += 20
        evidence.append("Took decisive action throughout the simulation")
    elif total_actions >= 3:
        score += 10
        evidence.append("Took moderate action during the simulation")
    else:
        score -= 10
        evidence.append("Limited action taken during the simulation")
    
    # Check for proactive vs reactive leadership
    early_actions = len([a for a in session.actions[:3]])
    if early_actions >= 2:
        score += 15
        evidence.append("Demonstrated proactive leadership early in the session")
    
    # Team morale management
    final_team_morale = calculate_team_morale(session.team_members)
    if final_team_morale > 0.6:
        score += 15
        evidence.append("Maintained high team morale")
    elif final_team_morale < 0.3:
        score -= 15
        evidence.append("Team morale declined during the session")
    
    score = max(0, min(100, score))
    
    feedback = generate_leadership_feedback(score, total_actions, final_team_morale)
    
    return CompetencyScore(
        name="Leadership",
        score=score,
        feedback=feedback,
        evidence=evidence
    )

def assess_professionalism(session: SessionState) -> CompetencyScore:
    """Assess professionalism based on consistency and time management."""
    score = 50
    evidence = []
    
    # Time management - did they use the available time effectively?
    total_duration = (session.phase_start_time - session.start_time).seconds / 60
    if 8 <= total_duration <= 12:  # Good time management (8-12 minutes)
        score += 20
        evidence.append("Managed time effectively within meeting duration")
    elif total_duration > 15:
        score -= 10
        evidence.append("Meeting ran significantly over time")
    
    # Consistency in approach
    action_types = [a.type for a in session.actions]
    if len(set(action_types)) >= 2:
        score += 10
        evidence.append("Used varied leadership approaches appropriately")
    
    # No evidence of unprofessional behavior (placeholder for future expansion)
    score += 10
    evidence.append("Maintained professional demeanor throughout")
    
    score = max(0, min(100, score))
    
    feedback = generate_professionalism_feedback(score, total_duration)
    
    return CompetencyScore(
        name="Professionalism",
        score=score,
        feedback=feedback,
        evidence=evidence
    )

def assess_equity_inclusion(session: SessionState) -> CompetencyScore:
    """Assess equity and inclusion based on ensuring all voices are heard."""
    score = 50
    evidence = []
    
    # Check if all team members were engaged
    members_contacted = set()
    for action in session.actions:
        if action.target_member and action.type in ["send_message", "ask_question", "delegate_task"]:
            members_contacted.add(action.target_member)
    
    inclusion_ratio = len(members_contacted) / len(session.team_members)
    
    if inclusion_ratio >= 0.8:  # 80%+ of team engaged
        score += 25
        evidence.append("Engaged with most team members equally")
    elif inclusion_ratio >= 0.5:
        score += 15
        evidence.append("Engaged with majority of team members")
    else:
        score -= 10
        evidence.append("Limited engagement with team members")
    
    # Check for adapting communication style (looking at different types of interactions)
    interaction_variety = len(set(a.type for a in session.actions if a.target_member))
    if interaction_variety >= 2:
        score += 15
        evidence.append("Adapted communication style for different situations")
    
    score = max(0, min(100, score))
    
    feedback = generate_equity_inclusion_feedback(score, inclusion_ratio)
    
    return CompetencyScore(
        name="Equity & Inclusion",
        score=score,
        feedback=feedback,
        evidence=evidence
    )

def calculate_team_morale(team_members: Dict) -> float:
    """Calculate overall team morale score (0-1)."""
    mood_scores = {
        MoodState.HAPPY: 1.0,
        MoodState.NEUTRAL: 0.5,
        MoodState.FRUSTRATED: 0.0
    }
    
    total_score = sum(mood_scores[member.mood] for member in team_members.values())
    return total_score / len(team_members)

def generate_critical_thinking_feedback(score: int, good_assignments: int, total_assignments: int) -> str:
    """Generate feedback for critical thinking competency."""
    if score >= 80:
        return "Excellent strategic thinking! You demonstrated strong analytical skills in task assignment and priority setting."
    elif score >= 60:
        return "Good critical thinking with room for improvement. Consider team member strengths more carefully when delegating."
    else:
        return "Focus on developing analytical skills. Take time to assess team capabilities before making decisions."

def generate_communication_feedback(score: int, messages: int, questions: int) -> str:
    """Generate feedback for communication competency."""
    if score >= 80:
        return "Outstanding communication! You actively engaged with team members and gathered valuable input."
    elif score >= 60:
        return "Good communication skills. Consider asking more questions to better understand team perspectives."
    else:
        return "Improve active listening and engagement. Regular communication builds trust and clarity."

def generate_teamwork_feedback(score: int, conflicts_addressed: int, happy: int, frustrated: int) -> str:
    """Generate feedback for teamwork competency."""
    if score >= 80:
        return "Excellent team management! You successfully maintained positive team dynamics and morale."
    elif score >= 60:
        return "Good teamwork skills. Pay attention to team member mood and address concerns promptly."
    else:
        return "Focus on team cohesion. Address conflicts early and ensure all members feel valued."

def generate_leadership_feedback(score: int, actions: int, morale: float) -> str:
    """Generate feedback for leadership competency."""
    if score >= 80:
        return "Strong leadership presence! You took decisive action and maintained team confidence."
    elif score >= 60:
        return "Good leadership foundation. Be more proactive in decision-making and team guidance."
    else:
        return "Develop leadership confidence. Take initiative and provide clear direction to your team."

def generate_professionalism_feedback(score: int, duration: float) -> str:
    """Generate feedback for professionalism competency."""
    if score >= 80:
        return "Exemplary professionalism! You managed time well and maintained appropriate meeting standards."
    elif score >= 60:
        return "Good professional behavior. Focus on time management and meeting efficiency."
    else:
        return "Improve professional meeting management. Practice time awareness and structured approaches."

def generate_equity_inclusion_feedback(score: int, inclusion_ratio: float) -> str:
    """Generate feedback for equity and inclusion competency."""
    if score >= 80:
        return "Excellent inclusive leadership! You ensured all team members had opportunities to contribute."
    elif score >= 60:
        return "Good awareness of inclusion. Make sure to engage with all team members equally."
    else:
        return "Focus on inclusive practices. Ensure every team member's voice is heard and valued."