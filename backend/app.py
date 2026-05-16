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
from cloudinary_api import (
    CloudinaryConfigError,
    CloudinaryRequestError,
    delete_image,
    upload_image,
)
from config import get_config
from database import (
    MissingDatabaseUrlError,
    clear_user_profile_image,
    delete_user_account,
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
    update_user_password_hash,
    update_user_profile_image,
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
MAX_PROFILE_PHOTO_BYTES = 5 * 1024 * 1024
PROFILE_IMAGE_FOLDER = "smarthiretime/profile-photos"


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
if COOKIE_SECURE and COOKIE_SAMESITE == "Lax":
    COOKIE_SAMESITE = "None"
if not COOKIE_SECURE and COOKIE_SAMESITE == "None":
    COOKIE_SAMESITE = "Lax"
COOKIE_DOMAIN = CONFIG["cookie_domain"] or None
BREVO_CONFIG = {
    "api_key": CONFIG["brevo_api_key"],
    "sender_email": CONFIG["brevo_sender_email"],
    "sender_name": CONFIG["brevo_sender_name"],
}
CLOUDINARY_CONFIG = {
    "cloud_name": CONFIG["cloudinary_cloud_name"],
    "api_key": CONFIG["cloudinary_api_key"],
    "api_secret": CONFIG["cloudinary_api_secret"],
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
        require_authenticated_user(allowed_purposes={"login"})
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
    except RuntimeError as exc:
        print(f"AI error: {exc}")
        return jsonify({"error": str(exc)}), 502
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
        mode = str(payload.get("mode", "signin")).strip().lower()
        first_name = str(payload.get("firstName", "")).strip()
        last_name = str(payload.get("lastName", "")).strip()
        email = normalize_email(str(payload.get("email", "")))
        password = str(payload.get("password", ""))

        if not email or not AUTH_EMAIL_PATTERN.match(email):
            return jsonify({"error": "Please provide a valid email address."}), 400
        if mode not in {"signin", "signup"}:
            return jsonify({"error": "Unsupported authentication mode."}), 400
        if mode == "signin" and len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters."}), 400
        if mode == "signup" and len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters."}), 400

        user = get_user_by_email(CONFIG["database_url"], email)
        if user:
            if not user.get("password_hash"):
                return (
                    jsonify({"error": "This account uses Google sign-in. Continue with Google."}),
                    400,
                )
            if mode == "signup":
                return jsonify({"error": "An account already exists for that email."}), 409
            if not verify_password(password, user["password_hash"]):
                return jsonify({"error": "Invalid email or password."}), 401
        else:
            if mode == "signin":
                return jsonify({"error": "No account found for that email."}), 404
            if not first_name or not last_name:
                return jsonify({"error": "Please add your first and last name to create an account."}), 400
            user = create_user(
                CONFIG["database_url"],
                first_name,
                last_name,
                email,
                password_hash=hash_password(password),
            )

        issue_auth_code(user, email, purpose="login")
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

        issue_auth_code(user, email, purpose="login")
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
        session_purpose = consumed["purpose"] or "login"
        create_refresh_token(
            CONFIG["database_url"],
            user["id"],
            token_hash,
            expires_at,
            purpose=session_purpose,
        )

        return create_session_response(user, refresh_token, session_purpose)
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to verify the code."}), 500


@app.post("/api/auth/forgot-password")
def auth_forgot_password():
    try:
        payload = request.get_json(silent=True) or {}
        email = normalize_email(str(payload.get("email", "")))

        if not email or not AUTH_EMAIL_PATTERN.match(email):
            return jsonify({"error": "Please provide a valid email address."}), 400

        user = get_user_by_email(CONFIG["database_url"], email)
        if not user:
            return jsonify({"error": "No account found for that email."}), 404
        if not user.get("password_hash"):
            return jsonify({"error": "This account uses Google sign-in. Continue with Google."}), 400

        issue_auth_code(user, email, purpose="recovery")
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
        return jsonify({"error": "Unable to send password reset code."}), 500


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
        session_purpose = record.get("purpose") or "login"
        new_id = create_refresh_token(
            CONFIG["database_url"],
            user["id"],
            new_hash,
            expires_at,
            purpose=session_purpose,
        )
        revoke_refresh_token(CONFIG["database_url"], record["id"], now, replaced_by=new_id)

        return create_session_response(user, new_refresh_token, session_purpose)
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


@app.post("/api/account/password")
def account_password_update():
    try:
        user, session = require_authenticated_session()
        payload = request.get_json(silent=True) or {}
        current_password = str(payload.get("currentPassword", ""))
        new_password = str(payload.get("newPassword", ""))

        if not new_password:
            return jsonify({"error": "Complete all password fields."}), 400
        if len(new_password) < 8:
            return jsonify({"error": "New password must be at least 8 characters."}), 400

        existing_hash = user.get("password_hash")
        if not existing_hash:
            return (
                jsonify({"error": "This account uses Google sign-in. Password updates are unavailable."}),
                400,
            )
        if session.get("purpose") != "recovery":
            if not current_password:
                return jsonify({"error": "Complete all password fields."}), 400
            if not verify_password(current_password, existing_hash):
                return jsonify({"error": "Current password is incorrect."}), 401

        updated_user = update_user_password_hash(
            CONFIG["database_url"],
            user["id"],
            hash_password(new_password),
        )
        if session.get("purpose") == "recovery":
            now = datetime.now(timezone.utc)
            refresh_token = generate_refresh_token()
            token_hash = hash_refresh_token(refresh_token, AUTH_SECRET)
            expires_at = now + timedelta(seconds=REFRESH_TOKEN_TTL_SECONDS)
            create_refresh_token(
                CONFIG["database_url"],
                user["id"],
                token_hash,
                expires_at,
                purpose="login",
            )
            return create_session_response(updated_user, refresh_token, "login")

        return jsonify({"status": "updated"})
    except AuthTokenError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to update password."}), 500


@app.post("/api/account/delete")
def account_delete():
    try:
        user = require_authenticated_user(allowed_purposes={"login"})
        photo_public_id = user.get("profile_image_public_id")

        if photo_public_id:
            try:
                delete_image(photo_public_id, CLOUDINARY_CONFIG)
            except CloudinaryRequestError as exc:
                print(f"Unable to delete Cloudinary profile photo: {exc}")

        delete_user_account(CONFIG["database_url"], user["id"])

        response = jsonify({"status": "deleted"})
        clear_refresh_cookie(response)
        return response
    except AuthTokenError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except CloudinaryConfigError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to delete account."}), 500


@app.post("/api/account/photo")
def account_photo_upload():
    try:
        user = require_authenticated_user(allowed_purposes={"login"})
        image_file = request.files.get("file")
        if not image_file:
            return jsonify({"error": "Choose a photo to upload."}), 400

        content_type = (image_file.content_type or "").lower()
        if not content_type.startswith("image/"):
            return jsonify({"error": "Only image files are allowed."}), 400

        image_bytes = image_file.read()
        if not image_bytes:
            return jsonify({"error": "Uploaded file is empty."}), 400
        if len(image_bytes) > MAX_PROFILE_PHOTO_BYTES:
            return jsonify({"error": "Image must be 5MB or smaller."}), 400

        upload_result = upload_image(
            file_bytes=image_bytes,
            filename=image_file.filename or f"user-{user['id']}.jpg",
            content_type=content_type,
            folder=PROFILE_IMAGE_FOLDER,
            config=CLOUDINARY_CONFIG,
        )

        previous_public_id = user.get("profile_image_public_id")
        updated_user = update_user_profile_image(
            CONFIG["database_url"],
            user["id"],
            upload_result["secure_url"],
            upload_result["public_id"],
        )

        if previous_public_id and previous_public_id != upload_result["public_id"]:
            try:
                delete_image(previous_public_id, CLOUDINARY_CONFIG)
            except CloudinaryRequestError as exc:
                print(f"Unable to delete previous Cloudinary image: {exc}")

        return jsonify({"user": to_public_user(updated_user)})
    except AuthTokenError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except CloudinaryConfigError as exc:
        return jsonify({"error": str(exc)}), 500
    except CloudinaryRequestError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to update photo."}), 500


@app.delete("/api/account/photo")
def account_photo_delete():
    try:
        user = require_authenticated_user(allowed_purposes={"login"})
        existing_public_id = user.get("profile_image_public_id")

        if existing_public_id:
            delete_image(existing_public_id, CLOUDINARY_CONFIG)

        updated_user = clear_user_profile_image(CONFIG["database_url"], user["id"])
        return jsonify({"user": to_public_user(updated_user)})
    except AuthTokenError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except MissingDatabaseUrlError as exc:
        return jsonify({"error": str(exc)}), 500
    except CloudinaryConfigError as exc:
        return jsonify({"error": str(exc)}), 500
    except CloudinaryRequestError as exc:
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:
        print(exc)
        return jsonify({"error": "Unable to delete photo."}), 500


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


def require_authenticated_user(allowed_purposes=None):
    user, _session = require_authenticated_session(allowed_purposes)
    return user


def require_authenticated_session(allowed_purposes=None):
    token = get_bearer_token()
    if not token:
        raise AuthTokenError("Authentication required.")

    payload = verify_access_token(AUTH_SECRET, token)
    purpose = payload.get("purpose") or "login"
    if allowed_purposes is not None and purpose not in allowed_purposes:
        raise AuthTokenError("Please finish resetting your password before continuing.", 403)

    try:
        user_id = int(payload.get("sub", 0))
    except (TypeError, ValueError):
        raise AuthTokenError("Invalid session token.")

    if not user_id:
        raise AuthTokenError("Invalid session token.")

    user = get_user_by_id(CONFIG["database_url"], user_id)
    if not user:
        raise AuthTokenError("User not found.")

    return user, payload


def get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return ""
    return auth_header.replace("Bearer ", "", 1).strip()


def issue_auth_code(user, email, purpose="login"):
    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=AUTH_CODE_TTL_MINUTES)
    create_auth_code(
        CONFIG["database_url"],
        user["id"],
        email,
        hash_code(code, AUTH_SECRET),
        expires_at,
        purpose=purpose,
    )
    send_code_email(email, code, BREVO_CONFIG, purpose)


def create_session_response(user, refresh_token, session_purpose="login"):
    access_token = create_access_token(AUTH_SECRET, user["id"], ACCESS_TOKEN_TTL_SECONDS, session_purpose)
    response = jsonify(
        {
            "token": access_token,
            "user": to_public_user(user),
            "tokenType": "Bearer",
            "expiresInSeconds": ACCESS_TOKEN_TTL_SECONDS,
            "sessionPurpose": session_purpose,
        }
    )
    set_refresh_cookie(response, refresh_token)
    return response


def get_refresh_cookie():
    return request.cookies.get(REFRESH_COOKIE_NAME, "")


def set_refresh_cookie(response, token):
    secure, samesite = get_refresh_cookie_policy()
    response.set_cookie(
        REFRESH_COOKIE_NAME,
        token,
        max_age=REFRESH_TOKEN_TTL_SECONDS,
        httponly=True,
        secure=secure,
        samesite=samesite,
        domain=COOKIE_DOMAIN,
        path="/",
    )


def clear_refresh_cookie(response):
    secure, samesite = get_refresh_cookie_policy()
    response.delete_cookie(
        REFRESH_COOKIE_NAME,
        domain=COOKIE_DOMAIN,
        path="/",
        secure=secure,
        samesite=samesite,
    )


def get_refresh_cookie_policy():
    origin = request.headers.get("Origin", "")
    is_https_frontend = origin.startswith("https://")
    if is_https_frontend:
        return True, "None"

    return COOKIE_SECURE, COOKIE_SAMESITE


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
        "profileImageUrl": user.get("profile_image_url"),
    }


if __name__ == "__main__":
    main()
else:
    initialize_app()
