// Notifications - Bell dropdown
let notificationPollInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    if (!auth.isAuthenticated()) return;
    initNotificationBell();
});

function initNotificationBell() {
    fetchUnreadCount();
    // Poll every 30 seconds
    notificationPollInterval = setInterval(fetchUnreadCount, 30000);
}

async function fetchUnreadCount() {
    try {
        const data = await Services.getUnreadCount();
        const badge = document.getElementById('notificationBadge');
        const count = data.unread_count || 0;
        if (badge) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = count > 0 ? 'inline' : 'none';
        }
    } catch (e) {
        // Silently fail - notification bell is non-critical
    }
}

async function loadNotifications() {
    try {
        const data = await Services.getNotifications();
        const notifications = data.results || [];
        const dropdown = document.getElementById('notificationDropdown');
        
        if (notifications.length === 0) {
            dropdown.innerHTML = `
                <div class="text-center text-muted py-3 px-3" style="min-width: 320px;">
                    <i class="fas fa-bell-slash fa-2x mb-2"></i>
                    <p class="mb-0 small">No notifications</p>
                </div>
            `;
            return;
        }

        dropdown.innerHTML = `
            <div style="min-width: 350px; max-height: 400px; overflow-y: auto;">
                <div class="d-flex justify-content-between align-items-center px-3 pt-2 pb-1">
                    <small class="fw-bold text-muted">NOTIFICATIONS</small>
                    <a href="#" class="small text-decoration-none" onclick="markAllNotificationsRead(event)">
                        Mark all read
                    </a>
                </div>
                ${notifications.slice(0, 15).map(n => `
                    <a href="${n.link || '#'}" class="dropdown-item py-2 ${n.is_read ? '' : 'bg-light'}"
                       onclick="${n.is_read ? '' : `markNotificationRead(event, ${n.id})`}">
                        <div class="d-flex">
                            <div class="me-2">
                                <span class="badge rounded-pill ${getNotificationIconClass(n.type)}">
                                    <i class="fas ${getNotificationIcon(n.type)} fa-sm"></i>
                                </span>
                            </div>
                            <div class="flex-grow-1" style="min-width: 0;">
                                <div class="small fw-bold ${n.is_read ? 'text-muted' : ''}">${escapeHtml(n.title)}</div>
                                <div class="small text-muted text-truncate">${escapeHtml(n.message)}</div>
                                <div class="small text-muted mt-1">
                                    <i class="far fa-clock me-1"></i>${timeAgo(n.created_at)}
                                </div>
                            </div>
                        </div>
                    </a>
                `).join('')}
                ${notifications.length > 15 ? `
                    <div class="text-center py-2">
                        <small class="text-muted">Showing 15 of ${notifications.length}</small>
                    </div>
                ` : ''}
            </div>
        `;
    } catch (e) {
        console.error('Error loading notifications:', e);
    }
}

async function markAllNotificationsRead(e) {
    e.preventDefault();
    e.stopPropagation();
    try {
        await Services.markAllRead();
        fetchUnreadCount();
        loadNotifications();
    } catch (e) {}
}

async function markNotificationRead(e, id) {
    e.preventDefault();
    e.stopPropagation();
    try {
        await Services.markNotificationsRead([id]);
        fetchUnreadCount();
    } catch (e) {}
}

function getNotificationIconClass(type) {
    const map = {
        'ticket_created': 'bg-success',
        'ticket_assigned': 'bg-primary',
        'ticket_status_changed': 'bg-warning text-dark',
        'comment_added': 'bg-info text-dark',
        'mention': 'bg-danger',
        'ticket_due': 'bg-warning text-dark',
        'ticket_overdue': 'bg-danger',
        'project_created': 'bg-success',
        'member_added': 'bg-info text-dark'
    };
    return map[type] || 'bg-secondary';
}

function getNotificationIcon(type) {
    const map = {
        'ticket_created': 'fa-plus-circle',
        'ticket_assigned': 'fa-user-check',
        'ticket_status_changed': 'fa-exchange-alt',
        'comment_added': 'fa-comment',
        'mention': 'fa-at',
        'ticket_due': 'fa-clock',
        'ticket_overdue': 'fa-exclamation-triangle',
        'project_created': 'fa-folder-plus',
        'member_added': 'fa-user-plus'
    };
    return map[type] || 'fa-bell';
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
