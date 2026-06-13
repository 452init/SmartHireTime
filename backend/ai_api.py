import json
from urllib import error, request

GEMINI_TIMEOUT_SECONDS = 90
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


class MissingApiKeyError(Exception):
    pass


def call_ai_api(prompt, api_key, question_count=3):
    if not api_key:
        raise MissingApiKeyError(
            "Missing GEMINI_API_KEY. Add it to your .env file and restart the server."
        )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{prompt}\n\nReturn only valid JSON."}],
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json",
        },
    }

    result = run_gemini_generation(body, api_key)

    if result.get("error"):
        raise RuntimeError(f"Gemini API error: {json.dumps(result.get('error'))}")

    return extract_response_text(result)


def run_gemini_generation(body, api_key):
    api_request = request.Request(
        GEMINI_API_URL + f"?key={api_key}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=GEMINI_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = f"HTTP {exc.code} {exc.reason}"

        print(f"Gemini HTTPError: code={exc.code} detail={detail}")

        raise RuntimeError(f"AI API request failed (HTTP {exc.code}): {detail}") from exc
    except error.URLError as exc:
        # Network-level errors (DNS, SSL, connection refused, etc.)
        print(f"Gemini URLError: {exc}")
        raise RuntimeError(f"Unable to reach Gemini API: {exc}") from exc


def extract_response_text(result):
    candidates = result.get("candidates") or []
    for candidate in candidates:
        content = candidate.get("content") if isinstance(candidate, dict) else None
        parts = content.get("parts") if isinstance(content, dict) else []
        for part in parts or []:
            if isinstance(part, dict):
                text = str(part.get("text", "")).strip()
                if text:
                    return text

    raise RuntimeError("Gemini API did not return any text.")
