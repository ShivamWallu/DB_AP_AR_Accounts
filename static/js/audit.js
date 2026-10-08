const Audit = {
  logs: [],
  total: 0,
  page: 1,
  pageSize: 15,
  totalPages: 1,
  search: "",
  status: "",
  role: "",

  async load() {
    this.renderSkeleton();
    await this.fetchData();
  },

  renderSkeleton() {
    const listEl = document.getElementById("audit-logs-list");
    if (!listEl) return;

    listEl.innerHTML = `
      <!-- Audit Filter Bar -->
      <div class="filter-bar" style="margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem; align-items: flex-end;">
        <div class="filter-group" style="flex: 2; min-width: 200px;">
          <label class="filter-label">Search Audit Logs</label>
          <div class="search-input-wrapper">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="text" id="audit-search-input" class="form-control" placeholder="Search user, action, voucher, IP..." value="${this.search}" />
          </div>
        </div>
        <div class="filter-group" style="min-width: 140px;">
          <label class="filter-label">Status</label>
          <select id="audit-status-select" class="form-select">
            <option value="">All Statuses</option>
            <option value="Success" ${this.status === 'Success' ? 'selected' : ''}>Success</option>
            <option value="Warning" ${this.status === 'Warning' ? 'selected' : ''}>Warning</option>
            <option value="Failed" ${this.status === 'Failed' ? 'selected' : ''}>Failed</option>
          </select>
        </div>
        <div class="filter-group" style="min-width: 140px;">
          <label class="filter-label">User Role</label>
          <select id="audit-role-select" class="form-select">
            <option value="">All Roles</option>
            <option value="Admin" ${this.role === 'Admin' ? 'selected' : ''}>Admin</option>
            <option value="Employee" ${this.role === 'Employee' ? 'selected' : ''}>Employee</option>
          </select>
        </div>
        <div class="filter-group" style="align-self: flex-end;">
          <button type="button" id="audit-btn-clear" class="btn btn-secondary btn-sm" style="padding: 0.42rem 0.85rem; height: 34px;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            Reset
          </button>
        </div>
      </div>

      <!-- Audit Table Container -->
      <div id="audit-table-wrapper" class="table-responsive">
        <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
          <span style="display:inline-block;width:14px;height:14px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:rotate 0.7s linear infinite;margin-right:6px;"></span>
          Loading audit records...
        </div>
      </div>

      <!-- Professional Pagination Bar -->
      <div id="audit-pagination-bar" class="dt-pagination-bar" style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); flex-wrap: wrap; gap: 0.75rem;">
      </div>
    `;

    this.bindEvents();
  },

  bindEvents() {
    const searchInput = document.getElementById("audit-search-input");
    const statusSelect = document.getElementById("audit-status-select");
    const roleSelect = document.getElementById("audit-role-select");
    const clearBtn = document.getElementById("audit-btn-clear");

    let searchTimer = null;
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(() => {
          this.search = e.target.value.trim();
          this.page = 1;
          this.fetchData();
        }, 300);
      });
    }

    if (statusSelect) {
      statusSelect.addEventListener("change", (e) => {
        this.status = e.target.value;
        this.page = 1;
        this.fetchData();
      });
    }

    if (roleSelect) {
      roleSelect.addEventListener("change", (e) => {
        this.role = e.target.value;
        this.page = 1;
        this.fetchData();
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        this.search = "";
        this.status = "";
        this.role = "";
        this.page = 1;
        if (searchInput) searchInput.value = "";
        if (statusSelect) statusSelect.value = "";
        if (roleSelect) roleSelect.value = "";
        this.fetchData();
      });
    }
  },

  async fetchData() {
    const tableWrapper = document.getElementById("audit-table-wrapper");
    if (tableWrapper) {
      tableWrapper.style.opacity = "0.6";
    }

    try {
      const params = {
        page: this.page,
        page_size: this.pageSize
      };
      if (this.search) params.search = this.search;
      if (this.status) params.status = this.status;
      if (this.role) params.role = this.role;

      const res = await API.getAuditLogs(params);
      if (res && res.items) {
        this.logs = res.items;
        this.total = res.total || 0;
        this.totalPages = res.total_pages || 1;
      } else if (Array.isArray(res)) {
        this.logs = res;
        this.total = res.length;
        this.totalPages = 1;
      }

      this.renderTable();
      this.renderPagination();
    } catch (err) {
      console.error("Failed to load audit logs:", err);
      if (tableWrapper) {
        tableWrapper.innerHTML = `
          <div style="text-align: center; padding: 2rem; color: var(--danger);">
            Failed to load audit logs: ${err.message}
          </div>
        `;
      }
    } finally {
      if (tableWrapper) tableWrapper.style.opacity = "1";
    }
  },

  renderTable() {
    const tableWrapper = document.getElementById("audit-table-wrapper");
    if (!tableWrapper) return;

    if (this.logs.length === 0) {
      tableWrapper.innerHTML = `
        <div style="text-align: center; padding: 3rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--border-radius-md); border: 1px solid var(--border-color);">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" style="margin-bottom: 0.5rem; opacity: 0.5;"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <div>No matching audit records found.</div>
        </div>
      `;
      return;
    }

    tableWrapper.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 170px;">Timestamp</th>
            <th style="width: 120px;">User</th>
            <th style="width: 100px;">Role</th>
            <th style="width: 200px;">Action</th>
            <th style="width: 90px; text-align: center;">Status</th>
            <th>Details</th>
            <th style="width: 110px;">IP Address</th>
          </tr>
        </thead>
        <tbody>
          ${this.logs.map(log => {
            const dateObj = new Date(log.timestamp);
            const dateStr = dateObj.toLocaleDateString([], { day: '2-digit', month: '2-digit', year: 'numeric' });
            const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            const isVerifiedAction = log.action && log.action.includes("Verified");
            const isUnverifiedAction = log.action && log.action.includes("Unverified");
            const isLogin = log.action && log.action.includes("Login");
            const isImport = log.action && log.action.includes("Import");
            const isExport = log.action && log.action.includes("Export");

            let actionBadge = `<span style="font-weight: 600; color: var(--text-primary);">${log.action}</span>`;
            if (isVerifiedAction) {
              actionBadge = `<span style="font-weight: 700; color: #16a34a;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" style="display:inline-block; vertical-align:-1px; margin-right:3px;"><polyline points="20 6 9 17 4 12"/></svg>${log.action}</span>`;
            } else if (isUnverifiedAction) {
              actionBadge = `<span style="font-weight: 700; color: #dc2626;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="display:inline-block; vertical-align:-1px; margin-right:3px;"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>${log.action}</span>`;
            } else if (isExport) {
              actionBadge = `<span style="font-weight: 600; color: #2563eb;">📥 ${log.action}</span>`;
            } else if (isImport) {
              actionBadge = `<span style="font-weight: 600; color: #7c3aed;">⚡ ${log.action}</span>`;
            } else if (isLogin) {
              actionBadge = `<span style="font-weight: 600; color: #0284c7;">🔑 ${log.action}</span>`;
            }

            return `
              <tr>
                <td style="font-size: 0.78rem; color: var(--text-secondary); white-space: nowrap;">
                  <strong>${dateStr}</strong> <span style="color: var(--text-muted); font-size: 0.74rem;">${timeStr}</span>
                </td>
                <td style="font-weight: 600;">
                  <span style="display: inline-flex; align-items: center; gap: 4px;">
                    <span style="display:inline-block; width: 16px; height: 16px; border-radius: 50%; background: #e2e8f0; color: #475569; font-size: 0.62rem; line-height: 16px; text-align: center; font-weight: 700;">${(log.user_username || 'U')[0].toUpperCase()}</span>
                    <span>${log.user_username}</span>
                  </span>
                </td>
                <td>
                  <span class="user-role-badge ${(log.user_role || '').toLowerCase()}" style="font-size: 0.72rem; padding: 0.12rem 0.45rem;">
                    ${log.user_role}
                  </span>
                </td>
                <td>${actionBadge}</td>
                <td style="text-align: center;">
                  <span class="badge ${log.status === 'Success' ? 'badge-success' : (log.status === 'Warning' ? 'badge-warning' : 'badge-danger')}" style="font-size: 0.72rem; padding: 0.12rem 0.45rem;">
                    ${log.status}
                  </span>
                </td>
                <td style="font-size: 0.80rem; color: var(--text-secondary); max-width: 320px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${(log.details || '').replace(/"/g, '&quot;')}">
                  ${log.details || '—'}
                </td>
                <td style="font-size: 0.76rem; color: var(--text-muted); font-family: monospace;">${log.ip_address || '—'}</td>
              </tr>
            `;
          }).join("")}
        </tbody>
      </table>
    `;
  },

  renderPagination() {
    const pagBar = document.getElementById("audit-pagination-bar");
    if (!pagBar) return;

    const start = this.total === 0 ? 0 : (this.page - 1) * this.pageSize + 1;
    const end = Math.min(this.page * this.pageSize, this.total);

    // Build page buttons list (max 5 visible numbered buttons)
    let pageBtnsHtml = '';
    const maxVisible = 5;
    let startPage = Math.max(1, this.page - Math.floor(maxVisible / 2));
    let endPage = Math.min(this.totalPages, startPage + maxVisible - 1);
    if (endPage - startPage + 1 < maxVisible) {
      startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let p = startPage; p <= endPage; p++) {
      pageBtnsHtml += `
        <button type="button" class="dt-page-btn ${p === this.page ? 'active' : ''}" data-page="${p}" style="min-width: 28px; height: 28px; padding: 0 0.35rem; font-size: 0.76rem; border-radius: 4px; border: 1px solid var(--border-color); background: ${p === this.page ? 'var(--primary)' : 'var(--bg-card)'}; color: ${p === this.page ? '#ffffff' : 'var(--text-primary)'}; cursor: pointer; font-weight: 600;">
          ${p}
        </button>
      `;
    }

    pagBar.innerHTML = `
      <div style="font-size: 0.82rem; color: var(--text-secondary);">
        Showing <strong>${start}</strong> to <strong>${end}</strong> of <strong>${this.total.toLocaleString()}</strong> audit entries
      </div>
      
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.80rem; color: var(--text-secondary);">
          <span>Rows:</span>
          <select id="audit-page-size-select" class="form-select" style="padding: 0.18rem 0.5rem; font-size: 0.76rem; height: 28px; min-width: 60px;">
            <option value="15" ${this.pageSize === 15 ? 'selected' : ''}>15</option>
            <option value="30" ${this.pageSize === 30 ? 'selected' : ''}>30</option>
            <option value="50" ${this.pageSize === 50 ? 'selected' : ''}>50</option>
            <option value="100" ${this.pageSize === 100 ? 'selected' : ''}>100</option>
          </select>
        </div>

        <div style="display: flex; align-items: center; gap: 0.25rem;">
          <button type="button" id="audit-btn-first" class="dt-page-btn" ${this.page <= 1 ? 'disabled' : ''} style="height: 28px; padding: 0 0.4rem; font-size: 0.76rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-card); cursor: pointer;" title="First Page">
            «
          </button>
          <button type="button" id="audit-btn-prev" class="dt-page-btn" ${this.page <= 1 ? 'disabled' : ''} style="height: 28px; padding: 0 0.5rem; font-size: 0.76rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-card); cursor: pointer;" title="Previous Page">
            ‹ Prev
          </button>
          ${pageBtnsHtml}
          <button type="button" id="audit-btn-next" class="dt-page-btn" ${this.page >= this.totalPages ? 'disabled' : ''} style="height: 28px; padding: 0 0.5rem; font-size: 0.76rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-card); cursor: pointer;" title="Next Page">
            Next ›
          </button>
          <button type="button" id="audit-btn-last" class="dt-page-btn" ${this.page >= this.totalPages ? 'disabled' : ''} style="height: 28px; padding: 0 0.4rem; font-size: 0.76rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-card); cursor: pointer;" title="Last Page">
            »
          </button>
        </div>
      </div>
    `;

    // Bind pagination controls
    const sizeSelect = document.getElementById("audit-page-size-select");
    if (sizeSelect) {
      sizeSelect.onchange = (e) => {
        this.pageSize = parseInt(e.target.value, 10);
        this.page = 1;
        this.fetchData();
      };
    }

    const firstBtn = document.getElementById("audit-btn-first");
    if (firstBtn) {
      firstBtn.onclick = () => {
        if (this.page > 1) {
          this.page = 1;
          this.fetchData();
        }
      };
    }

    const prevBtn = document.getElementById("audit-btn-prev");
    if (prevBtn) {
      prevBtn.onclick = () => {
        if (this.page > 1) {
          this.page--;
          this.fetchData();
        }
      };
    }

    const nextBtn = document.getElementById("audit-btn-next");
    if (nextBtn) {
      nextBtn.onclick = () => {
        if (this.page < this.totalPages) {
          this.page++;
          this.fetchData();
        }
      };
    }

    const lastBtn = document.getElementById("audit-btn-last");
    if (lastBtn) {
      lastBtn.onclick = () => {
        if (this.page < this.totalPages) {
          this.page = this.totalPages;
          this.fetchData();
        }
      };
    }

    pagBar.querySelectorAll(".dt-page-btn[data-page]").forEach(btn => {
      btn.onclick = () => {
        const p = parseInt(btn.dataset.page, 10);
        if (p && p !== this.page) {
          this.page = p;
          this.fetchData();
        }
      };
    });
  }
};
