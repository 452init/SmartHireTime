import json
from urllib import error, request

TINYFISH_TIMEOUT_SECONDS = 90


class MissingApiKeyError(Exception):
    pass


def call_ai_api(prompt, api_key, question_count=3):
    if not api_key:
        raise MissingApiKeyError(
            "Missing TINYFISH_API_KEY. Add it to your .env file and restart the server."
        )

    body = {
        "url": "https://example.com",
        "goal": (
            "Follow the prompt exactly and return JSON "
            f"with exactly {question_count} questions. "
            f"{prompt}"
        ),
        "browser_profile": "lite",
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
        with request.urlopen(api_request, timeout=TINYFISH_TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")
        except Exception:
            detail = f"HTTP {exc.code} {exc.reason}"

        print(f"TinyFish HTTPError: code={exc.code} detail={detail}")

        raise RuntimeError(f"AI API request failed (HTTP {exc.code}): {detail}") from exc
    except error.URLError as exc:
        # Network-level errors (DNS, SSL, connection refused, etc.)
        print(f"TinyFish URLError: {exc}")
        raise RuntimeError(f"Unable to reach TinyFish API: {exc}") from exc
