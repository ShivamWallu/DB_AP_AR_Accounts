const App = {
  currentView: "master",
  dtMaster: null,
  dtDayBook: null,
  dtAP: null,
  dtAR: null,
  filterData: null,

  parseDate(rawDt) {
    if (!rawDt) return null;
    let d;
    if (typeof rawDt === "string") {
      const clean = rawDt.trim();
      if (!clean.endsWith("Z") && !/[+-]\d{2}:\d{2}$/.test(clean)) {
        d = new Date(clean + "Z");
      } else {
        d = new Date(clean);
      }
    } else {
      d = new Date(rawDt);
    }
    return isNaN(d.getTime()) ? null : d;
  },

  formatDateTime(rawDt) {
    const d = this.parseDate(rawDt);
    if (!d) return rawDt ? String(rawDt) : "—";
    return d.toLocaleString([], {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true
    });
  },

  init() {
    Auth.init();
    Upload.init();
    this.initSidebarState();
    this.bindNavigation();
    this.bindModals();
    this.setupDataTables();
    this.bindCrossReference();
    this.bindKeyboardNavigation();
    if (window.VerificationManager && typeof window.VerificationManager.init === "function") {
      window.VerificationManager.init();
    }
  },

  bindKeyboardNavigation() {
    window.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      const activeEl = document.activeElement;
      // Do not interrupt user typing in input fields, textareas, selects
      if (activeEl && (activeEl.tagName === "INPUT" || activeEl.tagName === "TEXTAREA" || activeEl.tagName === "SELECT" || activeEl.isContentEditable)) {
        return;
      }
      
      // If statement modal is open, scroll statement table
      const statementModal = document.getElementById("statement-report-modal");
      if (statementModal && statementModal.classList.contains("show")) {
        const stmtWrapper = statementModal.querySelector(".statement-table-wrapper");
        if (stmtWrapper) {
          e.preventDefault();
          const scrollStep = e.key === "ArrowLeft" ? -240 : 240;
          stmtWrapper.scrollBy({ left: scrollStep, behavior: "smooth" });
          return;
        }
      }

      // Otherwise scroll active view's data table
      const activeView = document.querySelector(".view-section:not([style*='display: none'])");
      if (activeView) {
        const tableWrapper = activeView.querySelector(".table-responsive");
        if (tableWrapper) {
          e.preventDefault();
          const scrollStep = e.key === "ArrowLeft" ? -260 : 260;
          tableWrapper.scrollBy({ left: scrollStep, behavior: "smooth" });
        }
      }
    });
  },

  initSidebarState() {
    const isCollapsed = localStorage.getItem("sidebar_collapsed") === "true";
    if (isCollapsed) {
      document.body.classList.add("sidebar-collapsed");
    }
  },

  toggleSidebar() {
    document.body.classList.toggle("sidebar-collapsed");
    const isCollapsed = document.body.classList.contains("sidebar-collapsed");
    localStorage.setItem("sidebar_collapsed", isCollapsed ? "true" : "false");
    
    // Trigger resize & table scroll phantom updates for smooth UX
    setTimeout(() => {
      window.dispatchEvent(new Event("resize"));
      if (this.dtMaster) this.dtMaster.updateScrollPhantom();
      if (this.dtDayBook) this.dtDayBook.updateScrollPhantom();
      if (this.dtAP) this.dtAP.updateScrollPhantom();
      if (this.dtAR) this.dtAR.updateScrollPhantom();
    }, 280);
  },

  bindNavigation() {
    document.querySelectorAll(".nav-item[data-view]").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        this.navigate(view);
      });
    });
  },

  navigate(viewName) {
    this.currentView = viewName;

    // Update active nav state
    document.querySelectorAll(".nav-item").forEach(item => {
      item.classList.toggle("active", item.dataset.view === viewName);
    });

    // Toggle view containers
    document.querySelectorAll(".view-section").forEach(sec => {
      sec.style.display = "none";
    });

    const targetView = document.getElementById(`view-${viewName}`);
    if (targetView) {
      targetView.style.display = "block";
    }

    // Update top header title
    const titles = {
      dashboard: "Executive Dashboard",
      master: "Day Book Master 360° Ledger (Unified Day Book + AP + AR)",
      daybook: "Day Book Register",
      ap: "Account Payable (AP) Register",
      ar: "Account Receivable (AR) Register",
      explorer: "Cross-Reference Transaction Explorer",
      upload: "Upload Daily Excel Files",
      imports: "Import History & Batch Logs",
      audit: "System Audit Logs",
      users: "User Management"
    };
    const titleEl = document.getElementById("page-title");
    if (titleEl) titleEl.innerText = titles[viewName] || "Excel Data Management";

    // Trigger view-specific data loading
    this.onViewActivated(viewName);
  },

  async onViewActivated(viewName) {
    await this.refreshFilterOptions();

    if (viewName === "dashboard") {
      Dashboard.load();
    } else if (viewName === "master" && this.dtMaster) {
      this.dtMaster.populateFilterOptions(this.filterData);
      this.dtMaster.loadData();
    } else if (viewName === "daybook" && this.dtDayBook) {
      this.dtDayBook.populateFilterOptions(this.filterData);
      this.dtDayBook.loadData();
    } else if (viewName === "ap" && this.dtAP) {
      this.dtAP.populateFilterOptions(this.filterData);
      this.dtAP.loadData();
    } else if (viewName === "ar" && this.dtAR) {
      this.dtAR.populateFilterOptions(this.filterData);
      this.dtAR.loadData();
    } else if (viewName === "imports") {
      Imports.load();
    } else if (viewName === "audit") {
      Audit.load();
    } else if (viewName === "users") {
      this.loadUsers();
    }
  },

  async refreshFilterOptions() {
    if (!API.getToken()) return;
    try {
      this.filterData = await API.getFilterOptions();
      if (this.dtMaster) this.dtMaster.populateFilterOptions(this.filterData);
      if (this.dtDayBook) this.dtDayBook.populateFilterOptions(this.filterData);
      if (this.dtAP) this.dtAP.populateFilterOptions(this.filterData);
      if (this.dtAR) this.dtAR.populateFilterOptions(this.filterData);
    } catch (e) {
      console.warn("Could not fetch filter options:", e);
    }
  },

  setupDataTables() {
    // 0. Master 360 Unified Ledger (Day Book as Master Anchor + AP + AR Reconciled)
    this.dtMaster = new DataTableController({
      containerId: "master-table-container",
      datasetType: "master",
      fetchFn: (params) => API.getMaster(params),
      columns: [
        { key: "transaction_site", label: "Site" },
        { key: "voucher_number", label: "Voucher No." },
        { key: "voucher_date", label: "Voucher Date" },
        { key: "voucher_type", label: "Voucher Type" },
        { key: "source_tag", label: "Linked Register" },
        { key: "unified_invoice_no", label: "Invoice / Ref No." },
        { key: "unified_quantity", label: "Quantity" },
        { key: "unified_rate", label: "Rate (₹)", type: "currency" },
        { key: "combined_amount", label: "Total Amount (₹)", type: "currency" },
        { key: "unified_tax_amount", label: "Tax Amount (GST)", type: "currency" },
        { key: "unified_item_description", label: "Item / Expense Description" },
        { key: "expense_account", label: "Expense Account" },
        { key: "party_code", label: "Party Code" },
        { key: "party_description", label: "Party Description" },
        { key: "account_description", label: "Account Description" },
        { key: "voucher_status", label: "Status", type: "badge" },
        { key: "narration", label: "Narration" },
        { key: "created_by", label: "Created By" },
        { key: "approved_by", label: "Approved By" }
      ]
    });
    this.dtMaster.init();

    // 1. Day Book Table
    this.dtDayBook = new DataTableController({
      containerId: "daybook-table-container",
      datasetType: "daybook",
      fetchFn: (params) => API.getDayBook(params),
      columns: [
        { key: "transaction_site", label: "Site" },
        { key: "voucher_number", label: "Voucher No." },
        { key: "voucher_date", label: "Voucher Date" },
        { key: "voucher_type", label: "Voucher Type" },
        { key: "voucher_status", label: "Status", type: "badge" },
        { key: "party_code", label: "Party Code" },
        { key: "party_description", label: "Party Description" },
        { key: "account_description", label: "Account Description" },
        { key: "narration", label: "Narration" },
        { key: "created_by", label: "Created By" },
        { key: "approved_by", label: "Approved By" }
      ]
    });
    this.dtDayBook.init();

    // 2. AP Table
    this.dtAP = new DataTableController({
      containerId: "ap-table-container",
      datasetType: "ap",
      fetchFn: (params) => API.getAP(params),
      columns: [
        { key: "accounting_site_code", label: "Site Code" },
        { key: "voucher_number", label: "Voucher No." },
        { key: "voucher_type", label: "Voucher Type" },
        { key: "voucher_sub_type", label: "Voucher Sub-Type" },
        { key: "party_gst_tin", label: "Party GST TIN" },
        { key: "invoice_number", label: "Invoice No." },
        { key: "invoice_date", label: "Invoice Date" },
        { key: "due_date", label: "Due Date" },
        { key: "item_service_description", label: "Item Description" },
        { key: "item_service_expense_account_desc", label: "Expense Account" },
        { key: "booked_item_quantity", label: "Quantity" },
        { key: "item_service_rate", label: "Rate", type: "currency" },
        { key: "item_service_detail_amount", label: "Detail Amount", type: "currency" },
        { key: "total_tax_amount", label: "Tax Amount", type: "currency" },
        { key: "total_voucher_amount", label: "Total Voucher Amount", type: "currency" },
        { key: "total_tds", label: "Total TDS", type: "currency" },
        { key: "narration", label: "Narration" },
        { key: "created_by", label: "Created By" },
        { key: "approved_by", label: "Approved By" }
      ]
    });
    this.dtAP.init();

    // 3. AR Table
    this.dtAR = new DataTableController({
      containerId: "ar-table-container",
      datasetType: "ar",
      fetchFn: (params) => API.getAR(params),
      columns: [
        { key: "accounting_site_code", label: "Site Code" },
        { key: "voucher_number", label: "Voucher No." },
        { key: "voucher_type", label: "Voucher Type" },
        { key: "voucher_sub_type", label: "Voucher Sub-Type" },
        { key: "item_service_description", label: "Item Description" },
        { key: "item_quantity", label: "Item Qty" },
        { key: "item_service_rate", label: "Rate", type: "currency" },
        { key: "item_service_amount", label: "Amount", type: "currency" },
        { key: "item_service_charges", label: "Charges", type: "currency" },
        { key: "item_amount_net_off_discount", label: "Net of Discount", type: "currency" },
        { key: "item_service_taxes", label: "Taxes", type: "currency" },
        { key: "net_amount", label: "Net Amount", type: "currency" },
        { key: "total_cgst", label: "Total CGST", type: "currency" },
        { key: "total_sgst", label: "Total SGST", type: "currency" },
        { key: "total_igst", label: "Total IGST", type: "currency" },
        { key: "narration", label: "Narration" },
        { key: "created_by", label: "Created By" },
        { key: "approved_by", label: "Approved By" }
      ]
    });
    this.dtAR.init();
  },

  bindCrossReference() {
    const input = document.getElementById("explorer-search-input");
    const btn = document.getElementById("btn-explorer-search");

    const doSearch = async () => {
      const vNo = input.value.trim();
      if (!vNo) {
        App.toast("Please enter a Voucher Number to explore", "warning");
        return;
      }
      this.exploreVoucher(vNo);
    };

    if (btn) btn.addEventListener("click", doSearch);
    if (input) input.addEventListener("keypress", (e) => { if (e.key === "Enter") doSearch(); });
  },

  async exploreVoucher(voucherNo) {
    if (!voucherNo) return;
    this.navigate("explorer");
    
    const input = document.getElementById("explorer-search-input");
    if (input) input.value = voucherNo;

    const resultsEl = document.getElementById("explorer-results");
    if (!resultsEl) return;

    resultsEl.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted);">Linking records across Day Book, AP, and AR...</div>`;

    try {
      const res = await API.getCrossReference(voucherNo);
      this.renderExplorerResults(res);
    } catch (err) {
      resultsEl.innerHTML = `<div style="color: var(--danger); padding: 1rem;">Failed to retrieve cross-reference: ${err.message}</div>`;
    }
  },

  _crossRefData: null,

  showCrossRefDetail(datasetType, index) {
    if (!this._crossRefData) return;
    let list = [];
    if (datasetType === 'daybook') list = this._crossRefData.daybook_records || [];
    else if (datasetType === 'ap') list = this._crossRefData.ap_records || [];
    else if (datasetType === 'ar') list = this._crossRefData.ar_records || [];

    const record = list[index];
    if (record && window.DataTableController && typeof window.DataTableController.showRecordModal === "function") {
      window.DataTableController.showRecordModal(record, datasetType);
    }
  },

  renderExplorerResults(res) {
    const resultsEl = document.getElementById("explorer-results");
    if (!resultsEl) return;
    this._crossRefData = res;

    resultsEl.innerHTML = `
      <div style="margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-size: 1.1rem; font-weight: 700; color: #60a5fa;">
          Cross-Reference for Voucher: <u>${res.voucher_number}</u>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <span class="badge badge-info">Day Book: ${res.daybook_count}</span>
          <span class="badge badge-warning">AP: ${res.ap_count}</span>
          <span class="badge badge-success">AR: ${res.ar_count}</span>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 1.5rem;">
        <!-- Day Book Match -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">📖 Day Book Records (${res.daybook_count})</div>
          </div>
          ${res.daybook_count === 0 ? '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem;">No matching Day Book entries.</div>' : `
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Site</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Party</th>
                    <th>Account</th>
                    <th>Narration</th>
                    <th>Created By</th>
                    <th>Approved By</th>
                    <th style="width: 75px; text-align: center;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  ${res.daybook_records.map((r, idx) => `
                    <tr>
                      <td>${r.transaction_site || '—'}</td>
                      <td>${r.voucher_date || '—'}</td>
                      <td>${r.voucher_type || '—'}</td>
                      <td>${r.party_description || r.party_code || '—'}</td>
                      <td>${r.account_description || '—'}</td>
                      <td>${r.narration || '—'}</td>
                      <td>${window.PersonBadge ? window.PersonBadge.render(r.created_by, "created") : (r.created_by || '—')}</td>
                      <td>${window.PersonBadge ? window.PersonBadge.render(r.approved_by, "approved") : (r.approved_by || '—')}</td>
                      <td style="text-align: center;">
                        <button type="button" class="btn btn-secondary btn-sm dt-btn-view" onclick="App.showCrossRefDetail('daybook', ${idx})" style="padding: 0.22rem 0.55rem; font-size: 0.76rem; border-radius: 6px;" title="View Complete Record Details">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 3px; vertical-align: -1px;">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                          View
                        </button>
                      </td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>
          `}
        </div>

        <!-- AP Match -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">📉 Account Payable (AP) Records (${res.ap_count})</div>
          </div>
          ${res.ap_count === 0 ? '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem;">No matching AP entries.</div>' : `
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Site</th>
                    <th>Type</th>
                    <th>Sub-Type</th>
                    <th>Invoice No</th>
                    <th>Item Desc</th>
                    <th style="text-align: right;">Qty</th>
                    <th style="text-align: right;">Detail Amt</th>
                    <th style="text-align: right;">Tax Amt</th>
                    <th style="text-align: right;">Total Voucher Amt</th>
                    <th style="width: 75px; text-align: center;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  ${res.ap_records.map((r, idx) => `
                    <tr>
                      <td>${r.accounting_site_code || '—'}</td>
                      <td>${r.voucher_type || '—'}</td>
                      <td>${r.voucher_sub_type || '—'}</td>
                      <td>${r.invoice_number || '—'}</td>
                      <td>${r.item_service_description || '—'}</td>
                      <td style="text-align: right;" class="cell-quantity">${Number(r.booked_item_quantity || 0).toLocaleString("en-IN")}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.item_service_detail_amount || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.total_tax_amount || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.total_voucher_amount || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: center;">
                        <button type="button" class="btn btn-secondary btn-sm dt-btn-view" onclick="App.showCrossRefDetail('ap', ${idx})" style="padding: 0.22rem 0.55rem; font-size: 0.76rem; border-radius: 6px;" title="View Complete Record Details">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 3px; vertical-align: -1px;">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                          View
                        </button>
                      </td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>
          `}
        </div>

        <!-- AR Match -->
        <div class="card">
          <div class="card-header">
            <div class="card-title">📈 Account Receivable (AR) Records (${res.ar_count})</div>
          </div>
          ${res.ar_count === 0 ? '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem;">No matching AR entries.</div>' : `
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Site</th>
                    <th>Type</th>
                    <th>Sub-Type</th>
                    <th>Item Desc</th>
                    <th style="text-align: right;">Qty</th>
                    <th style="text-align: right;">Rate</th>
                    <th style="text-align: right;">Net Amt</th>
                    <th style="text-align: right;">CGST</th>
                    <th style="text-align: right;">SGST</th>
                    <th style="text-align: right;">IGST</th>
                    <th style="width: 75px; text-align: center;">Action</th>
                  </tr>
                </thead>
                <tbody>
                  ${res.ar_records.map((r, idx) => `
                    <tr>
                      <td>${r.accounting_site_code || '—'}</td>
                      <td>${r.voucher_type || '—'}</td>
                      <td>${r.voucher_sub_type || '—'}</td>
                      <td>${r.item_service_description || '—'}</td>
                      <td style="text-align: right;" class="cell-quantity">${Number(r.item_quantity || 0).toLocaleString("en-IN")}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.item_service_rate || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.net_amount || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.total_cgst || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.total_sgst || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: right;" class="cell-financial">₹ ${Number(r.total_igst || 0).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</td>
                      <td style="text-align: center;">
                        <button type="button" class="btn btn-secondary btn-sm dt-btn-view" onclick="App.showCrossRefDetail('ar', ${idx})" style="padding: 0.22rem 0.55rem; font-size: 0.76rem; border-radius: 6px;" title="View Complete Record Details">
                          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 3px; vertical-align: -1px;">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                          </svg>
                          View
                        </button>
                      </td>
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>
          `}
        </div>
      </div>
    `;
  },

  usersData: [],
  usersFilter: { search: "", status: "all" },

  async loadUsers() {
    const listEl = document.getElementById("users-list");
    if (!listEl) return;

    listEl.innerHTML = `
      <div style="padding: 2.5rem; text-align: center; color: var(--text-secondary);">
        <div class="spinner-border text-primary" role="status" style="display:inline-block; width:28px; height:28px; border:3px solid #3b82f6; border-right-color:transparent; border-radius:50%; animation:spin 0.6s linear infinite; vertical-align:middle; margin-bottom:12px;"></div>
        <div style="font-weight: 600; font-size: 0.95rem;">Loading User Directory & Roles...</div>
      </div>
    `;

    try {
      this.usersData = await API.getUsers();
      this.renderUsersView();
    } catch (err) {
      listEl.innerHTML = `
        <div style="color: #dc2626; padding: 1.5rem; background: #fef2f2; border-radius: 10px; border: 1px solid #fecaca; margin: 1rem;">
          <strong>Error:</strong> Failed to load users: ${err.message}
        </div>
      `;
    }
  },

  onUserSearchChange(val) {
    this.usersFilter.search = val;
    this.renderUsersView();
  },

  onUserStatusFilterChange(val) {
    this.usersFilter.status = val;
    this.renderUsersView();
  },

  async confirmToggleUser(userId, username, isCurrentlyActive, displayName) {
    const targetName = displayName || username;
    if (isCurrentlyActive) {
      const confirmed = confirm(`⚠️ SECURITY ACTION: BLOCK USER\n\nAre you sure you want to BLOCK user '${targetName}' (@${username})?\n\n• Login access will be immediately revoked.\n• Registration/OTP requests with this account will be blocked.\n• The user will not be able to access any ERP records.`);
      if (!confirmed) return;
    } else {
      const confirmed = confirm(`✓ RESTORE USER ACCESS\n\nAre you sure you want to UNBLOCK user '${targetName}' (@${username})?\n\n• Login permissions will be fully restored.`);
      if (!confirmed) return;
    }

    try {
      const newStatus = !isCurrentlyActive;
      await API.updateUserStatus(userId, newStatus);
      
      if (newStatus) {
        App.toast(`✓ User '${username}' successfully unblocked & activated!`, "success");
      } else {
        App.toast(`🚫 User '${username}' successfully BLOCKED and suspended.`, "warning");
      }
      
      // Update local state & refresh view
      const target = (this.usersData || []).find(u => u.id === userId);
      if (target) target.is_active = newStatus;
      this.renderUsersView();
    } catch (err) {
      App.toast(err.message || "Failed to update user status", "error");
    }
  },

  renderUsersView() {
    const listEl = document.getElementById("users-list");
    if (!listEl) return;

    const currentUsername = API.currentUser ? API.currentUser.username : "";
    const users = this.usersData || [];

    // KPI calculations
    const totalUsers = users.length;
    const activeUsers = users.filter(u => u.is_active).length;
    const blockedUsers = users.filter(u => !u.is_active).length;
    const adminUsers = users.filter(u => u.role === "Admin").length;

    // Filter computation
    const search = (this.usersFilter.search || "").toLowerCase().trim();
    const status = this.usersFilter.status || "all";

    const filtered = users.filter(u => {
      const matchSearch = !search ||
        (u.username && u.username.toLowerCase().includes(search)) ||
        (u.full_name && u.full_name.toLowerCase().includes(search)) ||
        (u.email && u.email.toLowerCase().includes(search));
      
      const matchStatus = status === "all" ||
        (status === "active" && u.is_active) ||
        (status === "blocked" && !u.is_active);

      return matchSearch && matchStatus;
    });

    listEl.innerHTML = `
      <div class="user-management-wrapper">
        <!-- Top KPI Metric Cards -->
        <div class="user-kpi-grid">
          <div class="user-kpi-card">
            <div class="user-kpi-icon total">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <div class="user-kpi-info">
              <div class="user-kpi-value">${totalUsers}</div>
              <div class="user-kpi-label">Total Accounts</div>
            </div>
          </div>
          <div class="user-kpi-card">
            <div class="user-kpi-icon active">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <div class="user-kpi-info">
              <div class="user-kpi-value text-success">${activeUsers}</div>
              <div class="user-kpi-label">Active Users</div>
            </div>
          </div>
          <div class="user-kpi-card">
            <div class="user-kpi-icon blocked">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line></svg>
            </div>
            <div class="user-kpi-info">
              <div class="user-kpi-value text-danger">${blockedUsers}</div>
              <div class="user-kpi-label">Blocked / Suspended</div>
            </div>
          </div>
          <div class="user-kpi-card">
            <div class="user-kpi-icon admin">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
            </div>
            <div class="user-kpi-info">
              <div class="user-kpi-value text-purple">${adminUsers}</div>
              <div class="user-kpi-label">Administrators</div>
            </div>
          </div>
        </div>

        <!-- Filter & Search Toolbar -->
        <div class="user-toolbar">
          <div class="user-search-wrapper">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" class="user-search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input type="text" id="user-search-input-field" class="user-search-input" placeholder="Search by name, username, or email address..." value="${this.usersFilter.search || ''}" oninput="App.onUserSearchChange(this.value)" />
          </div>
          <div class="user-filter-controls">
            <select id="user-status-filter-select" class="user-status-select" onchange="App.onUserStatusFilterChange(this.value)">
              <option value="all" ${status === 'all' ? 'selected' : ''}>All Accounts (${totalUsers})</option>
              <option value="active" ${status === 'active' ? 'selected' : ''}>Active Accounts (${activeUsers})</option>
              <option value="blocked" ${status === 'blocked' ? 'selected' : ''}>Blocked Accounts (${blockedUsers})</option>
            </select>
            <button class="btn btn-sm btn-secondary" onclick="App.loadUsers()" title="Reload user list">
              🔄 Refresh
            </button>
          </div>
        </div>

        <!-- Users Data Table -->
        <div class="table-responsive user-table-container">
          <table class="data-table user-data-table">
            <thead>
              <tr>
                <th style="width: 60px;">ID</th>
                <th>User Profile</th>
                <th>Email Address</th>
                <th>Role</th>
                <th>Access Status</th>
                <th>Registered At</th>
                <th style="text-align: center; width: 180px;">Account Action</th>
              </tr>
            </thead>
            <tbody>
              ${filtered.length === 0 ? `
                <tr>
                  <td colspan="7" style="text-align: center; padding: 2.8rem 1rem; color: var(--text-secondary);">
                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 4px;">No users found</div>
                    <div style="font-size: 0.85rem;">Try adjusting your search or status filter criteria.</div>
                  </td>
                </tr>
              ` : filtered.map(u => {
                const isSelf = currentUsername && u.username === currentUsername;
                const safeName = (u.full_name || u.username).replace(/'/g, "\\'");
                const safeUser = u.username.replace(/'/g, "\\'");

                return `
                  <tr class="${!u.is_active ? 'user-row-blocked' : ''}">
                    <td><span class="user-id-tag">#${u.id}</span></td>
                    <td>
                      <div class="user-profile-flex">
                        <div class="user-avatar-badge ${!u.is_active ? 'blocked' : (u.role === 'Admin' ? 'admin' : '')}">
                          ${(u.full_name || u.username || 'U').charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div class="user-display-name">${u.full_name || u.username}</div>
                          <div class="user-handle-name">@${u.username}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      ${u.email ? `<span class="user-email-tag">${u.email}</span>` : '<span style="color:#94a3b8; font-style:italic;">No Email</span>'}
                    </td>
                    <td>
                      <span class="user-role-badge ${u.role.toLowerCase()}">${u.role}</span>
                    </td>
                    <td>
                      ${u.is_active ? `
                        <span class="user-status-badge active">
                          <span class="status-dot active"></span> Active
                        </span>
                      ` : `
                        <span class="user-status-badge blocked">
                          <span class="status-dot blocked"></span> Blocked / Suspended
                        </span>
                      `}
                    </td>
                    <td style="font-size: 0.8rem; color: var(--text-secondary);">
                      ${App.formatDateTime(u.created_at)}
                    </td>
                    <td style="text-align: center;">
                      ${isSelf ? `
                        <span class="user-self-pill" title="Your current active session cannot be self-blocked">
                          🛡️ Current User
                        </span>
                      ` : u.is_active ? `
                        <button class="btn-user-action block" onclick="App.confirmToggleUser(${u.id}, '${safeUser}', true, '${safeName}')" title="Block this account immediately">
                          🚫 Block Account
                        </button>
                      ` : `
                        <button class="btn-user-action unblock" onclick="App.confirmToggleUser(${u.id}, '${safeUser}', false, '${safeName}')" title="Unblock and restore access">
                          ✓ Unblock Account
                        </button>
                      `}
                    </td>
                  </tr>
                `;
              }).join("")}
            </tbody>
          </table>
        </div>
      </div>
    `;
  },

  async refreshAllData(targetBatchId = null) {
    await this.refreshFilterOptions();
    
    // If a specific targetBatchId was provided (e.g. from a new batch upload),
    // sync the batch dropdown filter across all DataTables so active tables reflect the new dataset
    if (targetBatchId) {
      const dtInstances = [this.dtMaster, this.dtDayBook, this.dtAP, this.dtAR];
      dtInstances.forEach(dt => {
        if (dt) {
          const container = document.getElementById(dt.containerId);
          if (container) {
            const batchSelect = container.querySelector(".filter-batch");
            if (batchSelect) {
              batchSelect.value = targetBatchId;
              dt.filters.batch_id = targetBatchId;
              dt.pagination.page = 1;
            }
          }
        }
      });
    }

    if (this.dtMaster) this.dtMaster.loadData();
    if (this.dtDayBook) this.dtDayBook.loadData();
    if (this.dtAP) this.dtAP.loadData();
    if (this.dtAR) this.dtAR.loadData();
    if (this.currentView === "dashboard") Dashboard.load();
    if (this.currentView === "imports") Imports.load();
    if (this.currentView === "audit") Audit.load();
  },

  bindModals() {
    document.querySelectorAll(".modal-close").forEach(btn => {
      btn.addEventListener("click", () => {
        const modal = btn.closest(".modal-backdrop");
        if (modal) modal.classList.remove("show");
      });
    });

    document.querySelectorAll(".modal-backdrop").forEach(backdrop => {
      backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) {
          backdrop.classList.remove("show");
        }
      });
    });
  },

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.style.display = "flex";
      // Force reflow for CSS opacity/transform transition
      void modal.offsetWidth;
      modal.classList.add("show");
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("show");
      setTimeout(() => {
        if (!modal.classList.contains("show")) {
          modal.style.display = "none";
        }
      }, 200);
    }
  },

  toast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toastEl = document.createElement("div");
    toastEl.className = `toast ${type}`;
    toastEl.innerHTML = `
      <div style="font-size: 0.85rem; font-weight: 500;">${message}</div>
      <button style="background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 1rem;" onclick="this.parentElement.remove()">✕</button>
    `;
    container.appendChild(toastEl);

    setTimeout(() => {
      toastEl.style.opacity = "0";
      toastEl.style.transform = "translateX(100%)";
      toastEl.style.transition = "all 0.3s ease";
      setTimeout(() => toastEl.remove(), 300);
    }, 4000);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
