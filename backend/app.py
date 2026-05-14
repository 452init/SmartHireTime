from ai_api import MissingApiKeyError, call_ai_api
from auth import (
    AuthTokenError,
    create_access_token,
    generate_code,
    generate_refresh_token,
    hash_code,
    hash_password,
    hash_refresh_token,
    mask_email,
    normalize_email,
    send_code_email,
    verify_access_token,
    verify_password,
)
from config import get_config
from database import (
    MissingDatabaseUrlError,
    consume_auth_code,
    create_auth_code,
    create_refresh_token,
    create_user,
    get_refresh_token_by_hash,
    get_user_by_email,
    get_user_by_id,
    initialize_database,
    revoke_refresh_token,
    save_question_set,
    set_user_google_sub,
)
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from question_builder import build_interview_question_prompt, parse_questions

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
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
AUTH_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REFRESH_COOKIE_NAME = "sht_refresh"


def normalize_frontend_origins(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    elif not isinstance(value, list):
        return []

    cleaned_origins = []
    for item in value:
        if not isinstance(item, str):
            continue
        stripped_item = item.strip()
        if stripped_item:
            cleaned_origins.append(stripped_item)

    return cleaned_origins


def normalize_samesite(value):
    if not isinstance(value, str):
        return "Lax"

    cleaned = value.strip().lower()
    if cleaned == "none":
        return "None"
    if cleaned == "strict":
        return "Strict"

    return "Lax"


app = Flask(__name__)
raw_frontend_origins = CONFIG.get("frontend_origins", [])
has_configured_origins = bool(raw_frontend_origins)
configured_origins = list(dict.fromkeys(normalize_frontend_origins(raw_frontend_origins)))
configured_origin_set = set(configured_origins)
for origin in DEFAULT_FRONTEND_ORIGINS:
    if origin not in configured_origin_set:
        configured_origins.append(origin)
        configured_origin_set.add(origin)

CORS(
    app,
    resources={r"/api/*": {"origins": configured_origins}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
)

if not has_configured_origins:
    print("FRONTEND_ORIGIN is not set. Using default frontend origins for CORS.")

AUTH_SECRET = CONFIG["auth_secret"] or "dev-secret"
ACCESS_TOKEN_TTL_SECONDS = max(CONFIG["auth_access_ttl_minutes"], 1) * 60
AUTH_CODE_TTL_MINUTES = max(CONFIG["auth_code_ttl_minutes"], 1)
REFRESH_TOKEN_TTL_SECONDS = max(CONFIG["refresh_token_ttl_days"], 1) * 24 * 60 * 60
COOKIE_SECURE = CONFIG["cookie_secure"]
COOKIE_SAMESITE = normalize_samesite(CONFIG["cookie_samesite"])
COOKIE_DOMAIN = CONFIG["cookie_domain"] or None
BREVO_CONFIG = {
    "api_key": CONFIG["brevo_api_key"],
    "sender_email": CONFIG["brevo_sender_email"],
    "sender_name": CONFIG["brevo_sender_name"],
}

if not CONFIG["auth_secret"]:
    print("AUTH_SECRET is not set. Set it for production tokens.")
if not CONFIG["brevo_api_key"] or not CONFIG["brevo_sender_email"]:
    print("Brevo email settings are missing. Auth codes will be logged to the server.")


@app.get("/api/health")
def health_check():
    return jsonify({"status": "ok"})


@app.post("/api/interview-questions")
def create_interview_questions():
    try:
        require_authenticated_user()
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
    except AuthTokenError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to generate interview questions right now."}), 500


@app.get("/")
def root():
    return jsonify({"service": "SmartHireTime API", "status": "ok"})


@app.post("/api/auth/start")
def auth_start():
    try:
        payload = request.get_json(silent=True) or {}
        first_name = str(payload.get("firstName", "")).strip()
        last_name = str(payload.get("lastName", "")).strip()
        email = normalize_email(str(payload.get("email", "")))
        password = str(payload.get("password", ""))

        if not first_name or not last_name:
            return jsonify({"error": "Please enter your first and last name."}), 400
        if not email or not AUTH_EMAIL_PATTERN.match(email):
            return jsonify({"error": "Please provide a valid email address."}), 400
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters."}), 400

        user = get_user_by_email(CONFIG["database_url"], email)
        if user:
            if not user.get("password_hash"):
                return (
                    jsonify({"error": "This account uses Google sign-in. Continue with Google."}),
                    400,
                )
            if not verify_password(password, user["password_hash"]):
                return jsonify({"error": "Invalid email or password."}), 401
        else:
            user = create_user(
                CONFIG["database_url"],
                first_name,
                last_name,
                email,
                password_hash=hash_password(password),
            )

        issue_auth_code(user, email)
        return jsonify(
            {
                "status": "code_sent",
                "email": email,
                "maskedEmail": mask_email(email),
                "expiresInMinutes": AUTH_CODE_TTL_MINUTES,
            }
        )
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to start authentication."}), 500


@app.post("/api/auth/google")
def auth_google():
    try:
        payload = request.get_json(silent=True) or {}
        credential = str(payload.get("credential", "")).strip()
        if not credential:
            return jsonify({"error": "Missing Google credential."}), 400
        if not CONFIG["google_client_id"]:
            return jsonify({"error": "GOOGLE_CLIENT_ID is not configured."}), 500

        try:
            id_info = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                CONFIG["google_client_id"],
            )
        except ValueError:
            return jsonify({"error": "Google authentication failed."}), 401

        email = normalize_email(str(id_info.get("email", "")))
        if not email or not AUTH_EMAIL_PATTERN.match(email):
            return jsonify({"error": "Google account missing a valid email."}), 400
        if not id_info.get("email_verified", True):
            return jsonify({"error": "Google email is not verified."}), 401

        first_name = str(id_info.get("given_name") or "Google").strip() or "Google"
        last_name = str(id_info.get("family_name") or "User").strip() or "User"
        google_sub = str(id_info.get("sub", "")).strip() or None

        user = get_user_by_email(CONFIG["database_url"], email)
        if user:
            if google_sub and user.get("google_sub") != google_sub:
                user = set_user_google_sub(CONFIG["database_url"], user["id"], google_sub)
        else:
            user = create_user(
                CONFIG["database_url"],
                first_name,
                last_name,
                email,
                password_hash=None,
                google_sub=google_sub,
            )

        issue_auth_code(user, email)
        return jsonify(
            {
                "status": "code_sent",
                "email": email,
                "maskedEmail": mask_email(email),
                "expiresInMinutes": AUTH_CODE_TTL_MINUTES,
            }
        )
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to start Google authentication."}), 500


@app.post("/api/auth/request-code")
def auth_request_code():
    try:
        payload = request.get_json(silent=True) or {}
        email = normalize_email(str(payload.get("email", "")))
        if not email or not AUTH_EMAIL_PATTERN.match(email):
            return jsonify({"error": "Please provide a valid email address."}), 400

        user = get_user_by_email(CONFIG["database_url"], email)
        if not user:
            return jsonify({"error": "No account found for that email."}), 404

        issue_auth_code(user, email)
        return jsonify(
            {
                "status": "code_sent",
                "email": email,
                "maskedEmail": mask_email(email),
                "expiresInMinutes": AUTH_CODE_TTL_MINUTES,
            }
        )
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to send another code."}), 500


@app.post("/api/auth/verify")
def auth_verify():
    try:
        payload = request.get_json(silent=True) or {}
        email = normalize_email(str(payload.get("email", "")))
        code = str(payload.get("code", "")).strip()

        if not email or not AUTH_EMAIL_PATTERN.match(email):
            return jsonify({"error": "Please provide a valid email address."}), 400
        if not code or not code.isdigit() or len(code) != 6:
            return jsonify({"error": "Enter the 6-digit code from your email."}), 400

        user = get_user_by_email(CONFIG["database_url"], email)
        if not user:
            return jsonify({"error": "No account found for that email."}), 404

        now = datetime.now(timezone.utc)
        code_hash = hash_code(code, AUTH_SECRET)
        consumed = consume_auth_code(CONFIG["database_url"], user["id"], code_hash, now)
        if not consumed:
            return jsonify({"error": "Invalid or expired code."}), 400

        refresh_token = generate_refresh_token()
        token_hash = hash_refresh_token(refresh_token, AUTH_SECRET)
        expires_at = now + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS)
        create_refresh_token(CONFIG["database_url"], user["id"], token_hash, expires_at)

        return create_session_response(user, refresh_token)
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to verify the code."}), 500


@app.post("/api/auth/refresh")
def auth_refresh():
    try:
        refresh_token = get_refresh_cookie()
        if not refresh_token:
            return unauthorized_response("Authentication required.")

        token_hash = hash_refresh_token(refresh_token, AUTH_SECRET)
        record = get_refresh_token_by_hash(CONFIG["database_url"], token_hash)
        if not record:
            return unauthorized_response("Session expired. Please sign in again.")

        now = datetime.now(timezone.utc)
        if record["revoked_at"] or record["expires_at"] <= now:
            if record["id"]:
                revoke_refresh_token(CONFIG["database_url"], record["id"], now)
            return unauthorized_response("Session expired. Please sign in again.")

        user = get_user_by_id(CONFIG["database_url"], record["user_id"])
        if not user:
            return unauthorized_response("Session expired. Please sign in again.")

        new_refresh_token = generate_refresh_token()
        new_hash = hash_refresh_token(new_refresh_token, AUTH_SECRET)
        expires_at = now + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS)
        new_id = create_refresh_token(CONFIG["database_url"], user["id"], new_hash, expires_at)
        revoke_refresh_token(CONFIG["database_url"], record["id"], now, replaced_by=new_id)

        return create_session_response(user, new_refresh_token)
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to refresh session."}), 500


@app.post("/api/auth/logout")
def auth_logout():
    try:
        refresh_token = get_refresh_cookie()
        if refresh_token:
            token_hash = hash_refresh_token(refresh_token, AUTH_SECRET)
            record = get_refresh_token_by_hash(CONFIG["database_url"], token_hash)
            if record and not record["revoked_at"]:
                revoke_refresh_token(CONFIG["database_url"], record["id"], datetime.now(timezone.utc))

        response = jsonify({"status": "logged_out"})
        clear_refresh_cookie(response)
        return response
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to log out."}), 500


@app.get("/api/auth/me")
def auth_me():
    try:
        user = require_authenticated_user()
        return jsonify({"user": to_public_user(user)})
    except AuthTokenError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500


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


def require_authenticated_user():
    token = get_bearer_token()
    if not token:
        raise AuthTokenError("Authentication required.")

    payload = verify_access_token(AUTH_SECRET, token)
    try:
        user_id = int(payload.get("sub", 0))
    except (TypeError, ValueError):
        raise AuthTokenError("Invalid session token.")

    if not user_id:
        raise AuthTokenError("Invalid session token.")

    user = get_user_by_id(CONFIG["database_url"], user_id)
    if not user:
        raise AuthTokenError("User not found.")

    return user


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return ""
    return auth_header.replace("Bearer ", "", 1).strip()


def issue_auth_code(user, email):
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=AUTH_CODE_TTL_MINUTES)
    create_auth_code(CONFIG["database_url"], user["id"], email, hash_code(code, AUTH_SECRET), expires_at)
    send_code_email(email, code, BREVO_CONFIG)


def create_session_response(user, refresh_token):
    access_token = create_access_token(AUTH_SECRET, user["id"], ACCESS_TOKEN_TTL_SECONDS)
    response = jsonify(
        {
            "token": access_token,
            "user": to_public_user(user),
            "tokenType": "Bearer",
            "expiresInSeconds": ACCESS_TOKEN_TTL_SECONDS,
        }
    )
    set_refresh_cookie(response, refresh_token)
    return response


def get_refresh_cookie():
    return request.cookies.get(REFRESH_COOKIE_NAME, "")


def set_refresh_cookie(response, token):
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        max_age=REFRESH_TOKEN_TTL_SECONDS,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        domain=COOKIE_DOMAIN,
        path="/",
    )


def clear_refresh_cookie(response):
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        domain=COOKIE_DOMAIN,
        path="/",
    )


def unauthorized_response(message):
    response = jsonify({"error": message})
    clear_refresh_cookie(response)
    return response, 401


def to_public_user(user):
    return {
        "id": user["id"],
        "email": user["email"],
        "firstName": user["first_name"],
        "lastName": user["last_name"],
    }


if __name__ == "__main__":
    main()
else:
    initialize_app()
