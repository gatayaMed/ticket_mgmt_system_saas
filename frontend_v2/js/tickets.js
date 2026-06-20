// Tickets Management (Kanban Board)
let currentProjectId = null;
let projects = [];
let tickets = [];
let members = [];

document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    // Load projects
    await loadProjects();
    
    // Event listeners
    document.getElementById('projectSelector').addEventListener('change', function() {
        currentProjectId = this.value;
        if (currentProjectId) {
            loadTickets();
            loadProjectMembers(currentProjectId);
        } else {
            document.getElementById('ticketBoard').innerHTML = `
                <div class="col-12 text-center text-muted py-5">
                    <i class="fas fa-ticket-alt fa-3x mb-3"></i>
                    <p>Select a project to view tickets</p>
                </div>
            `;
        }
    });

    // Filter events
    document.getElementById('filterStatus').addEventListener('change', loadTickets);
    document.getElementById('filterPriority').addEventListener('change', loadTickets);
    document.getElementById('filterSearch').addEventListener('input', loadTickets);
    
    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', function() {
        if (currentProjectId) {
            loadTickets();
        }
    });

    // Create ticket form
    document.getElementById('createTicketForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await createTicket();
    });

    // Load project dropdown for create modal
    await loadProjectDropdown();

    // Check URL params
    const params = getUrlParams();
    if (params.project) {
        document.getElementById('projectSelector').value = params.project;
        document.getElementById('projectSelector').dispatchEvent(new Event('change'));
    }
});

async function loadProjects() {
    try {
        const data = await api.get('/organizations/');
        const organizations = data.results || [];
        
        const selector = document.getElementById('projectSelector');
        const ticketProject = document.getElementById('ticketProject');
        
        selector.innerHTML = '<option value="">-- Select Project --</option>';
        ticketProject.innerHTML = '<option value="">Select Project</option>';
        
        for (const org of organizations) {
            try {
                const projectsData = await api.get(`/organizations/${org.id}/projects/`);
                const orgProjects = projectsData.results || [];
                projects = [...projects, ...orgProjects];
                
                orgProjects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = `${org.name} - ${project.name}`;
                    selector.appendChild(option);
                    
                    const opt2 = document.createElement('option');
                    opt2.value = project.id;
                    opt2.textContent = `${org.name} - ${project.name}`;
                    ticketProject.appendChild(opt2);
                });
            } catch (e) {
                console.error(`Error loading projects for org ${org.id}:`, e);
            }
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        showToast('Error loading projects', 'danger');
    }
}

async function loadProjectDropdown() {
    // Already loaded in loadProjects()
}

async function loadProjectMembers(projectId) {
    try {
        const data = await api.get(`/projects/${projectId}/members/`);
        members = data.results || [];
        
        const assigneeSelect = document.getElementById('ticketAssignee');
        assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
        members.forEach(member => {
            const option = document.createElement('option');
            option.value = member.user;
            option.textContent = member.user_details?.email || `User ${member.user}`;
            assigneeSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading project members:', error);
    }
}

async function loadTickets() {
    if (!currentProjectId) return;
    
    try {
        showLoading();
        const status = document.getElementById('filterStatus').value;
        const priority = document.getElementById('filterPriority').value;
        const search = document.getElementById('filterSearch').value;
        
        let url = `/projects/${currentProjectId}/tickets/`;
        const params = new URLSearchParams();
        if (status) params.append('status', status);
        if (priority) params.append('priority', priority);
        if (search) params.append('search', search);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const data = await api.get(url);
        tickets = data.results || [];
        
        // Update project info
        const project = projects.find(p => p.id === parseInt(currentProjectId));
        document.getElementById('projectInfo').textContent = project ? `Project: ${project.name}` : '';
        
        renderKanbanBoard(tickets);
        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Error loading tickets:', error);
        showToast('Error loading tickets', 'danger');
    }
}

function renderKanbanBoard(tickets) {
    const statuses = [
        { key: 'backlog', label: 'Backlog' },
        { key: 'todo', label: 'Todo' },
        { key: 'in_progress', label: 'In Progress' },
        { key: 'review', label: 'Review' },
        { key: 'done', label: 'Done' },
        { key: 'closed', label: 'Closed' }
    ];
    
    const board = document.getElementById('ticketBoard');
    
    board.innerHTML = statuses.map(status => {
        const statusTickets = tickets.filter(t => t.status === status.key);
        
        return `
            <div class="ticket-column fade-in">
                <h6>
                    ${status.label}
                    <span class="badge bg-secondary float-end">${statusTickets.length}</span>
                </h6>
                ${statusTickets.length === 0 ? `
                    <div class="text-center text-muted small py-3">No tickets</div>
                ` : `
                    ${statusTickets.map(ticket => `
                        <div class="ticket-card" onclick="viewTicket(${ticket.id})">
                            <div class="d-flex justify-content-between align-items-start mb-1">
                                <strong class="small">${ticket.ticket_id}</strong>
                                <span class="badge ${getPriorityBadgeClass(ticket.priority)}">${ticket.priority_display || ticket.priority}</span>
                            </div>
                            <div class="small">${ticket.title}</div>
                            <div class="d-flex justify-content-between align-items-center mt-2">
                                <small class="text-muted">
                                    ${ticket.assignee_details ? ticket.assignee_details.username : 'Unassigned'}
                                </small>
                                <small class="text-muted">
                                    ${ticket.due_date ? formatDate(ticket.due_date) : 'No due date'}
                                </small>
                            </div>
                        </div>
                    `).join('')}
                `}
            </div>
        `;
    }).join('');
}

window.viewTicket = function(ticketId) {
    window.location.href = `/ticket-detail.html?id=${ticketId}`;
};

async function createTicket() {
    const projectId = document.getElementById('ticketProject').value;
    const title = document.getElementById('ticketTitle').value;
    const description = document.getElementById('ticketDescription').value;
    const status = document.getElementById('ticketStatus').value;
    const priority = document.getElementById('ticketPriority').value;
    const type = document.getElementById('ticketType').value;
    const assignee = document.getElementById('ticketAssignee').value;
    const dueDate = document.getElementById('ticketDueDate').value;
    const hours = document.getElementById('ticketHours').value;

    if (!projectId || !title || !description) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const data = {
            title,
            description,
            status,
            priority,
            ticket_type: type,
            organization: 1 // Get from project
        };
        
        if (assignee) data.assignee = parseInt(assignee);
        if (dueDate) data.due_date = new Date(dueDate).toISOString();
        if (hours) data.estimated_hours = parseFloat(hours);

        await api.post(`/projects/${projectId}/tickets/`, data);
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('createTicketModal'));
        modal.hide();
        document.getElementById('createTicketForm').reset();
        
        // Reload tickets
        if (currentProjectId) {
            await loadTickets();
        }
        
        showToast('Ticket created successfully!', 'success');
    } catch (error) {
        console.error('Error creating ticket:', error);
        showToast(error.error || 'Failed to create ticket', 'danger');
    }
}