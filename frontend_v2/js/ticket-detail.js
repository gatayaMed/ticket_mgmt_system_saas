// Ticket Detail View
let ticket = null;
let comments = [];
let attachments = [];
let currentUser = null;

document.addEventListener('DOMContentLoaded', async function() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return;
    }

    currentUser = auth.getCurrentUser();
    const params = getUrlParams();
    const ticketId = params.id;
    
    if (!ticketId) {
        window.location.href = '/tickets.html';
        return;
    }

    await loadTicketDetails(ticketId);
    
    // Event listeners
    document.getElementById('addCommentForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await addComment(ticketId);
    });
    
    document.getElementById('uploadAttachmentForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        await uploadAttachment(ticketId);
    });
    
    document.getElementById('updateStatusBtn').addEventListener('click', async function() {
        await updateTicketStatus(ticketId);
    });
});

async function loadTicketDetails(ticketId) {
    try {
        showLoading();
        
        // Load ticket
        ticket = await api.get(`/tickets/${ticketId}/`);
        
        // Load comments
        const commentsData = await api.get(`/tickets/${ticketId}/comments/`);
        comments = commentsData.results || [];
        
        // Load attachments
        const attachmentsData = await api.get(`/tickets/${ticketId}/attachments/`);
        attachments = attachmentsData.results || [];
        
        // Render ticket details
        renderTicketDetails(ticket);
        renderComments(comments);
        renderAttachments(attachments);
        renderHistory(ticketId);
        
        hideLoading();
    } catch (error) {
        hideLoading();
        console.error('Error loading ticket:', error);
        document.getElementById('ticketDetail').innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Error loading ticket. Please try again.
            </div>
        `;
    }
}

function renderTicketDetails(ticket) {
    const container = document.getElementById('ticketDetail');
    
    container.innerHTML = `
        <div class="card shadow-sm fade-in">
            <div class="card-header bg-white d-flex justify-content-between align-items-center">
                <div>
                    <h4 class="mb-0">${ticket.ticket_id}</h4>
                    <h5 class="text-muted mt-1">${ticket.title}</h5>
                </div>
                <div>
                    <span class="badge ${getStatusBadgeClass(ticket.status)} me-2">${ticket.status_display}</span>
                    <span class="badge ${getPriorityBadgeClass(ticket.priority)}">${ticket.priority_display}</span>
                </div>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h6>Description</h6>
                        <p>${ticket.description || 'No description provided'}</p>
                    </div>
                    <div class="col-md-4">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h6>Details</h6>
                                <table class="table table-sm table-borderless">
                                    <tr>
                                        <td><strong>Type:</strong></td>
                                        <td>${ticket.type_display || ticket.ticket_type}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Project:</strong></td>
                                        <td>${ticket.project_name}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Assignee:</strong></td>
                                        <td>${ticket.assignee_details ? ticket.assignee_details.username : 'Unassigned'}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Created By:</strong></td>
                                        <td>${ticket.created_by_details ? ticket.created_by_details.username : 'Unknown'}</td>
                                    </tr>
                                    <tr>
                                        <td><strong>Created:</strong></td>
                                        <td>${formatDate(ticket.created_at)}</td>
                                    </tr>
                                    ${ticket.due_date ? `
                                    <tr>
                                        <td><strong>Due Date:</strong></td>
                                        <td>${formatDate(ticket.due_date)}</td>
                                    </tr>
                                    ` : ''}
                                    ${ticket.estimated_hours ? `
                                    <tr>
                                        <td><strong>Est. Hours:</strong></td>
                                        <td>${ticket.estimated_hours}h</td>
                                    </tr>
                                    ` : ''}
                                    ${ticket.completed_at ? `
                                    <tr>
                                        <td><strong>Completed:</strong></td>
                                        <td>${formatDate(ticket.completed_at)}</td>
                                    </tr>
                                    ` : ''}
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Status Update -->
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="input-group">
                            <select id="newStatus" class="form-select">
                                <option value="backlog" ${ticket.status === 'backlog' ? 'selected' : ''}>Backlog</option>
                                <option value="todo" ${ticket.status === 'todo' ? 'selected' : ''}>Todo</option>
                                <option value="in_progress" ${ticket.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                <option value="review" ${ticket.status === 'review' ? 'selected' : ''}>Review</option>
                                <option value="done" ${ticket.status === 'done' ? 'selected' : ''}>Done</option>
                                <option value="closed" ${ticket.status === 'closed' ? 'selected' : ''}>Closed</option>
                            </select>
                            <button class="btn btn-primary" id="updateStatusBtn">Update Status</button>
                        </div>
                    </div>
                    <div class="col-md-6 text-end">
                        <a href="tickets.html" class="btn btn-secondary">
                            <i class="fas fa-arrow-left me-2"></i>Back to Board
                        </a>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Comments Section -->
        <div class="card shadow-sm mt-4">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-comments me-2"></i>Comments (${comments.length})</h5>
            </div>
            <div class="card-body">
                <form id="addCommentForm" class="mb-4">
                    <div class="input-group">
                        <input type="text" class="form-control" id="commentContent" placeholder="Add a comment..." required>
                        <button class="btn btn-primary" type="submit">
                            <i class="fas fa-paper-plane me-1"></i>Post
                        </button>
                    </div>
                </form>
                <div id="commentsList">
                    ${comments.length === 0 ? `
                        <div class="text-center text-muted py-3">No comments yet</div>
                    ` : `
                        ${comments.map(comment => `
                            <div class="comment-item border-bottom pb-2 mb-2">
                                <div class="d-flex justify-content-between">
                                    <strong>${comment.user_details.username}</strong>
                                    <small class="text-muted">${formatDate(comment.created_at)}</small>
                                </div>
                                <p class="mb-1">${comment.content}</p>
                                ${comment.is_edited ? '<small class="text-muted">(edited)</small>' : ''}
                            </div>
                        `).join('')}
                    `}
                </div>
            </div>
        </div>
        
        <!-- Attachments Section -->
        <div class="card shadow-sm mt-4">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-paperclip me-2"></i>Attachments (${attachments.length})</h5>
            </div>
            <div class="card-body">
                <form id="uploadAttachmentForm" class="mb-4">
                    <div class="row g-2">
                        <div class="col-md-8">
                            <input type="file" class="form-control" id="attachmentFile" required>
                        </div>
                        <div class="col-md-4">
                            <button class="btn btn-primary w-100" type="submit">
                                <i class="fas fa-upload me-1"></i>Upload
                            </button>
                        </div>
                    </div>
                    <div class="mt-2">
                        <input type="text" class="form-control" id="attachmentDescription" placeholder="Description (optional)">
                    </div>
                </form>
                <div id="attachmentsList">
                    ${attachments.length === 0 ? `
                        <div class="text-center text-muted py-3">No attachments</div>
                    ` : `
                        <div class="list-group">
                            ${attachments.map(attachment => `
                                <div class="list-group-item d-flex justify-content-between align-items-center">
                                    <div>
                                        <i class="fas fa-file me-2"></i>
                                        <a href="${attachment.file_url}" target="_blank">${attachment.filename}</a>
                                        <small class="text-muted ms-2">(${attachment.file_size_display})</small>
                                        ${attachment.description ? `<br><small class="text-muted">${attachment.description}</small>` : ''}
                                    </div>
                                    <button class="btn btn-sm btn-danger" onclick="deleteAttachment(${attachment.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            `).join('')}
                        </div>
                    `}
                </div>
            </div>
        </div>
        
        <!-- History Section -->
        <div class="card shadow-sm mt-4">
            <div class="card-header bg-white">
                <h5 class="mb-0"><i class="fas fa-history me-2"></i>History</h5>
            </div>
            <div class="card-body" id="historyList">
                <div class="text-center py-3">
                    <div class="spinner-border spinner-border-sm" role="status"></div>
                    <span class="ms-2">Loading history...</span>
                </div>
            </div>
        </div>
    `;
}

async function renderHistory(ticketId) {
    try {
        const history = await api.get(`/tickets/${ticketId}/history/`);
        
        const container = document.getElementById('historyList');
        if (history.length === 0) {
            container.innerHTML = `<div class="text-center text-muted py-3">No history available</div>`;
            return;
        }
        
        container.innerHTML = `
            <div class="timeline">
                ${history.map(item => `
                    <div class="d-flex mb-2">
                        <div class="flex-shrink-0 me-2">
                            <i class="fas fa-circle text-primary" style="font-size: 8px;"></i>
                        </div>
                        <div>
                            <strong>${item.user ? item.user.username : 'System'}</strong>
                            <span class="text-muted ms-2 small">${formatDate(item.created_at)}</span>
                            <div>${item.description}</div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    } catch (error) {
        console.error('Error loading history:', error);
        document.getElementById('historyList').innerHTML = `
            <div class="text-center text-muted py-3">Error loading history</div>
        `;
    }
}

function renderComments(comments) {
    const container = document.getElementById('commentsList');
    if (!container) return;
    
    // Already rendered in renderTicketDetails
}

function renderAttachments(attachments) {
    // Already rendered in renderTicketDetails
}

async function addComment(ticketId) {
    const content = document.getElementById('commentContent').value;
    if (!content) return;
    
    try {
        await api.post(`/tickets/${ticketId}/comments/`, { content });
        document.getElementById('commentContent').value = '';
        await loadTicketDetails(ticketId);
        showToast('Comment added!', 'success');
    } catch (error) {
        console.error('Error adding comment:', error);
        showToast('Error adding comment', 'danger');
    }
}

async function uploadAttachment(ticketId) {
    const fileInput = document.getElementById('attachmentFile');
    const description = document.getElementById('attachmentDescription').value;
    
    if (!fileInput.files.length) {
        showToast('Please select a file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    if (description) formData.append('description', description);
    
    try {
        await api.upload(`/tickets/${ticketId}/attachments/`, formData);
        fileInput.value = '';
        document.getElementById('attachmentDescription').value = '';
        await loadTicketDetails(ticketId);
        showToast('File uploaded!', 'success');
    } catch (error) {
        console.error('Error uploading attachment:', error);
        showToast('Error uploading file', 'danger');
    }
}

async function updateTicketStatus(ticketId) {
    const status = document.getElementById('newStatus').value;
    
    try {
        await api.post(`/tickets/${ticketId}/status/`, { status });
        await loadTicketDetails(ticketId);
        showToast('Status updated!', 'success');
    } catch (error) {
        console.error('Error updating status:', error);
        showToast('Error updating status', 'danger');
    }
}

window.deleteAttachment = async function(attachmentId) {
    if (!confirm('Are you sure you want to delete this attachment?')) return;
    
    try {
        await api.delete(`/attachments/${attachmentId}/`);
        const params = getUrlParams();
        await loadTicketDetails(params.id);
        showToast('Attachment deleted!', 'success');
    } catch (error) {
        console.error('Error deleting attachment:', error);
        showToast('Error deleting attachment', 'danger');
    }
};