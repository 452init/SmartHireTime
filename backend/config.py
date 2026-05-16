import os


def get_config(env_path):
    load_env_file(env_path)

    return {
        "database_url": os.getenv("DATABASE_URL", ""),
        "tinyfish_api_key": os.getenv("TINYFISH_API_KEY", ""),
        "cloudinary_cloud_name": os.getenv("CLOUDINARY_CLOUD_NAME", ""),
        "cloudinary_api_key": os.getenv("CLOUDINARY_API_KEY", ""),
        "cloudinary_api_secret": os.getenv("CLOUDINARY_API_SECRET", ""),
        "frontend_origins": get_csv_env("FRONTEND_ORIGIN"),
        "auth_secret": os.getenv("AUTH_SECRET", ""),
        "auth_access_ttl_minutes": int(os.getenv("AUTH_ACCESS_TTL_MINUTES", "15")),
        "auth_code_ttl_minutes": int(os.getenv("AUTH_CODE_TTL_MINUTES", "10")),
        "refresh_token_ttl_days": int(os.getenv("REFRESH_TOKEN_TTL_DAYS", "30")),
        "cookie_secure": os.getenv("COOKIE_SECURE", "false").lower() == "true",
        "cookie_samesite": os.getenv("COOKIE_SAMESITE", "lax"),
        "cookie_domain": os.getenv("COOKIE_DOMAIN", ""),
        "brevo_api_key": os.getenv("BREVO_API_KEY", ""),
        "brevo_sender_email": os.getenv("BREVO_SENDER_EMAIL", ""),
        "brevo_sender_name": os.getenv("BREVO_SENDER_NAME", "SmartHireTime"),
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "port": int(os.getenv("PORT", "3000")),
    }


def load_env_file(env_path):
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        clean_line = line.strip()

        if not clean_line or clean_line.startswith("#") or "=" not in clean_line:
            continue

        key, value = clean_line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_csv_env(key):
    value = os.getenv(key, "")
    return [item.strip() for item in value.split(",") if item.strip()]
