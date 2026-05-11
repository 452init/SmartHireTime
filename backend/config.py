import os


def get_config(env_path):
    load_env_file(env_path)

    return {
        "database_url": os.getenv("DATABASE_URL", ""),
        "tinyfish_api_key": os.getenv("TINYFISH_API_KEY", ""),
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
