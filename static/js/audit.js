const Audit = {
  logs: [],

  async load() {
    try {
      this.logs = await API.getAuditLogs({ limit: 100 });
      this.renderAuditList();
    } catch (err) {
      console.error("Failed to load audit logs:", err);
      App.toast("Failed to load audit logs", "error");
    }
  },

  renderAuditList() {
    const listEl = document.getElementById("audit-logs-list");
    if (!listEl) return;

    if (this.logs.length === 0) {
      listEl.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--border-radius-md); border: 1px solid var(--border-color);">
          No audit logs recorded yet.
        </div>
      `;
      return;
    }

    listEl.innerHTML = `
      <div class="table-responsive">
        <table class="data-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Role</th>
              <th>Action</th>
              <th>Status</th>
              <th>Details</th>
              <th>IP Address</th>
            </tr>
          </thead>
          <tbody>
            ${this.logs.map(log => `
              <tr>
                <td style="font-size: 0.78rem; color: var(--text-secondary);">${new Date(log.timestamp).toLocaleString()}</td>
                <td style="font-weight: 600;">${log.user_username}</td>
                <td><span class="user-role-badge ${log.user_role.toLowerCase()}">${log.user_role}</span></td>
                <td style="font-weight: 600; color: var(--text-primary);">${log.action}</td>
                <td>
                  <span class="badge ${log.status === 'Success' ? 'badge-success' : (log.status === 'Warning' ? 'badge-warning' : 'badge-danger')}">
                    ${log.status}
                  </span>
                </td>
                <td style="font-size: 0.82rem; color: var(--text-secondary); max-width: 300px; overflow: hidden; text-overflow: ellipsis;">${log.details || '—'}</td>
                <td style="font-size: 0.78rem; color: var(--text-muted);">${log.ip_address || '—'}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  }
};
