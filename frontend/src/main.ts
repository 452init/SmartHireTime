import "./styles.css";

type Difficulty = "Easy" | "Medium" | "Hard";

type GeneratedQuestion = {
  question: string;
  difficulty: Difficulty;
};

type QuestionsResponse = {
  jobTitle: string;
  questions: Array<string | GeneratedQuestion>;
};

type ErrorResponse = {
  error: string;
};

type AuthUser = {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  profileImageUrl?: string | null;
};

type AuthSession = {
  token: string;
  user: AuthUser;
};

type AuthStartResponse = {
  status: "code_sent";
  email: string;
  maskedEmail: string;
  expiresInMinutes: number;
};

type AuthVerifyResponse = {
  token: string;
  user: AuthUser;
  tokenType: "Bearer";
  expiresInSeconds: number;
};

type AuthRefreshResponse = AuthVerifyResponse;

type FocusProfile = {
  keywords: string[];
  areas: string[];
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "").trim().replace(/\/+$/, "");
const googleClientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || "").trim();
const levels = ["Junior", "Mid-Level", "Senior", "Executive"];
const defaultFocusAreas = [
  "Role-Specific Judgment",
  "Problem Solving",
  "Communication",
  "Collaboration",
  "Cultural Fit"
];
const focusProfiles: FocusProfile[] = [
  {
    keywords: ["ciso", "chief information security officer", "security executive"],
    areas: [
      "Security Strategy and Governance",
      "Board and Executive Communication",
      "Risk Appetite and Prioritization",
      "Incident Leadership",
      "Compliance and Program Maturity"
    ]
  },
  {
    keywords: ["penetration tester", "pentester", "ethical hacker", "red team", "application security tester"],
    areas: [
      "Reconnaissance and Scoping",
      "Exploitation Methodology",
      "Web and Network Testing",
      "Privilege Escalation",
      "Reporting and Remediation Guidance"
    ]
  },
  {
    keywords: ["reverse engineer", "malware analyst", "malware reverse", "binary analysis"],
    areas: [
      "Static and Dynamic Analysis",
      "Assembly and Debugging",
      "Malware Behavior",
      "Tooling and Automation",
      "Indicators and Reporting"
    ]
  },
  {
    keywords: ["incident responder", "incident response", "incident respondent", "soc analyst", "security operations"],
    areas: [
      "Triage and Prioritization",
      "Detection and Investigation",
      "Containment and Eradication",
      "Evidence Handling",
      "Post-Incident Review"
    ]
  },
  {
    keywords: ["digital forensics", "forensics analyst", "dfir", "forensic analyst"],
    areas: [
      "Evidence Preservation",
      "Endpoint Forensics",
      "Timeline Reconstruction",
      "Chain of Custody",
      "Findings Communication"
    ]
  },
  {
    keywords: ["cloud security", "cloud security specialist", "cloud security engineer"],
    areas: [
      "Identity and Access Controls",
      "Cloud Threat Modeling",
      "Network and Data Protection",
      "Misconfiguration Detection",
      "Compliance in Cloud Environments"
    ]
  },
  {
    keywords: ["security engineer", "information security analyst", "cybersecurity analyst", "security analyst"],
    areas: [
      "Threat Modeling",
      "Security Controls",
      "Vulnerability Management",
      "Detection Engineering",
      "Secure Implementation"
    ]
  },
  {
    keywords: ["vulnerability analyst", "vulnerability management", "vulnerability researcher"],
    areas: [
      "Asset and Exposure Analysis",
      "CVSS and Risk Ranking",
      "Patch Prioritization",
      "Validation and Retesting",
      "Remediation Coordination"
    ]
  },
  {
    keywords: ["cybersecurity risk", "grc", "security risk analyst", "information risk"],
    areas: [
      "Risk Assessment",
      "Control Mapping",
      "Compliance Frameworks",
      "Third-Party Risk",
      "Risk Communication"
    ]
  },
  {
    keywords: ["ai security", "ml security", "model security", "llm security"],
    areas: [
      "Model Threat Modeling",
      "Prompt Injection and Abuse Cases",
      "Data Privacy and Leakage",
      "Adversarial Testing",
      "AI Governance"
    ]
  },
  {
    keywords: ["ai engineer", "artificial intelligence engineer", "machine learning engineer", "ml engineer"],
    areas: [
      "Model Development",
      "Data Pipeline Design",
      "Evaluation and Metrics",
      "Deployment and MLOps",
      "Responsible AI"
    ]
  },
  {
    keywords: ["cloud architect", "cloud architecture", "solutions architect", "solution architect"],
    areas: [
      "Architecture Tradeoffs",
      "Scalability and Reliability",
      "Cloud Cost Optimization",
      "Security and Identity Design",
      "Migration Strategy"
    ]
  },
  {
    keywords: ["devops", "site reliability", "sre", "platform engineer", "infrastructure engineer"],
    areas: [
      "CI/CD and Release Management",
      "Infrastructure as Code",
      "Observability and Incident Response",
      "Reliability Engineering",
      "Cloud Operations"
    ]
  },
  {
    keywords: ["system admin", "systems admin", "systems administrator", "sysadmin", "network administrator"],
    areas: [
      "Server Administration",
      "Identity and Access Management",
      "Backup and Disaster Recovery",
      "Troubleshooting and Monitoring",
      "Patch and Change Management"
    ]
  },
  {
    keywords: ["customer success", "client success", "account manager", "implementation manager"],
    areas: [
      "Customer Onboarding",
      "Product Adoption",
      "Retention and Churn Risk",
      "Expansion and Account Growth",
      "Executive Communication"
    ]
  },
  {
    keywords: ["product manager", "product owner", "growth product", "platform product"],
    areas: [
      "Product Sense",
      "Execution and Prioritization",
      "Metrics and Analytics",
      "Stakeholder Management",
      "Strategy and Tradeoffs"
    ]
  },
  {
    keywords: ["software engineer", "frontend", "backend", "full stack", "developer", "mobile engineer"],
    areas: [
      "Coding and Algorithms",
      "System Design",
      "Technical Deep Dive",
      "Debugging and Reliability",
      "Engineering Collaboration"
    ]
  },
  {
    keywords: ["data scientist", "data analyst", "analytics engineer", "business intelligence", "bi analyst"],
    areas: [
      "Statistical Reasoning",
      "Experiment Design",
      "Data Storytelling",
      "Modeling Approach",
      "Business Impact"
    ]
  },
  {
    keywords: ["designer", "ux", "ui", "product design", "researcher"],
    areas: [
      "User Empathy",
      "Portfolio Deep Dive",
      "Interaction Design",
      "Research and Validation",
      "Design Critique"
    ]
  },
  {
    keywords: ["sales", "account executive", "business development", "sdr", "bdr"],
    areas: [
      "Discovery",
      "Objection Handling",
      "Pipeline Management",
      "Negotiation",
      "Revenue Ownership"
    ]
  },
  {
    keywords: ["marketing", "growth", "brand", "content", "demand generation"],
    areas: [
      "Campaign Strategy",
      "Audience Insight",
      "Positioning",
      "Performance Metrics",
      "Creative Judgment"
    ]
  },
  {
    keywords: ["recruiter", "talent", "hr", "people operations", "human resources"],
    areas: [
      "Candidate Experience",
      "Sourcing Strategy",
      "Stakeholder Alignment",
      "Structured Interviewing",
      "People Judgment"
    ]
  },
  {
    keywords: ["operations", "program manager", "project manager", "chief of staff"],
    areas: [
      "Operational Planning",
      "Risk Management",
      "Cross-Functional Execution",
      "Process Improvement",
      "Decision Making"
    ]
  },
  {
    keywords: ["finance", "accountant", "controller", "financial analyst"],
    areas: [
      "Financial Modeling",
      "Controls and Accuracy",
      "Business Partnering",
      "Forecasting",
      "Risk and Compliance"
    ]
  },
  {
    keywords: ["nurse", "registered nurse", "rn", "nursing", "nurse practitioner"],
    areas: [
      "Patient Assessment",
      "Clinical Judgment",
      "Medication Safety",
      "Care Coordination",
      "Patient Communication"
    ]
  },
  {
    keywords: ["surgeon", "surgery", "surgical"],
    areas: [
      "Operative Decision Making",
      "Preoperative Assessment",
      "Complication Management",
      "Team Communication",
      "Patient Safety"
    ]
  },
  {
    keywords: ["doctor", "physician", "medical officer", "clinician"],
    areas: [
      "Diagnosis and Clinical Reasoning",
      "Patient Management",
      "Ethics and Consent",
      "Interdisciplinary Collaboration",
      "Patient Communication"
    ]
  },
  {
    keywords: ["pharmacist", "pharmacy"],
    areas: [
      "Medication Therapy Management",
      "Drug Safety",
      "Patient Counseling",
      "Regulatory Compliance",
      "Clinical Collaboration"
    ]
  },
  {
    keywords: ["dentist", "dental"],
    areas: [
      "Clinical Diagnosis",
      "Treatment Planning",
      "Patient Comfort",
      "Infection Control",
      "Practice Communication"
    ]
  },
  {
    keywords: ["lawyer", "attorney", "legal counsel", "paralegal"],
    areas: [
      "Legal Analysis",
      "Client Advisory",
      "Negotiation",
      "Risk and Compliance",
      "Writing and Documentation"
    ]
  },
  {
    keywords: ["teacher", "educator", "lecturer", "professor", "instructor"],
    areas: [
      "Instructional Planning",
      "Student Engagement",
      "Assessment and Feedback",
      "Classroom Management",
      "Inclusive Teaching"
    ]
  },
  {
    keywords: ["consultant", "management consultant", "strategy consultant"],
    areas: [
      "Problem Structuring",
      "Client Communication",
      "Analytical Thinking",
      "Recommendation Quality",
      "Change Management"
    ]
  },
  {
    keywords: ["business analyst", "systems analyst", "process analyst"],
    areas: [
      "Requirements Gathering",
      "Process Mapping",
      "Stakeholder Communication",
      "Data-Backed Recommendations",
      "Solution Validation"
    ]
  },
  {
    keywords: ["architect", "civil engineer", "mechanical engineer", "electrical engineer"],
    areas: [
      "Technical Design",
      "Safety and Standards",
      "Project Coordination",
      "Design Tradeoffs",
      "Quality Assurance"
    ]
  },
  {
    keywords: ["research scientist", "scientist", "researcher"],
    areas: [
      "Research Design",
      "Experimental Rigor",
      "Data Interpretation",
      "Publication and Communication",
      "Ethics and Reproducibility"
    ]
  }
];

// ─── State ────────────────────────────────────────────────────────────────────

let selectedLevel = "Mid-Level";
let focusAreas = getFocusAreas("Customer Success Manager");
let selectedCategory = focusAreas[0];

let authSession: AuthSession | null = null;
let pendingEmail = "";
let pendingGenerate = false;        // tracks whether user tried to generate before auth
let isRegistering = false;
let isAuthLoading = false;
let postAuthView: "app" | "dashboard" = "app";
let selectedPhotoFile: File | null = null;

// ─── DOM References ───────────────────────────────────────────────────────────

const authTrigger = getElement<HTMLButtonElement>("#auth-trigger");
const authTriggerLabel = getElement<HTMLSpanElement>("#auth-trigger-label");
const logoutButton = getElement<HTMLButtonElement>("#logout-button");

const authPanel = getElement<HTMLElement>("#auth-panel");
const authSessionPanel = getElement<HTMLElement>("#auth-session");
const authSessionEmail = getElement<HTMLParagraphElement>("#auth-session-email");
const authStartPanel = getElement<HTMLElement>("#auth-start");
const authTitle = getElement<HTMLHeadingElement>("#auth-title");
const authForm = getElement<HTMLFormElement>("#auth-form");
const authNameFields = getElement<HTMLElement>("#auth-name-fields");
const firstNameInput = getElement<HTMLInputElement>("#first-name");
const lastNameInput = getElement<HTMLInputElement>("#last-name");
const authEmailInput = getElement<HTMLInputElement>("#auth-email");
const authPasswordInput = getElement<HTMLInputElement>("#auth-password");
const authSubmitButton = getElement<HTMLButtonElement>("#auth-submit");
const authModeToggle = getElement<HTMLButtonElement>("#auth-mode-toggle");
const authStatus = getElement<HTMLDivElement>("#auth-status");
const googleButton = getElement<HTMLDivElement>("#google-button");

const codePanel = getElement<HTMLElement>("#code-panel");
const codeForm = getElement<HTMLFormElement>("#code-form");
const codeInput = getElement<HTMLInputElement>("#auth-code");
const codeSubmitButton = getElement<HTMLButtonElement>("#code-submit");
const codeEmail = getElement<HTMLSpanElement>("#code-email");
const codeStatus = getElement<HTMLDivElement>("#code-status");
const codeResendButton = getElement<HTMLButtonElement>("#code-resend");
const codeBackButton = getElement<HTMLButtonElement>("#code-back");

const topbar = getElement<HTMLElement>(".topbar");
const dashboardPanel = getElement<HTMLElement>("#dashboard-panel");
const dashboardCloseButton = getElement<HTMLButtonElement>("#dashboard-close");
const profilePhotoInput = getElement<HTMLInputElement>("#profile-photo-input");
const profilePhotoUploadButton = getElement<HTMLButtonElement>("#profile-photo-upload");
const profilePhotoPreview = getElement<HTMLImageElement>("#profile-photo-preview");
const profilePhotoPlaceholder = getElement<HTMLElement>("#profile-photo-placeholder");
const profilePhotoStatus = getElement<HTMLDivElement>("#profile-photo-status");
const passwordForm = getElement<HTMLFormElement>("#password-form");
const currentPasswordInput = getElement<HTMLInputElement>("#current-password");
const newPasswordInput = getElement<HTMLInputElement>("#new-password");
const confirmPasswordInput = getElement<HTMLInputElement>("#confirm-password");
const passwordStatus = getElement<HTMLDivElement>("#password-status");
const deleteAccountButton = getElement<HTMLButtonElement>("#delete-account-button");
const deleteStatus = getElement<HTMLDivElement>("#delete-status");
const appPanel = getElement<HTMLElement>("#app-panel");
const form = getElement<HTMLFormElement>("#question-form");
const input = getElement<HTMLInputElement>("#job-title");
const submitButton = getElement<HTMLButtonElement>("#generate-button");
const statusMessage = getElement<HTMLDivElement>("#status");
const loadingPanel = getElement<HTMLElement>("#loading-panel");
const resultsPanel = getElement<HTMLElement>("#results-panel");
const questionsContainer = getElement<HTMLDivElement>("#questions");
const preparedCount = getElement<HTMLSpanElement>("#prepared-count");
const levelOptions = getElement<HTMLDivElement>("#level-options");
const categoryOptions = getElement<HTMLDivElement>("#category-options");

// ─── Initialise ───────────────────────────────────────────────────────────────

refreshOptionGroups();
updateGenerateButton();
setAuthMode(false);

// ─── Event Listeners ──────────────────────────────────────────────────────────

// When logged in, the auth-trigger opens the dashboard.
// When logged out, it opens the sign-in panel.
authTrigger.addEventListener("click", () => {
  if (authSession) {
    openDashboard();
  } else {
    postAuthView = "app";
    openAuthPanel();
  }
});

authModeToggle.addEventListener("click", () => {
  setAuthMode(!isRegistering);
});

logoutButton.addEventListener("click", () => {
  void handleLogout();
});

dashboardCloseButton.addEventListener("click", () => {
  closeDashboard();
});

profilePhotoInput.addEventListener("change", () => {
  const file = profilePhotoInput.files?.[0] || null;
  selectedPhotoFile = file;
  setProfilePhotoPreview(file);
});

profilePhotoUploadButton.addEventListener("click", () => {
  void handlePhotoUpload();
});

passwordForm.addEventListener("submit", (event) => {
  event.preventDefault();
  void handlePasswordChange();
});

deleteAccountButton.addEventListener("click", () => {
  void handleDeleteAccount();
});

authForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setAuthStatus("", "idle");

  const firstName = firstNameInput.value.trim();
  const lastName = lastNameInput.value.trim();
  const email = authEmailInput.value.trim();
  const password = authPasswordInput.value;

  if (!email || !password || (isRegistering && (!firstName || !lastName))) {
    setAuthStatus(
      isRegistering ? "Complete all fields to continue." : "Enter your email and password.",
      "error"
    );
    return;
  }

  setAuthLoading(true);

  try {
    const response = await fetch(getApiUrl("/api/auth/start"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        mode: isRegistering ? "signup" : "signin",
        firstName,
        lastName,
        email,
        password
      })
    });

    const data = (await response.json()) as AuthStartResponse | ErrorResponse;

    if (!response.ok || "error" in data) {
      // No account found during sign-in → switch to sign-up form automatically
      if (response.status === 404 && !isRegistering) {
        setAuthMode(true);
      }
      // Account already exists during sign-up → switch to sign-in form automatically
      if (response.status === 409 && isRegistering) {
        setAuthMode(false);
      }
      throw new Error("error" in data ? data.error : "Unable to start sign-in.");
    }

    pendingEmail = data.email;
    authPasswordInput.value = "";
    showCodePanel(data.maskedEmail);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to start sign-in.";
    setAuthStatus(message, "error");
  } finally {
    setAuthLoading(false);
  }
});

codeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setCodeStatus("", "idle");

  const email = pendingEmail.trim();
  const code = codeInput.value.trim();

  if (!email) {
    setCodeStatus("Missing email. Please start again.", "error");
    openAuthPanel();
    return;
  }

  if (!/^[0-9]{6}$/.test(code)) {
    setCodeStatus("Enter the 6-digit code.", "error");
    return;
  }

  setCodeLoading(true);

  try {
    const response = await fetch(getApiUrl("/api/auth/verify"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, code })
    });

    const data = (await response.json()) as AuthVerifyResponse | ErrorResponse;
    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Unable to verify code.");
    }

    // Apply session — this internally calls closeAuthPanel() and shows the right panel.
    applyAuthSession({ token: data.token, user: data.user });
    codeInput.value = "";

    // If the user was trying to generate before auth, resume that now.
    if (pendingGenerate) {
      pendingGenerate = false;
      form.requestSubmit();
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to verify code.";
    setCodeStatus(message, "error");
  } finally {
    setCodeLoading(false);
  }
});

codeResendButton.addEventListener("click", async () => {
  if (!pendingEmail) {
    openAuthPanel();
    return;
  }

  setCodeStatus("Sending a new code...", "idle");

  try {
    const response = await fetch(getApiUrl("/api/auth/request-code"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email: pendingEmail })
    });

    const data = (await response.json()) as AuthStartResponse | ErrorResponse;
    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Unable to resend code.");
    }

    showCodePanel(data.maskedEmail);
    setCodeStatus("Code sent. Check your inbox.", "success");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to resend code.";
    setCodeStatus(message, "error");
  }
});

codeBackButton.addEventListener("click", () => {
  pendingEmail = "";
  codeInput.value = "";
  openAuthPanel();
});

window.addEventListener("load", () => {
  initGoogleButton();
});

void initializeAuth();

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    form.requestSubmit();
  }
});

input.addEventListener("input", () => {
  focusAreas = getFocusAreas(input.value);
  if (!focusAreas.includes(selectedCategory)) {
    selectedCategory = focusAreas[0];
  }
  refreshOptionGroups();
  updateGenerateButton();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const role = input.value.trim();
  if (!role) {
    setStatus("Enter a position to begin.", "error");
    hideResults();
    return;
  }

  const hasSession = await ensureAuthSession();
  if (!hasSession) {
    // Intercept and remember the intent — resume after auth.
    pendingGenerate = true;
    postAuthView = "app";
    setStatus("Sign in to generate questions.", "error");
    openAuthPanel("Sign in to generate questions.");
    return;
  }

  setLoading(true);
  setStatus("", "idle");
  hideResults();

  try {
    const response = await fetchWithAuth(getApiUrl("/api/interview-questions"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jobTitle: role,
        level: selectedLevel,
        category: selectedCategory,
        focusAreas,
        questionCount: 8
      })
    });

    const data = (await response.json()) as QuestionsResponse | ErrorResponse;

    if (response.status === 401) {
      setStatus("Session expired. Please sign in again.", "error");
      openAuthPanel("Session expired. Please sign in again.");
      return;
    }

    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Request failed.");
    }

    const questions = normalizeQuestions(data.questions);
    renderQuestions(questions);
    setStatus("", "success");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Request failed.";
    setStatus(message, "error");
    hideResults();
  } finally {
    setLoading(false);
  }
});

// ─── Option Groups ────────────────────────────────────────────────────────────

function refreshOptionGroups() {
  renderOptions(levelOptions, levels, selectedLevel, (level) => {
    selectedLevel = level;
    refreshOptionGroups();
  });
  renderOptions(categoryOptions, focusAreas, selectedCategory, (category) => {
    selectedCategory = category;
    refreshOptionGroups();
  });
}

function getFocusAreas(role: string) {
  const normalizedRole = normalizeRole(role);
  const matchingProfile = focusProfiles.find((profile) =>
    profile.keywords.some((keyword) => normalizedRole.includes(normalizeRole(keyword)))
  );
  return matchingProfile?.areas || defaultFocusAreas;
}

function normalizeRole(role: string) {
  return role
    .toLowerCase()
    .replace(/[^a-z0-9+#.\s-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function renderOptions(
  container: HTMLDivElement,
  options: string[],
  activeOption: string,
  onSelect: (value: string) => void
) {
  container.innerHTML = "";
  options.forEach((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = option === activeOption ? "pill pill-active" : "pill pill-inactive";
    button.textContent = option;
    button.addEventListener("click", () => onSelect(option));
    container.appendChild(button);
  });
}

// ─── Questions ────────────────────────────────────────────────────────────────

function renderQuestions(questions: GeneratedQuestion[]) {
  questionsContainer.innerHTML = "";
  preparedCount.textContent = `${questions.length} prepared`;

  questions.forEach((item, index) => {
    const card = document.createElement("article");
    const body = document.createElement("div");
    const questionNumber = document.createElement("p");
    const questionText = document.createElement("p");
    const difficulty = document.createElement("span");

    card.className = "q-card";
    card.style.animationDelay = `${index * 0.08}s`;
    body.className = "q-body";
    questionNumber.className = "q-number";
    questionText.className = "q-text";
    difficulty.className = `difficulty difficulty-${item.difficulty.toLowerCase()}`;

    questionNumber.textContent = `Question ${String(index + 1).padStart(2, "0")}`;
    questionText.textContent = item.question;
    difficulty.textContent = item.difficulty;

    body.append(questionNumber, questionText);
    card.append(body, difficulty);
    questionsContainer.appendChild(card);
  });

  resultsPanel.hidden = false;
}

function normalizeQuestions(questions: Array<string | GeneratedQuestion>) {
  const fallbackDifficulties: Difficulty[] = ["Easy", "Medium", "Hard"];
  return questions.map((item, index) => {
    if (typeof item === "string") {
      return {
        question: item,
        difficulty: fallbackDifficulties[index % fallbackDifficulties.length]
      };
    }
    return {
      question: item.question,
      difficulty: item.difficulty || fallbackDifficulties[index % fallbackDifficulties.length]
    };
  });
}

function hideResults() {
  questionsContainer.innerHTML = "";
  preparedCount.textContent = "0 prepared";
  resultsPanel.hidden = true;
}

// ─── Status / Loading ─────────────────────────────────────────────────────────

function setStatus(message: string, type: "idle" | "success" | "error") {
  statusMessage.textContent = message;
  statusMessage.dataset.type = type;
}

function setLoading(isLoading: boolean) {
  loadingPanel.hidden = !isLoading;
  submitButton.textContent = isLoading ? "Generating..." : "Generate Questions";
  updateGenerateButton(isLoading);
}

function updateGenerateButton(isLoading = false) {
  submitButton.disabled = isLoading || !input.value.trim();
}

function setPanelStatus(
  element: HTMLDivElement,
  message: string,
  type: "idle" | "success" | "error"
) {
  element.textContent = message;
  element.dataset.type = type;
}

// ─── Utilities ────────────────────────────────────────────────────────────────

function getElement<T extends HTMLElement>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) {
    throw new Error(`Missing page element: ${selector}`);
  }
  return element;
}

function getApiUrl(path: string) {
  return apiBaseUrl ? `${apiBaseUrl}${path}` : path;
}

// ─── Auth Session ─────────────────────────────────────────────────────────────

async function initializeAuth() {
  updateAuthTrigger();
  const refreshed = await refreshSession();
  if (!refreshed) {
    clearAuthSession();
    closeAuthPanel();
  }
}

async function ensureAuthSession() {
  if (authSession) return true;
  return refreshSession();
}

async function refreshSession() {
  try {
    const response = await fetch(getApiUrl("/api/auth/refresh"), {
      method: "POST",
      credentials: "include"
    });
    if (!response.ok) return false;
    const data = (await response.json()) as AuthRefreshResponse;
    applyAuthSession({ token: data.token, user: data.user });
    return true;
  } catch {
    return false;
  }
}

async function fetchWithAuth(input: RequestInfo | URL, init: RequestInit) {
  const headers = new Headers(init.headers ?? {});
  if (authSession?.token) {
    headers.set("Authorization", `Bearer ${authSession.token}`);
  }

  const response = await fetch(input, { ...init, headers });
  if (response.status !== 401) return response;

  const refreshed = await refreshSession();
  if (!refreshed || !authSession?.token) return response;

  const retryHeaders = new Headers(init.headers ?? {});
  retryHeaders.set("Authorization", `Bearer ${authSession.token}`);
  return fetch(input, { ...init, headers: retryHeaders });
}

function applyAuthSession(session: AuthSession) {
  authSession = session;
  pendingEmail = session.user.email;
  authSessionEmail.textContent = `Signed in as ${session.user.email}`;
  authSessionPanel.hidden = true;
  updateAuthTrigger();
  updateDashboardView();
  closeAuthPanel();
}

function clearAuthSession() {
  authSession = null;
  pendingEmail = "";
  pendingGenerate = false;
  authSessionEmail.textContent = "Signed in.";
  authSessionPanel.hidden = true;
  dashboardPanel.hidden = true;
  updateAuthTrigger();
}

function updateAuthTrigger() {
  if (authSession) {
    // Show the user's first name on the trigger; clicking it opens the dashboard.
    authTriggerLabel.textContent = authSession.user.firstName || "Account";
    logoutButton.hidden = false;
  } else {
    authTriggerLabel.textContent = "Sign in";
    logoutButton.hidden = true;
  }
}

// ─── Auth Panel (overlay modal) ───────────────────────────────────────────────

function openAuthPanel(message?: string) {
  authPanel.hidden = false;
  document.body.classList.add("auth-open");
  topbar.hidden = true;
  dashboardPanel.hidden = true;
  appPanel.hidden = true;
  window.location.hash = "auth-panel";
  authPanel.scrollIntoView({ behavior: "smooth", block: "start" });

  if (authSession) {
    authSessionPanel.hidden = false;
    authStartPanel.hidden = true;
    codePanel.hidden = true;
    return;
  }

  setAuthMode(false);
  authSessionPanel.hidden = true;
  authStartPanel.hidden = false;
  codePanel.hidden = true;
  setAuthStatus(message || "", message ? "error" : "idle");
  firstNameInput.focus();
}

function showCodePanel(maskedEmail: string) {
  authPanel.hidden = false;
  document.body.classList.add("auth-open");
  topbar.hidden = true;
  dashboardPanel.hidden = true;
  appPanel.hidden = true;
  authSessionPanel.hidden = true;
  authStartPanel.hidden = true;
  codePanel.hidden = false;
  codeEmail.textContent = maskedEmail || pendingEmail;
  setCodeStatus("", "idle");
  codeInput.focus();
}

function closeAuthPanel() {
  authPanel.hidden = true;
  document.body.classList.remove("auth-open");
  topbar.hidden = false;

  if (postAuthView === "dashboard") {
    dashboardPanel.hidden = false;
    appPanel.hidden = true;
  } else {
    dashboardPanel.hidden = true;
    appPanel.hidden = false;
  }

  authStartPanel.hidden = false;
  codePanel.hidden = true;
  setAuthStatus("", "idle");
  setCodeStatus("", "idle");
  postAuthView = "app";
}

function setAuthStatus(message: string, type: "idle" | "success" | "error") {
  authStatus.textContent = message;
  authStatus.dataset.type = type;
}

function setCodeStatus(message: string, type: "idle" | "success" | "error") {
  codeStatus.textContent = message;
  codeStatus.dataset.type = type;
}

function setAuthLoading(isLoading: boolean) {
  isAuthLoading = isLoading;
  authSubmitButton.disabled = isLoading;
  authSubmitButton.textContent = isLoading ? "Continuing..." : getAuthSubmitText();
}

function setCodeLoading(isLoading: boolean) {
  codeSubmitButton.disabled = isLoading;
  codeSubmitButton.textContent = isLoading ? "Verifying..." : "Verify";
}

function setAuthMode(registering: boolean) {
  isRegistering = registering;
  authNameFields.hidden = !registering;
  firstNameInput.required = registering;
  lastNameInput.required = registering;
  authTitle.textContent = registering ? "Create your account" : "Sign in to continue";
  authModeToggle.textContent = registering
    ? "Already have an account? Sign in"
    : "New here? Create account";
  if (!isAuthLoading) {
    authSubmitButton.textContent = getAuthSubmitText();
  }
  if (!registering) {
    firstNameInput.value = "";
    lastNameInput.value = "";
  }
}

function getAuthSubmitText() {
  return isRegistering ? "Create account" : "Sign in";
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

function openDashboard() {
  if (!authSession) {
    postAuthView = "dashboard";
    openAuthPanel("Sign in to access your dashboard.");
    return;
  }

  authPanel.hidden = true;
  document.body.classList.remove("auth-open");
  topbar.hidden = false;
  dashboardPanel.hidden = false;
  appPanel.hidden = true;
  updateDashboardView();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function closeDashboard() {
  dashboardPanel.hidden = true;
  appPanel.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateDashboardView() {
  if (!authSession) return;
  const imageUrl = authSession.user.profileImageUrl || "";
  if (imageUrl) {
    profilePhotoPreview.src = imageUrl;
    profilePhotoPreview.hidden = false;
    profilePhotoPlaceholder.hidden = true;
  } else {
    profilePhotoPreview.hidden = true;
    profilePhotoPlaceholder.hidden = false;
  }
}

function setProfilePhotoPreview(file: File | null) {
  const existingUrl = profilePhotoPreview.dataset.previewUrl;
  if (existingUrl) {
    URL.revokeObjectURL(existingUrl);
    delete profilePhotoPreview.dataset.previewUrl;
  }

  if (file) {
    const url = URL.createObjectURL(file);
    profilePhotoPreview.src = url;
    profilePhotoPreview.dataset.previewUrl = url;
    profilePhotoPreview.hidden = false;
    profilePhotoPlaceholder.hidden = true;
    return;
  }

  updateDashboardView();
}

async function handlePhotoUpload() {
  if (!authSession) {
    postAuthView = "dashboard";
    openAuthPanel("Sign in to update your profile photo.");
    return;
  }

  if (!selectedPhotoFile) {
    setPanelStatus(profilePhotoStatus, "Choose a photo to upload.", "error");
    return;
  }

  setPanelStatus(profilePhotoStatus, "Uploading...", "idle");

  try {
    const formData = new FormData();
    formData.append("file", selectedPhotoFile);

    const response = await fetchWithAuth(getApiUrl("/api/account/photo"), {
      method: "POST",
      body: formData
    });

    const data = (await response.json()) as { user: AuthUser } | ErrorResponse;
    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Unable to update photo.");
    }

    authSession.user = data.user;
    selectedPhotoFile = null;
    updateDashboardView();
    setPanelStatus(profilePhotoStatus, "Photo updated.", "success");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to update photo.";
    setPanelStatus(profilePhotoStatus, message, "error");
  }
}

async function handlePasswordChange() {
  if (!authSession) {
    postAuthView = "dashboard";
    openAuthPanel("Sign in to update your password.");
    return;
  }

  const currentPassword = currentPasswordInput.value;
  const newPassword = newPasswordInput.value;
  const confirmPassword = confirmPasswordInput.value;

  if (!currentPassword || !newPassword || !confirmPassword) {
    setPanelStatus(passwordStatus, "Complete all password fields.", "error");
    return;
  }
  if (newPassword.length < 8) {
    setPanelStatus(passwordStatus, "New password must be at least 8 characters.", "error");
    return;
  }
  if (newPassword !== confirmPassword) {
    setPanelStatus(passwordStatus, "Passwords do not match.", "error");
    return;
  }

  setPanelStatus(passwordStatus, "Updating password...", "idle");

  try {
    const response = await fetchWithAuth(getApiUrl("/api/account/password"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ currentPassword, newPassword })
    });

    const data = (await response.json()) as { status?: string } | ErrorResponse;
    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Unable to update password.");
    }

    currentPasswordInput.value = "";
    newPasswordInput.value = "";
    confirmPasswordInput.value = "";
    setPanelStatus(passwordStatus, "Password updated.", "success");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to update password.";
    setPanelStatus(passwordStatus, message, "error");
  }
}

async function handleDeleteAccount() {
  if (!authSession) {
    postAuthView = "dashboard";
    openAuthPanel("Sign in to delete your account.");
    return;
  }

  if (!window.confirm("Delete your account? This cannot be undone.")) return;

  setPanelStatus(deleteStatus, "Deleting account...", "idle");

  try {
    const response = await fetchWithAuth(getApiUrl("/api/account/delete"), {
      method: "POST",
      credentials: "include"
    });

    const data = (await response.json()) as { status?: string } | ErrorResponse;
    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Unable to delete account.");
    }

    setPanelStatus(deleteStatus, "Account deleted.", "success");
    clearAuthSession();
    dashboardPanel.hidden = true;
    appPanel.hidden = false;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to delete account.";
    setPanelStatus(deleteStatus, message, "error");
  }
}

// ─── Logout ───────────────────────────────────────────────────────────────────

async function handleLogout() {
  try {
    await fetch(getApiUrl("/api/auth/logout"), {
      method: "POST",
      credentials: "include"
    });
  } catch {
    // Ignore logout errors.
  } finally {
    clearAuthSession();
    dashboardPanel.hidden = true;
    appPanel.hidden = false;
    hideResults();
    setStatus("", "idle");
    closeAuthPanel();
  }
}

// ─── Google Sign-in ───────────────────────────────────────────────────────────

function initGoogleButton() {
  if (!googleClientId) {
    googleButton.hidden = true;
    return;
  }

  const googleApi = (window as Window & { google?: any }).google;
  if (!googleApi?.accounts?.id) return;

  googleApi.accounts.id.initialize({
    client_id: googleClientId,
    callback: handleGoogleCredential
  });

  googleApi.accounts.id.renderButton(googleButton, {
    theme: "outline",
    size: "large",
    shape: "pill",
    text: "continue_with"
  });
}

async function handleGoogleCredential(response: { credential: string }) {
  setAuthStatus("Checking Google account...", "idle");
  setAuthLoading(true);
  openAuthPanel();

  try {
    const apiResponse = await fetch(getApiUrl("/api/auth/google"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ credential: response.credential })
    });

    const data = (await apiResponse.json()) as AuthStartResponse | ErrorResponse;
    if (!apiResponse.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Google sign-in failed.");
    }

    pendingEmail = data.email;
    showCodePanel(data.maskedEmail);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Google sign-in failed.";
    setAuthStatus(message, "error");
  } finally {
    setAuthLoading(false);
  }
}