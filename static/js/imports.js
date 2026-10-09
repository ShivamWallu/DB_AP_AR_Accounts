const Imports = {
  batches: [],

  async load() {
    try {
      this.batches = await API.getBatches();
      this.renderBatchesList();
    } catch (err) {
      console.error("Failed to load batches:", err);
      App.toast("Failed to load import history", "error");
    }
  },

  renderBatchesList() {
    const listEl = document.getElementById("imports-history-list");
    if (!listEl) return;

    if (this.batches.length === 0) {
      listEl.innerHTML = `
        <div style="text-align: center; padding: 2.5rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--border-radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 0.35rem; color: var(--text-primary);">No Import Batches Yet</div>
          <p style="font-size: 0.82rem;">Upload the mandatory 3 daily Excel files (Day Book, AP, AR) to record your first batch.</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = `
      <div class="batch-compact-list">
        ${this.batches.map(b => {
          let statusBadgeClass = "badge-success";
          let statusText = b.status || "Completed";
          if (b.status === "Pending" || b.status === "Incomplete") {
            statusBadgeClass = "badge-warning";
            statusText = "Pending";
          } else if (b.status === "Failed") {
            statusBadgeClass = "badge-danger";
            statusText = "Failed";
          } else if (b.status === "Completed") {
            statusBadgeClass = "badge-success";
            statusText = "Completed";
          }

          const voucherDateDisplay = b.voucher_date_range || b.upload_date_str || "—";

          return `
            <div class="batch-compact-card">
              <!-- Top Row: Batch Code, Status, Voucher Date, Upload Metadata, Audit Action -->
              <div class="batch-compact-header">
                <div class="batch-compact-left">
                  <span class="batch-compact-code">${b.batch_code}</span>
                  <span class="badge ${statusBadgeClass} batch-compact-status">${statusText}</span>
                  <span class="batch-vdate-chip" title="Voucher Date extracted from dataset">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                    <span>Voucher Date: <strong>${voucherDateDisplay}</strong></span>
                  </span>
                  <span class="batch-meta-info">
                    Uploaded <strong>${b.upload_date_str}</strong> (${b.upload_time_str}) by <strong>${b.created_by_user || 'admin'}</strong>
                  </span>
                </div>
                <div class="batch-compact-right">
                  <button class="btn btn-secondary btn-xs dt-batch-audit-btn" onclick="Imports.showBatchDetails(${b.id})">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:-2px; margin-right:3px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    View Audit
                  </button>
                </div>
              </div>

              <!-- Bottom Row: Inline Metrics & Ingested File Badges -->
              <div class="batch-compact-footer">
                <div class="batch-compact-stats">
                  <span class="batch-stat-item">Total Rows: <strong>${b.total_rows.toLocaleString()}</strong></span>
                  <span class="batch-stat-item stat-new">New Records: <strong>+${b.new_records.toLocaleString()}</strong></span>
                  <span class="batch-stat-item stat-dup">Duplicates: <strong>${b.duplicate_records.toLocaleString()}</strong></span>
                  <span class="batch-stat-item stat-rej">Rejected: <strong>${b.rejected_records.toLocaleString()}</strong></span>
                </div>
                <div class="batch-compact-files">
                  <span class="batch-file-chip ${b.daybook_filename ? 'chip-ok' : 'chip-err'}" title="${b.daybook_filename || 'DayBook'}">
                    Day Book: <strong>${b.daybook_rows.toLocaleString()}</strong>
                  </span>
                  <span class="batch-file-chip ${b.ap_filename ? 'chip-ok' : 'chip-err'}" title="${b.ap_filename || 'AP'}">
                    AP: <strong>${b.ap_rows.toLocaleString()}</strong>
                  </span>
                  <span class="batch-file-chip ${b.ar_filename ? 'chip-ok' : 'chip-err'}" title="${b.ar_filename || 'AR'}">
                    AR: <strong>${b.ar_rows.toLocaleString()}</strong>
                  </span>
                </div>
              </div>
            </div>
          `;
        }).join("")}
      </div>
    `;
  },

  async showBatchDetails(batchId) {
    try {
      const batch = await API.getBatch(batchId);
      const modalTitle = document.getElementById("record-detail-title");
      const modalBody = document.getElementById("record-detail-body");
      const modalFooter = document.querySelector("#record-detail-modal .modal-footer");

      if (modalTitle) modalTitle.innerText = `Batch Audit: ${batch.batch_code}`;

      let formattedTimestamp = batch.upload_timestamp;
      if (batch.upload_date_str && batch.upload_time_str) {
        formattedTimestamp = `${batch.upload_date_str} at ${batch.upload_time_str}`;
      } else if (batch.upload_timestamp) {
        try {
          const d = new Date(batch.upload_timestamp);
          formattedTimestamp = d.toLocaleString('en-IN', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
          });
        } catch (_) {}
      }

      if (modalBody) {
        modalBody.innerHTML = `
          <div style="margin-bottom: 1.15rem; background: var(--bg-hover); padding: 0.85rem 1rem; border-radius: 6px; border: 1px solid var(--border-color);">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0.65rem; font-size: 0.82rem; color: var(--text-secondary);">
              <div><strong>Batch Code:</strong> <span style="font-weight: 700; color: var(--accent-primary);">${batch.batch_code}</span></div>
              <div><strong>Voucher Date:</strong> <span style="font-weight: 700; color: #2563eb;">${batch.voucher_date_range || batch.upload_date_str}</span></div>
              <div><strong>Uploaded By:</strong> <span style="font-weight: 600; color: var(--text-primary);">${batch.created_by_user || 'admin'}</span></div>
              <div><strong>Upload Timestamp:</strong> <span>${formattedTimestamp}</span></div>
              <div><strong>Batch Status:</strong> <span class="badge ${batch.status === 'Completed' ? 'badge-success' : 'badge-danger'}">${batch.status}</span></div>
              <div><strong>Total Records:</strong> <span style="font-weight: 700; color: var(--text-primary);">${batch.total_rows.toLocaleString()} (+${batch.new_records.toLocaleString()} new)</span></div>
            </div>
            ${batch.error_summary ? `<div style="margin-top: 0.5rem; color: var(--danger); font-size: 0.80rem;"><strong>Error:</strong> ${batch.error_summary}</div>` : ''}
          </div>

          <div style="margin-bottom: 1.25rem;">
            <div style="font-weight: 700; font-size: 0.88rem; margin-bottom: 0.5rem; color: var(--text-primary);">Ingested Files & Column Verification:</div>
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
              ${(batch.files || []).map(f => `
                <div style="background: var(--bg-card); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                  <div>
                    <div style="font-weight: 600; font-size: 0.84rem; color: var(--text-primary);">${f.file_type}: ${f.original_filename}</div>
                    <div style="font-size: 0.74rem; color: var(--text-secondary); margin-top: 0.15rem;">
                      Header Row: <strong>${f.header_row_index || 1}</strong> | Total Rows: <strong>${(f.total_rows || 0).toLocaleString()}</strong> | Ingested: <strong>+${(f.valid_rows || 0).toLocaleString()}</strong>
                    </div>
                  </div>
                  <span class="badge ${f.status === 'Success' ? 'badge-success' : 'badge-danger'}" style="font-size: 0.68rem;">${f.status}</span>
                </div>
              `).join("")}
            </div>
          </div>
        `;
      }

      if (modalFooter) {
        modalFooter.innerHTML = `
          <button type="button" class="btn btn-secondary btn-sm modal-footer-close-btn" onclick="App.closeModal('record-detail-modal')">
            Close
          </button>
        `;
      }

      App.openModal("record-detail-modal");
    } catch (err) {
      App.toast("Failed to load batch details", "error");
    }
  }
};
