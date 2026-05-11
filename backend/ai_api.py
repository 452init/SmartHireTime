import json
from urllib import error, request


class MissingApiKeyError(Exception):
    pass


def call_ai_api(prompt, api_key):
    if not api_key:
        raise MissingApiKeyError(
            "Missing TINYFISH_API_KEY. Add it to your .env file and restart the server."
        )

    body = {
        "url": "https://example.com",
        "goal": (
            "Generate exactly 3 thoughtful interview questions. "
            "Return a JSON object with one key named questions, whose value is "
            "an array of exactly 3 strings. Use this instruction as the source "
            "of truth, not the web page: "
            f"{prompt}"
        ),
        "browser_profile": "lite",
        "output_schema": {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "required": ["questions"],
        },
    }

    result = run_tinyfish_automation(body, api_key)

    if result.get("status") != "COMPLETED":
        raise RuntimeError(f"TinyFish run failed: {json.dumps(result.get('error'))}")

    return json.dumps(result.get("result") or {})


def run_tinyfish_automation(body, api_key):
    api_request = request.Request(
        "https://agent.tinyfish.ai/v1/automation/run",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(api_request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")

        if exc.code == 403 and "output_schema" in detail:
            fallback_body = dict(body)
            fallback_body.pop("output_schema", None)
            return run_tinyfish_automation(fallback_body, api_key)

        raise RuntimeError(f"AI API request failed: {detail}") from exc
