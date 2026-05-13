from ai_api import MissingApiKeyError, call_ai_api
from config import get_config
from database import MissingDatabaseUrlError, initialize_database, save_question_set
from flask import Flask, jsonify, request
from flask_cors import CORS
from question_builder import build_interview_question_prompt, parse_questions

from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG = get_config(ROOT_DIR / ".env")
# Guardrails to limit prompt size, response latency, and API usage per request.
MIN_QUESTION_COUNT = 1
MAX_QUESTION_COUNT = 12
DEFAULT_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://smart-hire-time.vercel.app",
]

app = Flask(__name__)
configured_origins = CONFIG["frontend_origins"]
allowed_origins = configured_origins.copy()

for origin in DEFAULT_FRONTEND_ORIGINS:
    if origin not in allowed_origins:
        allowed_origins.append(origin)

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
)

if not configured_origins:
    print("FRONTEND_ORIGIN is not set. Using default frontend origins for CORS.")


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"})


@app.post("/api/interview-questions")
def create_interview_questions():
    try:
        payload = request.get_json(silent=True) or {}
        job_title = str(payload.get("jobTitle", "")).strip()

        if not job_title:
            return jsonify({"error": "Please provide a job title."}), 400

        level = str(payload.get("level", "Mid-Level")).strip() or "Mid-Level"
        category = str(payload.get("category", "Technical")).strip() or "Technical"
        try:
            question_count = int(payload.get("questionCount", 8))
        except (TypeError, ValueError):
            return jsonify({"error": "questionCount must be a valid number."}), 400

        if question_count < MIN_QUESTION_COUNT or question_count > MAX_QUESTION_COUNT:
            return (
                jsonify(
                    {
                        "error": (
                            "questionCount must be between "
                            f"{MIN_QUESTION_COUNT} and {MAX_QUESTION_COUNT}."
                        )
                    }
                ),
                400,
            )

        focus_areas = payload.get("focusAreas") or []
        if not isinstance(focus_areas, list):
            focus_areas = []

        if not CONFIG["database_url"]:
            raise MissingDatabaseUrlError(
                "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
            )

        prompt = build_interview_question_prompt(
             job_title, level, category, question_count, focus_areas
             )
        ai_text = call_ai_api(prompt, CONFIG["tinyfish_api_key"], question_count)
        questions = parse_questions(ai_text, question_count)
        question_set_id = save_question_set(
            CONFIG["database_url"], job_title, questions
        )
        return jsonify(
            {
                "id": question_set_id,
                "jobTitle": job_title,
                "questions": questions,
            }
        )
    except (MissingApiKeyError, MissingDatabaseUrlError) as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to generate interview questions right now."}), 500


@app.get("/")
def root():
    return jsonify({"service": "SmartHireTime API", "status": "ok"})


def initialize_app():
    if CONFIG["database_url"]:
        log_database_host(CONFIG["database_url"])
        initialize_database(CONFIG["database_url"])
    else:
        print("DATABASE_URL is not set. PostgreSQL is required for production.")


def log_database_host(database_url):
    parsed = urlparse(database_url)
    host = parsed.hostname
    port = parsed.port

    if not host:
        print("Database host could not be parsed.")
        return

    if port:
        print(f"Database host: {host}:{port}")
    else:
        print(f"Database host: {host}")


def main():
    initialize_app()
    app.run(host="0.0.0.0", port=CONFIG["port"])


if __name__ == "__main__":
    main()
else:
    initialize_app()
