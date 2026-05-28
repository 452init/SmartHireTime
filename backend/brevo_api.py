import os

import requests

# Brevo transactional email over HTTPS (not SMTP). Path name contains "smtp" in Brevo's API only.
BREVO_TRANSACTIONAL_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoConfigError(Exception):
    pass


class BrevoRequestError(Exception):
    pass


def send_transactional_email(*, to_email, subject, text_content):
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    sender_email = os.getenv("BREVO_SENDER_EMAIL", "").strip()
    sender_name = os.getenv("BREVO_SENDER_NAME", "SmartHireTime").strip() or "SmartHireTime"

    if not api_key or not sender_email:
        raise BrevoConfigError("BREVO_API_KEY and BREVO_SENDER_EMAIL must be set.")

    response = requests.post(
        BREVO_TRANSACTIONAL_EMAIL_URL,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "sender": {"email": sender_email, "name": sender_name},
            "to": [{"email": to_email}],
            "subject": subject,
            "textContent": text_content,
        },
        timeout=15,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = response.text or str(exc)
        raise BrevoRequestError(f"Brevo email request failed: {detail}") from exc
    except requests.RequestException as exc:
        raise BrevoRequestError("Unable to reach Brevo to send email.") from exc
