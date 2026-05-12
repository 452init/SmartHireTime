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

type FocusProfile = {
  keywords: string[];
  areas: string[];
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "").trim().replace(/\/+$/, "");
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

let selectedLevel = "Mid-Level";
let focusAreas = getFocusAreas("Customer Success Manager");
let selectedCategory = focusAreas[0];

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

refreshOptionGroups();
updateGenerateButton();

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

  setLoading(true);
  setStatus("", "idle");
  hideResults();

  try {
    const response = await fetch(getApiUrl("/api/interview-questions"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        jobTitle: role,
        level: selectedLevel,
        category: selectedCategory,
        focusAreas,
        questionCount: 8
      })
    });

    const data = (await response.json()) as QuestionsResponse | ErrorResponse;

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
