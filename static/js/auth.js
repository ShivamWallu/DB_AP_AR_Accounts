const Auth = {
  pendingRegistration: null,
  otpTimerInterval: null,

  init() {
    this.bindEvents();
    this.initOtpBoxes();
    this.init3DTilt();
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

  init3DTilt() {
    const card = document.getElementById("auth-main-card");
    if (!card) return;

    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      const rotateX = ((y - centerY) / centerY) * -6;
      const rotateY = ((x - centerX) / centerX) * 6;
      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-2px)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = `perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)`;
      card.style.transition = "transform 0.4s ease";
    });

    card.addEventListener("mouseenter", () => {
      card.style.transition = "none";
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
    const role = document.getElementById("reg-role").value || "Admin";
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
