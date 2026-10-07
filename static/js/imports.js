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
        <div style="text-align: center; padding: 3rem; color: var(--text-muted); background: var(--bg-card); border-radius: var(--border-radius-md); border: 1px solid var(--border-color);">
          <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem; color: var(--text-primary);">No Import Batches Yet</div>
          <p style="font-size: 0.85rem;">Upload the mandatory 3 daily Excel files (Day Book, AP, AR) to record your first batch.</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = this.batches.map(b => {
      let statusBadgeClass = "badge-success";
      let statusText = b.status || "Completed";
      if (b.status === "Pending" || b.status === "Incomplete") {
        statusBadgeClass = "badge-warning";
        statusText = "Pending / Incomplete";
      } else if (b.status === "Failed") {
        statusBadgeClass = "badge-danger";
        statusText = "Failed";
      } else if (b.status === "Completed") {
        statusBadgeClass = "badge-success";
        statusText = "Completed / Successful";
      }

      return `
        <div class="card" style="margin-bottom: 1.25rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border-color);">
            <div>
              <div style="display: flex; align-items: center; gap: 0.65rem; margin-bottom: 0.25rem;">
                <span style="font-weight: 700; font-size: 1.05rem; color: var(--accent-primary);">${b.batch_code}</span>
                <span class="badge ${statusBadgeClass}">${statusText}</span>
              </div>
              <div style="font-size: 0.8rem; color: var(--text-secondary);">
                Uploaded on <strong>${b.upload_date_str}</strong> at <strong>${b.upload_time_str}</strong> by <strong>${b.created_by_user}</strong>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="Imports.showBatchDetails(${b.id})">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block; vertical-align:-2px; margin-right:4px;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
              View Full Audit Details
            </button>
          </div>

          <!-- Dataset Summary Metrics -->
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.75rem; margin-bottom: 1rem;">
            <div style="background: var(--bg-hover); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600;">Total Rows</div>
              <div style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">${b.total_rows.toLocaleString()}</div>
            </div>
            <div style="background: var(--success-bg); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid rgba(16,185,129,0.3);">
              <div style="font-size: 0.7rem; color: var(--success); text-transform: uppercase; font-weight: 600;">New Records</div>
              <div style="font-size: 1.15rem; font-weight: 700; color: var(--success);">+${b.new_records.toLocaleString()}</div>
            </div>
            <div style="background: var(--warning-bg); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid rgba(245,158,11,0.3);">
              <div style="font-size: 0.7rem; color: var(--warning); text-transform: uppercase; font-weight: 600;">Duplicates Prevented</div>
              <div style="font-size: 1.15rem; font-weight: 700; color: var(--warning);">${b.duplicate_records.toLocaleString()}</div>
            </div>
            <div style="background: var(--danger-bg); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid rgba(239,68,68,0.3);">
              <div style="font-size: 0.7rem; color: var(--danger); text-transform: uppercase; font-weight: 600;">Rejected Rows</div>
              <div style="font-size: 1.15rem; font-weight: 700; color: var(--danger);">${b.rejected_records.toLocaleString()}</div>
            </div>
          </div>

          <!-- Mandatory 3-File Dataset Breakdown -->
          <div style="font-size: 0.82rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.5rem;">
            Mandatory 3-File Dataset Breakdown:
          </div>
          <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 0.75rem;">
            <!-- Day Book -->
            <div style="background: var(--bg-hover); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: var(--text-primary);">Day Book</span>
                <span class="badge ${b.daybook_filename ? 'badge-success' : 'badge-danger'}">${b.daybook_filename ? 'Validated' : 'Missing'}</span>
              </div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); word-break: break-all;">
                ${b.daybook_filename || 'No Day Book uploaded'}
              </div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                Rows: <strong>${b.daybook_rows.toLocaleString()}</strong> | Columns: <strong>Validated</strong>
              </div>
            </div>

            <!-- AP -->
            <div style="background: var(--bg-hover); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: var(--text-primary);">Account Payable (AP)</span>
                <span class="badge ${b.ap_filename ? 'badge-success' : 'badge-danger'}">${b.ap_filename ? 'Validated' : 'Missing'}</span>
              </div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); word-break: break-all;">
                ${b.ap_filename || 'No AP uploaded'}
              </div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                Rows: <strong>${b.ap_rows.toLocaleString()}</strong> | Columns: <strong>Validated</strong>
              </div>
            </div>

            <!-- AR -->
            <div style="background: var(--bg-hover); padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color);">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                <span style="font-weight: 600; color: var(--text-primary);">Account Receivable (AR)</span>
                <span class="badge ${b.ar_filename ? 'badge-success' : 'badge-danger'}">${b.ar_filename ? 'Validated' : 'Missing'}</span>
              </div>
              <div style="font-size: 0.75rem; color: var(--text-secondary); word-break: break-all;">
                ${b.ar_filename || 'No AR uploaded'}
              </div>
              <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                Rows: <strong>${b.ar_rows.toLocaleString()}</strong> | Columns: <strong>Validated</strong>
              </div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  },

  async showBatchDetails(batchId) {
    try {
      const batch = await API.getBatch(batchId);
      const modalTitle = document.getElementById("record-detail-title");
      const modalBody = document.getElementById("record-detail-body");
      const modalFooter = document.querySelector("#record-detail-modal .modal-footer");

      if (modalTitle) modalTitle.innerText = `Batch Detail: ${batch.batch_code}`;

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
          <div style="margin-bottom: 1.25rem;">
            <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.6;">
              <strong>Batch Code:</strong> <span style="font-weight: 700; color: var(--accent-primary);">${batch.batch_code}</span><br>
              <strong>Uploaded By:</strong> ${batch.created_by_user || 'admin'}<br>
              <strong>Upload Date & Time:</strong> ${formattedTimestamp}<br>
              <strong>Batch Status:</strong> <span class="badge ${batch.status === 'Completed' ? 'badge-success' : 'badge-danger'}">${batch.status}</span>
              ${batch.error_summary ? `<div style="margin-top: 0.5rem; color: var(--danger); font-size: 0.82rem;"><strong>Error:</strong> ${batch.error_summary}</div>` : ''}
            </div>
          </div>

          <div style="margin-bottom: 1.5rem;">
            <div style="font-weight: 700; font-size: 0.92rem; margin-bottom: 0.75rem; color: var(--text-primary);">Ingested Files & Column Verification:</div>
            <div style="display: flex; flex-direction: column; gap: 0.65rem;">
              ${(batch.files || []).map(f => `
                <div style="background: var(--bg-hover); padding: 0.85rem 1rem; border-radius: 6px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                  <div>
                    <div style="font-weight: 600; font-size: 0.88rem; color: var(--text-primary);">${f.file_type}: ${f.original_filename}</div>
                    <div style="font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.2rem;">
                      Detected Header Row: <strong>${f.header_row_index || 1}</strong> | Total Rows: <strong>${(f.total_rows || 0).toLocaleString()}</strong> | Added: <strong>+${(f.valid_rows || 0).toLocaleString()}</strong> | Duplicates: <strong>${(f.duplicate_rows || 0).toLocaleString()}</strong>
                    </div>
                  </div>
                  <span class="badge ${f.status === 'Success' ? 'badge-success' : 'badge-danger'}">${f.status}</span>
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
