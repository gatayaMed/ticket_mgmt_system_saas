// Organizations Management
document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    const container = document.getElementById('organizationsList');
    const createForm = document.getElementById('createOrgForm');
    const createModal = new bootstrap.Modal(document.getElementById('createOrgModal'));

    // Load organizations
    async function loadOrganizations() {
        try {
            const data = await api.get('/organizations/');
            const organizations = data.results || [];
            
            if (organizations.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fas fa-building fa-3x text-muted mb-3"></i>
                        <h5>No Organizations</h5>
                        <p class="text-muted">Create your first organization to get started.</p>
                        <button class="btn btn-primary" onclick="openCreateModal()">
                            <i class="fas fa-plus me-2"></i>Create Organization
                        </button>
                    </div>
                `;
            } else {
                container.innerHTML = organizations.map(org => `
                    <div class="col-md-4">
                        <div class="card h-100 shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title">${org.name}</h5>
                                <p class="card-text text-muted">${org.description || 'No description'}</p>
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="badge bg-primary">${org.user_role || 'Member'}</span>
                                    <span class="badge bg-secondary">${org.member_count || 0} members</span>
                                </div>
                                <div class="mt-3">
                                    <a href="projects.html?org=${org.id}" class="btn btn-outline-primary btn-sm">
                                        <i class="fas fa-project-diagram me-1"></i>Projects
                                    </a>
                                    <button class="btn btn-outline-danger btn-sm" onclick="deleteOrganization(${org.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');
            }
        } catch (error) {
            console.error('Error loading organizations:', error);
            container.innerHTML = `
                <div class="col-12 text-center text-danger">
                    <p>Error loading organizations. Please refresh.</p>
                </div>
            `;
        }
    }

    // Create organization
    if (createForm) {
        createForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = {
                name: formData.get('name'),
                description: formData.get('description'),
                website: formData.get('website')
            };

            try {
                await api.post('/organizations/', data);
                createModal.hide();
                this.reset();
                await loadOrganizations();
                showToast('Organization created successfully!', 'success');
            } catch (error) {
                showToast(error.error || 'Failed to create organization', 'danger');
            }
        });
    }

    // Delete organization
    window.deleteOrganization = async function(id) {
        if (confirm('Are you sure you want to delete this organization?')) {
            try {
                await api.delete(`/organizations/${id}/`);
                await loadOrganizations();
                showToast('Organization deleted successfully', 'success');
            } catch (error) {
                showToast('Failed to delete organization', 'danger');
            }
        }
    };

    // Open create modal
    window.openCreateModal = function() {
        if (createModal) {
            createModal.show();
        }
    };

    // Toast notification helper
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer') || createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 show`;
        toast.role = 'alert';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
        return container;
    }

    // Load organizations
    await loadOrganizations();
});