// Services - API wrappers for backend apps
const Services = {
    // ============ Notifications ============
    async getNotifications() {
        return api.get('/notifications/');
    },

    async getUnreadCount() {
        return api.get('/notifications/unread-count/');
    },

    async markAllRead() {
        return api.post('/notifications/mark-read/', {});
    },

    async markNotificationsRead(notificationIds) {
        return api.post('/notifications/mark-read/', { notification_ids: notificationIds });
    },

    async getNotificationPreferences() {
        return api.get('/notifications/preferences/');
    },

    async updateNotificationPreferences(prefs) {
        return api.put('/notifications/preferences/', prefs);
    },

    // ============ Activity Feed ============
    async getActivityFeed(limit = 20) {
        return api.get(`/activity/feed/?limit=${limit}`);
    },

    async getEntityActivity(contentType, objectId) {
        return api.get(`/activity/entity/${contentType}/${objectId}/`);
    },

    // ============ Dashboard ============
    async getDashboardOverview() {
        return api.get('/dashboard/overview/');
    },

    async getProjectDashboard(projectId) {
        return api.get(`/dashboard/projects/${projectId}/`);
    },

    // ============ Sprints ============
    async getSprints(projectId) {
        return api.get(`/sprints/projects/${projectId}/`);
    },

    async getSprintDetail(sprintId) {
        return api.get(`/sprints/${sprintId}/`);
    },

    async createSprint(projectId, data) {
        return api.post(`/sprints/projects/${projectId}/`, data);
    },

    async updateSprint(sprintId, data) {
        return api.put(`/sprints/${sprintId}/`, data);
    },

    async deleteSprint(sprintId) {
        return api.delete(`/sprints/${sprintId}/`);
    },

    async addTicketsToSprint(sprintId, ticketIds) {
        return api.post(`/sprints/${sprintId}/add-tickets/`, { ticket_ids: ticketIds });
    },

    async completeSprint(sprintId) {
        return api.post(`/sprints/${sprintId}/complete/`);
    },

    // ============ Search ============
    async globalSearch(query) {
        return api.get(`/search/?q=${encodeURIComponent(query)}`);
    },

    async advancedTicketSearch(filters) {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([k, v]) => { if (v) params.append(k, v); });
        return api.get(`/search/tickets/advanced/?${params.toString()}`);
    },

    // ============ Reports ============
    async getTicketReport(organizationId, params = {}) {
        const query = new URLSearchParams();
        Object.entries(params).forEach(([k, v]) => { if (v) query.append(k, v); });
        return api.get(`/reports/organizations/${organizationId}/tickets/?${query.toString()}`);
    },

    async exportReport(format, data) {
        const query = new URLSearchParams({ format, data: JSON.stringify(data) });
        return api.get(`/reports/export/?${query.toString()}`);
    },

    // ============ Webhooks ============
    async getWebhooks(organizationId) {
        return api.get(`/webhooks/organizations/${organizationId}/`);
    },

    async getWebhookDetail(webhookId) {
        return api.get(`/webhooks/${webhookId}/`);
    },

    async createWebhook(organizationId, data) {
        return api.post(`/webhooks/organizations/${organizationId}/`, data);
    },

    async updateWebhook(webhookId, data) {
        return api.put(`/webhooks/${webhookId}/`, data);
    },

    async deleteWebhook(webhookId) {
        return api.delete(`/webhooks/${webhookId}/`);
    },

    async testWebhook(webhookId) {
        return api.post(`/webhooks/${webhookId}/test/`);
    }
};
