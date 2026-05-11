import "./styles.css";

type QuestionsResponse = {
  jobTitle: string;
  questions: string[];
};

type ErrorResponse = {
  error: string;
};

const form = getElement<HTMLFormElement>("#question-form");
const input = getElement<HTMLInputElement>("#job-title");
const statusMessage = getElement<HTMLDivElement>("#status");
const questionsList = getElement<HTMLOListElement>("#questions");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const jobTitle = input.value.trim();

  if (!jobTitle) {
    setStatus("Enter a job title to begin.", "error");
    renderQuestions([]);
    return;
  }

  setStatus("Generating role-specific questions...", "loading");
  renderQuestions([]);

  try {
    const response = await fetch("/api/interview-questions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ jobTitle })
    });

    const data = (await response.json()) as QuestionsResponse | ErrorResponse;

    if (!response.ok || "error" in data) {
      throw new Error("error" in data ? data.error : "Request failed.");
    }

    setStatus(`Questions for ${data.jobTitle}`, "success");
    renderQuestions(data.questions);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Request failed.";
    setStatus(message, "error");
  }
});

function renderQuestions(questions: string[]) {
  questionsList.innerHTML = "";

  questions.forEach((question) => {
    const item = document.createElement("li");
    item.textContent = question;
    questionsList.appendChild(item);
  });
}

function setStatus(message: string, type: "loading" | "success" | "error") {
  statusMessage.textContent = message;
  statusMessage.dataset.type = type;
}

function getElement<T extends HTMLElement>(selector: string): T {
  const element = document.querySelector<T>(selector);

  if (!element) {
    throw new Error(`Missing page element: ${selector}`);
  }

  return element;
}
