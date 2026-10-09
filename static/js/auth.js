const Auth = {
  pendingRegistration: null,
  otpTimerInterval: null,
  resetTimerInterval: null,

  init() {
    this.bindEvents();
    this.initOtpBoxes();
    this.initResetTokenCheck();
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

    const forgotForm = document.getElementById("forgot-password-form");
    if (forgotForm) {
      forgotForm.addEventListener("submit", (e) => this.handleForgotPassword(e));
    }

    const resetForm = document.getElementById("reset-password-form");
    if (resetForm) {
      resetForm.addEventListener("submit", (e) => this.handleResetPassword(e));
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

  initOtpBoxes() {
    const boxes = document.querySelectorAll(".otp-digit-box");
    if (!boxes || boxes.length === 0) return;

    boxes.forEach((box, idx) => {
      // 1. Keydown handling for arrows & backspace
      box.addEventListener("keydown", (e) => {
        if (e.key === "Backspace") {
          if (!box.value && idx > 0) {
            boxes[idx - 1].focus();
            boxes[idx - 1].value = "";
            this.syncOtpFromBoxes();
          } else {
            box.value = "";
            this.syncOtpFromBoxes();
          }
        } else if (e.key === "ArrowLeft" && idx > 0) {
          boxes[idx - 1].focus();
        } else if (e.key === "ArrowRight" && idx < boxes.length - 1) {
          boxes[idx + 1].focus();
        }
      });

      // 2. Input handling (1 digit numeric)
      box.addEventListener("input", (e) => {
        const val = e.target.value.replace(/\D/g, "");
        if (val.length > 1) {
          // User typed/pasted multi digits inside single box
          this.setOtpFromValue(e.target.value);
          return;
        }
        box.value = val;
        this.syncOtpFromBoxes();

        if (val && idx < boxes.length - 1) {
          boxes[idx + 1].focus();
          boxes[idx + 1].select();
        }
      });

      // 3. Paste event anywhere in the box
      box.addEventListener("paste", (e) => {
        e.preventDefault();
        const text = (e.clipboardData || window.clipboardData).getData("text");
        if (text) {
          this.setOtpFromValue(text);
        }
      });

      box.addEventListener("focus", () => {
        box.select();
      });
    });
  },

  setOtpFromValue(rawVal) {
    if (!rawVal) return;
    const digits = String(rawVal).replace(/\D/g, "").slice(0, 6);
    const boxes = document.querySelectorAll(".otp-digit-box");
    
    boxes.forEach((box, i) => {
      box.value = digits[i] || "";
    });

    this.syncOtpFromBoxes();

    // Focus on the next empty box or the last box
    if (digits.length < 6 && boxes[digits.length]) {
      boxes[digits.length].focus();
    } else if (boxes[5]) {
      boxes[5].focus();
    }

    if (digits.length === 6) {
      App.toast("✓ 6-Digit OTP pasted successfully!", "success");
    }
  },

  syncOtpFromBoxes() {
    const boxes = document.querySelectorAll(".otp-digit-box");
    let fullCode = "";
    boxes.forEach(b => {
      fullCode += (b.value || "").trim();
    });
    const hiddenInput = document.getElementById("reg-otp-code");
    if (hiddenInput) {
      hiddenInput.value = fullCode;
    }
    return fullCode;
  },

  async pasteFromClipboard() {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          this.setOtpFromValue(text);
          return;
        }
      }
      // Fallback prompt if clipboard permission denied
      const manual = prompt("Paste your 6-digit OTP code copied from Gmail here:");
      if (manual) {
        this.setOtpFromValue(manual);
      }
    } catch (err) {
      const manual = prompt("Paste your 6-digit OTP code copied from Gmail here:");
      if (manual) {
        this.setOtpFromValue(manual);
      }
    }
  },

  switchAuthTab(mode) {
    const tabLogin = document.getElementById("tab-btn-login");
    const tabRegister = document.getElementById("tab-btn-register");
    const loginForm = document.getElementById("login-form");
    const registerContainer = document.getElementById("register-container");
    const forgotContainer = document.getElementById("forgot-container");
    const resetContainer = document.getElementById("reset-password-container");
    const quickCreds = document.getElementById("quick-creds-container");
    const navTabs = document.querySelector(".auth-nav-tabs");

    if (forgotContainer) forgotContainer.style.display = "none";
    if (resetContainer) resetContainer.style.display = "none";

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
      if (quickCreds) quickCreds.style.display = "flex";
    }
  },

  showForgotPasswordView() {
    const tabLogin = document.getElementById("tab-btn-login");
    const tabRegister = document.getElementById("tab-btn-register");
    const loginForm = document.getElementById("login-form");
    const registerContainer = document.getElementById("register-container");
    const forgotContainer = document.getElementById("forgot-container");
    const resetContainer = document.getElementById("reset-password-container");
    const quickCreds = document.getElementById("quick-creds-container");

    if (tabLogin) tabLogin.classList.remove("active");
    if (tabRegister) tabRegister.classList.remove("active");
    if (loginForm) loginForm.style.display = "none";
    if (registerContainer) registerContainer.style.display = "none";
    if (resetContainer) resetContainer.style.display = "none";
    if (quickCreds) quickCreds.style.display = "none";

    if (forgotContainer) {
      forgotContainer.style.display = "block";
      const identInput = document.getElementById("forgot-identifier");
      if (identInput) {
        identInput.value = "";
        setTimeout(() => identInput.focus(), 80);
      }
    }
  },

  async handleForgotPassword(e) {
    if (e) e.preventDefault();
    const identInput = document.getElementById("forgot-identifier");
    const submitBtn = document.getElementById("btn-forgot-submit");
    const identifier = identInput ? identInput.value.trim() : "";

    if (!identifier) {
      App.toast("Please enter your username or registered email address", "warning");
      return;
    }

    try {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Dispatching 10-Minute Reset Link...";
      }

      const res = await API.requestPasswordReset(identifier);
      App.toast(`✓ ${res.message}`, "success");
      
      // Update info banner
      const banner = document.querySelector("#forgot-container .auth-info-banner");
      if (banner) {
        banner.style.background = "#f0fdf4";
        banner.style.borderColor = "#86efac";
        banner.style.color = "#15803d";
        banner.innerHTML = `
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.2" style="flex-shrink:0; margin-top:2px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          <div>
            <strong>Reset Link Dispatched!</strong><br/>
            We've sent a 10-minute password reset link to <strong>${res.email}</strong>. Please check your inbox / spam folder.
          </div>
        `;
      }
    } catch (err) {
      App.toast(err.message || "Failed to send reset link", "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = "Send Reset Link to Email ➔";
      }
    }
  },

  async initResetTokenCheck() {
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get("reset_token");
    if (resetToken) {
      this.showResetPasswordView(resetToken);
    }
  },

  async showResetPasswordView(token) {
    try {
      const res = await API.verifyResetToken(token);
      
      const tabLogin = document.getElementById("tab-btn-login");
      const tabRegister = document.getElementById("tab-btn-register");
      const loginForm = document.getElementById("login-form");
      const registerContainer = document.getElementById("register-container");
      const forgotContainer = document.getElementById("forgot-container");
      const resetContainer = document.getElementById("reset-password-container");
      const quickCreds = document.getElementById("quick-creds-container");
      const navTabs = document.querySelector(".auth-nav-tabs");

      if (navTabs) navTabs.style.display = "none";
      if (tabLogin) tabLogin.classList.remove("active");
      if (tabRegister) tabRegister.classList.remove("active");
      if (loginForm) loginForm.style.display = "none";
      if (registerContainer) registerContainer.style.display = "none";
      if (forgotContainer) forgotContainer.style.display = "none";
      if (quickCreds) quickCreds.style.display = "none";

      if (resetContainer) {
        resetContainer.style.display = "block";
        const hiddenToken = document.getElementById("reset-token-hidden");
        const userDisplay = document.getElementById("reset-user-display");
        const p1 = document.getElementById("reset-new-password");
        const p2 = document.getElementById("reset-confirm-password");

        if (hiddenToken) hiddenToken.value = token;
        if (userDisplay) userDisplay.innerText = `@${res.username} (${res.full_name || res.username})`;
        if (p1) p1.value = "";
        if (p2) p2.value = "";
        if (p1) setTimeout(() => p1.focus(), 100);

        this.startResetTimer(res.remaining_seconds || 600);
      }

      App.toast(`✓ Password reset session verified for @${res.username}`, "info");
    } catch (err) {
      App.toast(err.message || "This password reset link is invalid or has expired.", "error");
      window.history.replaceState({}, document.title, window.location.pathname);
      this.switchAuthTab("login");
    }
  },

  startResetTimer(seconds = 600) {
    clearInterval(this.resetTimerInterval);
    let remaining = seconds;
    const timerEl = document.getElementById("reset-timer-val");

    const updateTimer = () => {
      const mins = Math.floor(remaining / 60);
      const secs = remaining % 60;
      if (timerEl) {
        timerEl.innerText = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
      }

      if (remaining <= 0) {
        clearInterval(this.resetTimerInterval);
        if (timerEl) timerEl.innerText = "00:00 (Expired)";
        App.toast("⚠️ This password reset link has expired. Please request a new link.", "warning");
      } else {
        remaining--;
      }
    };

    updateTimer();
    this.resetTimerInterval = setInterval(updateTimer, 1000);
  },

  checkPasswordStrength(password) {
    if (!password || password.length < 8) {
      return "Password must be at least 8 characters long.";
    }
    if (!/[A-Z]/.test(password)) {
      return "Password must contain at least one uppercase letter (A-Z).";
    }
    if (!/[a-z]/.test(password)) {
      return "Password must contain at least one lowercase letter (a-z).";
    }
    if (!/\d/.test(password)) {
      return "Password must contain at least one number (0-9).";
    }
    if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/~`]/.test(password)) {
      return "Password must contain at least one special character (!@#$%^&*...).";
    }
    return null;
  },

  async handleResetPassword(e) {
    if (e) e.preventDefault();
    const tokenInput = document.getElementById("reset-token-hidden");
    const p1Input = document.getElementById("reset-new-password");
    const p2Input = document.getElementById("reset-confirm-password");
    const submitBtn = document.getElementById("btn-reset-password-submit");

    const token = tokenInput ? tokenInput.value.trim() : "";
    const p1 = p1Input ? p1Input.value : "";
    const p2 = p2Input ? p2Input.value : "";

    if (!token) {
      App.toast("Missing password reset token. Please request a new link.", "error");
      return;
    }

    const pwdError = this.checkPasswordStrength(p1);
    if (pwdError) {
      App.toast(`⚠️ ${pwdError}`, "warning");
      return;
    }

    if (p1 !== p2) {
      App.toast("Password confirmation does not match", "warning");
      return;
    }

    try {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = "Updating Password...";
      }

      const res = await API.resetPassword(token, p1);
      clearInterval(this.resetTimerInterval);
      
      // Clean query param from URL
      window.history.replaceState({}, document.title, window.location.pathname);

      App.toast(res.message || "Password updated successfully!", "success");

      // Switch to login tab and prefill username
      this.switchAuthTab("login");
      const uInput = document.getElementById("login-username");
      if (uInput && res.username) {
        uInput.value = res.username;
        const pInput = document.getElementById("login-password");
        if (pInput) {
          pInput.value = "";
          pInput.focus();
        }
      }
    } catch (err) {
      App.toast(err.message || "Failed to reset password", "error");
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerText = "✓ Set New Password & Sign In";
      }
    }
  },

  async handleSendOTP(e) {
    if (e) e.preventDefault();
    const fullName = document.getElementById("reg-fullname").value.trim();
    const username = document.getElementById("reg-username").value.trim();
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-password").value;
    const role = document.getElementById("reg-role").value || "Admin";
    const btnSend = document.getElementById("btn-send-otp");

    if (!fullName || !username || !email || !password) {
      App.toast("Please fill in all required registration fields", "warning");
      return;
    }

    if (username.length < 3) {
      App.toast("Username must be at least 3 characters long", "warning");
      return;
    }

    if (!email.includes("@") || !email.includes(".")) {
      App.toast("Please enter a valid email address", "warning");
      return;
    }

    const pwdError = this.checkPasswordStrength(password);
    if (pwdError) {
      App.toast(`⚠️ ${pwdError}`, "warning");
      return;
    }

    try {
      btnSend.disabled = true;
      btnSend.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true" style="display:inline-block; width:14px; height:14px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:spin 0.6s linear infinite; vertical-align:middle; margin-right:6px;"></span>
        Generating Secure 6-Digit OTP...
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
        role: "Admin" // Everyone gets Admin access
      };

      App.toast(`✓ 6-Digit OTP sent to ${email}`, "success");

      // Transition to Step 2 OTP Form
      document.getElementById("register-step1-form").style.display = "none";
      const step2Form = document.getElementById("register-step2-form");
      step2Form.style.display = "block";
      
      const emailDisplay = document.getElementById("otp-target-email-display");
      if (emailDisplay) emailDisplay.innerText = email;

      // Clear & focus first digit box
      const boxes = document.querySelectorAll(".otp-digit-box");
      boxes.forEach(b => b.value = "");
      const hiddenInput = document.getElementById("reg-otp-code");
      if (hiddenInput) hiddenInput.value = "";
      if (boxes[0]) setTimeout(() => boxes[0].focus(), 100);

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

    const otpCode = this.syncOtpFromBoxes();
    const btnVerify = document.getElementById("btn-verify-otp-submit");

    if (!otpCode || otpCode.length < 6) {
      App.toast("Please enter the complete 6-digit OTP code", "warning");
      const boxes = document.querySelectorAll(".otp-digit-box");
      for (let i = 0; i < boxes.length; i++) {
        if (!boxes[i].value) {
          boxes[i].focus();
          break;
        }
      }
      return;
    }

    try {
      btnVerify.disabled = true;
      btnVerify.innerText = "Verifying & Activating Admin Account...";

      const payload = {
        ...this.pendingRegistration,
        otp: otpCode,
        role: "Admin"
      };

      const res = await API.registerWithOTP(payload);
      API.setAuth(res.access_token, res.role, res.username, res.full_name);

      clearInterval(this.otpTimerInterval);
      this.pendingRegistration = null;
      this.backToStep1();
      this.switchAuthTab("login");

      // Clear registration inputs
      ["reg-fullname", "reg-username", "reg-email", "reg-password"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
      });
      const boxes = document.querySelectorAll(".otp-digit-box");
      boxes.forEach(b => b.value = "");
      const hiddenOtp = document.getElementById("reg-otp-code");
      if (hiddenOtp) hiddenOtp.value = "";

      App.toast(`🎉 Admin Account activated! Welcome, ${res.full_name || res.username}!`, "success");

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
      
      const boxes = document.querySelectorAll(".otp-digit-box");
      boxes.forEach(b => b.value = "");
      this.syncOtpFromBoxes();
      if (boxes[0]) boxes[0].focus();

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
      submitBtn.innerText = "Sign In ➔";
    }
  },

  handleLogout() {
    API.clearAuth();
    this.pendingRegistration = null;
    this.backToStep1();
    this.switchAuthTab("login");

    // Clear login inputs
    const uInput = document.getElementById("login-username");
    const pInput = document.getElementById("login-password");
    if (uInput) uInput.value = "";
    if (pInput) pInput.value = "";

    // Clear registration inputs
    ["reg-fullname", "reg-username", "reg-email", "reg-password"].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    const boxes = document.querySelectorAll(".otp-digit-box");
    boxes.forEach(b => b.value = "");
    const hiddenOtp = document.getElementById("reg-otp-code");
    if (hiddenOtp) hiddenOtp.value = "";

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
    this.pendingRegistration = null;
    this.backToStep1();
    this.switchAuthTab("login");

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

    const role = user.role || "Admin";
    const displayName = user.full_name || user.username || "User";

    if (userNameEl) userNameEl.innerText = displayName;
    if (userRoleEl) {
      userRoleEl.innerText = role;
      userRoleEl.className = `user-role-badge ${role.toLowerCase()}`;
    }
    if (userAvatarEl) {
      userAvatarEl.innerText = displayName.charAt(0).toUpperCase();
    }

    // Role-based visibility toggles - Admin has full control
    const adminOnlyElements = document.querySelectorAll(".admin-only");
    adminOnlyElements.forEach(el => {
      el.style.display = "";
    });
  }
};

window.Auth = Auth;
