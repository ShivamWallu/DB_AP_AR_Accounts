const Upload = {
  slots: {
    daybook: { file: null, validation: null, status: "pending" },
    ap: { file: null, validation: null, status: "pending" },
    ar: { file: null, validation: null, status: "pending" }
  },

  init() {
    this.bindBoxes();
    this.bindGlobalInputs();
    this.bindActions();
  },

  bindBoxes() {
    const boxConfigs = [
      { key: "daybook", boxId: "upload-box-daybook", inputId: "input-file-daybook", type: "Day Book" },
      { key: "ap", boxId: "upload-box-ap", inputId: "input-file-ap", type: "AP" },
      { key: "ar", boxId: "upload-box-ar", inputId: "input-file-ar", type: "AR" }
    ];

    boxConfigs.forEach(cfg => {
      const box = document.getElementById(cfg.boxId);
      const input = document.getElementById(cfg.inputId);
      if (!box || !input) return;

      // Click to browse
      box.addEventListener("click", (e) => {
        if (e.target.closest(".btn-remove-box-file")) return;
        input.click();
      });

      // File selected
      input.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
          this.processFileForSlot(e.target.files[0], cfg.key, cfg.type);
        }
      });

      // Drag over box
      box.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.stopPropagation();
        box.classList.add("drag-over");
      });

      box.addEventListener("dragleave", (e) => {
        e.preventDefault();
        e.stopPropagation();
        box.classList.remove("drag-over");
      });

      box.addEventListener("drop", (e) => {
        e.preventDefault();
        e.stopPropagation();
        box.classList.remove("drag-over");
        if (e.dataTransfer.files.length > 0) {
          if (e.dataTransfer.files.length === 1) {
            this.processFileForSlot(e.dataTransfer.files[0], cfg.key, cfg.type);
          } else {
            this.handleMultipleFiles(Array.from(e.dataTransfer.files));
          }
        }
      });
    });
  },

  bindGlobalInputs() {
    const globalInput = document.getElementById("upload-global-input");
    const browseAllBtn = document.getElementById("btn-upload-all-browse");
    const uploadView = document.getElementById("view-upload");

    if (browseAllBtn && globalInput) {
      browseAllBtn.addEventListener("click", () => globalInput.click());
    }

    if (globalInput) {
      globalInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
          this.handleMultipleFiles(Array.from(e.target.files));
        }
      });
    }

    // Global drag over upload view
    if (uploadView) {
      uploadView.addEventListener("dragover", (e) => {
        e.preventDefault();
      });
      uploadView.addEventListener("drop", (e) => {
        if (e.target.closest(".upload-box")) return; // Handled by box drop
        e.preventDefault();
        if (e.dataTransfer.files.length > 0) {
          this.handleMultipleFiles(Array.from(e.dataTransfer.files));
        }
      });
    }
  },

  bindActions() {
    const btnConfirm = document.getElementById("btn-confirm-import");
    const btnClear = document.getElementById("btn-clear-upload-files");
    const btnSeed = document.getElementById("btn-seed-initial-files");

    if (btnConfirm) {
      btnConfirm.addEventListener("click", () => this.executeImport());
    }

    if (btnClear) {
      btnClear.addEventListener("click", () => this.resetAllSlots());
    }

    if (btnSeed) {
      btnSeed.addEventListener("click", () => this.seedInitialFiles());
    }
  },

  async processFileForSlot(file, slotKey, expectedType) {
    if (!file.name.endsWith(".xlsx") && !file.name.endsWith(".xls")) {
      App.toast(`File '${file.name}' is not an Excel file (.xlsx / .xls)`, "warning");
      return;
    }

    // Set validating state in UI
    this.slots[slotKey] = { file: file, validation: null, status: "validating" };
    this.renderSlotUI(slotKey);
    this.updateStepperAndBanner();

    try {
      const formData = new FormData();
      formData.append("files", file);

      const valResponse = await API.validateFiles(formData);
      const fileVal = valResponse.files_validation && valResponse.files_validation[0];

      if (!fileVal) {
        throw new Error("No validation data returned from server");
      }

      // Check if file matches expected type or if it was auto-detected
      if (fileVal.status === "Valid") {
        if (fileVal.file_type === expectedType) {
          this.slots[slotKey] = { file: file, validation: fileVal, status: "validated" };
          App.toast(`✓ ${expectedType} verified: ${fileVal.valid_data_rows} valid records`, "success");
        } else {
          // File valid but belongs to another slot! Auto route it!
          const targetSlot = this.getSlotKeyByType(fileVal.file_type);
          if (targetSlot) {
            this.slots[targetSlot] = { file: file, validation: fileVal, status: "validated" };
            this.slots[slotKey] = { file: null, validation: null, status: "pending" };
            this.renderSlotUI(targetSlot);
            App.toast(`✓ Routed '${file.name}' to ${fileVal.file_type} box (${fileVal.valid_data_rows} rows)`, "info");
          } else {
            this.slots[slotKey] = { file: file, validation: fileVal, status: "error" };
          }
        }
      } else {
        this.slots[slotKey] = { file: file, validation: fileVal, status: "error" };
        App.toast(`Validation notice for '${file.name}': ${fileVal.message}`, "warning");
      }
    } catch (err) {
      this.slots[slotKey] = {
        file: file,
        validation: {
          file_type: expectedType,
          filename: file.name,
          status: "Failed",
          message: err.message || "Failed to validate file structure"
        },
        status: "error"
      };
      App.toast(`Error validating '${file.name}': ${err.message}`, "error");
    }

    this.renderSlotUI(slotKey);
    this.updateStepperAndBanner();
  },

  async handleMultipleFiles(files) {
    const excelFiles = files.filter(f => f.name.endsWith(".xlsx") || f.name.endsWith(".xls"));
    if (excelFiles.length === 0) {
      App.toast("Please select Excel files (.xlsx / .xls)", "warning");
      return;
    }

    App.toast(`Scanning and validating ${excelFiles.length} file(s)...`, "info");

    for (const f of excelFiles) {
      // Find candidate slot or test file
      const formData = new FormData();
      formData.append("files", f);

      try {
        const valResponse = await API.validateFiles(formData);
        const fileVal = valResponse.files_validation && valResponse.files_validation[0];

        if (fileVal) {
          const slotKey = this.getSlotKeyByType(fileVal.file_type);
          if (slotKey) {
            this.slots[slotKey] = {
              file: f,
              validation: fileVal,
              status: fileVal.status === "Valid" ? "validated" : "error"
            };
            this.renderSlotUI(slotKey);
          } else {
            App.toast(`Could not identify document type for '${f.name}'`, "warning");
          }
        }
      } catch (err) {
        console.error("Error analyzing file:", err);
      }
    }

    this.updateStepperAndBanner();
  },

  getSlotKeyByType(fileType) {
    if (fileType === "Day Book") return "daybook";
    if (fileType === "AP") return "ap";
    if (fileType === "AR") return "ar";
    return null;
  },

  renderSlotUI(slotKey) {
    const box = document.getElementById(`upload-box-${slotKey}`);
    const body = document.getElementById(`box-body-${slotKey}`);
    const badge = document.getElementById(`box-badge-${slotKey}`);
    if (!box || !body || !badge) return;

    const state = this.slots[slotKey];

    // Reset classes
    box.classList.remove("validating", "validated", "error");

    if (state.status === "pending") {
      badge.innerText = "Required";
      badge.className = "upload-box-badge badge-pending";
      body.innerHTML = `
        <div class="upload-box-placeholder">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.8"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"></path></svg>
          <div class="upload-box-prompt">Drop file here</div>
          <div class="upload-box-hint">or click to browse (.xlsx, .xls)</div>
        </div>
      `;
    } else if (state.status === "validating") {
      box.classList.add("validating");
      badge.innerText = "Validating...";
      badge.className = "upload-box-badge badge-pending";
      body.innerHTML = `
        <div class="upload-box-placeholder">
          <div style="font-size: 1.8rem; animation: pulseScan 1s infinite;">🔍</div>
          <div class="upload-box-prompt" style="color: #2563eb;">Validating Column Signatures...</div>
          <div class="upload-box-hint">${state.file ? state.file.name : ''}</div>
        </div>
      `;
    } else if (state.status === "validated") {
      box.classList.add("validated");
      badge.innerText = "✓ Validated";
      badge.className = "upload-box-badge badge-valid";

      const val = state.validation || {};
      const sizeKb = state.file ? (state.file.size / 1024).toFixed(1) : "0";

      body.innerHTML = `
        <div class="validated-file-card">
          <div class="validated-file-header">
            <div class="validated-file-name">📄 ${state.file ? state.file.name : 'Excel File'}</div>
            <span class="badge badge-success" style="font-size: 0.68rem;">Verified</span>
          </div>
          <div class="validated-file-stats">
            <div>📊 <strong>${(val.valid_data_rows || 0).toLocaleString()}</strong> Verified Data Rows</div>
            <div>📋 Header Row: <strong>${val.detected_header_row || 'Auto'}</strong> | Size: <strong>${sizeKb} KB</strong></div>
            <div style="color: #16a34a; font-size: 0.72rem; margin-top: 0.2rem;">✓ All Required Columns Present</div>
          </div>
          <div class="validated-file-actions">
            <button class="btn-remove-box-file" onclick="Upload.removeSlotFile('${slotKey}')">✕ Remove / Change</button>
          </div>
        </div>
      `;
    } else if (state.status === "error") {
      box.classList.add("error");
      badge.innerText = "⚠ Failed";
      badge.className = "upload-box-badge badge-error";

      const val = state.validation || {};
      const errMsg = val.message || (val.columns_missing && val.columns_missing.length > 0 ? `Missing: ${val.columns_missing.join(', ')}` : "Validation failed");

      body.innerHTML = `
        <div class="validated-file-card" style="border-color: #fecaca; background: #fff5f5;">
          <div class="validated-file-header">
            <div class="validated-file-name" style="color: #b91c1c;">⚠ ${state.file ? state.file.name : 'Invalid File'}</div>
          </div>
          <div style="font-size: 0.75rem; color: #b91c1c; line-height: 1.4; margin-top: 0.2rem;">
            ${errMsg}
          </div>
          <div class="validated-file-actions">
            <button class="btn-remove-box-file" onclick="Upload.removeSlotFile('${slotKey}')">✕ Replace File</button>
          </div>
        </div>
      `;
    }
  },

  removeSlotFile(slotKey) {
    this.slots[slotKey] = { file: null, validation: null, status: "pending" };
    const input = document.getElementById(`input-file-${slotKey}`);
    if (input) input.value = "";
    this.renderSlotUI(slotKey);
    this.updateStepperAndBanner();
  },

  resetAllSlots() {
    ['daybook', 'ap', 'ar'].forEach(key => {
      this.slots[key] = { file: null, validation: null, status: "pending" };
      const input = document.getElementById(`input-file-${key}`);
      if (input) input.value = "";
      this.renderSlotUI(key);
    });
    this.updateStepperAndBanner();
    App.toast("Upload boxes reset", "info");
  },

  updateStepperAndBanner() {
    const slots = this.slots;
    const banner = document.getElementById("upload-summary-banner");
    const confirmBtn = document.getElementById("btn-confirm-import");
    const clearBtn = document.getElementById("btn-clear-upload-files");

    let validatedCount = 0;
    let anyFilePresent = false;

    // Update each step pill
    ['daybook', 'ap', 'ar'].forEach(k => {
      const pill = document.getElementById(`step-pill-${k}`);
      const statusText = document.getElementById(`step-status-${k}`);
      const numSpan = document.getElementById(`step-num-${k}`);
      const s = slots[k];

      if (!pill || !statusText || !numSpan) return;

      pill.classList.remove("validating", "validated", "error");

      if (s.file) anyFilePresent = true;

      if (s.status === "validated") {
        validatedCount++;
        pill.classList.add("validated");
        numSpan.innerText = "✓";
        const rows = s.validation ? s.validation.valid_data_rows : 0;
        statusText.innerText = `Validated (${rows} rows)`;
      } else if (s.status === "validating") {
        pill.classList.add("validating");
        numSpan.innerText = "⏳";
        statusText.innerText = "Validating...";
      } else if (s.status === "error") {
        pill.classList.add("error");
        numSpan.innerText = "!";
        statusText.innerText = "Validation Failed";
      } else {
        numSpan.innerText = k === 'daybook' ? '1' : (k === 'ap' ? '2' : '3');
        statusText.innerText = "Pending Upload";
      }
    });

    // Update connectors
    const conn1 = document.getElementById("step-conn-1");
    const conn2 = document.getElementById("step-conn-2");
    if (conn1) conn1.classList.toggle("active", slots.daybook.status === "validated" && slots.ap.status === "validated");
    if (conn2) conn2.classList.toggle("active", slots.ap.status === "validated" && slots.ar.status === "validated");

    // Clear button visibility
    if (clearBtn) {
      clearBtn.style.display = anyFilePresent ? "inline-flex" : "none";
    }

    // Update Banner and Confirm Button
    if (!banner || !confirmBtn) return;

    if (validatedCount === 3) {
      banner.style.display = "flex";
      banner.className = "upload-summary-banner success-banner";
      banner.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div style="font-size: 1.5rem; color: #16a34a;">🎉</div>
          <div>
            <div style="font-weight: 700; font-size: 0.95rem; color: #15803d;">
              All 3 Mandatory Files Validated Successfully!
            </div>
            <div style="font-size: 0.8rem; color: #166534;">
              Dataset is complete (Day Book + AP + AR). Ready to commit into a unified historical batch.
            </div>
          </div>
        </div>
        <span class="badge badge-success" style="font-size: 0.8rem; padding: 0.35rem 0.75rem;">3/3 Ready</span>
      `;
      confirmBtn.disabled = false;
      confirmBtn.classList.add("pulse-ready");
    } else if (anyFilePresent) {
      banner.style.display = "flex";
      banner.className = "upload-summary-banner incomplete-banner";

      const missing = [];
      if (slots.daybook.status !== "validated") missing.push("Day Book");
      if (slots.ap.status !== "validated") missing.push("Account Payable (AP)");
      if (slots.ar.status !== "validated") missing.push("Account Receivable (AR)");

      banner.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <div style="font-size: 1.4rem; color: #d97706;">⏳</div>
          <div>
            <div style="font-weight: 700; font-size: 0.9rem; color: #b45309;">
              Incomplete Dataset (${validatedCount}/3 Validated)
            </div>
            <div style="font-size: 0.78rem; color: #92400e;">
              Pending files: <strong>${missing.join(", ")}</strong>. All 3 files are mandatory before dataset can be processed.
            </div>
          </div>
        </div>
        <span class="badge badge-warning" style="font-size: 0.78rem;">${validatedCount}/3 Valid</span>
      `;
      confirmBtn.disabled = true;
      confirmBtn.classList.remove("pulse-ready");
    } else {
      banner.style.display = "none";
      confirmBtn.disabled = true;
      confirmBtn.classList.remove("pulse-ready");
    }
  },

  showHud(title, subtitle) {
    const modal = document.getElementById("upload-progress-modal");
    const titleEl = document.getElementById("upload-hud-title");
    const subtitleEl = document.getElementById("upload-hud-subtitle");
    const barEl = document.getElementById("upload-hud-progress-bar");
    
    if (titleEl && title) titleEl.innerText = title;
    if (subtitleEl && subtitle) subtitleEl.innerText = subtitle;
    if (barEl) barEl.style.width = "18%";

    for (let i = 1; i <= 4; i++) {
      const stepEl = document.getElementById(`hud-step-${i}`);
      if (!stepEl) continue;
      stepEl.className = "hud-step-item" + (i === 1 ? " active" : "");
      const bullet = stepEl.querySelector(".hud-step-bullet");
      const status = stepEl.querySelector(".hud-step-status");
      if (bullet) bullet.innerText = i;
      if (status) {
        status.innerText = i === 1 ? "In Progress..." : "Pending";
        status.style.color = i === 1 ? "#2563eb" : "#94a3b8";
      }
    }

    if (modal) {
      modal.style.display = "flex";
      void modal.offsetWidth;
      modal.classList.add("show");
    }
  },

  setHudStep(stepNum, progressPercent, statusText = "Completed") {
    const barEl = document.getElementById("upload-hud-progress-bar");
    if (barEl) barEl.style.width = `${progressPercent}%`;

    for (let i = 1; i <= 4; i++) {
      const stepEl = document.getElementById(`hud-step-${i}`);
      if (!stepEl) continue;
      const bullet = stepEl.querySelector(".hud-step-bullet");
      const status = stepEl.querySelector(".hud-step-status");

      if (i < stepNum) {
        stepEl.className = "hud-step-item completed";
        if (bullet) bullet.innerText = "✓";
        if (status) {
          status.innerText = "Completed";
          status.style.color = "#16a34a";
        }
      } else if (i === stepNum) {
        stepEl.className = "hud-step-item active";
        if (bullet) bullet.innerText = i;
        if (status) {
          status.innerText = statusText;
          status.style.color = "#2563eb";
        }
      } else {
        stepEl.className = "hud-step-item";
        if (bullet) bullet.innerText = i;
        if (status) {
          status.innerText = "Pending";
          status.style.color = "#94a3b8";
        }
      }
    }
  },

  closeHud() {
    const modal = document.getElementById("upload-progress-modal");
    if (modal) {
      modal.classList.remove("show");
      setTimeout(() => {
        if (!modal.classList.contains("show")) {
          modal.style.display = "none";
        }
      }, 250);
    }
  },

  async executeImport() {
    const { daybook, ap, ar } = this.slots;

    if (daybook.status !== "validated" || ap.status !== "validated" || ar.status !== "validated") {
      App.toast("Cannot import: All 3 files (Day Book, AP, AR) must be successfully validated.", "warning");
      return;
    }

    const formData = new FormData();
    formData.append("files", daybook.file);
    formData.append("files", ap.file);
    formData.append("files", ar.file);

    const confirmBtn = document.getElementById("btn-confirm-import");
    
    this.showHud("🚀 Ingesting 3-File Dataset...", "2X High-speed direct streaming parser & batch mapping");
    this.setHudStep(1, 25, "✓ 3/3 Headers Verified");

    const timer2 = setTimeout(() => this.setHudStep(2, 55, "Streaming & Storing Rows..."), 200);
    const timer3 = setTimeout(() => this.setHudStep(3, 80, "Reconciling Master 360°..."), 500);

    try {
      if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.innerText = "⏳ Ingesting 3-File Dataset...";
      }

      const batch = await API.importFiles(formData);
      clearTimeout(timer2);
      clearTimeout(timer3);

      this.setHudStep(4, 100, "✓ Tables Synchronized");
      const titleEl = document.getElementById("upload-hud-title");
      if (titleEl) titleEl.innerText = `🎉 Batch ${batch.batch_code} Ingested!`;

      await new Promise(r => setTimeout(r, 600));
      this.closeHud();

      App.toast(`🎉 Success! Batch ${batch.batch_code} ingested: +${batch.new_records} new records added!`, "success");
      
      this.resetAllSlots();
      await App.refreshAllData(batch.id);
      App.navigate("master");
    } catch (err) {
      clearTimeout(timer2);
      clearTimeout(timer3);
      this.closeHud();
      App.toast(err.message || "Failed to import batch", "error");
    } finally {
      if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.innerText = "Commit & Ingest 3-File Dataset";
      }
    }
  },

  async seedInitialFiles() {
    const btn = document.getElementById("btn-seed-initial-files");
    this.showHud("⚡ Auto-Importing Dataset...", "Ingesting Day Book, AP, and AR from 'data_files' folder");
    this.setHudStep(1, 25, "Scanning Files...");

    const timer2 = setTimeout(() => this.setHudStep(2, 55, "2X Streaming Ingestion..."), 200);
    const timer3 = setTimeout(() => this.setHudStep(3, 80, "Reconciling Master 360°..."), 450);

    try {
      if (btn) {
        btn.disabled = true;
        btn.innerText = "⏳ Ingesting data_files...";
      }

      const batch = await API.importInitialData();
      clearTimeout(timer2);
      clearTimeout(timer3);

      this.setHudStep(4, 100, "✓ Tables Synchronized");
      const titleEl = document.getElementById("upload-hud-title");
      if (titleEl) titleEl.innerText = `🎉 Batch ${batch.batch_code} Ingested!`;

      await new Promise(r => setTimeout(r, 600));
      this.closeHud();

      App.toast(`🎉 Batch ${batch.batch_code} imported from 'data_files' folder (+${batch.new_records} new records)`, "success");
      await App.refreshAllData(batch.id);
      App.navigate("master");
    } catch (err) {
      clearTimeout(timer2);
      clearTimeout(timer3);
      this.closeHud();
      App.toast(err.message || "Failed to import initial files", "error");
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerText = "Auto-Import from 'data_files' Folder";
      }
    }
  }
};
