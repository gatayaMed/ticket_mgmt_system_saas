// Reports
let currentReportData = null;
let organizations = [];

document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    await loadOrganizations();

    document.getElementById('reportOrg').addEventListener('change', async function() {
        const orgId = this.value;
        document.getElementById('generateReportBtn').disabled = !orgId;
        document.getElementById('exportCsvBtn').disabled = true;
        document.getElementById('exportJsonBtn').disabled = true;
        if (orgId) await loadProjects(orgId);
    });

    document.getElementById('generateReportBtn').addEventListener('click', generateReport);
    document.getElementById('exportCsvBtn').addEventListener('click', () => exportReport('csv'));
    document.getElementById('exportJsonBtn').addEventListener('click', () => exportReport('json'));
});

async function loadOrganizations() {
    try {
        const data = await api.get('/organizations/');
        organizations = data.results || [];
        const selector = document.getElementById('reportOrg');
        organizations.forEach(org => {
            const option = document.createElement('option');
            option.value = org.id;
            option.textContent = org.name;
            selector.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading organizations:', error);
    }
}

async function loadProjects(orgId) {
    const selector = document.getElementById('reportProject');
    selector.innerHTML = '<option value="">All projects</option>';
    try {
        const data = await api.get(`/organizations/${orgId}/projects/`);
        const projects = data.results || [];
        projects.forEach(p => {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = p.name;
            selector.appendChild(option);
        });
    } catch (e) {
        console.error('Error loading projects:', e);
    }
}

async function generateReport() {
    const orgId = document.getElementById('reportOrg').value;
    const projectId = document.getElementById('reportProject').value;
    const startDate = document.getElementById('reportStart').value;
    const endDate = document.getElementById('reportEnd').value;

    if (!orgId) {
        showToast('Please select an organization', 'warning');
        return;
    }

    try {
        const params = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        if (projectId) params.project_id = projectId;

        currentReportData = await Services.getTicketReport(orgId, params);
        renderReport(currentReportData);

        document.getElementById('exportCsvBtn').disabled = false;
        document.getElementById('exportJsonBtn').disabled = false;
    } catch (error) {
        console.error('Error generating report:', error);
        showToast('Error generating report', 'danger');
    }
}

function renderReport(report) {
    const container = document.getElementById('reportResults');
    const summary = report.summary || report;

    container.innerHTML = `
        <div class="row g-4 mb-4 fade-in">
            <div class="col-md-3">
                <div class="card bg-primary text-white"><div class="card-body text-center">
                    <h3>${summary.total_tickets || 0}</h3><small>Total Tickets</small>
                </div></div>
            </div>
            <div class="col-md-3">
                <div class="card bg-success text-white"><div class="card-body text-center">
                    <h3>${summary.done || 0}</h3><small>Completed</small>
                </div></div>
            </div>
            <div class="col-md-3">
                <div class="card bg-warning text-white"><div class="card-body text-center">
                    <h3>${summary.in_progress || 0}</h3><small>In Progress</small>
                </div></div>
            </div>
            <div class="col-md-3">
                <div class="card bg-danger text-white"><div class="card-body text-center">
                    <h3>${summary.avg_completion_time ? Math.round(summary.avg_completion_time) + 'd' : 'N/A'}</h3><small>Avg. Completion</small>
                </div></div>
            </div>
        </div>

        <div class="card shadow-sm mb-4">
            <div class="card-header bg-white"><h5 class="mb-0">Ticket Breakdown</h5></div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>By Status</h6>
                        <div class="mb-2">Backlog: <strong>${summary.backlog || 0}</strong></div>
                        <div class="mb-2">Todo: <strong>${summary.todo || 0}</strong></div>
                        <div class="mb-2">In Progress: <strong>${summary.in_progress || 0}</strong></div>
                        <div class="mb-2">Review: <strong>${summary.review || 0}</strong></div>
                        <div class="mb-2">Done: <strong>${summary.done || 0}</strong></div>
                    </div>
                    <div class="col-md-6">
                        <h6>By Priority</h6>
                        <div class="mb-2">Critical: <strong>${summary.critical || 0}</strong></div>
                        <div class="mb-2">High: <strong>${summary.high || 0}</strong></div>
                        <div class="mb-2">Medium: <strong>${summary.medium || 0}</strong></div>
                        <div class="mb-2">Low: <strong>${summary.low || 0}</strong></div>
                    </div>
                </div>
            </div>
        </div>

        ${summary.recent_activity ? `
        <div class="card shadow-sm">
            <div class="card-header bg-white"><h5 class="mb-0">Recent Activity</h5></div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-sm table-hover">
                        <thead><tr><th>Ticket ID</th><th>Title</th><th>Status</th><th>Updated</th></tr></thead>
                        <tbody>
                            ${summary.recent_activity.map(t => `
                                <tr>
                                    <td><code>${t.ticket_id || '#' + t.id}</code></td>
                                    <td>${escapeHtml(t.title)}</td>
                                    <td><span class="badge-status badge-status-${t.status}">${t.status}</span></td>
                                    <td><small>${formatDate(t.updated_at)}</small></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>` : ''}
    `;
}

async function exportReport(format) {
    if (!currentReportData) {
        showToast('Generate a report first', 'warning');
        return;
    }
    try {
        const response = await Services.exportReport(format, currentReportData);
        // For CSV exports, we may get a blob
        if (typeof response === 'string' && format === 'csv') {
            const blob = new Blob([response], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${new Date().toISOString().slice(0,10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        } else if (typeof response === 'string') {
            const blob = new Blob([response], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${new Date().toISOString().slice(0,10)}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }
        showToast(`Report exported as ${format.toUpperCase()}`, 'success');
    } catch (error) {
        console.error('Error exporting report:', error);
        showToast('Error exporting report', 'danger');
    }
}
