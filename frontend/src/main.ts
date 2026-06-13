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

type FocusProfile = {
  keywords: string[];
  areas: string[];
};

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "").trim().replace(/\/+$/, "");
const levelOptionsList = ["Junior", "Mid-Level", "Senior", "Executive"];
const defaultFocusAreas = [
  "Role-Specific Judgment",
  "Problem Solving",
  "Communication",
  "Collaboration",
  "Decision Making"
];

const focusProfiles: FocusProfile[] = [
  {
    keywords: ["customer success", "account manager", "renewals", "support"],
    areas: ["Customer Communication", "Retention Strategy", "Escalation Handling", "Value Realization", "Stakeholder Alignment"]
  },
  {
    keywords: ["sales", "business development", "account executive", "sdr", "bdr"],
    areas: ["Discovery", "Pipeline Management", "Objection Handling", "Commercial Judgment", "Closing Strategy"]
  },
  {
    keywords: ["product manager", "product owner", "program manager", "project manager"],
    areas: ["Prioritization", "Product Strategy", "Cross-Functional Delivery", "User Insight", "Metrics and Experimentation"]
  },
  {
    keywords: ["software engineer", "developer", "frontend", "backend", "full stack", "engineer"],
    areas: ["Coding and Debugging", "System Design", "Testing Discipline", "Technical Collaboration", "Tradeoff Reasoning"]
  },
  {
    keywords: ["marketing", "content", "growth", "brand", "demand generation"],
    areas: ["Campaign Strategy", "Audience Insight", "Positioning", "Performance Metrics", "Creative Judgment"]
  },
  {
    keywords: ["finance", "analyst", "accountant", "controller", "auditor"],
    areas: ["Financial Analysis", "Controls and Compliance", "Forecasting", "Reporting", "Business Partnership"]
  },
  {
    keywords: ["health", "medical", "doctor", "nurse", "clinician"],
    areas: ["Clinical Judgment", "Patient Communication", "Safety", "Ethics", "Interdisciplinary Care"]
  },
  {
    keywords: ["operations", "chief of staff", "supply chain", "program"],
    areas: ["Execution Planning", "Risk Management", "Process Improvement", "Stakeholder Coordination", "Operational Judgment"]
  }
];

let selectedLevel = "Mid-Level";
let focusAreas = getFocusAreas("Customer Success Manager");
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
    setStatus(data.id ? `Saved set #${data.id}.` : "Generated successfully.", "success");
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
