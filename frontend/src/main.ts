import "./styles.css";

type Difficulty = "Easy" | "Medium" | "Hard";

type GeneratedQuestion = {
  question: string;
  difficulty: Difficulty;
};

type QuestionsResponse = {
  id?: number;
  jobTitle: string;
  questions: Array<string | GeneratedQuestion>;
};

type ErrorResponse = {
  error: string;
};

type ProfessionProfile = {
  keywords: string[];
  seniorityLevels: string[];
  areas: string[];
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "").trim().replace(/\/+$/, "");

const defaultProfile: ProfessionProfile = {
  keywords: [],
  seniorityLevels: ["Entry-Level", "Associate", "Mid-Level", "Senior", "Lead", "Manager"],
  areas: [
    "Role-Specific Skills",
    "Communication and Collaboration",
    "Problem Solving",
    "Professional Judgment",
    "Career Motivation"
  ]
};

const professionProfiles: ProfessionProfile[] = [
  {
    keywords: ["ciso", "chief information security officer", "security executive"],
    seniorityLevels: ["Director", "Senior Director", "VP Security", "CISO", "Chief Security Officer", "Board Advisor"],
    areas: [
      "Security Strategy and Governance",
      "Board and Executive Communication",
      "Risk Appetite and Prioritization",
      "Incident Leadership",
      "Compliance and Program Maturity"
    ]
  },
  {
    keywords: ["software engineer", "developer", "frontend", "backend", "full stack", "programmer"],
    seniorityLevels: ["Intern", "Junior Engineer", "Mid-Level Engineer", "Senior Engineer", "Staff Engineer", "Principal Engineer"],
    areas: [
      "Coding and Debugging",
      "System Design",
      "Data Structures and Algorithms",
      "Code Quality and Testing",
      "Technical Collaboration"
    ]
  },
  {
    keywords: ["doctor", "physician", "surgeon", "clinician", "medical officer", "nurse", "nursing"],
    seniorityLevels: ["Student", "Resident", "Fellow", "Attending", "Consultant", "Medical Director"],
    areas: [
      "Clinical Judgment",
      "Patient Communication",
      "Ethics and Safety",
      "Diagnosis and Treatment Planning",
      "Interdisciplinary Care"
    ]
  },
  {
    keywords: ["teacher", "educator", "lecturer", "professor", "instructor", "tutor"],
    seniorityLevels: ["Trainee Teacher", "Classroom Teacher", "Senior Teacher", "Department Lead", "Principal", "Academic Director"],
    areas: [
      "Lesson Planning",
      "Classroom Management",
      "Student Assessment",
      "Inclusive Teaching",
      "Parent and Stakeholder Communication"
    ]
  },
  {
    keywords: ["lawyer", "attorney", "legal counsel", "advocate", "solicitor", "paralegal"],
    seniorityLevels: ["Paralegal", "Junior Associate", "Associate", "Senior Associate", "Counsel", "Partner"],
    areas: [
      "Legal Research and Analysis",
      "Client Advisory",
      "Negotiation and Drafting",
      "Ethics and Confidentiality",
      "Case Strategy"
    ]
  },
  {
    keywords: ["accountant", "finance", "financial analyst", "auditor", "controller", "bookkeeper"],
    seniorityLevels: ["Junior Analyst", "Analyst", "Senior Analyst", "Manager", "Controller", "Finance Director"],
    areas: [
      "Financial Reporting",
      "Budgeting and Forecasting",
      "Controls and Compliance",
      "Data Analysis",
      "Stakeholder Reporting"
    ]
  },
  {
    keywords: ["sales", "account executive", "business development", "customer success", "account manager"],
    seniorityLevels: ["Sales Development Rep", "Account Executive", "Senior Account Executive", "Account Manager", "Sales Manager", "Revenue Leader"],
    areas: [
      "Discovery and Qualification",
      "Pipeline Management",
      "Objection Handling",
      "Customer Relationship Management",
      "Commercial Negotiation"
    ]
  },
  {
    keywords: ["product manager", "product owner", "program manager", "project manager", "scrum master"],
    seniorityLevels: ["Associate PM", "Product Manager", "Senior Product Manager", "Group Product Manager", "Director of Product", "VP Product"],
    areas: [
      "Product Strategy",
      "User Research",
      "Prioritization",
      "Cross-Functional Delivery",
      "Metrics and Experimentation"
    ]
  },
  {
    keywords: ["designer", "ux", "ui", "product designer", "graphic designer", "creative director"],
    seniorityLevels: ["Junior Designer", "Designer", "Senior Designer", "Lead Designer", "Design Manager", "Creative Director"],
    areas: [
      "User-Centered Design",
      "Visual Craft",
      "Prototyping and Testing",
      "Design Systems",
      "Stakeholder Critique"
    ]
  },
  {
    keywords: ["hr", "human resources", "recruiter", "talent acquisition", "people operations"],
    seniorityLevels: ["HR Assistant", "Recruiter", "HR Generalist", "Senior HR Partner", "People Manager", "CHRO"],
    areas: [
      "Talent Acquisition",
      "Employee Relations",
      "Policy and Compliance",
      "Performance Management",
      "Culture and Engagement"
    ]
  }
];

let activeProfile = getProfessionProfile("Customer Success Manager");
let levelOptionsList = activeProfile.seniorityLevels;
let selectedLevel = levelOptionsList[0];
let focusAreas = activeProfile.areas;
let selectedCategory = focusAreas[0];

const input = getElement<HTMLInputElement>("#job-title");
const form = getElement<HTMLFormElement>("#question-form");
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

input.addEventListener("input", () => {
  activeProfile = getProfessionProfile(input.value);
  levelOptionsList = activeProfile.seniorityLevels;
  focusAreas = activeProfile.areas;
  if (!levelOptionsList.includes(selectedLevel)) {
    selectedLevel = levelOptionsList[0];
  }
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
  setStatus("Generating interview questions...", "idle");
  hideResults();

  try {
    const response = await fetch(getApiUrl("/api/interview-questions"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jobTitle: role,
        level: selectedLevel,
        category: selectedCategory,
        focusAreas,
        questionCount: 3
      })
    });

    const data = (await response.json()) as QuestionsResponse | ErrorResponse;

    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Request failed.");
    }

    const questions = normalizeQuestions(data.questions);
    renderQuestions(questions);
    setStatus("Success", "success");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Request failed.";
    setStatus(message, "error");
    hideResults();
  } finally {
    setLoading(false);
  }
});

function refreshOptionGroups() {
  renderOptions(levelOptions, levelOptionsList, selectedLevel, (level) => {
    selectedLevel = level;
    refreshOptionGroups();
  });

  renderOptions(categoryOptions, focusAreas, selectedCategory, (category) => {
    selectedCategory = category;
    refreshOptionGroups();
  });
}

function getProfessionProfile(role: string) {
  const normalizedRole = normalizeRole(role);
  const matchingProfile = professionProfiles.find((profile) =>
    profile.keywords.some((keyword) => normalizedRole.includes(normalizeRole(keyword)))
  );

  return matchingProfile || defaultProfile;
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
