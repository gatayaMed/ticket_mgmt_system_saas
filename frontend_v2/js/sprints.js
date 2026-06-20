// Sprints Management
let currentProjectId = null;
let projects = [];
let sprints = [];

document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    await loadProjects();

    document.getElementById('projectSelector').addEventListener('change', function() {
        currentProjectId = this.value;
        document.getElementById('createSprintBtn').disabled = !currentProjectId;
        if (currentProjectId) {
            loadSprints();
            const project = projects.find(p => p.id === parseInt(currentProjectId));
            document.getElementById('projectInfo').textContent = project ? `Project: ${project.name}` : '';
        } else {
            document.getElementById('sprintsContainer').innerHTML =
                '<div class="text-center text-muted py-5">Select a project to view sprints.</div>';
            document.getElementById('projectInfo').textContent = 'Select a project to view sprints';
        }
    });

    document.getElementById('createSprintForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await createSprint();
    });

    // Global search
    document.getElementById('searchInput').addEventListener('keypress', async function(e) {
        if (e.key === 'Enter') {
            await globalSearch(this.value);
        }
    });
});

async function loadProjects() {
    try {
        const data = await api.get('/organizations/');
        const organizations = data.results || [];
        const selector = document.getElementById('projectSelector');

        for (const org of organizations) {
            try {
                const projectsData = await api.get(`/organizations/${org.id}/projects/`);
                const orgProjects = projectsData.results || [];
                orgProjects.forEach(p => {
                    projects.push(p);
                    const option = document.createElement('option');
                    option.value = p.id;
                    option.textContent = `${org.name} / ${p.name}`;
                    selector.appendChild(option);
                });
            } catch (e) {
                console.error(`Error loading projects for org ${org.id}:`, e);
            }
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function loadSprints() {
    if (!currentProjectId) return;
    try {
        const data = await Services.getSprints(currentProjectId);
        sprints = data.results || [];
        renderSprints();
    } catch (error) {
        console.error('Error loading sprints:', error);
        showToast('Error loading sprints', 'danger');
    }
}

function renderSprints() {
    const container = document.getElementById('sprintsContainer');

    if (sprints.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-running fa-3x text-muted mb-3"></i>
                <p class="text-muted">No sprints yet. Create your first sprint.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = sprints.map(sprint => {
        const progress = sprint.progress || 0;
        const statusBadge = getSprintStatusBadge(sprint.status);
        const daysRemaining = Math.ceil((new Date(sprint.end_date) - new Date()) / (1000 * 60 * 60 * 24));

        return `
            <div class="card shadow-sm mb-3 fade-in">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <h5 class="mb-1">
                                <a href="#" onclick="viewSprintDetail(${sprint.id})" class="text-decoration-none">${escapeHtml(sprint.name)}</a>
                            </h5>
                            <span class="badge ${statusBadge.class}">${statusBadge.label}</span>
                            ${daysRemaining > 0 && sprint.status !== 'completed' ? `
                                <small class="text-muted ms-2">${daysRemaining} days left</small>
                            ` : ''}
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted d-block">Tickets</small>
                            <strong>${sprint.ticket_count || 0}</strong>
                        </div>
                        <div class="col-md-2">
                            <small class="text-muted d-block">Points</small>
                            <strong>${sprint.completed_points || 0} / ${sprint.total_points || 0}</strong>
                        </div>
                        <div class="col-md-3">
                            <small class="text-muted d-block mb-1">Progress</small>
                            <div class="progress" style="height: 8px;">
                                <div class="progress-bar ${progress === 100 ? 'bg-success' : 'bg-primary'}"
                                     style="width: ${progress}%"></div>
                            </div>
                            <small class="text-muted">${progress}%</small>
                        </div>
                        <div class="col-md-2 text-end">
                            ${sprint.status !== 'completed' ? `
                                <button class="btn btn-sm btn-outline-success me-1" onclick="completeSprint(${sprint.id})" title="Complete Sprint">
                                    <i class="fas fa-check"></i>
                                </button>
                            ` : ''}
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteSprint(${sprint.id})" title="Delete Sprint">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function createSprint() {
    const name = document.getElementById('sprintName').value;
    const goal = document.getElementById('sprintGoal').value;
    const startDate = document.getElementById('sprintStart').value;
    const endDate = document.getElementById('sprintEnd').value;

    if (!name || !startDate || !endDate) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }

    if (new Date(startDate) >= new Date(endDate)) {
        showToast('End date must be after start date', 'warning');
        return;
    }

    try {
        await Services.createSprint(currentProjectId, {
            name, goal, start_date: startDate, end_date: endDate, status: 'planning'
        });

        document.getElementById('createSprintForm').reset();
        bootstrap.Modal.getInstance(document.getElementById('createSprintModal')).hide();
        showToast('Sprint created successfully', 'success');
        loadSprints();
    } catch (error) {
        console.error('Error creating sprint:', error);
        showToast('Error creating sprint', 'danger');
    }
}

async function completeSprint(sprintId) {
    if (!confirm('Complete this sprint? Unfinished tickets will remain in their current status.')) return;
    try {
        await Services.completeSprint(sprintId);
        showToast('Sprint completed', 'success');
        loadSprints();
    } catch (error) {
        showToast('Error completing sprint', 'danger');
    }
}

async function deleteSprint(sprintId) {
    if (!confirm('Delete this sprint?')) return;
    try {
        await Services.deleteSprint(sprintId);
        showToast('Sprint deleted', 'success');
        loadSprints();
    } catch (error) {
        showToast('Error deleting sprint', 'danger');
    }
}

async function viewSprintDetail(sprintId) {
    try {
        const sprint = await Services.getSprintDetail(sprintId);
        const modal = new bootstrap.Modal(document.getElementById('sprintDetailModal'));
        document.getElementById('sprintDetailTitle').textContent = sprint.name;

        const progress = sprint.progress || 0;
        const statusBadge = getSprintStatusBadge(sprint.status);

        document.getElementById('sprintDetailBody').innerHTML = `
            <div class="row mb-4">
                <div class="col-md-8">
                    <h5>${escapeHtml(sprint.name)}</h5>
                    <span class="badge ${statusBadge.class} me-2">${statusBadge.label}</span>
                    ${sprint.goal ? `<p class="text-muted mt-2">${escapeHtml(sprint.goal)}</p>` : ''}
                </div>
                <div class="col-md-4 text-end">
                    <div class="mb-2">
                        <small class="text-muted">Progress</small>
                        <div class="progress" style="height: 10px;">
                            <div class="progress-bar ${progress === 100 ? 'bg-success' : 'bg-primary'}" style="width: ${progress}%"></div>
                        </div>
                        <strong>${progress}%</strong>
                    </div>
                    <div><small class="text-muted">Tickets: ${sprint.ticket_count || 0}</small></div>
                    <div><small class="text-muted">Points: ${sprint.completed_points || 0} / ${sprint.total_points || 0}</small></div>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-6">
                    <p><strong>Start:</strong> ${formatDate(sprint.start_date)}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>End:</strong> ${formatDate(sprint.end_date)}</p>
                </div>
            </div>
            <hr>
            <h6>Sprint Stats</h6>
            <div class="table-responsive">
                <table class="table table-sm">
                    <thead><tr><th>Status</th><th>Count</th></tr></thead>
                    <tbody>
                        <tr><td>Backlog</td><td>?</td></tr>
                        <tr><td>Todo</td><td>?</td></tr>
                        <tr><td>In Progress</td><td>?</td></tr>
                        <tr><td>Review</td><td>?</td></tr>
                        <tr><td>Done</td><td>?</td></tr>
                    </tbody>
                </table>
            </div>
        `;
        modal.show();
    } catch (error) {
        showToast('Error loading sprint details', 'danger');
    }
}

function getSprintStatusBadge(status) {
    const map = {
        'planning': { class: 'badge bg-secondary', label: 'Planning' },
        'active': { class: 'badge bg-primary', label: 'Active' },
        'completed': { class: 'badge bg-success', label: 'Completed' },
        'cancelled': { class: 'badge bg-danger', label: 'Cancelled' }
    };
    return map[status] || { class: 'badge bg-secondary', label: status };
}

async function globalSearch(query) {
    if (!query || query.length < 2) return;
    try {
        const results = await Services.globalSearch(query);
        // Redirect to tickets page with search query
        window.location.href = `tickets.html?search=${encodeURIComponent(query)}`;
    } catch (e) {}
}
