// Webhooks Management
let currentOrgId = null;
let webhooks = [];

document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    await loadOrganizations();

    document.getElementById('webhookOrg').addEventListener('change', function() {
        currentOrgId = this.value;
        document.getElementById('createWebhookBtn').disabled = !currentOrgId;
        if (currentOrgId) loadWebhooks();
        else document.getElementById('webhooksContainer').innerHTML =
            '<div class="text-center text-muted py-5">Select an organization to view webhooks.</div>';
    });

    document.getElementById('createWebhookForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await createWebhook();
    });
});

async function loadOrganizations() {
    try {
        const data = await api.get('/organizations/');
        const orgs = data.results || [];
        const selector = document.getElementById('webhookOrg');
        orgs.forEach(org => {
            const option = document.createElement('option');
            option.value = org.id;
            option.textContent = org.name;
            selector.appendChild(option);
        });
    } catch (e) {
        console.error('Error loading organizations:', e);
    }
}

async function loadWebhooks() {
    if (!currentOrgId) return;
    try {
        const data = await Services.getWebhooks(currentOrgId);
        webhooks = data.results || [];
        renderWebhooks();
    } catch (error) {
        console.error('Error loading webhooks:', error);
        showToast('Error loading webhooks', 'danger');
    }
}

function renderWebhooks() {
    const container = document.getElementById('webhooksContainer');

    if (webhooks.length === 0) {
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-plug fa-3x text-muted mb-3"></i>
                <p class="text-muted">No webhooks configured. Add one to start receiving events.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = webhooks.map(wh => `
        <div class="card shadow-sm mb-3 fade-in">
            <div class="card-body">
                <div class="row align-items-center">
                    <div class="col-md-3">
                        <h6 class="mb-1">${escapeHtml(wh.name)}</h6>
                        <span class="badge ${wh.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${wh.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                    <div class="col-md-4">
                        <small class="text-muted d-block">URL</small>
                        <code class="small">${escapeHtml(wh.url)}</code>
                    </div>
                    <div class="col-md-3">
                        <small class="text-muted d-block">Events</small>
                        ${(wh.events || []).map(e => `<span class="badge bg-light text-dark me-1 small">${e}</span>`).join('')}
                    </div>
                    <div class="col-md-2 text-end">
                        <button class="btn btn-sm btn-outline-info me-1" onclick="testWebhook(${wh.id})" title="Test">
                            <i class="fas fa-play"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteWebhook(${wh.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                ${wh.last_triggered ? `
                <div class="mt-2 small text-muted">
                    Last triggered: ${formatDate(wh.last_triggered)}
                    ${wh.failure_count > 0 ? ` | <span class="text-danger">Failures: ${wh.failure_count}</span>` : ''}
                </div>` : ''}
            </div>
        </div>
    `).join('');
}

async function createWebhook() {
    const name = document.getElementById('webhookName').value;
    const url = document.getElementById('webhookUrl').value;

    const events = [];
    document.querySelectorAll('#eventCheckboxes input:checked').forEach(cb => events.push(cb.value));

    if (!name || !url || events.length === 0) {
        showToast('Please fill all fields and select at least one event', 'warning');
        return;
    }

    try {
        await Services.createWebhook(currentOrgId, { name, url, events, is_active: true });
        document.getElementById('createWebhookForm').reset();
        bootstrap.Modal.getInstance(document.getElementById('createWebhookModal')).hide();
        showToast('Webhook created successfully', 'success');
        loadWebhooks();
    } catch (error) {
        console.error('Error creating webhook:', error);
        showToast('Error creating webhook', 'danger');
    }
}

async function testWebhook(webhookId) {
    try {
        const result = await Services.testWebhook(webhookId);
        if (result.error) {
            showToast(`Test failed: ${result.error}`, 'danger');
        } else {
            showToast(`Test sent! Status: ${result.status_code}`, result.status_code < 400 ? 'success' : 'warning');
        }
    } catch (error) {
        showToast('Error testing webhook', 'danger');
    }
}

async function deleteWebhook(webhookId) {
    if (!confirm('Delete this webhook?')) return;
    try {
        await Services.deleteWebhook(webhookId);
        showToast('Webhook deleted', 'success');
        loadWebhooks();
    } catch (error) {
        showToast('Error deleting webhook', 'danger');
    }
}
