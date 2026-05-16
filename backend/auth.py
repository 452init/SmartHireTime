import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from urllib import error, request

import bcrypt
import jwt
_BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"


class AuthTokenError(Exception):
    def __init__(self, message, status=401):
        super().__init__(message)
        self.status = status


def hash_password(password):
    password_bytes = _to_bytes(password)
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(password, password_hash):
    if not password_hash:
        return False
    return bcrypt.checkpw(_to_bytes(password), _to_bytes(password_hash))


def normalize_email(email):
    return email.strip().lower()


def mask_email(email):
    if "@" not in email:
        return email

    name, domain = email.split("@", 1)
    if len(name) <= 2:
        masked = f"{name[:1]}***"
    else:
        masked = f"{name[:1]}***{name[-1:]}"

    return f"{masked}@{domain}"


def _to_bytes(value):
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


def generate_code():
    return f"{secrets.randbelow(1000000):06d}"


def hash_code(code, secret):
    return hashlib.sha256(f"{secret}:{code}".encode("utf-8")).hexdigest()


def create_access_token(secret, user_id, ttl_seconds, purpose="login"):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=ttl_seconds)).timestamp()),
        "purpose": purpose,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_access_token(secret, token):
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise AuthTokenError("Session expired. Please sign in again.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthTokenError("Invalid session token. Please sign in again.") from exc


def generate_refresh_token():
    return secrets.token_urlsafe(48)


def hash_refresh_token(token, secret):
    return hashlib.sha256(f"{secret}:{token}".encode("utf-8")).hexdigest()


def send_code_email(email, code, brevo_config):
    api_key = brevo_config.get("api_key", "")
    sender_email = brevo_config.get("sender_email", "")
    sender_name = brevo_config.get("sender_name", "SmartHireTime")

    if not api_key or not sender_email:
        print(f"Auth code for {email}: {code}")
        return

    body = {
        "sender": {"email": sender_email, "name": sender_name},
        "to": [{"email": email}],
        "subject": "Your SmartHireTime sign-in code",
        "textContent": (
            "Your SmartHireTime verification code is:\n\n"
            f"{code}\n\n"
            "This code expires soon. If you did not request this, you can ignore this email."
        ),
    }

    api_request = request.Request(
        _BREVO_ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=15) as response:
            response.read()
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"Brevo email request failed: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError("Unable to reach Brevo to send email.") from exc
