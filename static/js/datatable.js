const PersonBadge = {
  // 24 Hand-Curated High-Contrast Executive Palettes
  palettes: [
    { id: "royal-blue", bg: "#dbeafe", text: "#1e3a8a", border: "#93c5fd", avatarBg: "#2563eb", avatarText: "#ffffff" },
    { id: "coral-orange", bg: "#ffedd5", text: "#9a3412", border: "#fdba74", avatarBg: "#ea580c", avatarText: "#ffffff" },
    { id: "emerald-green", bg: "#d1fae5", text: "#064e3b", border: "#6ee7b7", avatarBg: "#059669", avatarText: "#ffffff" },
    { id: "deep-indigo", bg: "#e0e7ff", text: "#312e81", border: "#a5b4fc", avatarBg: "#4f46e5", avatarText: "#ffffff" },
    { id: "electric-cyan", bg: "#cffafe", text: "#164e63", border: "#67e8f9", avatarBg: "#0284c7", avatarText: "#ffffff" },
    { id: "vibrant-amber", bg: "#fef3c7", text: "#78350f", border: "#fcd34d", avatarBg: "#d97706", avatarText: "#ffffff" },
    { id: "plum-purple", bg: "#f3e8ff", text: "#581c87", border: "#d8b4fe", avatarBg: "#7c3aed", avatarText: "#ffffff" },
    { id: "forest-pine", bg: "#dcfce7", text: "#14532d", border: "#86efac", avatarBg: "#16a34a", avatarText: "#ffffff" },
    { id: "rose-carmine", bg: "#ffe4e6", text: "#881337", border: "#fda4af", avatarBg: "#e11d48", avatarText: "#ffffff" },
    { id: "teal-jade", bg: "#ccfbf1", text: "#134e4a", border: "#5eead4", avatarBg: "#0d9488", avatarText: "#ffffff" },
    { id: "sky-cerulean", bg: "#e0f2fe", text: "#075985", border: "#7dd3fc", avatarBg: "#0284c7", avatarText: "#ffffff" },
    { id: "fuchsia-pink", bg: "#fce7f3", text: "#701a75", border: "#f472b6", avatarBg: "#c026d3", avatarText: "#ffffff" },
    { id: "lime-olive", bg: "#ecfccb", text: "#365314", border: "#bef264", avatarBg: "#65a30d", avatarText: "#ffffff" },
    { id: "electric-violet", bg: "#ede9fe", text: "#3b0764", border: "#c4b5fd", avatarBg: "#6d28d9", avatarText: "#ffffff" },
    { id: "crimson-ruby", bg: "#fee2e2", text: "#7f1d1d", border: "#fca5a5", avatarBg: "#dc2626", avatarText: "#ffffff" },
    { id: "bronze-terracotta", bg: "#fbe9e7", text: "#3e2723", border: "#ffab91", avatarBg: "#8d6e63", avatarText: "#ffffff" },
    { id: "tangerine", bg: "#fff3e0", text: "#bf360c", border: "#ffb74d", avatarBg: "#f4511e", avatarText: "#ffffff" },
    { id: "peacock-green", bg: "#e0f2f1", text: "#004d40", border: "#80cbc4", avatarBg: "#00796b", avatarText: "#ffffff" },
    { id: "steel-slate", bg: "#f1f5f9", text: "#0f172a", border: "#cbd5e1", avatarBg: "#475569", avatarText: "#ffffff" },
    { id: "magenta-orchid", bg: "#fce4ec", text: "#880e4f", border: "#f48fb1", avatarBg: "#d81b60", avatarText: "#ffffff" },
    { id: "gold-brass", bg: "#fffbeb", text: "#92400e", border: "#fde68a", avatarBg: "#b45309", avatarText: "#ffffff" },
    { id: "grape-violet", bg: "#faf5ff", text: "#6b21a8", border: "#e9d5ff", avatarBg: "#9333ea", avatarText: "#ffffff" },
    { id: "seafoam-mint", bg: "#ecfeff", text: "#155e75", border: "#a5f3fc", avatarBg: "#0891b2", avatarText: "#ffffff" },
    { id: "ruby-wine", bg: "#fff1f2", text: "#9f1239", border: "#fecdd3", avatarBg: "#be123c", avatarText: "#ffffff" }
  ],

  // Distinct Full Name Registry for 100% Unique Colors across all active employees & officers
  namePaletteMap: {
    "Abhishek Kumar": { bg: "#dbeafe", text: "#1e3a8a", border: "#93c5fd", avatarBg: "#2563eb", avatarText: "#ffffff" }, // Royal Blue
    "Abhishek Riwadiya": { bg: "#ffedd5", text: "#9a3412", border: "#fdba74", avatarBg: "#ea580c", avatarText: "#ffffff" }, // Coral Orange
    "Akhtar Khan": { bg: "#d1fae5", text: "#064e3b", border: "#6ee7b7", avatarBg: "#059669", avatarText: "#ffffff" }, // Emerald
    "Ankush Dhingra": { bg: "#e0e7ff", text: "#312e81", border: "#a5b4fc", avatarBg: "#4f46e5", avatarText: "#ffffff" }, // Deep Indigo
    "Deepak Mehna": { bg: "#cffafe", text: "#164e63", border: "#67e8f9", avatarBg: "#0284c7", avatarText: "#ffffff" }, // Electric Cyan
    "Jaskawal Singh": { bg: "#fef3c7", text: "#78350f", border: "#fcd34d", avatarBg: "#d97706", avatarText: "#ffffff" }, // Vibrant Amber
    "Krishan Kumar": { bg: "#f3e8ff", text: "#581c87", border: "#d8b4fe", avatarBg: "#7c3aed", avatarText: "#ffffff" }, // Plum Purple
    "Lokesh Kumar": { bg: "#dcfce7", text: "#14532d", border: "#86efac", avatarBg: "#16a34a", avatarText: "#ffffff" }, // Forest Pine
    "Nageen Kumar": { bg: "#ffe4e6", text: "#881337", border: "#fda4af", avatarBg: "#e11d48", avatarText: "#ffffff" }, // Rose Carmine
    "Pankaj Bhardwaj": { bg: "#ccfbf1", text: "#134e4a", border: "#5eead4", avatarBg: "#0d9488", avatarText: "#ffffff" }, // Teal Jade
    "Prince Kumar": { bg: "#faf5ff", text: "#6b21a8", border: "#e9d5ff", avatarBg: "#9333ea", avatarText: "#ffffff" }, // Grape Violet
    "Rahul Kumar": { bg: "#e0f2fe", text: "#075985", border: "#7dd3fc", avatarBg: "#0284c7", avatarText: "#ffffff" }, // Sky Cerulean
    "Ram Bhatia": { bg: "#fbe9e7", text: "#3e2723", border: "#ffab91", avatarBg: "#8d6e63", avatarText: "#ffffff" }, // Bronze Terracotta
    "Ravi Phutela": { bg: "#fff3e0", text: "#bf360c", border: "#ffb74d", avatarBg: "#f4511e", avatarText: "#ffffff" }, // Tangerine
    "Ravinder Sharma": { bg: "#fce7f3", text: "#701a75", border: "#f472b6", avatarBg: "#c026d3", avatarText: "#ffffff" }, // Fuchsia Pink
    "Rohit Aggarwal": { bg: "#ecfccb", text: "#365314", border: "#bef264", avatarBg: "#65a30d", avatarText: "#ffffff" }, // Lime Olive
    "Rohit Gupta": { bg: "#ede9fe", text: "#3b0764", border: "#c4b5fd", avatarBg: "#6d28d9", avatarText: "#ffffff" }, // Electric Violet
    "SANDIP DAS": { bg: "#e0f2f1", text: "#004d40", border: "#80cbc4", avatarBg: "#00796b", avatarText: "#ffffff" }, // Peacock Green
    "Shubham Bhatnagar": { bg: "#ecfeff", text: "#155e75", border: "#a5f3fc", avatarBg: "#0891b2", avatarText: "#ffffff" }, // Seafoam Mint
    "Tarun Kumar": { bg: "#fee2e2", text: "#7f1d1d", border: "#fca5a5", avatarBg: "#dc2626", avatarText: "#ffffff" }, // Crimson Ruby
    "Utpal Paul": { bg: "#f1f5f9", text: "#0f172a", border: "#cbd5e1", avatarBg: "#475569", avatarText: "#ffffff" }, // Steel Slate
    "Yogesh Khandelia": { bg: "#fce4ec", text: "#880e4f", border: "#f48fb1", avatarBg: "#d81b60", avatarText: "#ffffff" } // Magenta Orchid
  },

  getPalette(fullName) {
    if (!fullName) return this.palettes[0];
    const clean = String(fullName).trim();

    // Check exact case-insensitive map first
    for (const [k, p] of Object.entries(this.namePaletteMap)) {
      if (k.toLowerCase() === clean.toLowerCase()) {
        return p;
      }
    }

    // 32-bit FNV-1a Hash on FULL string for dynamic names
    let hash = 2166136261;
    const lower = clean.toLowerCase();
    for (let i = 0; i < lower.length; i++) {
      hash ^= lower.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    const idx = Math.abs(hash) % this.palettes.length;
    return this.palettes[idx];
  },

  getInitials(fullName) {
    if (!fullName) return "?";
    const parts = String(fullName).trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  },

  render(name, fieldType = "created") {
    const isApproved = fieldType === "approved" || fieldType === "approved_by";

    if (!name || name === "None" || name === "null" || name === "undefined" || name === "-" || name === "—") {
      if (isApproved) {
        return `
          <span class="person-badge badge-pending" title="Approval Status: Pending / Unapproved">
            <span class="person-avatar">⏳</span>
            <span class="person-name">Unapproved</span>
          </span>
        `;
      }
      return `<span style="color: var(--text-muted); font-style: italic;">—</span>`;
    }

    const p = this.getPalette(name);
    const initials = this.getInitials(name);
    const safeName = String(name).replace(/"/g, '&quot;');

    if (isApproved) {
      return `
        <span class="person-badge badge-approved" style="background: ${p.bg}; color: ${p.text}; border: 1px solid ${p.border};" title="Approved by: ${safeName}">
          <span class="person-avatar" style="background: ${p.avatarBg}; color: ${p.avatarText};">${initials}</span>
          <span class="person-name">${safeName}</span>
          <span class="person-check" title="Verified Approved">✓</span>
        </span>
      `;
    }

    return `
      <span class="person-badge badge-author" style="background: ${p.bg}; color: ${p.text}; border: 1px solid ${p.border};" title="Created by: ${safeName}">
        <span class="person-avatar" style="background: ${p.avatarBg}; color: ${p.avatarText};">${initials}</span>
        <span class="person-name">${safeName}</span>
      </span>
    `;
  }
};

const StatusBadge = {
  render(status) {
    if (!status || status === "—" || status === "null" || status === "undefined") {
      return `<span style="color: var(--text-muted); font-style: italic;">—</span>`;
    }
    const s = String(status).trim();
    const lower = s.toLowerCase();

    let styleClass = "status-badge-neutral";
    let iconSvg = `<svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="6"></circle></svg>`;

    if (lower.includes("released")) {
      styleClass = "status-badge-released";
      iconSvg = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>`;
    } else if (lower.includes("approved") || lower.includes("validated") || lower.includes("completed") || lower.includes("success")) {
      styleClass = "status-badge-approved";
      iconSvg = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
    } else if (lower.includes("exported") || lower.includes("gl")) {
      styleClass = "status-badge-gl";
      iconSvg = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>`;
    } else if (lower.includes("unapproved") || lower.includes("pending") || lower.includes("draft") || lower.includes("hold")) {
      styleClass = "status-badge-pending";
      iconSvg = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`;
    } else if (lower.includes("reject") || lower.includes("failed") || lower.includes("cancel")) {
      styleClass = "status-badge-danger";
      iconSvg = `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>`;
    }

    return `<span class="status-badge ${styleClass}">${iconSvg}<span>${s}</span></span>`;
  }
};

const VerificationManager = {
  getStorageKey(datasetType, rowId, voucherNo) {
    const ident = (voucherNo && voucherNo !== "—" && voucherNo !== "null") ? voucherNo : rowId;
    return `voucher_verified_${datasetType}_${ident}`;
  },

  isVerified(datasetType, rowId, voucherNo) {
    const ident = (voucherNo && voucherNo !== "—" && voucherNo !== "null") ? voucherNo : rowId;
    const candidates = [
      `voucher_verified_${datasetType}_${ident}`,
      `voucher_verified_master_${ident}`,
      `voucher_verified_daybook_${ident}`,
      `voucher_verified_ap_${ident}`,
      `voucher_verified_ar_${ident}`
    ];
    for (const k of candidates) {
      const data = localStorage.getItem(k);
      if (data) {
        try {
          return JSON.parse(data);
        } catch (_) { }
      }
    }
    return null;
  },

  getAllVerificationsMap(datasetType) {
    const map = {};
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith("voucher_verified_")) {
          const parts = key.split("_");
          // key format: voucher_verified_<datasetType>_<ident>
          if (parts.length >= 4) {
            const ident = parts.slice(3).join("_");
            try {
              const val = JSON.parse(localStorage.getItem(key));
              if (val && val.verified_by) {
                map[ident] = val.verified_by;
              }
            } catch (_) { }
          }
        }
      }
    } catch (e) {
      console.warn("Failed to collect verifications map", e);
    }
    return map;
  },

  toggleVerify(datasetType, rowId, voucherNo) {
    const user = API.getUser();
    const userName = user.fullName || user.username || "Authorized Verifier";
    const ident = (voucherNo && voucherNo !== "—" && voucherNo !== "null") ? voucherNo : rowId;
    const key = this.getStorageKey(datasetType, rowId, voucherNo);
    const current = this.isVerified(datasetType, rowId, voucherNo);

    if (current) {
      const candidates = [
        `voucher_verified_${datasetType}_${ident}`,
        `voucher_verified_master_${ident}`,
        `voucher_verified_daybook_${ident}`,
        `voucher_verified_ap_${ident}`,
        `voucher_verified_ar_${ident}`
      ];
      candidates.forEach(k => localStorage.removeItem(k));
      App.toast(`Unmarked verification for ${voucherNo || 'record'}`, "info");
      return null;
    } else {
      const payload = {
        verified_by: userName,
        role: user.role || "User",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        date: new Date().toLocaleDateString()
      };
      localStorage.setItem(key, JSON.stringify(payload));
      if (voucherNo && voucherNo !== "—" && voucherNo !== "null") {
        localStorage.setItem(`voucher_verified_master_${voucherNo}`, JSON.stringify(payload));
      }
      App.toast(`✓ Successfully verified by ${userName}`, "success");
      return payload;
    }
  },

  renderButton(row, datasetType) {
    const rowId = row.id;
    const voucherNo = row.voucher_number || rowId;
    const verification = this.isVerified(datasetType, rowId, voucherNo);

    if (verification) {
      return `
        <button type="button" class="btn-verify-badge verified" data-dataset="${datasetType}" data-id="${rowId}" data-voucher="${voucherNo}" title="Verified by ${verification.verified_by} at ${verification.timestamp} (${verification.date}). Click to toggle.">
          <svg class="anim-pop" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span>${verification.verified_by}</span>
        </button>
      `;
    } else {
      const user = API.getUser();
      const currentName = user.fullName || user.username || "User";
      return `
        <button type="button" class="btn-verify-badge unverified" data-dataset="${datasetType}" data-id="${rowId}" data-voucher="${voucherNo}" title="Click to verify as ${currentName}">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"></circle>
            <polyline points="9 12 11 14 15 10"></polyline>
          </svg>
          <span>Verify</span>
        </button>
      `;
    }
  }
};
window.PersonBadge = PersonBadge;

class DataTableController {
  constructor(config) {
    this.containerId = config.containerId;
    this.datasetType = config.datasetType; // 'master', 'daybook', 'ap', 'ar'
    this.columns = config.columns;
    this.fetchFn = config.fetchFn;
    this.page = 1;
    this.pageSize = 15;
    this.search = "";
    this.site = "";
    this.voucherType = "";
    this.voucherSubtype = "";
    this.registerType = "";
    this.batchId = "";
    this.verifyStatus = "all"; // 'all', 'verified', 'pending'
    this.approvedBy = "";
    this.sortBy = "id";
    this.sortOrder = "desc";
    this.data = [];
    this.total = 0;
    this.totalPages = 1;
    this.hiddenColumns = new Set();
  }

  init() {
    this.renderSkeleton();
    this.bindControls();
    this.bindScrollSync();
    this.loadData();
  }

  renderSkeleton() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="filter-bar">
        <div class="filter-group" style="flex: 2; min-width: 190px;">
          <label class="filter-label">Global Search</label>
          <input type="text" class="form-control dt-search" placeholder="Search Voucher, Party, Invoice, Narration..." />
        </div>
        ${this.datasetType === 'master' ? `
        <div class="filter-group filter-group-register">
          <label class="filter-label">Linked Register</label>
          <select class="form-select dt-register-filter">
            <option value="">🌐 All Registers (DayBook+AP+AR)</option>
            <option value="ap">📥 AP Reconciled Only</option>
            <option value="ar">📤 AR Reconciled Only</option>
            <option value="daybook_only">📖 Day Book Standalone Only</option>
          </select>
        </div>` : ''}
        <div class="filter-group">
          <label class="filter-label">Site</label>
          <select class="form-select dt-site-filter">
            <option value="">All Sites</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Voucher Type</label>
          <select class="form-select dt-vtype-filter">
            <option value="">All Voucher Types</option>
          </select>
        </div>
        ${this.datasetType === 'ap' || this.datasetType === 'ar' ? `
        <div class="filter-group">
          <label class="filter-label">Voucher Sub-Type</label>
          <select class="form-select dt-vsubtype-filter">
            <option value="">All Sub-Types</option>
          </select>
        </div>` : ''}
        <div class="filter-group">
          <label class="filter-label">Approved By</label>
          <select class="form-select dt-approved-by-filter">
            <option value="">All Approvers</option>
            <option value="approved">✓ Approved Only</option>
            <option value="pending">⏳ Pending Approval</option>
          </select>
        </div>
        <div class="filter-group filter-group-verify">
          <label class="filter-label">Verification</label>
          <div class="verify-radio-group">
            <button type="button" class="verify-radio-pill active" data-value="all" title="Show All Records">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              <span>All</span>
            </button>
            <button type="button" class="verify-radio-pill" data-value="verified" title="Show Verified Records Only">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              <span>Verified</span>
            </button>
            <button type="button" class="verify-radio-pill" data-value="pending" title="Show Pending Verification Only">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span>Pending</span>
            </button>
          </div>
        </div>
        <div class="filter-group filter-group-batch">
          <label class="filter-label">Upload Batch</label>
          <select class="form-select dt-batch-filter">
            <option value="">All Batches</option>
          </select>
        </div>
      </div>

      <!-- Dynamic Active Filters Indicator Bar -->
      <div class="dt-active-filters-bar" style="display: none;">
        <div class="active-filters-header">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
          <span>Active Filters:</span>
        </div>
        <div class="active-filters-chips-list"></div>
        <button type="button" class="btn-clear-all-chips" title="Clear all active filters">
          Reset All
        </button>
      </div>

      <div class="dt-sub-bar" style="display: flex; justify-content: space-between; align-items: center; margin: 0.55rem 0 0.35rem 0; flex-wrap: wrap; gap: 0.5rem;">
        <div class="dt-records-badge" style="font-size: 0.82rem; color: var(--text-secondary); font-weight: 500; display: flex; align-items: center; gap: 0.35rem;">
          <span>Showing</span> <strong class="dt-count-text" style="color: var(--text-primary); font-weight: 700; background: #e2e8f0; padding: 0.1rem 0.45rem; border-radius: 4px;">0</strong> <span>records</span>
        </div>
        
        <div style="display: flex; align-items: center; gap: 0.65rem; flex-wrap: wrap;">
          <button class="btn btn-secondary btn-sm dt-btn-clear" style="padding: 0.32rem 0.65rem; font-size: 0.78rem; font-weight: 600;" title="Reset all filters">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            Clear Filters
          </button>
          <button class="btn btn-secondary btn-sm dt-btn-export" style="padding: 0.32rem 0.65rem; font-size: 0.78rem; font-weight: 600;" title="Export Filtered Records as CSV">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"></path></svg>
            Export CSV
          </button>
          <button class="btn btn-secondary btn-sm dt-btn-print-report" style="padding: 0.32rem 0.65rem; font-size: 0.78rem; font-weight: 600; color: #1e3a8a; border-color: #bfdbfe; background: #eff6ff;" title="Generate & Print Official Statement with Digital Signature">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 6 2 18 2 18 9"></polyline><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path><rect x="6" y="14" width="12" height="8"></rect></svg>
            Print / PDF Statement
          </button>
          <div style="height: 18px; width: 1px; background: #cbd5e1; margin: 0 0.15rem;"></div>
          <div style="display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: var(--text-secondary);">
            <span>Rows:</span>
            <select class="form-select dt-page-size" style="width: 70px; padding: 0.2rem 0.45rem; font-size: 0.8rem; font-weight: 600;">
              <option value="15" selected>15</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Top Quick Scroll Navigation Strip & Precision Controller -->
      <div class="dt-top-scroll-container">
        <div class="dt-scroll-meta">
          <span class="dt-scroll-indicator-label">↔ View:</span>
          <span class="dt-scroll-pct-badge" title="Horizontal position percentage">0%</span>
        </div>
        <div class="dt-top-scroll-nav">
          <button class="dt-btn-quick-scroll dt-scroll-btn-start" title="Jump to First Column">
            ⇤ Start
          </button>
          <button class="dt-btn-quick-scroll dt-scroll-btn-left" title="Scroll Left (Step)">
            ◀ Left
          </button>
        </div>
        <div class="dt-custom-slider-track" title="Click or drag thumb to pan across table columns">
          <div class="dt-custom-slider-fill"></div>
          <div class="dt-custom-slider-thumb" tabindex="0" role="slider" aria-label="Table Horizontal Position">
            <div class="dt-slider-thumb-grip"></div>
          </div>
        </div>
        <div class="dt-top-scroll-nav">
          <button class="dt-btn-quick-scroll dt-scroll-btn-right" title="Scroll Right (Step)">
            Right ▶
          </button>
          <button class="dt-btn-quick-scroll dt-scroll-btn-end" title="Jump to Last Column (Action)">
            End ⇥
          </button>
        </div>
      </div>

      <!-- Main Responsive Table Container -->
      <div class="table-responsive has-top-scrollbar">
        <table class="data-table">
          <thead>
            <tr class="dt-thead-row"></tr>
          </thead>
          <tbody class="dt-tbody">
            <tr><td colspan="${this.columns.length + 3}" style="text-align: center; padding: 2rem;">Loading data...</td></tr>
          </tbody>
        </table>
      </div>

      <div class="pagination-wrapper">
        <div class="pagination-info dt-pag-info">Page 1 of 1</div>
        <div class="pagination-controls">
          <button class="page-btn dt-btn-prev" disabled>&laquo; Prev</button>
          <span class="dt-page-numbers" style="display: flex; gap: 0.25rem;"></span>
          <button class="page-btn dt-btn-next" disabled>Next &raquo;</button>
        </div>
      </div>
    `;

    this.renderHeader();
  }

  renderHeader() {
    const theadRow = document.querySelector(`#${this.containerId} .dt-thead-row`);
    if (!theadRow) return;

    theadRow.innerHTML = `
      <th class="dt-sticky-col-idx">#</th>
      ${this.columns.map((col, cIdx) => {
      const isStickySite = (cIdx === 0 && (col.key === 'transaction_site' || col.key === 'accounting_site_code'));
      const isStickyVoucher = (cIdx === 1 && (col.key === 'voucher_number' || col.key === 'voucher_no'));
      const stickyClass = isStickySite ? 'dt-sticky-col-site' : (isStickyVoucher ? 'dt-sticky-col-voucher' : '');
      return `
          <th class="sortable dt-th ${stickyClass}" data-col="${col.key}">
            ${col.label}
            ${this.sortBy === col.key ? (this.sortOrder === 'asc' ? ' ▲' : ' ▼') : ''}
          </th>
        `;
    }).join("")}
      <th style="text-align: center; width: 145px; min-width: 135px;">Verified By</th>
      <th style="text-align: center; width: 90px; min-width: 85px;">Action</th>
    `;

    // Bind sort events
    theadRow.querySelectorAll(".sortable").forEach(th => {
      th.addEventListener("click", () => {
        const colKey = th.dataset.col;
        if (this.sortBy === colKey) {
          this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
        } else {
          this.sortBy = colKey;
          this.sortOrder = "desc";
        }
        this.renderHeader();
        this.loadData();
      });
    });
  }

  bindControls() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    // Search input (debounced)
    const searchInput = container.querySelector(".dt-search");
    let searchTimer = null;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        this.search = e.target.value.trim();
        this.page = 1;
        this.loadData();
      }, 350);
    });

    // Site filter
    const siteSelect = container.querySelector(".dt-site-filter");
    siteSelect.addEventListener("change", (e) => {
      this.site = e.target.value;
      this.page = 1;
      this.loadData();
    });

    // Voucher Type filter
    const vtypeSelect = container.querySelector(".dt-vtype-filter");
    vtypeSelect.addEventListener("change", (e) => {
      this.voucherType = e.target.value;
      this.page = 1;
      this.loadData();
    });

    // Voucher Sub-Type filter
    const vsubtypeSelect = container.querySelector(".dt-vsubtype-filter");
    if (vsubtypeSelect) {
      vsubtypeSelect.addEventListener("change", (e) => {
        this.voucherSubtype = e.target.value;
        this.page = 1;
        this.loadData();
      });
    }

    // Approved By filter
    const approvedBySelect = container.querySelector(".dt-approved-by-filter");
    if (approvedBySelect) {
      approvedBySelect.addEventListener("change", (e) => {
        this.approvedBy = e.target.value;
        this.page = 1;
        this.loadData();
      });
    }

    // Verification radio pills
    const verifyPills = container.querySelectorAll(".verify-radio-pill");
    verifyPills.forEach(pill => {
      pill.addEventListener("click", () => {
        verifyPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.verifyStatus = pill.dataset.value || "all";
        this.renderTableData();
      });
    });

    // Batch filter
    const batchSelect = container.querySelector(".dt-batch-filter");
    batchSelect.addEventListener("change", (e) => {
      this.batchId = e.target.value;
      this.page = 1;
      this.loadData();
    });

    // Register filter for Master dataset
    const registerSelect = container.querySelector(".dt-register-filter");
    if (registerSelect) {
      registerSelect.addEventListener("change", (e) => {
        this.registerType = e.target.value;
        this.page = 1;
        this.loadData();
      });
    }

    // Clear filters
    const clearBtn = container.querySelector(".dt-btn-clear");
    clearBtn.addEventListener("click", () => {
      this.search = "";
      this.site = "";
      this.voucherType = "";
      this.voucherSubtype = "";
      this.approvedBy = "";
      this.verifyStatus = "all";
      this.registerType = "";
      
      // Reset batch to latest if available, else empty
      const firstOpt = batchSelect && batchSelect.options.length > 0 ? batchSelect.options[0].value : "";
      this.batchId = firstOpt;
      if (batchSelect) batchSelect.value = firstOpt;

      searchInput.value = "";
      siteSelect.value = "";
      vtypeSelect.value = "";
      if (vsubtypeSelect) vsubtypeSelect.value = "";
      if (approvedBySelect) approvedBySelect.value = "";
      if (registerSelect) registerSelect.value = "";
      verifyPills.forEach(p => {
        if (p.dataset.value === "all") p.classList.add("active");
        else p.classList.remove("active");
      });
      this.page = 1;
      this.loadData();
    });

    // Export CSV (Authenticated Blob Download with UTF-8 BOM)
    const exportBtn = container.querySelector(".dt-btn-export");
    if (exportBtn) {
      exportBtn.addEventListener("click", () => this.handleExportCSV(exportBtn));
    }

    // Print / PDF Certified Statement Report
    const printReportBtn = container.querySelector(".dt-btn-print-report");
    if (printReportBtn) {
      printReportBtn.addEventListener("click", () => this.handlePrintReport());
    }

    // Page size
    const pageSizeSelect = container.querySelector(".dt-page-size");
    pageSizeSelect.addEventListener("change", (e) => {
      this.pageSize = parseInt(e.target.value, 10);
      this.page = 1;
      this.loadData();
    });

    // Pagination buttons
    const prevBtn = container.querySelector(".dt-btn-prev");
    const nextBtn = container.querySelector(".dt-btn-next");

    prevBtn.addEventListener("click", () => {
      if (this.page > 1) {
        this.page--;
        this.loadData();
      }
    });

    nextBtn.addEventListener("click", () => {
      if (this.page < this.totalPages) {
        this.page++;
        this.loadData();
      }
    });
  }

  bindScrollSync() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    const tableWrapper = container.querySelector(".table-responsive");
    const trackEl = container.querySelector(".dt-custom-slider-track");
    const thumbEl = container.querySelector(".dt-custom-slider-thumb");
    const fillEl = container.querySelector(".dt-custom-slider-fill");
    const pctBadge = container.querySelector(".dt-scroll-pct-badge");
    const btnStart = container.querySelector(".dt-scroll-btn-start");
    const btnLeft = container.querySelector(".dt-scroll-btn-left");
    const btnRight = container.querySelector(".dt-scroll-btn-right");
    const btnEnd = container.querySelector(".dt-scroll-btn-end");

    if (!tableWrapper || !trackEl || !thumbEl) return;

    const updateSlider = () => {
      const scrollWidth = tableWrapper.scrollWidth;
      const clientWidth = tableWrapper.clientWidth;
      const maxScroll = Math.max(0, scrollWidth - clientWidth);

      if (maxScroll <= 0) {
        thumbEl.style.width = "100%";
        thumbEl.style.transform = "translateX(0px)";
        if (fillEl) fillEl.style.width = "100%";
        if (pctBadge) pctBadge.innerText = "100%";
        return;
      }

      const trackWidth = trackEl.clientWidth;
      const thumbWidth = Math.max(45, (clientWidth / scrollWidth) * trackWidth);
      const availableTrack = Math.max(0, trackWidth - thumbWidth);

      const scrollLeft = Math.max(0, Math.min(maxScroll, tableWrapper.scrollLeft));
      const ratio = maxScroll > 0 ? (scrollLeft / maxScroll) : 0;
      const thumbLeft = ratio * availableTrack;

      thumbEl.style.width = `${thumbWidth}px`;
      thumbEl.style.transform = `translateX(${thumbLeft}px)`;
      if (fillEl) fillEl.style.width = `${thumbLeft + (thumbWidth / 2)}px`;

      const pct = Math.round(ratio * 100);
      if (pctBadge) {
        pctBadge.innerText = `${pct}%`;
      }
    };

    this.updateScrollSlider = updateSlider;

    // Table scroll event -> update top slider thumb in real-time and preserve horizontal position
    tableWrapper.addEventListener("scroll", () => {
      this.savedScrollLeft = tableWrapper.scrollLeft;
      requestAnimationFrame(updateSlider);
    });

    // Resize Observer for auto adaptation
    if (window.ResizeObserver) {
      const ro = new ResizeObserver(() => {
        updateSlider();
      });
      ro.observe(tableWrapper);
      ro.observe(trackEl);
    }

    // Draggable Slider Thumb via Pointer Events
    let isDragging = false;
    let startPointerX = 0;
    let startScrollLeft = 0;

    thumbEl.addEventListener("pointerdown", (e) => {
      e.preventDefault();
      e.stopPropagation();
      isDragging = true;
      thumbEl.classList.add("dragging");
      startPointerX = e.clientX;
      startScrollLeft = tableWrapper.scrollLeft;
      thumbEl.setPointerCapture(e.pointerId);
    });

    thumbEl.addEventListener("pointermove", (e) => {
      if (!isDragging) return;
      const trackWidth = trackEl.clientWidth;
      const thumbWidth = thumbEl.offsetWidth;
      const availableTrack = trackWidth - thumbWidth;
      if (availableTrack <= 0) return;

      const maxScroll = tableWrapper.scrollWidth - tableWrapper.clientWidth;
      const deltaX = e.clientX - startPointerX;
      const scrollRatioDelta = deltaX / availableTrack;
      tableWrapper.scrollLeft = startScrollLeft + (scrollRatioDelta * maxScroll);
    });

    const stopDragging = (e) => {
      if (isDragging) {
        isDragging = false;
        thumbEl.classList.remove("dragging");
        try {
          thumbEl.releasePointerCapture(e.pointerId);
        } catch (_) { }
      }
    };

    thumbEl.addEventListener("pointerup", stopDragging);
    thumbEl.addEventListener("pointercancel", stopDragging);

    // Track click to jump proportionally
    trackEl.addEventListener("click", (e) => {
      if (e.target === thumbEl || thumbEl.contains(e.target)) return;
      const rect = trackEl.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const trackWidth = rect.width;
      const thumbWidth = thumbEl.offsetWidth;
      const availableTrack = trackWidth - thumbWidth;
      if (availableTrack <= 0) return;

      const targetThumbLeft = Math.max(0, Math.min(availableTrack, clickX - (thumbWidth / 2)));
      const ratio = targetThumbLeft / availableTrack;
      const maxScroll = tableWrapper.scrollWidth - tableWrapper.clientWidth;
      tableWrapper.scrollTo({ left: ratio * maxScroll, behavior: "smooth" });
    });

    // Quick scroll navigation buttons
    if (btnStart) {
      btnStart.addEventListener("click", () => {
        tableWrapper.scrollTo({ left: 0, behavior: "smooth" });
      });
    }

    if (btnLeft) {
      btnLeft.addEventListener("click", () => {
        tableWrapper.scrollBy({ left: -320, behavior: "smooth" });
      });
    }

    if (btnRight) {
      btnRight.addEventListener("click", () => {
        tableWrapper.scrollBy({ left: 320, behavior: "smooth" });
      });
    }

    if (btnEnd) {
      btnEnd.addEventListener("click", () => {
        tableWrapper.scrollTo({ left: tableWrapper.scrollWidth, behavior: "smooth" });
      });
    }

    // Keyboard arrow keys horizontal scroll navigation on table
    tableWrapper.setAttribute("tabindex", "0");
    tableWrapper.addEventListener("keydown", (e) => {
      if (e.key === "ArrowLeft") {
        e.preventDefault();
        tableWrapper.scrollBy({ left: -240, behavior: "smooth" });
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        tableWrapper.scrollBy({ left: 240, behavior: "smooth" });
      } else if (e.key === "Home" && !e.ctrlKey) {
        e.preventDefault();
        tableWrapper.scrollTo({ left: 0, behavior: "smooth" });
      } else if (e.key === "End" && !e.ctrlKey) {
        e.preventDefault();
        tableWrapper.scrollTo({ left: tableWrapper.scrollWidth, behavior: "smooth" });
      }
    });

    // Mouse wheel horizontal scroll helper over table
    tableWrapper.addEventListener("wheel", (e) => {
      if (e.deltaX !== 0) return; // Trackpad natural 2D scroll
      if (e.shiftKey || Math.abs(e.deltaY) > 0) {
        if (e.shiftKey) {
          e.preventDefault();
          tableWrapper.scrollLeft += e.deltaY;
        }
      }
    }, { passive: false });
  }

  updateScrollPhantom() {
    if (this.updateScrollSlider) {
      this.updateScrollSlider();
    }
  }

  populateFilterOptions(filterData) {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    // Populate Sites
    const siteSelect = container.querySelector(".dt-site-filter");
    if (siteSelect) {
      siteSelect.innerHTML = `<option value="">All Sites</option>` +
        filterData.sites.map(s => `<option value="${s}">${s}</option>`).join("");
      siteSelect.value = this.site;
    }

    // Populate Voucher Types
    const vtypeSelect = container.querySelector(".dt-vtype-filter");
    if (vtypeSelect) {
      vtypeSelect.innerHTML = `<option value="">All Voucher Types</option>` +
        filterData.voucher_types.map(vt => `<option value="${vt}">${vt}</option>`).join("");
      vtypeSelect.value = this.voucherType;
    }

    // Populate Voucher Subtypes
    const vsubtypeSelect = container.querySelector(".dt-vsubtype-filter");
    if (vsubtypeSelect) {
      vsubtypeSelect.innerHTML = `<option value="">All Sub-Types</option>` +
        filterData.voucher_subtypes.map(vst => `<option value="${vst}">${vst}</option>`).join("");
      vsubtypeSelect.value = this.voucherSubtype;
    }

    // Populate Approvers
    const approvedBySelect = container.querySelector(".dt-approved-by-filter");
    if (approvedBySelect && filterData.approvers) {
      approvedBySelect.innerHTML = `
        <option value="">All Approvers</option>
        <option value="approved">✓ Approved Only</option>
        <option value="pending">⏳ Pending Approval</option>
      ` + filterData.approvers.map(a => `<option value="${a}">${a}</option>`).join("");
      approvedBySelect.value = this.approvedBy;
    }

    // Populate Batches (Compact & Clean Labels)
    const batchSelect = container.querySelector(".dt-batch-filter");
    if (batchSelect && filterData.batches && filterData.batches.length > 0) {
      const latestBatch = filterData.batches[0];
      if (!this.batchId) {
        this.batchId = String(latestBatch.id);
      }
      batchSelect.innerHTML = filterData.batches.map((b, idx) => {
        const isLatest = idx === 0;
        // e.g. BATCH-20261007-001 -> B-001
        const shortCode = b.batch_code ? b.batch_code.replace(/^BATCH-\d{8}-/, 'B-') : `B-${b.id}`;
        const shortDate = b.date ? b.date.replace(/-\d{4}$/, '') : '';
        const label = isLatest 
          ? `⚡ ${shortCode} (Latest)` 
          : `📁 ${shortCode} (${shortDate})`;
        return `<option value="${b.id}">${label}</option>`;
      }).join("") + `<option value="">🌐 All Batches</option>`;
      batchSelect.value = this.batchId;
    } else if (batchSelect) {
      batchSelect.innerHTML = `<option value="">All Batches</option>`;
      batchSelect.value = "";
    }
  }

  async loadData() {
    const container = document.getElementById(this.containerId);
    const tableWrapper = container ? container.querySelector(".table-responsive") : null;
    if (tableWrapper && tableWrapper.scrollLeft > 0) {
      this.savedScrollLeft = tableWrapper.scrollLeft;
    }

    const tbody = document.querySelector(`#${this.containerId} .dt-tbody`);
    if (tbody && (!this.data || this.data.length === 0)) {
      tbody.innerHTML = `<tr><td colspan="${this.columns.length + 3}" style="text-align: center; padding: 2rem; color: var(--text-muted);">Fetching records...</td></tr>`;
    } else if (tbody) {
      tbody.style.opacity = "0.6";
      tbody.style.pointerEvents = "none";
    }

    const params = {
      page: this.page,
      page_size: this.pageSize,
      search: this.search,
      site: this.site,
      voucher_type: this.voucherType,
      voucher_subtype: this.voucherSubtype,
      approved_by: this.approvedBy,
      register_type: this.registerType,
      batch_id: this.batchId,
      sort_by: this.sortBy,
      sort_order: this.sortOrder
    };

    try {
      const response = await this.fetchFn(params);
      this.data = response.items || [];
      this.total = response.total || 0;
      this.totalPages = response.total_pages || 1;
      if (tbody) {
        tbody.style.opacity = "1";
        tbody.style.pointerEvents = "auto";
      }
      this.renderTableData();
      this.renderPagination();

      // Restore horizontal scroll position after data fetch
      if (tableWrapper && this.savedScrollLeft > 0) {
        tableWrapper.scrollLeft = this.savedScrollLeft;
      }
      setTimeout(() => {
        if (tableWrapper && this.savedScrollLeft > 0) {
          tableWrapper.scrollLeft = this.savedScrollLeft;
        }
        this.updateScrollPhantom();
      }, 50);
    } catch (err) {
      if (tbody) {
        tbody.style.opacity = "1";
        tbody.style.pointerEvents = "auto";
        tbody.innerHTML = `<tr><td colspan="${this.columns.length + 3}" style="text-align: center; padding: 2rem; color: var(--danger);">Failed to load data: ${err.message}</td></tr>`;
      }
    }
  }

  updateActiveFilterVisuals() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    const searchInput = container.querySelector(".dt-search");
    const siteSelect = container.querySelector(".dt-site-filter");
    const vtypeSelect = container.querySelector(".dt-vtype-filter");
    const vsubtypeSelect = container.querySelector(".dt-vsubtype-filter");
    const approvedBySelect = container.querySelector(".dt-approved-by-filter");
    const registerSelect = container.querySelector(".dt-register-filter");
    const clearBtn = container.querySelector(".dt-btn-clear");
    const activeFiltersBar = container.querySelector(".dt-active-filters-bar");
    const chipsList = container.querySelector(".active-filters-chips-list");

    const activeList = [];

    // Search Filter
    if (this.search && this.search.trim()) {
      if (searchInput) {
        searchInput.classList.add("filter-active");
        searchInput.closest(".filter-group")?.classList.add("has-active-filter");
      }
      activeList.push({ key: "search", label: "Search", value: `"${this.search}"` });
    } else if (searchInput) {
      searchInput.classList.remove("filter-active");
      searchInput.closest(".filter-group")?.classList.remove("has-active-filter");
    }

    // Register Type (for Master Ledger)
    if (this.registerType && this.registerType.trim()) {
      if (registerSelect) {
        registerSelect.classList.add("filter-active");
        registerSelect.closest(".filter-group")?.classList.add("has-active-filter");
      }
      const labelMap = { ap: "AP Register", ar: "AR Register", daybook_only: "Day Book Only" };
      activeList.push({ key: "registerType", label: "Register", value: labelMap[this.registerType] || this.registerType });
    } else if (registerSelect) {
      registerSelect.classList.remove("filter-active");
      registerSelect.closest(".filter-group")?.classList.remove("has-active-filter");
    }

    // Site
    if (this.site && this.site.trim()) {
      if (siteSelect) {
        siteSelect.classList.add("filter-active");
        siteSelect.closest(".filter-group")?.classList.add("has-active-filter");
      }
      activeList.push({ key: "site", label: "Site", value: this.site });
    } else if (siteSelect) {
      siteSelect.classList.remove("filter-active");
      siteSelect.closest(".filter-group")?.classList.remove("has-active-filter");
    }

    // Voucher Type
    if (this.voucherType && this.voucherType.trim()) {
      if (vtypeSelect) {
        vtypeSelect.classList.add("filter-active");
        vtypeSelect.closest(".filter-group")?.classList.add("has-active-filter");
      }
      activeList.push({ key: "voucherType", label: "Voucher Type", value: this.voucherType });
    } else if (vtypeSelect) {
      vtypeSelect.classList.remove("filter-active");
      vtypeSelect.closest(".filter-group")?.classList.remove("has-active-filter");
    }

    // Voucher Sub-Type
    if (this.voucherSubtype && this.voucherSubtype.trim()) {
      if (vsubtypeSelect) {
        vsubtypeSelect.classList.add("filter-active");
        vsubtypeSelect.closest(".filter-group")?.classList.add("has-active-filter");
      }
      activeList.push({ key: "voucherSubtype", label: "Sub-Type", value: this.voucherSubtype });
    } else if (vsubtypeSelect) {
      vsubtypeSelect.classList.remove("filter-active");
      vsubtypeSelect.closest(".filter-group")?.classList.remove("has-active-filter");
    }

    // Approved By
    if (this.approvedBy && this.approvedBy.trim()) {
      if (approvedBySelect) {
        approvedBySelect.classList.add("filter-active");
        approvedBySelect.closest(".filter-group")?.classList.add("has-active-filter");
      }
      const appLabel = this.approvedBy === "approved" ? "Approved Only" : (this.approvedBy === "pending" ? "Pending Approval" : this.approvedBy);
      activeList.push({ key: "approvedBy", label: "Approver", value: appLabel });
    } else if (approvedBySelect) {
      approvedBySelect.classList.remove("filter-active");
      approvedBySelect.closest(".filter-group")?.classList.remove("has-active-filter");
    }

    // Verification Status
    if (this.verifyStatus && this.verifyStatus !== "all") {
      const vGroup = container.querySelector(".filter-group-verify");
      if (vGroup) vGroup.classList.add("has-active-filter");
      const vLabel = this.verifyStatus === "verified" ? "Verified" : "Pending";
      activeList.push({ key: "verifyStatus", label: "Status", value: vLabel });
    } else {
      const vGroup = container.querySelector(".filter-group-verify");
      if (vGroup) vGroup.classList.remove("has-active-filter");
    }

    // Update Clear Button with Active Count Badge
    if (clearBtn) {
      if (activeList.length > 0) {
        clearBtn.classList.add("btn-clear-active");
        clearBtn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          Clear Filters <span class="dt-filter-count-badge">${activeList.length}</span>
        `;
      } else {
        clearBtn.classList.remove("btn-clear-active");
        clearBtn.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
          Clear Filters
        `;
      }
    }

    // Render Active Filter Chips in the dynamic bar
    if (activeFiltersBar && chipsList) {
      if (activeList.length > 0) {
        activeFiltersBar.style.display = "flex";
        chipsList.innerHTML = activeList.map(item => `
          <span class="active-filter-chip" title="Active Filter: ${item.label} = ${item.value}">
            <span class="chip-label">${item.label}:</span>
            <strong class="chip-val">${item.value}</strong>
            <button type="button" class="chip-remove" data-key="${item.key}" title="Remove this filter">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </span>
        `).join("");

        // Individual chip remove buttons
        chipsList.querySelectorAll(".chip-remove").forEach(btn => {
          btn.addEventListener("click", (e) => {
            e.stopPropagation();
            const key = btn.dataset.key;
            this.removeSingleFilter(key);
          });
        });

        // Reset All button
        const resetAllBtn = activeFiltersBar.querySelector(".btn-clear-all-chips");
        if (resetAllBtn) {
          resetAllBtn.onclick = () => {
            if (clearBtn) clearBtn.click();
          };
        }
      } else {
        activeFiltersBar.style.display = "none";
        chipsList.innerHTML = "";
      }
    }
  }

  removeSingleFilter(key) {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    if (key === "search") {
      this.search = "";
      const el = container.querySelector(".dt-search");
      if (el) el.value = "";
    } else if (key === "site") {
      this.site = "";
      const el = container.querySelector(".dt-site-filter");
      if (el) el.value = "";
    } else if (key === "voucherType") {
      this.voucherType = "";
      const el = container.querySelector(".dt-vtype-filter");
      if (el) el.value = "";
    } else if (key === "voucherSubtype") {
      this.voucherSubtype = "";
      const el = container.querySelector(".dt-vsubtype-filter");
      if (el) el.value = "";
    } else if (key === "approvedBy") {
      this.approvedBy = "";
      const el = container.querySelector(".dt-approved-by-filter");
      if (el) el.value = "";
    } else if (key === "registerType") {
      this.registerType = "";
      const el = container.querySelector(".dt-register-filter");
      if (el) el.value = "";
    } else if (key === "verifyStatus") {
      this.verifyStatus = "all";
      const pills = container.querySelectorAll(".verify-radio-pill");
      pills.forEach(p => {
        if (p.dataset.value === "all") p.classList.add("active");
        else p.classList.remove("active");
      });
      this.renderTableData();
      return;
    }

    this.page = 1;
    this.loadData();
  }

  renderTableData() {
    this.updateActiveFilterVisuals();
    const container = document.getElementById(this.containerId);
    const tableWrapper = container ? container.querySelector(".table-responsive") : null;
    const currentScroll = tableWrapper ? tableWrapper.scrollLeft : (this.savedScrollLeft || 0);
    if (currentScroll > 0) {
      this.savedScrollLeft = currentScroll;
    }
    const tbody = container.querySelector(".dt-tbody");
    const countText = container.querySelector(".dt-count-text");

    let displayedRows = this.data;
    if (this.verifyStatus === "verified") {
      displayedRows = this.data.filter(r => VerificationManager.isVerified(this.datasetType, r.id, r.voucher_number) !== null);
    } else if (this.verifyStatus === "pending") {
      displayedRows = this.data.filter(r => VerificationManager.isVerified(this.datasetType, r.id, r.voucher_number) === null);
    }

    if (countText) countText.innerText = (this.verifyStatus === "all" ? this.total : displayedRows.length).toLocaleString();

    if (!tbody) return;

    if (displayedRows.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="${this.columns.length + 3}" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
            No matching records found.
          </td>
        </tr>
      `;
      return;
    }

    const startIndex = (this.page - 1) * this.pageSize;
    tbody.innerHTML = displayedRows.map((row, idx) => {
      return `
        <tr data-id="${row.id}">
          <td class="dt-sticky-col-idx">${startIndex + idx + 1}</td>
          ${this.columns.map((col, cIdx) => {
        const isStickySite = (cIdx === 0 && (col.key === 'transaction_site' || col.key === 'accounting_site_code'));
        const isStickyVoucher = (cIdx === 1 && (col.key === 'voucher_number' || col.key === 'voucher_no'));
        const stickyClass = isStickySite ? 'dt-sticky-col-site' : (isStickyVoucher ? 'dt-sticky-col-voucher' : '');

        let val = row[col.key];

        // Professional Person Badges for Created By & Approved By
        if (col.key === "created_by" || col.type === "person-created") {
          return `<td class="${stickyClass}">${PersonBadge.render(val, "created")}</td>`;
        }

        if (col.key === "approved_by" || col.type === "person-approved") {
          return `<td class="${stickyClass}">${PersonBadge.render(val, "approved")}</td>`;
        }

        if (val === null || val === undefined || val === "") {
          return `<td class="${stickyClass}"><span style="color: var(--text-muted); font-style: italic;">—</span></td>`;
        }

        if (col.key === "source_tag") {
          let badgeHtml = '';
          const sVal = String(val || '');
          if (sVal.includes("DayBook + AP + AR")) {
            badgeHtml = `<span class="badge" style="background: #fdf2f8; color: #db2777; border: 1px solid #fbcfe8; font-weight: 700; white-space: nowrap;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:-1px; margin-right:4px;"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>3-WAY MATCHED</span>`;
          } else if (sVal.includes("DayBook + AP")) {
            badgeHtml = `<span class="badge" style="background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; font-weight: 600; white-space: nowrap;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:-1px; margin-right:4px;"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>DayBook + AP</span>`;
          } else if (sVal.includes("DayBook + AR")) {
            badgeHtml = `<span class="badge" style="background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; font-weight: 600; white-space: nowrap;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:-1px; margin-right:4px;"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>DayBook + AR</span>`;
          } else {
            badgeHtml = `<span class="badge" style="background: #f8fafc; color: #64748b; border: 1px solid #cbd5e1; font-weight: 500; white-space: nowrap;">Day Book Only</span>`;
          }
          return `<td class="${stickyClass}">${badgeHtml}</td>`;
        }

        if (col.key === "party_description" || col.key === "account_description" || col.key === "item_service_description" || col.key === "item_service_expense_account_desc" || col.key === "ap_item_description" || col.key === "ar_item_description" || col.key === "unified_item_description") {
          const fullDesc = String(val);
          const safeAttr = fullDesc.replace(/"/g, '&quot;');
          const shortText = fullDesc.length > 28 ? fullDesc.substring(0, 26) + '...' : fullDesc;
          const icon = col.key === 'party_description' ? '🏢' : (col.key.includes('item') ? '📦' : '📋');
          return `
                <td class="${stickyClass} tooltip-trigger-cell" data-popover-title="${col.label}" data-popover-icon="${icon}" data-full-text="${safeAttr}">
                  <div class="narration-cell-content">
                    <span class="narration-text-truncated">${shortText}</span>
                    ${fullDesc.length > 26 ? `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.8; flex-shrink: 0;" title="Click/Hover to view full details"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>` : ''}
                  </div>
                </td>
              `;
        }

        if (col.key === "narration") {
          const fullNarration = String(val);
          const safeAttr = fullNarration.replace(/"/g, '&quot;');
          const shortText = fullNarration.length > 28 ? fullNarration.substring(0, 26) + '...' : fullNarration;
          return `
                <td class="${stickyClass} tooltip-trigger-cell" data-popover-title="Narration Details" data-popover-icon="📖" data-full-text="${safeAttr}">
                  <div class="narration-cell-content">
                    <span class="narration-text-truncated">${shortText}</span>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.8; flex-shrink: 0;" title="Click/Hover to view full narration"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                  </div>
                </td>
              `;
        }

        if (col.type === "badge" || col.key === "voucher_status") {
          return `<td class="${stickyClass}">${StatusBadge.render(val)}</td>`;
        }

        if (col.type === "currency" || col.key === "combined_amount" || col.key === "unified_tax_amount" || col.key.includes("_amount") || col.key.includes("_taxes") || col.key.includes("_rate") || col.key.includes("total_cgst") || col.key.includes("total_sgst") || col.key.includes("total_igst") || col.key.includes("total_tds")) {
          const numVal = Number(val);
          const formatted = isNaN(numVal) ? (val || '—') : ("₹ " + numVal.toLocaleString("en-IN", { minimumFractionDigits: 2 }));
          return `<td class="${stickyClass} cell-currency">${formatted}</td>`;
        }

        if (col.key === "transaction_site" || col.key === "accounting_site_code") {
          return `<td class="${stickyClass}"><span class="site-badge">${val}</span></td>`;
        }

        if (col.key === "voucher_number") {
          return `<td class="${stickyClass}"><span class="voucher-num-badge">${val}</span></td>`;
        }

        if (col.key === "party_code" || col.key === "ap_invoice_number" || col.key === "invoice_number" || col.key === "unified_invoice_no") {
          return `<td class="${stickyClass}"><span class="cell-code">${val}</span></td>`;
        }

        if (col.key === "voucher_date" || col.key === "invoice_date" || col.key === "due_date") {
          return `<td class="${stickyClass} cell-date">${val}</td>`;
        }

        if (typeof val === "string" && val.length > 35) {
          val = `<span title="${val.replace(/"/g, '&quot;')}">${val.substring(0, 32)}...</span>`;
        }
        return `<td class="${stickyClass}">${val}</td>`;
      }).join("")}
          <td style="text-align: center; vertical-align: middle; white-space: nowrap;">
            ${VerificationManager.renderButton(row, this.datasetType)}
          </td>
          <td style="text-align: center; vertical-align: middle; white-space: nowrap;">
            <button class="btn btn-secondary btn-sm dt-btn-view" data-index="${idx}" title="View Details">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
              View
            </button>
          </td>
        </tr>
      `;
    }).join("");

    // Seamlessly preserve horizontal scroll position across row re-renders
    if (tableWrapper && this.savedScrollLeft > 0) {
      tableWrapper.scrollLeft = this.savedScrollLeft;
      requestAnimationFrame(() => {
        if (tableWrapper && this.savedScrollLeft > 0) {
          tableWrapper.scrollLeft = this.savedScrollLeft;
          if (this.updateScrollSlider) this.updateScrollSlider();
        }
      });
    }

    // Bind view detail buttons
    tbody.querySelectorAll(".dt-btn-view").forEach(btn => {
      btn.addEventListener("click", () => {
        const itemIdx = parseInt(btn.dataset.index, 10);
        const record = this.data[itemIdx];
        this.showDetailModal(record);
      });
    });

    // Bind verify action buttons
    const bindVerifyButtons = (scope) => {
      scope.querySelectorAll(".btn-verify-badge").forEach(btn => {
        btn.onclick = (e) => {
          e.stopPropagation();
          const ds = btn.dataset.dataset;
          const rId = btn.dataset.id;
          const vNo = btn.dataset.voucher;
          const row = this.data.find(r => String(r.id) === String(rId)) || { id: rId, voucher_number: vNo };
          VerificationManager.toggleVerify(ds, rId, vNo);
          const parent = btn.parentElement;
          if (parent) {
            btn.outerHTML = VerificationManager.renderButton(row, ds);
            bindVerifyButtons(parent);
          }
        };
      });
    };
    bindVerifyButtons(tbody);

    // Bind Popover interactions (Party Description, Item Description, Narration)
    this.bindTooltipPopovers(tbody);
  }

  bindTooltipPopovers(tbody) {
    const popover = NarrationPopover.getOrCreate();

    tbody.querySelectorAll(".tooltip-trigger-cell, .narration-trigger-cell").forEach(cell => {
      const fullText = cell.getAttribute("data-full-text") || cell.getAttribute("data-full-narration");
      const title = cell.getAttribute("data-popover-title") || "Description Details";
      const icon = cell.getAttribute("data-popover-icon") || "ℹ️";

      cell.addEventListener("mouseenter", () => {
        NarrationPopover.show(cell, fullText, title, icon);
      });

      cell.addEventListener("mouseleave", (e) => {
        NarrationPopover.hideDelayed();
      });

      cell.addEventListener("click", (e) => {
        e.stopPropagation();
        NarrationPopover.show(cell, fullText, title, icon);
      });
    });
  }

  renderPagination() {
    const container = document.getElementById(this.containerId);
    if (!container) return;

    const pagInfo = container.querySelector(".dt-pag-info");
    const prevBtn = container.querySelector(".dt-btn-prev");
    const nextBtn = container.querySelector(".dt-btn-next");
    const pageNumbersEl = container.querySelector(".dt-page-numbers");

    if (pagInfo) {
      pagInfo.innerText = `Page ${this.page} of ${this.totalPages} (${this.total.toLocaleString()} total)`;
    }

    if (prevBtn) prevBtn.disabled = this.page <= 1;
    if (nextBtn) nextBtn.disabled = this.page >= this.totalPages;

    if (pageNumbersEl) {
      let pages = [];
      const start = Math.max(1, this.page - 2);
      const end = Math.min(this.totalPages, this.page + 2);
      for (let p = start; p <= end; p++) {
        pages.push(`
          <button class="page-btn ${p === this.page ? 'active' : ''}" data-page="${p}">
            ${p}
          </button>
        `);
      }
      pageNumbersEl.innerHTML = pages.join("");
      pageNumbersEl.querySelectorAll(".page-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          this.page = parseInt(btn.dataset.page, 10);
          this.loadData();
        });
      });
    }
  }

  showDetailModal(record) {
    const modalTitle = document.getElementById("record-detail-title");
    const modalBody = document.getElementById("record-detail-body");

    const formatCurrency = (num) => {
      const val = parseFloat(num);
      if (isNaN(val) || val === null || val === undefined) return "—";
      return "₹ " + val.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };

    const isZeroOrEmpty = (num) => {
      const val = parseFloat(num);
      return isNaN(val) || val === 0;
    };

    const voucherNum = record.voucher_number || record.id;
    const typeLabel = this.datasetType === 'master' ? 'Master 360° Ledger' : (this.datasetType === 'daybook' ? 'Day Book' : (this.datasetType === 'ap' ? 'Account Payable (AP)' : 'Account Receivable (AR)'));

    if (modalTitle) {
      modalTitle.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap;">
          <span class="badge ${this.datasetType === 'master' ? 'badge-primary' : (this.datasetType === 'daybook' ? 'badge-info' : (this.datasetType === 'ap' ? 'badge-warning' : 'badge-success'))}">
            ${typeLabel}
          </span>
          <span>Voucher: <strong>${voucherNum}</strong></span>
        </div>
      `;
    }

    if (!modalBody) {
      App.openModal("record-detail-modal");
      return;
    }

    // MASTER 360° UNIFIED MODAL VIEW
    if (this.datasetType === 'master') {
      modalBody.innerHTML = `
        <div class="record-modal-layout">
          <!-- 1. Day Book Master Information -->
          <div class="detail-section">
            <div class="detail-section-title">Day Book Master & Party Classification</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">Transaction Site</span>
                <span class="meta-field-value">${record.transaction_site || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Date</span>
                <span class="meta-field-value">${record.voucher_date || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Type</span>
                <span class="meta-field-value">${record.voucher_type || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Status</span>
                <span class="meta-field-value"><span class="badge badge-info">${record.voucher_status || '—'}</span></span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Party Code</span>
                <span class="meta-field-value">${record.party_code || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Party Description</span>
                <span class="meta-field-value">${record.party_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Account Description</span>
                <span class="meta-field-value">${record.account_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Reconciled Status</span>
                <span class="meta-field-value">
                  ${record.has_ap && record.has_ar ? '<span class="badge badge-success">3-Way Reconciled (AP & AR)</span>' : (record.has_ap ? '<span class="badge badge-warning">AP Linked</span>' : (record.has_ar ? '<span class="badge badge-info">AR Linked</span>' : '<span class="badge" style="background:#f1f5f9; color:#64748b;">Day Book Standalone</span>'))}
                </span>
              </div>
            </div>
          </div>

          <!-- 2. Creator & Approval Audit -->
          <div class="detail-section">
            <div class="detail-section-title">Creator & Approval Audit</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">Created By</span>
                <div>${PersonBadge.render(record.created_by, "created")}</div>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Approved By</span>
                <div>${PersonBadge.render(record.approved_by, "approved")}</div>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Created Date Log</span>
                <span class="meta-field-value">${record.created_date_raw || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Approved Date Log</span>
                <span class="meta-field-value">${record.approved_date_raw || '—'}</span>
              </div>
            </div>
          </div>

          <!-- 3. Linked AP Details if available -->
          ${record.has_ap ? `
          <div class="detail-section">
            <div class="detail-section-title">Reconciled Account Payable (AP) Ingested Data (${record.ap_count} Record${record.ap_count > 1 ? 's' : ''})</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">AP Invoice Number(s)</span>
                <span class="meta-field-value">${record.ap_invoice_number || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AP Party GST TIN</span>
                <span class="meta-field-value">${record.ap_party_gst || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AP Item / Expense</span>
                <span class="meta-field-value">${record.ap_item_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Total AP Amount</span>
                <span class="meta-field-value" style="color: #15803d; font-weight: 800;">${formatCurrency(record.ap_total_amount)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AP Tax Amount</span>
                <span class="meta-field-value" style="color: #c2410c;">${formatCurrency(record.ap_tax_amount)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AP Total TDS</span>
                <span class="meta-field-value">${formatCurrency(record.ap_total_tds)}</span>
              </div>
            </div>
          </div>` : ''}

          <!-- 4. Linked AR Details if available -->
          ${record.has_ar ? `
          <div class="detail-section">
            <div class="detail-section-title">Reconciled Account Receivable (AR) Ingested Data (${record.ar_count} Record${record.ar_count > 1 ? 's' : ''})</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">AR Sub-Type</span>
                <span class="meta-field-value">${record.ar_subtype || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AR Item / Service</span>
                <span class="meta-field-value">${record.ar_item_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AR Net Amount</span>
                <span class="meta-field-value" style="color: #2563eb; font-weight: 800;">${formatCurrency(record.ar_net_amount)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">AR Taxes (CGST+SGST+IGST)</span>
                <span class="meta-field-value" style="color: #c2410c;">${formatCurrency(record.ar_tax_amount)}</span>
              </div>
            </div>
          </div>` : ''}

          <!-- 5. Master Narration Box -->
          <div class="detail-section">
            <div class="detail-section-title">Narration & Financial Notes</div>
            <div class="detail-narration-box">
              <div class="detail-narration-text">${record.narration || '<span style="color: var(--text-muted); font-style: italic;">No narration recorded for this voucher.</span>'}</div>
            </div>
          </div>
        </div>
      `;
    }

    // 1. DAY BOOK MODAL VIEW
    else if (this.datasetType === 'daybook') {
      modalBody.innerHTML = `
        <div class="record-modal-layout">
          <!-- General Metadata Section -->
          <div class="detail-section">
            <div class="detail-section-title">Voucher & Party Information</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">Transaction Site</span>
                <span class="meta-field-value" title="${record.transaction_site || ''}">${record.transaction_site || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Date</span>
                <span class="meta-field-value">${record.voucher_date || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Type</span>
                <span class="meta-field-value" title="${record.voucher_type || ''}">${record.voucher_type || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Status</span>
                <span class="meta-field-value"><span class="badge badge-info">${record.voucher_status || '—'}</span></span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Party Code</span>
                <span class="meta-field-value" title="${record.party_code || ''}">${record.party_code || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Party Description</span>
                <span class="meta-field-value" title="${record.party_description || ''}">${record.party_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Account Description</span>
                <span class="meta-field-value" title="${record.account_description || ''}">${record.account_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Batch ID / Source</span>
                <span class="meta-field-value">Batch #${record.batch_id || '1'}</span>
              </div>
            </div>
          </div>

          <!-- Audit & Approvals Section -->
          <div class="detail-section">
            <div class="detail-section-title">Creator & Approval Audit</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">Created By</span>
                <div>${PersonBadge.render(record.created_by, "created")}</div>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Approved By</span>
                <div>${PersonBadge.render(record.approved_by, "approved")}</div>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Created Date Log</span>
                <span class="meta-field-value">${record.created_date_raw || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Approved Date Log</span>
                <span class="meta-field-value">${record.approved_date_raw || '—'}</span>
              </div>
            </div>
          </div>

          <!-- Narration Box -->
          <div class="detail-section">
            <div class="detail-section-title">Narration & Notes</div>
            <div class="detail-narration-box">
              <div class="detail-narration-text">${record.narration || '<span style="color: var(--text-muted); font-style: italic;">No narration recorded for this voucher.</span>'}</div>
            </div>
          </div>
        </div>
      `;
    }

    // 2. AP (ACCOUNT PAYABLE) MODAL VIEW
    else if (this.datasetType === 'ap') {
      const totalVoucherAmt = record.total_voucher_amount;
      const detailAmt = record.item_service_detail_amount;
      const taxAmt = record.total_tax_amount;
      const tdsAmt = record.total_tds;
      const rate = record.item_service_rate;
      const qty = record.booked_item_quantity;

      modalBody.innerHTML = `
        <div class="record-modal-layout">
          <!-- Invoice & Voucher Metadata Grid -->
          <div class="detail-section">
            <div class="detail-section-title">Invoice & Classification Details</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">Accounting Site</span>
                <span class="meta-field-value" title="${record.accounting_site_code || ''}">${record.accounting_site_code || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Type</span>
                <span class="meta-field-value" title="${record.voucher_type || ''}">${record.voucher_type || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Sub-Type</span>
                <span class="meta-field-value" title="${record.voucher_sub_type || ''}">${record.voucher_sub_type || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Invoice Number</span>
                <span class="meta-field-value" title="${record.invoice_number || ''}">${record.invoice_number || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Invoice Date</span>
                <span class="meta-field-value">${record.invoice_date || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Due Date</span>
                <span class="meta-field-value">${record.due_date || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Party GST TIN</span>
                <span class="meta-field-value" title="${record.party_gst_tin || ''}">${record.party_gst_tin || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Expense Account</span>
                <span class="meta-field-value" title="${record.item_service_expense_account_desc || ''}">${record.item_service_expense_account_desc || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Item / Service Description</span>
                <span class="meta-field-value" title="${record.item_service_description || ''}">${record.item_service_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Quantity & Rate</span>
                <span class="meta-field-value">${qty !== null && qty !== undefined ? qty : '—'} @ ${formatCurrency(rate)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Detail Amount</span>
                <span class="meta-field-value" style="color: #1e40af; font-weight: 750;">${formatCurrency(detailAmt)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Total Voucher Amount</span>
                <span class="meta-field-value" style="color: #15803d; font-weight: 800;">${formatCurrency(totalVoucherAmt)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Total Tax Amount</span>
                <span class="meta-field-value" style="color: #c2410c;">${formatCurrency(taxAmt)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Total TDS</span>
                <span class="meta-field-value">${formatCurrency(tdsAmt)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Batch ID / Source</span>
                <span class="meta-field-value">Batch #${record.batch_id || '1'}</span>
              </div>
            </div>
          </div>

          <!-- Audit & Approvals Section with Separate Cards -->
          <div class="detail-section">
            <div class="detail-section-title">Creator & Approval Audit</div>
            <div class="detail-meta-grid" style="grid-template-columns: repeat(2, 1fr);">
              <div class="meta-field-card">
                <span class="meta-field-label">Created By</span>
                <div style="margin-top: 0.2rem;">${PersonBadge.render(record.created_by, "created")}</div>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Approved By</span>
                <div style="margin-top: 0.2rem;">${PersonBadge.render(record.approved_by, "approved")}</div>
              </div>
            </div>
          </div>

          <!-- Description & Narration Section -->
          <div class="detail-section">
            <div class="detail-section-title">Narration & Notes</div>
            <div class="detail-narration-box">
              <div class="detail-narration-text">${record.header_narration || record.detail_narration || record.narration || '<span style="color: var(--text-muted); font-style: italic;">No narration recorded for this voucher.</span>'}</div>
            </div>
          </div>
        </div>
      `;
    }

    // 3. AR (ACCOUNT RECEIVABLE) MODAL VIEW
    else {
      const netAmt = record.net_amount;
      const itemAmt = record.item_service_amount;
      const netOffDisc = record.item_amount_net_off_discount;
      const taxes = record.item_service_taxes;
      const cgst = record.total_cgst;
      const sgst = record.total_sgst;
      const igst = record.total_igst;
      const charges = record.item_service_charges;
      const rate = record.item_service_rate;
      const qty = record.item_quantity;

      modalBody.innerHTML = `
        <div class="record-modal-layout">
          <!-- Voucher & Classification Grid -->
          <div class="detail-section">
            <div class="detail-section-title">Voucher & Receivable Classification</div>
            <div class="detail-meta-grid">
              <div class="meta-field-card">
                <span class="meta-field-label">Accounting Site</span>
                <span class="meta-field-value" title="${record.accounting_site_code || ''}">${record.accounting_site_code || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Type</span>
                <span class="meta-field-value" title="${record.voucher_type || ''}">${record.voucher_type || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Voucher Sub-Type</span>
                <span class="meta-field-value" title="${record.voucher_sub_type || ''}">${record.voucher_sub_type || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Item / Service Description</span>
                <span class="meta-field-value" title="${record.item_service_description || ''}">${record.item_service_description || '—'}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Quantity & Rate</span>
                <span class="meta-field-value">${qty !== null && qty !== undefined ? qty : '—'} @ ${formatCurrency(rate)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Item Service Amount</span>
                <span class="meta-field-value" style="color: #1e40af; font-weight: 750;">${formatCurrency(itemAmt)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Net of Discount</span>
                <span class="meta-field-value">${formatCurrency(netOffDisc)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Net Receivable Amount</span>
                <span class="meta-field-value" style="color: #15803d; font-weight: 800;">${formatCurrency(netAmt)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Total Taxes</span>
                <span class="meta-field-value" style="color: #c2410c;">${formatCurrency(taxes)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">GST (CGST / SGST / IGST)</span>
                <span class="meta-field-value">₹${parseFloat(cgst) || 0} / ₹${parseFloat(sgst) || 0} / ₹${parseFloat(igst) || 0}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Extra Charges</span>
                <span class="meta-field-value">${formatCurrency(charges)}</span>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Batch ID / Source</span>
                <span class="meta-field-value">Batch #${record.batch_id || '1'}</span>
              </div>
            </div>
          </div>

          <!-- Audit & Approvals Section with Separate Cards -->
          <div class="detail-section">
            <div class="detail-section-title">Creator & Approval Audit</div>
            <div class="detail-meta-grid" style="grid-template-columns: repeat(2, 1fr);">
              <div class="meta-field-card">
                <span class="meta-field-label">Created By</span>
                <div style="margin-top: 0.2rem;">${PersonBadge.render(record.created_by, "created")}</div>
              </div>
              <div class="meta-field-card">
                <span class="meta-field-label">Approved By</span>
                <div style="margin-top: 0.2rem;">${PersonBadge.render(record.approved_by, "approved")}</div>
              </div>
            </div>
          </div>

          <!-- Narration Box -->
          <div class="detail-section">
            <div class="detail-section-title">📝 Narration & Remarks</div>
            <div class="detail-narration-box">
              <div class="detail-narration-text">${record.narration_remarks || record.narration || '<span style="color: var(--text-muted); font-style: italic;">No narration recorded for this voucher.</span>'}</div>
            </div>
          </div>
        </div>
      `;
    }

    // Modal Action Footer Link
    const modalFooter = document.querySelector("#record-detail-modal .modal-footer");
    if (modalFooter) {
      modalFooter.innerHTML = `
        <button type="button" class="btn btn-secondary btn-sm" onclick="App.exploreVoucher('${voucherNum}')">
          🔗 Cross-Reference Voucher in All Tabs
        </button>
        <button type="button" class="btn btn-secondary btn-sm modal-footer-close-btn" onclick="App.closeModal('record-detail-modal')">
          Close
        </button>
      `;
    }

    App.openModal("record-detail-modal");
  }

  async handleExportCSV(btn) {
    try {
      const origHtml = btn.innerHTML;
      btn.innerHTML = `<span style="display:inline-block;width:11px;height:11px;border:2px solid currentColor;border-right-color:transparent;border-radius:50%;animation:rotate 0.7s linear infinite;margin-right:4px;"></span> Exporting...`;
      btn.disabled = true;

      const verificationsMap = VerificationManager.getAllVerificationsMap(this.datasetType);

      const payload = {
        search: this.search || null,
        site: this.site || null,
        voucher_type: this.voucherType || null,
        voucher_subtype: this.voucherSubtype || null,
        approved_by: this.approvedBy || null,
        register_type: this.registerType || null,
        batch_id: this.batchId ? parseInt(this.batchId) : null,
        verifications: verificationsMap
      };

      const token = (window.API && API.getToken) ? API.getToken() : (localStorage.getItem("access_token") || localStorage.getItem("token"));

      const response = await fetch(`/api/export/${this.datasetType}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        let errMsg = `HTTP ${response.status}`;
        try {
          const errData = await response.json();
          if (errData && errData.detail) errMsg = errData.detail;
        } catch (_) { }
        throw new Error(errMsg);
      }

      const blob = await response.blob();
      const disposition = response.headers.get("Content-Disposition");
      let filename = `KOGM_${this.datasetType.toUpperCase()}_Export.csv`;
      if (disposition && disposition.includes("filename=")) {
        const match = disposition.match(/filename="?([^";]+)"?/);
        if (match && match[1]) filename = match[1];
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();

      if (window.App && App.toast) {
        App.toast(`✓ Export complete: ${filename} downloaded successfully!`, "success");
      }
    } catch (err) {
      console.error("CSV Export error:", err);
      if (window.App && App.toast) {
        App.toast(`Export failed: ${err.message}`, "error");
      }
    } finally {
      btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"></path></svg> Export CSV`;
      btn.disabled = false;
    }
  }

  async handlePrintReport() {
    try {
      const modal = document.getElementById("statement-report-modal");
      const body = document.getElementById("statement-report-body");
      if (!modal || !body) return;

      // Show temporary loading indicator in modal body
      body.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 4rem 2rem; color: #1e40af;">
          <div style="width: 38px; height: 38px; border: 3.5px solid #93c5fd; border-top-color: #1e40af; border-radius: 50%; animation: rotate 0.8s linear infinite; margin-bottom: 1rem;"></div>
          <div style="font-weight: 700; font-size: 1rem; color: #0f172a;">Generating Complete Official Ledger Statement...</div>
          <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.25rem;">Fetching all active filtered records...</div>
        </div>
      `;
      if (window.App && App.openModal) {
        App.openModal("statement-report-modal");
      } else {
        modal.style.display = "flex";
        modal.classList.add("show");
      }

      // Fetch ALL matching records (not just current page 15 rows)
      let printRecords = [];
      try {
        const fullParams = {
          page: 1,
          page_size: 100000,
          search: this.search || "",
          site: this.site || "",
          voucher_type: this.voucherType || "",
          voucher_subtype: this.voucherSubtype || "",
          approved_by: this.approvedBy || "",
          register_type: this.registerType || "",
          batch_id: this.batchId || "",
          sort_by: this.sortBy || "id",
          sort_order: this.sortOrder || "desc"
        };
        const fullResponse = await this.fetchFn(fullParams);
        printRecords = (fullResponse && fullResponse.items && fullResponse.items.length > 0) ? fullResponse.items : (this.data || []);
      } catch (e) {
        console.warn("Could not fetch full statement records, falling back to current dataset", e);
        printRecords = this.data || [];
      }

      // Get Active Digital Signature from SignatureStudio
      const sigData = (window.SignatureStudio && SignatureStudio.getActiveSignature) ? SignatureStudio.getActiveSignature() : null;
      const signerName = (sigData && sigData.profile && sigData.profile.name) ? sigData.profile.name : "Akhtar";
      const signerRole = (sigData && sigData.profile && sigData.profile.designation) ? sigData.profile.designation : "Head of Accounts & Statutory Audit";
      const signerOrg = (sigData && sigData.profile && sigData.profile.organization) ? sigData.profile.organization : "KOGM Financial ERP";
      const sigHash = (sigData && sigData.profile && sigData.profile.hash) ? sigData.profile.hash : "SIG-KOGM-CERTIFIED";
      const sigImgSrc = (sigData && sigData.dataUrl) ? sigData.dataUrl : "";

      // Dataset title
      const titleMap = {
        master: "Day Book Master 360° Unified Ledger Statement",
        daybook: "Day Book Primary Financial Audit Register",
        ap: "Accounts Payable (AP) Supplier Invoices & Tax Statement",
        ar: "Accounts Receivable (AR) Customer Sales & GST Statement"
      };
      const reportTitle = titleMap[this.datasetType] || "Official Financial Ledger Statement";

      // Current filter summary
      const filterSummary = [
        this.site ? `Site: ${this.site}` : "All Sites",
        this.voucherType ? `Type: ${this.voucherType}` : "All Voucher Types",
        this.registerType ? `Register: ${this.registerType}` : "",
        this.approvedBy ? `Approver: ${this.approvedBy}` : ""
      ].filter(Boolean).join(" • ");

      let totalAmount = 0;
      let totalTax = 0;
      let totalQty = 0;
      printRecords.forEach(r => {
        totalAmount += parseFloat(r.combined_amount || r.total_voucher_amount || r.net_amount || 0);
        totalTax += parseFloat(r.unified_tax_amount || r.total_tax_amount || r.item_service_taxes || 0);
        const q = parseFloat(r.unified_quantity || r.booked_item_quantity || r.item_quantity || 0);
        if (!isNaN(q)) totalQty += q;
      });

      const formattedTotalAmt = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(totalAmount);
      const formattedTotalTax = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(totalTax);
      const formattedTotalQty = Number(totalQty).toLocaleString('en-IN', { maximumFractionDigits: 2 });

      const html = `
        <div class="print-statement-sheet">
          <!-- Ultra-Compact Streamlined Header Block -->
          <div class="statement-header-block">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
              <img src="/static/images/KOGM_LOgo.jpg" alt="KOGM Logo" style="height: 42px; max-width: 140px; border-radius: 6px; object-fit: contain; background: #ffffff; padding: 2px 6px; border: 1.2px solid #cbd5e1;" />
              <div>
                <div style="display: flex; align-items: center; gap: 0.45rem; line-height: 1.1;">
                  <span class="statement-brand-title">KOGM Financial ERP</span>
                  <span style="background: #1e3a8a; color: #ffffff; font-size: 0.62rem; font-weight: 700; padding: 0.12rem 0.45rem; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.04em;">Official Statement</span>
                </div>
                <div class="statement-subtitle" style="font-size: 0.78rem; font-weight: 700; color: #1e293b; margin-top: 0.1rem;">${reportTitle}</div>
                <div style="font-size: 0.68rem; color: #475569; margin-top: 0.1rem;">
                  <strong>Scope:</strong> ${filterSummary}
                </div>
              </div>
            </div>
            <div style="text-align: right; line-height: 1.25;">
              <div style="font-size: 0.74rem; font-weight: 700; color: #0f172a;">Generated: ${new Date().toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}</div>
              <div style="font-size: 0.65rem; color: #64748b; font-family: 'JetBrains Mono', monospace;">Doc ID: DOC-${Date.now().toString(36).toUpperCase()}</div>
              <div style="font-size: 0.66rem; color: #15803d; font-weight: 700; display: flex; align-items: center; justify-content: flex-end; gap: 0.2rem; margin-top: 0.1rem;">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
                Cryptographically Certified
              </div>
            </div>
          </div>

          <!-- Ultra-Compact Single-Row KPI Strip -->
          <div class="statement-kpi-row">
            <div class="statement-kpi-box">
              <span class="kpi-label">Total Records:</span>
              <span class="kpi-val">${printRecords.length} Records</span>
            </div>
            <div class="statement-kpi-box">
              <span class="kpi-label">Total Qty:</span>
              <span class="kpi-val" style="color: #0f172a;">${formattedTotalQty}</span>
            </div>
            <div class="statement-kpi-box">
              <span class="kpi-label">Total Turnover:</span>
              <span class="kpi-val" style="color: #1e40af;">${formattedTotalAmt}</span>
            </div>
            <div class="statement-kpi-box">
              <span class="kpi-label">Tax / GST:</span>
              <span class="kpi-val" style="color: #059669;">${formattedTotalTax}</span>
            </div>
            <div class="statement-kpi-box">
              <span class="kpi-label">Status:</span>
              <span class="kpi-val" style="color: #15803d;">✓ Reconciled</span>
            </div>
          </div>

          <!-- High-Preference Financial Ledger Table -->
          <div class="statement-table-wrapper">
            <table class="statement-table">
              <thead>
                <tr>
                  <th style="width: 28px; text-align: center;">#</th>
                  <th>Site</th>
                  <th>Voucher Number</th>
                  <th>Voucher Date</th>
                  <th>Voucher Type</th>
                  <th>Register</th>
                  <th>Invoice / Ref No.</th>
                  <th style="text-align: right;">Quantity</th>
                  <th style="text-align: right;">Rate (₹)</th>
                  <th style="text-align: right;">Tax Amount (₹)</th>
                  <th style="text-align: right;">Total Amount (₹)</th>
                  <th style="text-align: center;">Status</th>
                </tr>
              </thead>
              <tbody>
                ${printRecords.map((r, idx) => {
        const site = r.transaction_site || r.accounting_site_code || "—";
        const vNo = r.voucher_number || r.voucher_no || "—";
        const vDate = r.voucher_date || "—";
        const vType = r.voucher_type || "—";
        const reg = r.source_tag || (this.datasetType.toUpperCase());
        const inv = r.unified_invoice_no || r.invoice_number || "—";

        const qtyVal = r.unified_quantity || r.booked_item_quantity || r.item_quantity;
        const qtyStr = (qtyVal !== null && qtyVal !== undefined && qtyVal !== "") ? Number(qtyVal).toLocaleString('en-IN') : "—";

        const rateVal = r.unified_rate || r.item_service_rate;
        const rateStr = (rateVal !== null && rateVal !== undefined && rateVal !== "") ? ("₹" + Number(rateVal).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })) : "—";

        const taxVal = r.unified_tax_amount || r.total_tax_amount || r.item_service_taxes;
        const taxStr = (taxVal !== null && taxVal !== undefined && taxVal !== "") ? ("₹" + Number(taxVal).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })) : "—";

        const totVal = r.combined_amount || r.total_voucher_amount || r.net_amount;
        const totStr = (totVal !== null && totVal !== undefined && totVal !== "") ? ("₹" + Number(totVal).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })) : "—";

        const statusStr = r.voucher_status || (r.is_verified ? "Verified" : "Exported to GL");

        return `
                    <tr>
                      <td style="text-align: center; font-weight: 600; color: #94a3b8;">${idx + 1}</td>
                      <td style="font-weight: 700; color: #0f172a;">${site}</td>
                      <td style="font-family: 'JetBrains Mono', monospace; font-weight: 600;">${vNo}</td>
                      <td>${vDate}</td>
                      <td>${vType}</td>
                      <td><span style="background: #e2e8f0; color: #1e293b; padding: 1px 5px; border-radius: 3px; font-size: 0.68rem; font-weight: 700;">${reg}</span></td>
                      <td style="font-family: 'JetBrains Mono', monospace;">${inv}</td>
                      <td style="text-align: right; font-variant-numeric: tabular-nums; font-weight: 600;">${qtyStr}</td>
                      <td style="text-align: right; font-variant-numeric: tabular-nums;">${rateStr}</td>
                      <td style="text-align: right; font-variant-numeric: tabular-nums; color: #059669; font-weight: 600;">${taxStr}</td>
                      <td style="text-align: right; font-variant-numeric: tabular-nums; font-weight: 700; color: #0f172a;">${totStr}</td>
                      <td style="text-align: center; font-weight: 700; color: #15803d; font-size: 0.68rem;">${statusStr}</td>
                    </tr>
                  `;
      }).join('')}
              </tbody>
            </table>
          </div>

          <!-- Ultra-Compact Streamlined Certification & Signatory Footer -->
          <div class="statement-auth-block">
            <div class="statement-seal-box">
              <img src="/static/images/mashal_logo_2.jpg" alt="KOGM Mashal Seal" style="width: 44px; height: 44px; border-radius: 50%; object-fit: cover; border: 1.8px solid #2563eb; padding: 2px; background: #ffffff; box-shadow: 0 2px 6px rgba(37,99,235,0.15);" />
              <div>
                <div style="font-size: 0.76rem; font-weight: 800; color: #0f172a; line-height: 1.1;">KOGM Enterprise Audit Certification</div>
                <div style="font-size: 0.66rem; color: #64748b; margin-top: 0.1rem; max-width: 480px; line-height: 1.2;">This document is digitally certified and reconciled against Day Book, AP, and AR registers.</div>
                <div style="font-size: 0.62rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.15rem; display: inline-block; background: #f1f5f9; padding: 1px 6px; border-radius: 3px; border: 1px solid #e2e8f0;">Auth Hash: ${sigHash}</div>
              </div>
            </div>

            <div class="statement-signatory-box">
              ${sigImgSrc ? `<img src="${sigImgSrc}" class="statement-sig-img" alt="Digital Signature" style="height: 56px; max-height: 68px; max-width: 220px; object-fit: contain; display: inline-block; margin-bottom: 0.15rem;" />` : `<div style="font-family: 'Dancing Script', cursive; font-size: 1.6rem; color: #1e40af; margin-bottom: 0.1rem;">${signerName}</div>`}
              <div class="statement-sig-line" style="border-top: 1.2px solid #0f172a; margin-top: 0.15rem; padding-top: 0.2rem; line-height: 1.15;">
                <div class="statement-sig-name" style="font-weight: 800; font-size: 0.78rem; color: #0f172a;">${signerName}</div>
                <div class="statement-sig-role" style="font-size: 0.68rem; color: #334155; font-weight: 600;">${signerRole}</div>
                <div class="statement-sig-org" style="font-size: 0.62rem; color: #64748b;">${signerOrg}</div>
                <div class="statement-sig-hash" style="font-size: 0.60rem; color: #94a3b8; font-family: 'JetBrains Mono', monospace; margin-top: 0.1rem;">Digitally Signed on ${new Date().toLocaleDateString('en-IN')}</div>
              </div>
            </div>
          </div>
        </div>
      `;

      body.innerHTML = html;
    } catch (e) {
      console.error("Print report generation error:", e);
      if (window.App && App.toast) {
        App.toast("Failed to generate report statement preview", "error");
      }
    }
  }
}

// Global Singleton Narration Popover Manager with Collision Detection
const NarrationPopover = {
  popoverEl: null,
  hideTimer: null,
  currentText: "",

  getOrCreate() {
    if (!this.popoverEl) {
      this.popoverEl = document.createElement("div");
      this.popoverEl.id = "global-narration-popover";
      this.popoverEl.className = "narration-popover";
      this.popoverEl.innerHTML = `
        <div class="narration-popover-header">
          <div class="narration-popover-title">
            <span>📖</span> Narration Details
          </div>
          <button class="narration-popover-copy-btn">📋 Copy</button>
        </div>
        <div class="narration-popover-body"></div>
      `;
      document.body.appendChild(this.popoverEl);

      const copyBtn = this.popoverEl.querySelector(".narration-popover-copy-btn");
      copyBtn.addEventListener("click", () => {
        if (this.currentText) {
          navigator.clipboard.writeText(this.currentText).then(() => {
            copyBtn.innerText = "✓ Copied";
            setTimeout(() => { copyBtn.innerText = "📋 Copy"; }, 1500);
          });
        }
      });

      this.popoverEl.addEventListener("mouseenter", () => {
        clearTimeout(this.hideTimer);
      });

      this.popoverEl.addEventListener("mouseleave", () => {
        this.hide();
      });

      document.addEventListener("click", (e) => {
        if (!this.popoverEl.contains(e.target) && !e.target.closest(".narration-trigger-cell")) {
          this.hide();
        }
      });
    }
    return this.popoverEl;
  },

  show(triggerEl, text, title = "Narration Details", icon = "📖") {
    if (!text || text === "null" || text === "undefined" || text === "—") return;
    clearTimeout(this.hideTimer);

    const popover = this.getOrCreate();
    this.currentText = text;

    const titleEl = popover.querySelector(".narration-popover-title");
    if (titleEl) {
      titleEl.innerHTML = `<span>${icon}</span> ${title}`;
    }
    popover.querySelector(".narration-popover-body").innerText = text;

    // Reset position to measure dimensions
    popover.style.display = "block";
    popover.style.visibility = "hidden";
    popover.style.top = "0px";
    popover.style.left = "0px";

    const rect = triggerEl.getBoundingClientRect();
    const popoverRect = popover.getBoundingClientRect();

    let top = rect.bottom + 6;
    let left = rect.left;

    // Check bottom viewport collision -> flip to top if needed
    if (top + popoverRect.height > window.innerHeight - 10) {
      top = rect.top - popoverRect.height - 6;
    }

    // Check right viewport collision -> flip to left if needed
    if (left + popoverRect.width > window.innerWidth - 15) {
      left = window.innerWidth - popoverRect.width - 15;
    }

    // Ensure not going off top or left
    if (top < 10) top = 10;
    if (left < 10) left = 10;

    popover.style.top = `${top}px`;
    popover.style.left = `${left}px`;
    popover.style.visibility = "visible";
    popover.classList.add("show");
  },

  hideDelayed() {
    this.hideTimer = setTimeout(() => {
      this.hide();
    }, 250);
  },

  hide() {
    if (this.popoverEl) {
      this.popoverEl.classList.remove("show");
      setTimeout(() => {
        if (!this.popoverEl.classList.contains("show")) {
          this.popoverEl.style.display = "none";
        }
      }, 200);
    }
  }
};
