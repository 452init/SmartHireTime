import json
from urllib import error, request

MISTRAL_TIMEOUT_SECONDS = 90
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


class MissingApiKeyError(Exception):
    pass


def call_ai_api(prompt, api_key, question_count=3):
    if not api_key:
        raise MissingApiKeyError(
            "Missing MISTRAL_API_KEY. Add it to your .env file and restart the server."
        )

    body = {
        "model": MISTRAL_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"{prompt}\n\nReturn only valid JSON.",
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 1024,
        "response_format": {"type": "json_object"},
    }

    result = run_mistral_generation(body, api_key)

    if result.get("error"):
        raise RuntimeError(f"Mistral API error: {json.dumps(result.get('error'))}")

    return extract_response_text(result)


def run_mistral_generation(body, api_key):
    api_request = request.Request(
        MISTRAL_API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=MISTRAL_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = f"HTTP {exc.code} {exc.reason}"

        print(f"Mistral HTTPError: code={exc.code} detail={detail}")

        raise RuntimeError(f"AI API request failed (HTTP {exc.code}): {detail}") from exc
    except error.URLError as exc:
        print(f"Mistral URLError: {exc}")
        raise RuntimeError(f"Unable to reach Mistral API: {exc}") from exc


def extract_response_text(result):
    choices = result.get("choices") or []
    for choice in choices:
        message = choice.get("message") if isinstance(choice, dict) else None
        content = message.get("content") if isinstance(message, dict) else ""

        if isinstance(content, str):
            text = content.strip()
            if text:
                return text

        if isinstance(content, list):
            text = "".join(
                str(part.get("text", ""))
                for part in content
                if isinstance(part, dict)
            ).strip()
            if text:
                return text

    raise RuntimeError("Mistral API did not return any text.")
