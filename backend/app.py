from pathlib import Path

from ai_api import MissingApiKeyError, call_ai_api
from config import get_config
from database import MissingDatabaseUrlError, initialize_database, save_question_set
from flask import Flask, jsonify, request, send_from_directory
from question_builder import build_interview_question_prompt, parse_questions

ROOT_DIR = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT_DIR / "frontend" / "dist"
CONFIG = get_config(ROOT_DIR / ".env")

app = Flask(__name__, static_folder=str(DIST_DIR), static_url_path="")


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

        if not CONFIG["database_url"]:
            raise MissingDatabaseUrlError(
                "Missing DATABASE_URL. Add a PostgreSQL connection string to your .env file."
            )

        prompt = build_interview_question_prompt(job_title)
        ai_text = call_ai_api(prompt, CONFIG["openai_api_key"])
        questions = parse_questions(ai_text)
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
def serve_index():
    return send_frontend_file("index.html")


@app.get("/<path:file_path>")
def serve_frontend(file_path):
    if file_path.startswith("api/"):
        return jsonify({"error": "Not found."}), 404

    target = DIST_DIR / file_path

    if target.exists() and target.is_file():
        return send_from_directory(DIST_DIR, file_path)

    return send_frontend_file("index.html")


def send_frontend_file(file_name):
    target = DIST_DIR / file_name

    if not target.exists():
        return (
            jsonify(
                {
                    "error": (
                        "Frontend build not found. Run 'npm run build' before "
                        "starting the Flask server."
                    )
                }
            ),
            500,
        )

    return send_from_directory(DIST_DIR, file_name)


def main():
    if CONFIG["database_url"]:
        initialize_database(CONFIG["database_url"])
    else:
        print("DATABASE_URL is not set. PostgreSQL will be required before saving questions.")

    app.run(host="127.0.0.1", port=CONFIG["port"])


if __name__ == "__main__":
    main()
