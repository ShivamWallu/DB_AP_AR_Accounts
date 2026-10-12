/**
 * Day Book Module - Upload, Excel Validation & Dashboard Controller
 * KOGM Finance Day Book ERP
 */

const DayBook = {
  currentSubTab: "dashboard", // "upload" | "dashboard"
  activeStatusFilter: "All Transactions",
  dtController: null,
  selectedFile: null,

  // Main Primary Columns (Previous Core Columns + Created & Approved Dates + Validation Status)
  columns: [
    { key: "transaction_site", label: "Site", isSticky: true },
    { key: "voucher_number", label: "Voucher No.", isSticky: true },
    { key: "voucher_date", label: "Voucher Date", isSticky: true, type: "date" },
    { key: "created_date", label: "Created Date", isSticky: true, type: "date" },
    { key: "approved_date", label: "Approved Date", isSticky: true, type: "date" },
    { key: "voucher_type", label: "Voucher Type" },
    { key: "voucher_status", label: "Status", type: "badge" },
    { key: "party_code", label: "Party Code" },
    { key: "party_description", label: "Party Description" },
    { key: "account_description", label: "Account Description" },
    { key: "validation_status", label: "Validation Status", type: "validation_badge" },
    { key: "narration", label: "Narration" },
    { key: "created_by", label: "Created By" },
    { key: "approved_by", label: "Approved By" }
  ],

  init() {
    this.bindSubTabEvents();
    this.bindUploadEvents();
    this.bindFilterEvents();
    this.setupTable();
  },

  // 1. SUB-TAB MANAGEMENT
  bindSubTabEvents() {
    // Top sub-tab button clicks
    document.querySelectorAll(".daybook-subtab-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        const subtab = btn.dataset.subtab;
        this.switchSubTab(subtab);
      });
    });

    // Sidebar sub-item clicks
    document.querySelectorAll(".nav-subitem[data-view]").forEach(item => {
      item.addEventListener("click", (e) => {
        e.preventDefault();
        const view = item.dataset.view;
        if (view === "daybook-upload") {
          App.navigate("daybook");
          this.switchSubTab("upload");
        } else if (view === "daybook-dashboard") {
          App.navigate("daybook");
          this.switchSubTab("dashboard");
        }
      });
    });
  },

  switchSubTab(tabName) {
    this.currentSubTab = tabName;

    // Toggle subviews
    const uploadView = document.getElementById("daybook-subview-upload");
    const dashboardView = document.getElementById("daybook-subview-dashboard");

    if (uploadView && dashboardView) {
      if (tabName === "upload") {
        uploadView.style.display = "block";
        dashboardView.style.display = "none";
      } else {
        uploadView.style.display = "none";
        dashboardView.style.display = "block";
      }
    }

    // Toggle top button active states
    document.querySelectorAll(".daybook-subtab-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.subtab === tabName);
    });

    // Toggle sidebar subitem active states
    document.querySelectorAll(".nav-subitem").forEach(item => {
      const match = (tabName === "upload" && item.dataset.view === "daybook-upload") ||
                    (tabName === "dashboard" && item.dataset.view === "daybook-dashboard");
      item.classList.toggle("active", match);
    });

    // If switching to dashboard, reload cards and table
    if (tabName === "dashboard") {
      this.loadDashboardData();
    }
  },

  // 2. SETUP TABLE CONTROLLER
  setupTable() {
    const container = document.getElementById("daybook-table-container");
    if (!container) return;

    this.dtController = new DataTableController({
      containerId: "daybook-table-container",
      datasetType: "daybook",
      columns: this.columns,
      fetchFn: (params) => {
        // Inject current validation status filter
        if (this.activeStatusFilter && this.activeStatusFilter !== "All Transactions") {
          params.validation_status = this.activeStatusFilter;
        }
        return API.getDayBook(params);
      }
    });

    this.dtController.init();
  },

  // 3. DASHBOARD DATA & SUMMARY CARDS
  async loadDashboardData() {
    await this.loadSummaryCards();
    if (this.dtController) {
      this.dtController.loadData();
    }
  },

  async loadSummaryCards() {
    try {
      const params = {};
      // If table controller has active search/site, forward to stats
      if (this.dtController) {
        if (this.dtController.site) params.site = this.dtController.site;
        if (this.dtController.voucherType) params.voucher_type = this.dtController.voucherType;
        if (this.dtController.search) params.search = this.dtController.search;
      }

      const res = await API.getDayBookStats(params);
      if (!res) return;

      this.updateCardValue("card-val-total", res.total_transactions || 0);
      this.updateCardValue("card-val-matched", res.matched || 0);
      this.updateCardValue("card-val-backdate", res.back_date_entry || 0);
      this.updateCardValue("card-val-lateappr", res.late_approval || 0);
      this.updateCardValue("card-val-combined", res.back_date_late_approval || 0);
      this.updateCardValue("card-val-pending", res.pending_check_dates || 0);
      this.updateCardValue("card-val-other", res.balance_other || 0);

      // Total count badge
      const badge = document.getElementById("daybook-batch-code-badge");
      if (badge) {
        badge.innerText = `${(res.total_transactions || 0).toLocaleString()} Records Active`;
      }

      // Update Filter Bar active pill
      this.syncFilterPills();
    } catch (err) {
      console.warn("Failed to load Day Book summary metrics:", err);
    }
  },

  updateCardValue(elemId, num) {
    const el = document.getElementById(elemId);
    if (el) {
      el.innerText = Number(num).toLocaleString("en-IN");
    }
  },

  // 4. FILTER CONTROLS & STATUS PILLS
  bindFilterEvents() {
    // Interactive KPI Ribbon Status Pills: Click to filter (with toggle off back to All)
    document.querySelectorAll(".val-filter-pill").forEach(pill => {
      pill.addEventListener("click", (e) => {
        e.preventDefault();
        const targetStatus = pill.dataset.status;
        if (this.activeStatusFilter === targetStatus && targetStatus !== "All Transactions") {
          // Toggle off if already active
          this.setStatusFilter("All Transactions");
        } else {
          this.setStatusFilter(targetStatus);
        }
      });
    });

    // Reset / Clear filters button
    const clearBtn = document.getElementById("btn-clear-daybook-filters");
    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        this.resetAllFilters();
      });
    }

    // Export button
    const exportBtn = document.getElementById("btn-export-daybook-dashboard");
    if (exportBtn) {
      exportBtn.addEventListener("click", () => {
        this.exportData();
      });
    }
  },

  setStatusFilter(statusName) {
    this.activeStatusFilter = statusName || "All Transactions";
    this.syncFilterPills();

    // Reload datatable from page 1
    if (this.dtController) {
      this.dtController.page = 1;
      this.dtController.loadData();
    }

    // Update active filter chip indicator
    const chipText = document.getElementById("active-filter-indicator");
    if (chipText) {
      if (this.activeStatusFilter === "All Transactions") {
        chipText.innerHTML = `Showing: <strong>All Transactions</strong>`;
      } else {
        chipText.innerHTML = `Filtered: <strong>${this.activeStatusFilter}</strong> <a href="javascript:void(0)" onclick="DayBook.setStatusFilter('All Transactions')" style="margin-left:6px; color:#2563eb; font-size:0.75rem; text-decoration:underline;">(Reset)</a>`;
      }
    }
  },

  syncFilterPills() {
    document.querySelectorAll(".val-filter-pill").forEach(pill => {
      pill.classList.toggle("active", pill.dataset.status === this.activeStatusFilter);
    });
  },

  resetAllFilters() {
    this.activeStatusFilter = "All Transactions";
    this.syncFilterPills();
    if (this.dtController) {
      this.dtController.search = "";
      this.dtController.site = "";
      this.dtController.selectedSites = [];
      this.dtController.voucherType = "";
      this.dtController.selectedVTypes = [];
      this.dtController.approvedBy = "";
      this.dtController.selectedApprovers = [];
      this.dtController.page = 1;
      const searchInput = document.querySelector("#daybook-table-container .dt-search");
      if (searchInput) searchInput.value = "";
      this.dtController.loadData();
    }
    this.loadSummaryCards();
  },

  async exportData() {
    try {
      App.toast("Generating complete Day Book register (44 Columns + Validation Status)...", "info");
      const res = await fetch("/api/export/daybook", {
        headers: { "Authorization": `Bearer ${API.getToken()}` }
      });
      if (!res.ok) throw new Error("Export request failed");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `DayBook_Register_Validated_${new Date().toISOString().slice(0,10)}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      App.toast("Export downloaded successfully!", "success");
    } catch (e) {
      App.toast("Export failed: " + e.message, "danger");
    }
  },

  // 5. UPLOAD & EXCEL VALIDATION WORKFLOW
  bindUploadEvents() {
    const dropZone = document.getElementById("daybook-drop-zone");
    const fileInput = document.getElementById("daybook-file-input");
    const chooseBtn = document.getElementById("btn-choose-daybook-file");
    const validateBtn = document.getElementById("btn-daybook-validate");
    const commitBtn = document.getElementById("btn-daybook-commit");

    if (chooseBtn && fileInput) {
      chooseBtn.addEventListener("click", () => fileInput.click());
    }

    if (dropZone && fileInput) {
      dropZone.addEventListener("click", (e) => {
        if (e.target !== chooseBtn && !e.target.closest("#btn-choose-daybook-file")) {
          fileInput.click();
        }
      });

      dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
      });

      dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
      });

      dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
          this.handleFileSelected(e.dataTransfer.files[0]);
        }
      });

      fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
          this.handleFileSelected(e.target.files[0]);
        }
      });
    }

    if (validateBtn) {
      validateBtn.addEventListener("click", () => {
        if (!this.selectedFile) {
          App.toast("Please select a Day Book Excel file first.", "warning");
          return;
        }
        this.runValidation(this.selectedFile);
      });
    }

    if (commitBtn) {
      commitBtn.addEventListener("click", () => {
        if (!this.selectedFile) {
          App.toast("Please select a Day Book Excel file first.", "warning");
          return;
        }
        this.runUploadAndCommit(this.selectedFile);
      });
    }
  },

  handleFileSelected(file) {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
      App.toast("Please upload a valid Excel spreadsheet (.xlsx or .xls).", "danger");
      return;
    }

    this.selectedFile = file;

    // Show file info card
    const infoCard = document.getElementById("daybook-file-info-box");
    const nameEl = document.getElementById("daybook-file-name");
    const sizeEl = document.getElementById("daybook-file-size");

    if (infoCard && nameEl && sizeEl) {
      nameEl.innerText = file.name;
      sizeEl.innerText = (file.size / 1024).toFixed(1) + " KB";
      infoCard.style.display = "flex";
    }

    // Enable buttons
    const validateBtn = document.getElementById("btn-daybook-validate");
    const commitBtn = document.getElementById("btn-daybook-commit");
    if (validateBtn) validateBtn.disabled = false;
    if (commitBtn) commitBtn.disabled = false;

    // Auto-run validation for immediate user feedback
    this.runValidation(file);
  },

  async runValidation(file) {
    const reportCard = document.getElementById("daybook-validation-report-card");
    const loader = document.getElementById("daybook-upload-loader");
    if (loader) loader.style.display = "flex";

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await API.validateDayBook(formData);
      if (loader) loader.style.display = "none";

      this.renderValidationReport(res);
      if (reportCard) reportCard.style.display = "block";

      if (res.is_valid) {
        App.toast("Day Book verified successfully! All 44 columns match in exact sequence.", "success");
      } else {
        App.toast("Validation warning: " + res.message, "warning");
      }
    } catch (err) {
      if (loader) loader.style.display = "none";
      App.toast("Validation failed: " + err.message, "danger");
    }
  },

  renderValidationReport(data) {
    const container = document.getElementById("daybook-report-content");
    if (!container) return;

    const stats = data.stats || {};
    const isValid = data.is_valid;

    container.innerHTML = `
      <!-- 1. Header Validation Status Pill -->
      <div class="report-header-banner ${isValid ? 'banner-success' : 'banner-warning'}">
        <div class="banner-icon">${isValid ? '✅' : '⚠️'}</div>
        <div class="banner-text">
          <h4>${isValid ? 'Excel Column Structure & Sequence 100% Verified' : 'Column Mismatch Detected'}</h4>
          <p>${data.message || ''}</p>
        </div>
        <div class="banner-meta">
          <span class="badge ${isValid ? 'badge-success' : 'badge-danger'}">${data.columns_matched || 0} / 44 Columns Matched</span>
        </div>
      </div>

      <!-- 2. Dynamic Metric Summary Pills -->
      <div class="report-metrics-grid">
        <div class="report-metric-card">
          <div class="rm-num">${(stats.total_rows || 0).toLocaleString()}</div>
          <div class="rm-label">Total Valid Data Rows</div>
        </div>
        <div class="report-metric-card metric-matched">
          <div class="rm-num">${(stats.matched || 0).toLocaleString()}</div>
          <div class="rm-label">Matched (V = A)</div>
        </div>
        <div class="report-metric-card metric-backdate">
          <div class="rm-num">${(stats.back_date_entry || 0).toLocaleString()}</div>
          <div class="rm-label">Back Date Entry (C = A)</div>
        </div>
        <div class="report-metric-card metric-lateappr">
          <div class="rm-num">${(stats.late_approval || 0).toLocaleString()}</div>
          <div class="rm-label">Late Approval (V = C)</div>
        </div>
        <div class="report-metric-card metric-combined">
          <div class="rm-num">${(stats.back_date_late_approval || 0).toLocaleString()}</div>
          <div class="rm-label">Back Date & Late Appr.</div>
        </div>
        <div class="report-metric-card metric-pending">
          <div class="rm-num">${(stats.pending_check_dates || 0).toLocaleString()}</div>
          <div class="rm-label">Pending / Check Dates</div>
        </div>
      </div>

      <!-- 3. Top 10 Preview Table with Status Badges -->
      <div class="report-preview-section">
        <div class="report-preview-header">
          <h5>Verified Transaction Preview (Top ${data.preview_items ? data.preview_items.length : 0} rows)</h5>
          <span style="font-size:0.78rem; color:#64748b;">All 44 Excel columns preserved with evaluated status</span>
        </div>
        <div class="table-responsive" style="max-height: 280px; overflow-y: auto;">
          <table class="data-table preview-table" style="font-size: 0.78rem;">
            <thead>
              <tr>
                <th>#</th>
                <th>Validation Status</th>
                <th>Voucher No.</th>
                <th>Site</th>
                <th>Voucher Date</th>
                <th>Created Date</th>
                <th>Approved Date</th>
                <th>Voucher Type</th>
                <th>Party Description</th>
                <th>Total Amount</th>
              </tr>
            </thead>
            <tbody>
              ${(data.preview_items || []).map((row, idx) => `
                <tr>
                  <td>${idx + 1}</td>
                  <td>${ValidationStatusBadge.render(row.validation_status)}</td>
                  <td><strong>${row['Voucher Number'] || row.voucher_number || '—'}</strong></td>
                  <td><span class="site-badge">${row['Transaction Site'] || row.transaction_site || '—'}</span></td>
                  <td>${row['Voucher Date'] || '—'}</td>
                  <td>${row['Created Date'] || '—'}</td>
                  <td>${row['Approved Date'] || '—'}</td>
                  <td>${row['Voucher Type'] || '—'}</td>
                  <td>${row['Party Description'] || '—'}</td>
                  <td>₹ ${Number(row['Total Amount in Domestic Currency'] || 0).toLocaleString('en-IN', {minimumFractionDigits: 2})}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. Save to Dashboard Action Callout -->
      <div class="report-actions-bar">
        <button type="button" class="btn btn-primary btn-lg" onclick="DayBook.runUploadAndCommit(DayBook.selectedFile)">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" style="vertical-align:-3px; margin-right:6px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
          Commit & Save Verified Records to Dashboard
        </button>
      </div>
    `;
  },

  async runUploadAndCommit(file) {
    if (!file) return;
    const loader = document.getElementById("daybook-upload-loader");
    if (loader) loader.style.display = "flex";

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await API.uploadDayBook(formData);
      if (loader) loader.style.display = "none";

      App.toast(res.message || "Day Book successfully saved to dashboard!", "success");

      // Auto-switch to Dashboard sub-tab and display fresh dataset
      this.switchSubTab("dashboard");
    } catch (err) {
      if (loader) loader.style.display = "none";
      App.toast("Failed to import Day Book: " + err.message, "danger");
    }
  }
};

window.DayBook = DayBook;
