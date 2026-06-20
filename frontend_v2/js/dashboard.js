// Dashboard Logic
document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }
    await loadDashboard();
});

async function refreshDashboard() {
    await loadDashboard();
    showToast('Dashboard refreshed', 'success');
}

async function loadDashboard() {
    try {
        // Try to get comprehensive dashboard stats from backend
        let stats = null;
        try {
            stats = await Services.getDashboardOverview();
        } catch (e) {
            // Fallback to manual calculation if overview endpoint fails
            console.log('Dashboard overview endpoint not available, using fallback');
        }

        if (stats) {
            // Use real backend stats
            document.getElementById('orgCount').textContent = stats.organizations || 0;
            document.getElementById('projectCount').textContent = stats.projects || 0;

            const tickets = stats.tickets || {};
            document.getElementById('ticketCount').textContent = tickets.total || 0;
            document.getElementById('overdueCount').textContent = stats.overdue || 0;
            document.getElementById('backlogCount').textContent = tickets.backlog || 0;
            document.getElementById('todoCount').textContent = tickets.todo || 0;
            document.getElementById('inProgressCount').textContent = tickets.in_progress || 0;
            document.getElementById('reviewCount').textContent = tickets.review || 0;
            document.getElementById('doneCount').textContent = tickets.done || 0;
            document.getElementById('completedThisWeek').textContent = stats.completed_this_week || 0;
        }

        // Load organizations
        const orgData = await api.get('/organizations/');
        const organizations = orgData.results || [];

        if (!stats) {
            // Manual fallback counts
            document.getElementById('orgCount').textContent = organizations.length;
            let totalProjects = 0;
            for (const org of organizations) {
                try {
                    const projects = await api.get(`/organizations/${org.id}/projects/`);
                    totalProjects += projects.count || 0;
                } catch (e) {}
            }
            document.getElementById('projectCount').textContent = totalProjects;
        }

        // Render organizations
        renderOrganizations(organizations);

        // Load activity feed
        loadActivityFeed();

    } catch (error) {
        console.error('Error loading dashboard:', error);
        document.getElementById('organizationsList').innerHTML =
            '<div class="text-center text-danger py-3">Error loading dashboard. Please try again.</div>';
    }
}

function renderOrganizations(organizations) {
    const container = document.getElementById('organizationsList');

    if (organizations.length === 0) {
        container.innerHTML = `
            <div class="text-center py-3">
                <p class="text-muted">You are not a member of any organization yet.</p>
                <a href="organizations.html" class="btn btn-primary btn-sm">Create Organization</a>
            </div>
        `;
        return;
    }

    container.innerHTML = organizations.slice(0, 6).map(org => `
        <div class="d-flex align-items-center mb-3 pb-2 border-bottom">
            <div class="flex-grow-1">
                <strong>${escapeHtml(org.name)}</strong>
                <div class="small text-muted">
                    <span class="badge bg-primary me-1">${org.user_role || 'Member'}</span>
                    ${org.member_count || 0} members
                </div>
            </div>
            <a href="projects.html?org=${org.id}" class="btn btn-sm btn-outline-secondary">
                <i class="fas fa-arrow-right"></i>
            </a>
        </div>
    `).join('');

    if (organizations.length > 6) {
        container.innerHTML += `
            <div class="text-center mt-2">
                <a href="organizations.html" class="small">+${organizations.length - 6} more</a>
            </div>
        `;
    }
}

async function loadActivityFeed() {
    try {
        const data = await Services.getActivityFeed(15);
        const activities = data.results || [];
        const container = document.getElementById('activityFeed');

        if (activities.length === 0) {
            container.innerHTML = '<div class="text-center text-muted py-3">No recent activity.</div>';
            return;
        }

        container.innerHTML = activities.map(a => `
            <div class="d-flex mb-2 pb-2 border-bottom small">
                <div class="me-2">
                    <span class="badge ${getActivityBadgeClass(a.action)}">
                        <i class="fas ${getActivityIcon(a.action)} fa-xs"></i>
                    </span>
                </div>
                <div class="flex-grow-1">
                    <strong>${escapeHtml(a.user)}</strong>
                    <span class="text-muted">${escapeHtml(a.description)}</span>
                    <div class="text-muted" style="font-size: 0.7rem;">${timeAgo(a.created_at)}</div>
                </div>
            </div>
        `).join('');

        // Store timeAgo for use
        window._timeAgo = timeAgo;
    } catch (e) {
        document.getElementById('activityFeed').innerHTML =
            '<div class="text-center text-muted py-3">Activity feed unavailable.</div>';
    }
}

function getActivityBadgeClass(action) {
    const map = {
        'created': 'bg-success',
        'updated': 'bg-primary',
        'deleted': 'bg-danger',
        'status_changed': 'bg-warning text-dark',
        'assigned': 'bg-info text-dark',
        'commented': 'bg-info text-dark',
        'attached': 'bg-secondary',
        'completed': 'bg-success'
    };
    return map[action] || 'bg-secondary';
}

function getActivityIcon(action) {
    const map = {
        'created': 'fa-plus-circle',
        'updated': 'fa-edit',
        'deleted': 'fa-trash',
        'status_changed': 'fa-exchange-alt',
        'assigned': 'fa-user-check',
        'commented': 'fa-comment',
        'attached': 'fa-paperclip',
        'completed': 'fa-check-circle'
    };
    return map[action] || 'fa-circle';
}

function timeAgo(dateString) {
    const now = new Date();
    const past = new Date(dateString);
    const seconds = Math.floor((now - past) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;
    return past.toLocaleDateString();
}
