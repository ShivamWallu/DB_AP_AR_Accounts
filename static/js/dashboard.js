const Dashboard = {
  async load() {
    // 1. Instant Cache Render (0ms initial paint)
    try {
      const cached = sessionStorage.getItem("cached_dashboard_stats");
      if (cached) {
        const stats = JSON.parse(cached);
        this.renderAll(stats);
      }
    } catch (_) {}

    // 2. Fetch fresh live statistics
    try {
      const stats = await API.getDashboardStats();
      sessionStorage.setItem("cached_dashboard_stats", JSON.stringify(stats));
      this.renderAll(stats);
    } catch (err) {
      console.error("Failed to load dashboard:", err);
      // Only show error if no cached data was rendered
      if (!sessionStorage.getItem("cached_dashboard_stats")) {
        App.toast("Failed to load dashboard statistics", "error");
      }
    }
  },

  renderAll(stats) {
    if (!stats) return;
    this.renderOverviewCards(stats);
    this.renderFinancialMetrics(stats);
    this.renderDistributions(stats);
  },

  renderOverviewCards(stats) {
    document.getElementById("stat-total-daybook").innerText = stats.total_daybook_records.toLocaleString();
    document.getElementById("stat-total-ap").innerText = stats.total_ap_records.toLocaleString();
    document.getElementById("stat-total-ar").innerText = stats.total_ar_records.toLocaleString();
    document.getElementById("stat-total-historical").innerText = stats.total_historical_records.toLocaleString();
    document.getElementById("stat-today-imported").innerText = stats.today_imported_records.toLocaleString();
    document.getElementById("stat-last-upload").innerText = stats.last_upload_date ? `${stats.last_upload_date} ${stats.last_upload_time}` : "No uploads yet";
  },

  renderFinancialMetrics(stats) {
    const apAmtEl = document.getElementById("stat-ap-amount");
    const arAmtEl = document.getElementById("stat-ar-amount");
    const taxAmtEl = document.getElementById("stat-total-taxes");

    const formatCurrency = (num) => "₹ " + Number(num || 0).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

    if (apAmtEl) apAmtEl.innerText = formatCurrency(stats.ap_total_amount);
    if (arAmtEl) arAmtEl.innerText = formatCurrency(stats.ar_total_amount);
    if (taxAmtEl) taxAmtEl.innerText = formatCurrency(stats.total_tax_collected_or_paid);
  },

  renderDistributions(stats) {
    // Render Top Sites
    const siteListEl = document.getElementById("dashboard-site-list");
    if (siteListEl) {
      if (!stats.site_distribution || stats.site_distribution.length === 0) {
        siteListEl.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">No site data available yet.</div>`;
      } else {
        const maxCount = Math.max(...stats.site_distribution.map(s => s.count), 1);
        siteListEl.innerHTML = stats.site_distribution.map(s => {
          const pct = Math.round((s.count / maxCount) * 100);
          return `
            <div style="margin-bottom: 0.85rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: var(--text-primary);">${s.site}</span>
                <span style="color: var(--text-secondary);">${s.count.toLocaleString()} records</span>
              </div>
              <div style="height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden;">
                <div style="width: ${pct}%; height: 100%; background: #3b82f6; border-radius: 3px;"></div>
              </div>
            </div>
          `;
        }).join("");
      }
    }

    // Render Voucher Types
    const vtypeListEl = document.getElementById("dashboard-vtype-list");
    if (vtypeListEl) {
      if (!stats.voucher_type_distribution || stats.voucher_type_distribution.length === 0) {
        vtypeListEl.innerHTML = `<div style="color: var(--text-muted); font-size: 0.85rem; padding: 1rem 0;">No voucher type data available yet.</div>`;
      } else {
        const maxCount = Math.max(...stats.voucher_type_distribution.map(v => v.count), 1);
        vtypeListEl.innerHTML = stats.voucher_type_distribution.map(v => {
          const pct = Math.round((v.count / maxCount) * 100);
          return `
            <div style="margin-bottom: 0.85rem;">
              <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: var(--text-primary);">${v.voucher_type}</span>
                <span style="color: var(--text-secondary);">${v.count.toLocaleString()} records</span>
              </div>
              <div style="height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden;">
                <div style="width: ${pct}%; height: 100%; background: #10b981; border-radius: 3px;"></div>
              </div>
            </div>
          `;
        }).join("");
      }
    }
  }
};
