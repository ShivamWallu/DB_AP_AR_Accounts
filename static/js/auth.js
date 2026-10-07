const Auth = {
  pendingRegistration: null,
  otpTimerInterval: null,

  init() {
    this.bindEvents();
    this.checkSession();
  },

  bindEvents() {
    const loginForm = document.getElementById("login-form");
    if (loginForm) {
      loginForm.addEventListener("submit", (e) => this.handleLogin(e));
    }

    const regStep1Form = document.getElementById("register-step1-form");
    if (regStep1Form) {
      regStep1Form.addEventListener("submit", (e) => this.handleSendOTP(e));
    }

    const regStep2Form = document.getElementById("register-step2-form");
    if (regStep2Form) {
      regStep2Form.addEventListener("submit", (e) => this.handleVerifyOTP(e));
    }

    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => this.handleLogout());
    }

    window.addEventListener("auth:unauthorized", () => {
      this.showLoginView();
      App.toast("Session expired or unauthorized. Please log in.", "warning");
    });
  },

  switchAuthTab(mode) {
    const tabLogin = document.getElementById("tab-btn-login");
    const tabRegister = document.getElementById("tab-btn-register");
    const loginForm = document.getElementById("login-form");
    const registerContainer = document.getElementById("register-container");
    const quickCreds = document.getElementById("quick-creds-container");

    if (mode === "register") {
      if (tabLogin) tabLogin.classList.remove("active");
      if (tabRegister) tabRegister.classList.add("active");
      if (loginForm) loginForm.style.display = "none";
      if (registerContainer) registerContainer.style.display = "block";
      if (quickCreds) quickCreds.style.display = "none";
      this.backToStep1();
    } else {
      if (tabLogin) tabLogin.classList.add("active");
      if (tabRegister) tabRegister.classList.remove("active");
      if (loginForm) loginForm.style.display = "block";
      if (registerContainer) registerContainer.style.display = "none";
      if (quickCreds) quickCreds.style.display = "block";
    }
  },

  async handleSendOTP(e) {
    if (e) e.preventDefault();
    const fullName = document.getElementById("reg-fullname").value.trim();
    const username = document.getElementById("reg-username").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const role = document.getElementById("reg-role").value;
    const btnSend = document.getElementById("btn-send-otp");

    if (!fullName || !username || !email || !password) {
      App.toast("Please fill in all required registration fields", "warning");
      return;
    }

    if (!email.includes("@") || !email.includes(".")) {
      App.toast("Please enter a valid email address", "warning");
      return;
    }

    if (password.length < 6) {
      App.toast("Password must be at least 6 characters", "warning");
      return;
    }

    try {
      btnSend.disabled = true;
      btnSend.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="display:inline-block; width:14px; height:14px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:spin 0.6s linear infinite; vertical-align:middle; margin-right:6px;"></span>
        Sending Verification OTP...
      `;

      const res = await API.sendRegistrationOTP({
        full_name: fullName,
        username: username,
        email: email
      });

      this.pendingRegistration = {
        full_name: fullName,
        username: username,
        email: email,
        password: password,
        role: role
      };

      App.toast(`✓ 6-Digit OTP sent to ${email}`, "success");

      // Transition to Step 2 OTP Form
      document.getElementById("register-step1-form").style.display = "none";
      const step2Form = document.getElementById("register-step2-form");
      step2Form.style.display = "block";
      
      const emailDisplay = document.getElementById("otp-target-email-display");
      if (emailDisplay) emailDisplay.innerText = email;

      const otpInput = document.getElementById("reg-otp-code");
      if (otpInput) {
        otpInput.value = "";
        otpInput.focus();
      }

      this.startOtpTimer(res.expires_in_seconds || 600);
    } catch (err) {
      App.toast(err.message || "Failed to send OTP", "error");
    } finally {
      btnSend.disabled = false;
      btnSend.innerText = "Send Verification OTP ➔";
    }
  },

  async handleVerifyOTP(e) {
    if (e) e.preventDefault();
    if (!this.pendingRegistration) {
      App.toast("Registration session expired. Please start over.", "warning");
      this.backToStep1();
      return;
    }

    const otpInput = document.getElementById("reg-otp-code");
    const otpCode = otpInput ? otpInput.value.trim() : "";
    const btnVerify = document.getElementById("btn-verify-otp-submit");

    if (!otpCode || otpCode.length < 6) {
      App.toast("Please enter the complete 6-digit OTP code", "warning");
      return;
    }

    try {
      btnVerify.disabled = true;
      btnVerify.innerText = "Verifying & Activating...";

      const payload = {
        ...this.pendingRegistration,
        otp: otpCode
      };

      const res = await API.registerWithOTP(payload);
      API.setAuth(res.access_token, res.role, res.username, res.full_name);

      clearInterval(this.otpTimerInterval);
      App.toast(`🎉 Account created successfully! Welcome, ${res.full_name || res.username}!`, "success");

      this.showAppView(res);
      App.navigate("master");
    } catch (err) {
      App.toast(err.message || "OTP verification failed", "error");
    } finally {
      btnVerify.disabled = false;
      btnVerify.innerText = "✓ Verify OTP & Activate Account";
    }
  },

  async handleResendOTP() {
    if (!this.pendingRegistration || !this.pendingRegistration.email) {
      App.toast("Please fill in your email address first", "warning");
      this.backToStep1();
      return;
    }

    const resendBtn = document.getElementById("btn-resend-otp");
    try {
      if (resendBtn) {
        resendBtn.disabled = true;
        resendBtn.innerText = "Sending...";
      }

      const res = await API.sendRegistrationOTP({
        full_name: this.pendingRegistration.full_name,
        username: this.pendingRegistration.username,
        email: this.pendingRegistration.email
      });

      App.toast(`✓ Fresh OTP resent to ${this.pendingRegistration.email}`, "success");
      this.startOtpTimer(res.expires_in_seconds || 600);
    } catch (err) {
      App.toast(err.message || "Failed to resend OTP", "error");
      if (resendBtn) {
        resendBtn.disabled = false;
        resendBtn.innerText = "Resend OTP";
      }
    }
  },

  backToStep1() {
    clearInterval(this.otpTimerInterval);
    const step1 = document.getElementById("register-step1-form");
    const step2 = document.getElementById("register-step2-form");
    if (step1) step1.style.display = "block";
    if (step2) step2.style.display = "none";
  },

  startOtpTimer(seconds = 600) {
    clearInterval(this.otpTimerInterval);
    let remaining = seconds;
    const timerVal = document.getElementById("otp-timer-val");
    const resendBtn = document.getElementById("btn-resend-otp");

    if (resendBtn) resendBtn.disabled = true;

    const updateDisplay = () => {
      const mins = Math.floor(remaining / 60);
      const secs = remaining % 60;
      if (timerVal) {
        timerVal.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }

      if (remaining <= 0) {
        clearInterval(this.otpTimerInterval);
        if (timerVal) timerVal.innerText = "00:00 (Expired)";
        if (resendBtn) {
          resendBtn.disabled = false;
          resendBtn.innerText = "Resend OTP";
        }
      } else {
        remaining--;
      }
    };

    updateDisplay();
    this.otpTimerInterval = setInterval(updateDisplay, 1000);
  },

  async checkSession() {
    const token = API.getToken();
    if (!token) {
      this.showLoginView();
      return;
    }

    try {
      const user = await API.getMe();
      API.setAuth(token, user.role, user.username, user.full_name);
      this.showAppView(user);
      App.navigate(App.currentView || "master");
    } catch (err) {
      this.showLoginView();
    }
  },

  async handleLogin(e) {
    e.preventDefault();
    const usernameInput = document.getElementById("login-username");
    const passwordInput = document.getElementById("login-password");
    const submitBtn = document.getElementById("btn-login-submit");

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username || !password) {
      App.toast("Please enter both username and password", "warning");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerText = "Signing in...";

      const res = await API.login(username, password);
      API.setAuth(res.access_token, res.role, res.username, res.full_name);
      
      App.toast(`Welcome back, ${res.full_name || res.username}!`, "success");
      this.showAppView(res);
      App.navigate("master");
    } catch (err) {
      App.toast(err.message || "Invalid credentials", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerText = "Sign In";
    }
  },

  handleLogout() {
    API.clearAuth();
    this.showLoginView();
    App.toast("Logged out successfully", "info");
  },

  fillDemoCredentials(username, password) {
    this.switchAuthTab("login");
    const uInput = document.getElementById("login-username");
    const pInput = document.getElementById("login-password");
    if (uInput && pInput) {
      uInput.value = username;
      pInput.value = password;
      App.toast(`Demo credentials filled for ${username}`, "info");
    }
  },

  showLoginView() {
    const authScreen = document.getElementById("auth-screen");
    const appScreen = document.getElementById("app-screen");
    if (authScreen) authScreen.style.display = "flex";
    if (appScreen) appScreen.style.display = "none";
  },

  showAppView(user) {
    const authScreen = document.getElementById("auth-screen");
    const appScreen = document.getElementById("app-screen");
    if (authScreen) authScreen.style.display = "none";
    if (appScreen) appScreen.style.display = "flex";

    // Update user profile in sidebar
    const userNameEl = document.getElementById("sidebar-user-name");
    const userRoleEl = document.getElementById("sidebar-user-role");
    const userAvatarEl = document.getElementById("sidebar-user-avatar");

    const role = user.role || "Employee";
    const displayName = user.full_name || user.username || "User";

    if (userNameEl) userNameEl.innerText = displayName;
    if (userRoleEl) {
      userRoleEl.innerText = role;
      userRoleEl.className = `user-role-badge ${role.toLowerCase()}`;
    }
    if (userAvatarEl) {
      userAvatarEl.innerText = displayName.charAt(0).toUpperCase();
    }

    // Role-based visibility toggles
    const adminOnlyElements = document.querySelectorAll(".admin-only");
    adminOnlyElements.forEach(el => {
      el.style.display = (role === "Admin") ? "" : "none";
    });
  }
};
