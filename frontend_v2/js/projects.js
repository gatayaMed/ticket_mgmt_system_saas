// Projects Management
let currentOrganizationId = null;
let organizations = [];
let projects = [];

document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    // Load organizations
    await loadOrganizations();
    await loadProjects();

    // Event listeners
    document.getElementById('orgSelector').addEventListener('change', function() {
        currentOrganizationId = this.value;
        if (currentOrganizationId) {
            loadProjects();
            // Update projects dropdown in create modal
            loadProjectsDropdown(currentOrganizationId);
        } else {
            document.getElementById('projectsList').innerHTML = `
                <div class="col-12 text-center text-muted py-5">
                    <i class="fas fa-project-diagram fa-3x mb-3"></i>
                    <p>Select an organization to view projects</p>
                </div>
            `;
        }
    });

    // Create project form
    document.getElementById('createProjectForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await createProject();
    });

    // Load organization dropdown for create modal
    await loadOrganizationDropdowns();
});

async function loadOrganizations() {
    try {
        const data = await api.get('/organizations/');
        organizations = data.results || [];
        
        const selector = document.getElementById('orgSelector');
        const projectOrg = document.getElementById('projectOrg');
        
        // Clear existing options
        selector.innerHTML = '<option value="">-- Select Organization --</option>';
        
        organizations.forEach(org => {
            const option = document.createElement('option');
            option.value = org.id;
            option.textContent = org.name;
            selector.appendChild(option);
            
            // Also add to project org dropdown
            const opt2 = document.createElement('option');
            opt2.value = org.id;
            opt2.textContent = org.name;
            projectOrg.appendChild(opt2);
        });
        
        // Check URL params for org selection
        const params = getUrlParams();
        if (params.org) {
            selector.value = params.org;
            currentOrganizationId = params.org;
            selector.dispatchEvent(new Event('change'));
        }
    } catch (error) {
        console.error('Error loading organizations:', error);
        showToast('Error loading organizations', 'danger');
    }
}

async function loadProjects() {
    if (!currentOrganizationId) return;
    
    try {
        showLoading();
        const data = await api.get(`/organizations/${currentOrganizationId}/projects/`);
        projects = data.results || [];
        
        const container = document.getElementById('projectsList');
        
        if (projects.length === 0) {
            container.innerHTML = `
                <div class="col-12 text-center py-5">
                    <i class="fas fa-folder-open fa-3x text-muted mb-3"></i>
                    <h5>No Projects</h5>
                    <p class="text-muted">Create your first project in this organization.</p>
                </div>
            `;
        } else {
            container.innerHTML = projects.map(project => `
                <div class="col-md-4">
                    <div class="card h-100 shadow-sm fade-in">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <h5 class="card-title">${project.name}</h5>
                                <span class="badge ${getStatusBadgeClass(project.status)}">${project.status_display || project.status}</span>
                            </div>
                            <p class="card-text text-muted small">${project.description || 'No description'}</p>
                            <div class="d-flex gap-2 mb-2">
                                <span class="badge ${getPriorityBadgeClass(project.priority)}">${project.priority_display || project.priority}</span>
                                <span class="badge bg-secondary">${project.member_count || 0} members</span>
                            </div>
                            <div class="progress mb-2" style="height: 6px;">
                                <div class="progress-bar bg-success" style="width: ${project.progress || 0}%"></div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">${project.created_at ? formatDate(project.created_at) : 'N/A'}</small>
                                <div>
                                    <button class="btn btn-outline-primary btn-sm" onclick="viewProject(${project.id})">
                                        <i class="fas fa-eye"></i>
                                    </button>
                                    <a href="tickets.html?project=${project.id}" class="btn btn-primary btn-sm">
                                        <i class="fas fa-ticket-alt"></i>
                                    </a>
                                    <button class="btn btn-outline-danger btn-sm" onclick="deleteProject(${project.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Error loading projects:', error);
        showToast('Error loading projects', 'danger');
    }
}

async function loadProjectsDropdown(orgId) {
    try {
        const data = await api.get(`/organizations/${orgId}/projects/`);
        const projects = data.results || [];
        const selector = document.getElementById('ticketProject');
        
        selector.innerHTML = '<option value="">Select Project</option>';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            selector.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading projects dropdown:', error);
    }
}

async function loadOrganizationDropdowns() {
    try {
        const data = await api.get('/organizations/');
        const orgs = data.results || [];
        
        const projectOrg = document.getElementById('projectOrg');
        projectOrg.innerHTML = '<option value="">Select Organization</option>';
        orgs.forEach(org => {
            const option = document.createElement('option');
            option.value = org.id;
            option.textContent = org.name;
            projectOrg.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

async function createProject() {
    const orgId = document.getElementById('projectOrg').value;
    const name = document.getElementById('projectName').value;
    const description = document.getElementById('projectDescription').value;
    const status = document.getElementById('projectStatus').value;
    const priority = document.getElementById('projectPriority').value;
    const dueDate = document.getElementById('projectDueDate').value;

    if (!orgId || !name) {
        showToast('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const data = {
            name,
            description,
            status,
            priority,
            organization: parseInt(orgId)
        };
        
        if (dueDate) {
            data.due_date = new Date(dueDate).toISOString();
        }

        await api.post(`/organizations/${orgId}/projects/`, data);
        
        // Close modal and reset form
        const modal = bootstrap.Modal.getInstance(document.getElementById('createProjectModal'));
        modal.hide();
        document.getElementById('createProjectForm').reset();
        
        // Reload projects
        if (currentOrganizationId) {
            await loadProjects();
        }
        
        showToast('Project created successfully!', 'success');
    } catch (error) {
        console.error('Error creating project:', error);
        showToast(error.error || 'Failed to create project', 'danger');
    }
}

window.viewProject = async function(projectId) {
    try {
        const project = projects.find(p => p.id === projectId);
        if (!project) return;
        
        const modal = new bootstrap.Modal(document.getElementById('projectDetailModal'));
        document.getElementById('projectDetailTitle').textContent = project.name;
        document.getElementById('projectDetailBody').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Description:</strong><br>${project.description || 'No description'}</p>
                    <p><strong>Status:</strong> <span class="badge ${getStatusBadgeClass(project.status)}">${project.status_display || project.status}</span></p>
                    <p><strong>Priority:</strong> <span class="badge ${getPriorityBadgeClass(project.priority)}">${project.priority_display || project.priority}</span></p>
                </div>
                <div class="col-md-6">
                    <p><strong>Created:</strong> ${formatDate(project.created_at)}</p>
                    <p><strong>Members:</strong> ${project.member_count || 0}</p>
                    <p><strong>Progress:</strong> ${project.progress || 0}%</p>
                    ${project.due_date ? `<p><strong>Due Date:</strong> ${formatDate(project.due_date)}</p>` : ''}
                </div>
            </div>
        `;
        document.getElementById('viewTicketsBtn').href = `tickets.html?project=${projectId}`;
        modal.show();
    } catch (error) {
        console.error('Error viewing project:', error);
        showToast('Error loading project details', 'danger');
    }
};

window.deleteProject = async function(projectId) {
    if (!confirm('Are you sure you want to delete this project? This will also delete all associated tickets.')) {
        return;
    }
    
    try {
        await api.delete(`/projects/${projectId}/`);
        await loadProjects();
        showToast('Project deleted successfully', 'success');
    } catch (error) {
        console.error('Error deleting project:', error);
        showToast('Failed to delete project', 'danger');
    }
};