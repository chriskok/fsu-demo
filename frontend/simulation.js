class SimulationManager {
    constructor() {
        this.sessionId = null;
        this.currentState = null;
        this.timer = null;
        this.startTime = null;
        this.phaseData = {
            'meet_team': {
                title: 'Meet Your Team (2 minutes)',
                description: 'Get to know your team members and understand their working styles.'
            },
            'delegate_tasks': {
                title: 'Delegate Tasks (5 minutes)',
                description: 'Assign project tasks based on team member skills and availability.'
            },
            'navigate_conflicts': {
                title: 'Navigate Conflicts (3 minutes)',
                description: 'Handle any tensions and ensure team cohesion.'
            },
            'completed': {
                title: 'Simulation Complete',
                description: 'Review your performance and get feedback.'
            }
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Start simulation
        document.getElementById('start-simulation').addEventListener('click', () => {
            this.startSimulation();
        });

        // Action buttons
        document.getElementById('ask-question-btn').addEventListener('click', () => {
            this.showQuestionModal();
        });

        document.getElementById('send-message-btn').addEventListener('click', () => {
            this.showMessageModal();
        });

        document.getElementById('delegate-task-btn').addEventListener('click', () => {
            this.showTaskModal();
        });

        document.getElementById('address-conflict-btn').addEventListener('click', () => {
            this.showConflictModal();
        });

        // Modal action buttons
        document.getElementById('send-question').addEventListener('click', () => {
            this.submitQuestion();
        });

        document.getElementById('send-message').addEventListener('click', () => {
            this.submitMessage();
        });

        document.getElementById('delegate-task').addEventListener('click', () => {
            this.submitTaskDelegation();
        });

        document.getElementById('resolve-conflict').addEventListener('click', () => {
            this.submitConflictResolution();
        });
    }

    async startSimulation() {
        try {
            const response = await fetch('/api/session/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Failed to start simulation');
            }

            const data = await response.json();
            this.sessionId = data.session_id;
            this.startTime = new Date();

            // Hide welcome screen, show simulation
            document.getElementById('welcome-screen').classList.add('d-none');
            document.getElementById('simulation-screen').classList.remove('d-none');

            // Start timer
            this.startTimer();

            // Load initial state
            await this.updateSimulationState();

        } catch (error) {
            console.error('Error starting simulation:', error);
            alert('Failed to start simulation. Please try again.');
        }
    }

    startTimer() {
        this.timer = setInterval(() => {
            const elapsed = Math.floor((new Date() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            document.getElementById('timer').textContent = 
                `Time: ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    async updateSimulationState() {
        try {
            const response = await fetch(`/api/session/${this.sessionId}/state`);
            if (!response.ok) {
                throw new Error('Failed to get simulation state');
            }

            this.currentState = await response.json();
            this.renderSimulationState();

            // Check if simulation is complete
            if (this.currentState.phase === 'completed') {
                await this.showResults();
            }

        } catch (error) {
            console.error('Error updating simulation state:', error);
        }
    }

    renderSimulationState() {
        // Update phase indicator
        const phaseInfo = this.phaseData[this.currentState.phase];
        document.getElementById('phase-indicator').textContent = `Phase: ${this.currentState.phase}`;
        document.getElementById('current-phase').textContent = phaseInfo.title;

        // Update phase content
        document.getElementById('phase-content').innerHTML = `
            <p class="lead">${phaseInfo.description}</p>
        `;

        // Render team members
        this.renderTeamMembers();

        // Render available tasks
        this.renderAvailableTasks();

        // Update modal dropdowns
        this.updateModalDropdowns();
    }

    renderTeamMembers() {
        const teamContainer = document.getElementById('team-members');
        teamContainer.innerHTML = '';

        Object.values(this.currentState.team_members).forEach(member => {
            const moodEmoji = {
                'happy': '😊',
                'neutral': '😐',
                'frustrated': '😟'
            }[member.mood] || '😐';

            const memberCard = document.createElement('div');
            memberCard.className = 'mb-3 p-3 border rounded';
            memberCard.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${member.name} ${moodEmoji}</h6>
                        <small class="text-muted">${member.role}</small>
                        <p class="mb-1 small">${member.description}</p>
                        <div class="progress mb-2" style="height: 6px;">
                            <div class="progress-bar" role="progressbar" 
                                 style="width: ${member.workload}%" 
                                 aria-valuenow="${member.workload}" aria-valuemin="0" aria-valuemax="100">
                            </div>
                        </div>
                        <small class="text-muted">Workload: ${member.workload}%</small>
                    </div>
                </div>
                ${member.current_tasks.length > 0 ? `
                    <div class="mt-2">
                        <small class="text-muted">Current tasks:</small>
                        <ul class="list-unstyled mb-0">
                            ${member.current_tasks.map(task => `<li class="small">• ${task}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
            teamContainer.appendChild(memberCard);
        });
    }

    renderAvailableTasks() {
        const tasksContainer = document.getElementById('available-tasks');
        tasksContainer.innerHTML = '';

        if (this.currentState.available_tasks) {
            this.currentState.available_tasks.forEach(task => {
                const urgencyClass = {
                    'high': 'danger',
                    'medium': 'warning',
                    'low': 'success'
                }[task.urgency] || 'secondary';

                const taskCard = document.createElement('div');
                taskCard.className = 'mb-2 p-2 border rounded';
                taskCard.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-1">${task.name}</h6>
                            <p class="mb-1 small">${task.description}</p>
                            <small class="text-muted">${task.estimated_hours}h • </small>
                            <span class="badge bg-${urgencyClass}">${task.urgency}</span>
                        </div>
                    </div>
                `;
                tasksContainer.appendChild(taskCard);
            });
        }
    }

    updateModalDropdowns() {
        // Update team member dropdowns
        const teamOptions = Object.keys(this.currentState.team_members).map(key => {
            const member = this.currentState.team_members[key];
            return `<option value="${key}">${member.name} (${member.role})</option>`;
        }).join('');

        document.getElementById('question-target').innerHTML = '<option value="">Choose a team member...</option>' + teamOptions;
        document.getElementById('message-target').innerHTML = '<option value="">Choose a team member...</option>' + teamOptions;
        document.getElementById('task-assignee').innerHTML = '<option value="">Choose a team member...</option>' + teamOptions;

        // Update task dropdown
        if (this.currentState.available_tasks) {
            const taskOptions = this.currentState.available_tasks.map(task => 
                `<option value="${task.id}">${task.name}</option>`
            ).join('');
            document.getElementById('task-select').innerHTML = '<option value="">Choose a task...</option>' + taskOptions;
        }
    }

    showQuestionModal() {
        const modal = new bootstrap.Modal(document.getElementById('questionModal'));
        modal.show();
    }

    showMessageModal() {
        const modal = new bootstrap.Modal(document.getElementById('messageModal'));
        modal.show();
    }

    showTaskModal() {
        const modal = new bootstrap.Modal(document.getElementById('taskModal'));
        modal.show();
    }

    showConflictModal() {
        const modal = new bootstrap.Modal(document.getElementById('conflictModal'));
        modal.show();
    }

    async submitQuestion() {
        const target = document.getElementById('question-target').value;
        const question = document.getElementById('question-text').value;

        if (!target || !question.trim()) {
            alert('Please select a team member and enter a question.');
            return;
        }

        await this.submitAction({
            type: 'ask_question',
            target_member: target,
            message: question
        });

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('questionModal')).hide();
        document.getElementById('question-text').value = '';
        document.getElementById('question-target').value = '';
    }

    async submitMessage() {
        const target = document.getElementById('message-target').value;
        const message = document.getElementById('message-text').value;

        if (!target || !message.trim()) {
            alert('Please select a team member and enter a message.');
            return;
        }

        await this.submitAction({
            type: 'send_message',
            target_member: target,
            message: message
        });

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('messageModal')).hide();
        document.getElementById('message-text').value = '';
        document.getElementById('message-target').value = '';
    }

    async submitTaskDelegation() {
        const taskId = document.getElementById('task-select').value;
        const assignee = document.getElementById('task-assignee').value;
        const message = document.getElementById('task-message').value;

        if (!taskId || !assignee) {
            alert('Please select both a task and a team member.');
            return;
        }

        await this.submitAction({
            type: 'delegate_task',
            target_member: assignee,
            task_id: taskId,
            message: message
        });

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('taskModal')).hide();
        document.getElementById('task-select').value = '';
        document.getElementById('task-assignee').value = '';
        document.getElementById('task-message').value = '';
    }

    async submitConflictResolution() {
        const approach = document.querySelector('input[name="conflictApproach"]:checked');

        if (!approach) {
            alert('Please select an approach to address the conflict.');
            return;
        }

        await this.submitAction({
            type: 'address_conflict',
            data: { approach: approach.value }
        });

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('conflictModal')).hide();
        document.querySelectorAll('input[name="conflictApproach"]').forEach(radio => radio.checked = false);
    }

    async submitAction(action) {
        try {
            const response = await fetch(`/api/session/${this.sessionId}/action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(action)
            });

            if (!response.ok) {
                throw new Error('Failed to submit action');
            }

            const result = await response.json();
            this.logActivity(action, result);

            // Update simulation state
            await this.updateSimulationState();

        } catch (error) {
            console.error('Error submitting action:', error);
            alert('Failed to submit action. Please try again.');
        }
    }

    logActivity(action, result) {
        const logContainer = document.getElementById('activity-log');
        const entry = document.createElement('div');
        entry.className = 'mb-2 p-2 border-start border-3 border-primary';
        
        let actionDescription = '';
        switch (action.type) {
            case 'ask_question':
                actionDescription = `Asked question to ${this.currentState.team_members[action.target_member]?.name}`;
                break;
            case 'send_message':
                actionDescription = `Sent message to ${this.currentState.team_members[action.target_member]?.name}`;
                break;
            case 'delegate_task':
                actionDescription = `Delegated task to ${this.currentState.team_members[action.target_member]?.name}`;
                break;
            case 'address_conflict':
                actionDescription = 'Addressed team conflict';
                break;
        }

        entry.innerHTML = `
            <div class="small">
                <strong>${actionDescription}</strong>
                <div class="text-muted mt-1">${result.message}</div>
                ${result.team_member_reaction ? `<div class="text-info mt-1"><em>${result.team_member_reaction}</em></div>` : ''}
                ${result.consequences && result.consequences.length > 0 ? 
                    `<div class="text-warning mt-1">${result.consequences.join(', ')}</div>` : ''}
            </div>
        `;

        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    async showResults() {
        // Stop timer
        if (this.timer) {
            clearInterval(this.timer);
        }

        try {
            const response = await fetch(`/api/session/${this.sessionId}/results`);
            if (!response.ok) {
                throw new Error('Failed to get results');
            }

            const results = await response.json();
            this.renderResults(results);

            // Hide simulation screen, show results
            document.getElementById('simulation-screen').classList.add('d-none');
            document.getElementById('results-screen').classList.remove('d-none');

        } catch (error) {
            console.error('Error getting results:', error);
            alert('Failed to get simulation results.');
        }
    }

    renderResults(results) {
        const scoresContainer = document.getElementById('competency-scores');
        scoresContainer.innerHTML = '';

        // Calculate overall rating
        const scores = Object.values(results.competency_scores);
        const averageScore = scores.reduce((sum, comp) => sum + comp.score, 0) / scores.length;
        
        let overallRating = 'Needs Improvement';
        let ratingClass = 'danger';
        if (averageScore >= 80) {
            overallRating = 'Excellent';
            ratingClass = 'success';
        } else if (averageScore >= 60) {
            overallRating = 'Good';
            ratingClass = 'warning';
        }

        // Overall summary
        const summaryCard = document.createElement('div');
        summaryCard.className = 'card mb-4';
        summaryCard.innerHTML = `
            <div class="card-body text-center">
                <h3>Overall Rating: <span class="badge bg-${ratingClass}">${overallRating}</span></h3>
                <p class="lead">Average Score: ${Math.round(averageScore)}%</p>
                <p>Duration: ${Math.round(results.total_duration)} minutes | Actions Taken: ${results.actions_taken}</p>
            </div>
        `;
        scoresContainer.appendChild(summaryCard);

        // Individual competency scores
        Object.entries(results.competency_scores).forEach(([key, competency]) => {
            const scoreClass = competency.score >= 80 ? 'success' : 
                             competency.score >= 60 ? 'warning' : 'danger';

            const competencyCard = document.createElement('div');
            competencyCard.className = 'card mb-3';
            competencyCard.innerHTML = `
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h5 class="card-title mb-0">${competency.name}</h5>
                        <span class="badge bg-${scoreClass}">${competency.score}%</span>
                    </div>
                    <div class="progress mb-3">
                        <div class="progress-bar bg-${scoreClass}" role="progressbar" 
                             style="width: ${competency.score}%" 
                             aria-valuenow="${competency.score}" aria-valuemin="0" aria-valuemax="100">
                        </div>
                    </div>
                    <p class="card-text">${competency.feedback}</p>
                    ${competency.evidence.length > 0 ? `
                        <div class="mt-2">
                            <small class="text-muted">Evidence:</small>
                            <ul class="list-unstyled mt-1">
                                ${competency.evidence.map(item => `<li class="small">• ${item}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
            scoresContainer.appendChild(competencyCard);
        });
    }
}

// Initialize simulation when page loads
document.addEventListener('DOMContentLoaded', () => {
    new SimulationManager();
});