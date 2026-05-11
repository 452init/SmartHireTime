import json
from urllib import error, request


class MissingApiKeyError(Exception):
    pass


def call_ai_api(prompt, api_key):
    if not api_key:
        raise MissingApiKeyError(
            "Missing OPENAI_API_KEY. Add it to your .env file and restart the server."
        )

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert hiring manager. Return only valid JSON "
                    "with a questions array."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.7,
    }

    api_request = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"AI API request failed: {detail}") from exc

    return result["choices"][0]["message"]["content"]
