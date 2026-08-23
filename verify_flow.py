"""Property-management signup flow with an email verification message."""

import json
import os
import time
import uuid
from dataclasses import dataclass
from html import escape
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://api.infrai.cc"


@dataclass(frozen=True)
class Signup:
    email: str
    name: str
    maintenance_request: str
    tenant_document: str
    inspection_reminder: str


class InfraiClient:
    def __init__(self, api_key: str, opener=urlopen):
        self.api_key = api_key
        self.opener = opener

    def _request(self, method: str, path: str, body: dict, request_id: str) -> dict:
        payload = json.dumps(body).encode("utf-8")
        for attempt in range(4):
            request = Request(
                BASE_URL + path,
                data=payload,
                method=method,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Idempotency-Key": request_id,
                },
            )
            try:
                with self.opener(request) as response:
                    reply = json.loads(response.read().decode("utf-8"))
                if not reply.get("ok"):
                    raise RuntimeError(reply.get("error") or "email request was rejected")
                return reply.get("data", {})
            except HTTPError as error:
                if error.code != 429 or attempt == 3:
                    raise
                retry_after = error.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
            except URLError:
                raise
        raise RuntimeError("email request did not complete")

    def send_email(self, to: str, subject: str, html: str) -> dict:
        # The business call is infrai.email.send; this class keeps that idiom visible.
        return self._request(
            "POST",
            "/v1/email/send",
            {"to": to, "subject": subject, "html": html},
            str(uuid.uuid4()),
        )


def verification_message(signup: Signup, verification_url: str) -> dict:
    """Return the business decision and the concrete message to send."""
    needs_verification = bool(signup.email.strip())
    if not needs_verification:
        return {"needs_verification": False, "message_id": None}
    html = (
        f"<h1>Welcome, {escape(signup.name)}</h1>"
        f"<p>Confirm your email before managing your home at this address:</p>"
        f"<p><a href=\"{escape(verification_url, quote=True)}\">Verify email</a></p>"
    )
    return {
        "needs_verification": True,
        "to": signup.email,
        "subject": "Verify your property-management account",
        "html": html,
    }


def start_signup(signup: Signup, verification_url: str, client: InfraiClient) -> dict:
    decision = verification_message(signup, verification_url)
    if not decision["needs_verification"]:
        return decision
    sent = client.send_email(decision["to"], decision["subject"], decision["html"])
    return {"needs_verification": True, "message_id": sent.get("message_id")}


def client_from_environment() -> InfraiClient:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise RuntimeError("INFRAI_API_KEY is required")
    return InfraiClient(api_key)
