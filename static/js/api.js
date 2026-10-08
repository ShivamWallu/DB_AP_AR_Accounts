const API = {
  getToken() {
    return localStorage.getItem("access_token");
  },

  setAuth(token, role, username, fullName) {
    localStorage.setItem("access_token", token);
    localStorage.setItem("user_role", role);
    localStorage.setItem("username", username);
    if (fullName) localStorage.setItem("user_fullname", fullName);
  },

  clearAuth() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
    localStorage.removeItem("username");
    localStorage.removeItem("user_fullname");
  },

  getUser() {
    return {
      token: localStorage.getItem("access_token"),
      role: localStorage.getItem("user_role") || "Guest",
      username: localStorage.getItem("username") || "",
      fullName: localStorage.getItem("user_fullname") || "User"
    };
  },

  buildQueryString(params = {}) {
    const cleanParams = {};
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== null && v !== "") {
        cleanParams[k] = v;
      }
    }
    return new URLSearchParams(cleanParams).toString();
  },

  async request(endpoint, options = {}) {
    const token = this.getToken();
    const headers = options.headers || {};
    
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
      headers["Content-Type"] = "application/json";
    }

    try {
      const response = await fetch(endpoint, {
        ...options,
        headers
      });

      if (response.status === 401) {
        this.clearAuth();
        window.dispatchEvent(new CustomEvent("auth:unauthorized"));
        throw new Error("Session expired. Please log in again.");
      }

      if (!response.ok) {
        let errorMsg = "An error occurred";
        try {
          const errData = await response.json();
          if (Array.isArray(errData.detail)) {
            errorMsg = errData.detail.map(d => d.msg || JSON.stringify(d)).join(", ");
          } else if (typeof errData.detail === "object" && errData.detail !== null) {
            errorMsg = JSON.stringify(errData.detail);
          } else {
            errorMsg = errData.detail || errData.message || JSON.stringify(errData);
          }
        } catch (e) {
          errorMsg = await response.text() || `HTTP ${response.status}`;
        }
        throw new Error(errorMsg);
      }

      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        return await response.json();
      }
      return response;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  async login(username, password) {
    return await this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
  },

  async sendRegistrationOTP(payload) {
    return await this.request("/api/auth/send-registration-otp", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  async registerWithOTP(payload) {
    return await this.request("/api/auth/register-with-otp", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  async getMe() {
    return await this.request("/api/auth/me");
  },

  async getUsers() {
    return await this.request("/api/auth/users");
  },

  // Dashboard Endpoints
  async getDashboardStats() {
    return await this.request("/api/dashboard/stats");
  },

  // Filters Endpoints
  async getFilterOptions() {
    return await this.request("/api/data/filters");
  },

  async getMaster(params = {}) {
    const qs = this.buildQueryString(params);
    return await this.request(`/api/data/master?${qs}`);
  },

  async getDayBook(params = {}) {
    const qs = this.buildQueryString(params);
    return await this.request(`/api/data/daybook?${qs}`);
  },

  async getAP(params = {}) {
    const qs = this.buildQueryString(params);
    return await this.request(`/api/data/ap?${qs}`);
  },

  async getAR(params = {}) {
    const qs = this.buildQueryString(params);
    return await this.request(`/api/data/ar?${qs}`);
  },

  async getCrossReference(voucherNo) {
    return await this.request(`/api/data/cross-reference/${encodeURIComponent(voucherNo)}`);
  },

  // Upload & Import Endpoints
  async validateFiles(formData) {
    return await this.request("/api/upload/validate", {
      method: "POST",
      body: formData
    });
  },

  async importFiles(formData) {
    return await this.request("/api/upload/import", {
      method: "POST",
      body: formData
    });
  },

  async importInitialData() {
    return await this.request("/api/upload/import-initial-data", {
      method: "POST"
    });
  },

  // Import History Endpoints
  async getBatches() {
    return await this.request("/api/imports");
  },

  async getBatch(batchId) {
    return await this.request(`/api/imports/${batchId}`);
  },

  // Audit Logs
  async getAuditLogs(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return await this.request(`/api/audit/logs?${qs}`);
  },

  // Real-time Server Verification Endpoints
  async getVerifications(params = {}) {
    const qs = this.buildQueryString(params);
    return await this.request(`/api/data/verifications?${qs}`);
  },

  async toggleVerification(payload) {
    return await this.request("/api/data/verify", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  }
};

