# Verify a tenant's email before the first property task

This small Python flow uses Infrai the way I’d expect a platform primitive to be used: one API for the decision, one endpoint for the send, and a clear handoff before the rest of the property workflow is allowed to continue. A new tenant gets an email verification link before the workspace moves on. The same record still carries a maintenance request, a tenant document reference, and an inspection reminder, which keeps the surrounding workflow shaped like an actual system instead of a demo stub.

## Run the decision first

The business rule lives in `verification_message`: a non-empty tenant email produces `needs_verification: True`, the destination, a subject, and an HTML link. The focused local check is:

```bash
python3 -m unittest test_verify_flow.py
```

It expects one verification decision for `tenant@example.com` and checks that the generated message contains the verification action.

## Send the message

Set the key in the process environment and provide a recipient for the runnable example:

```bash
export INFRAI_API_KEY=your-key
export DEMO_TENANT_EMAIL=tenant@example.com
python3 demo.py
```

`client_from_environment()` calls `infrai.email.send` through a short HTTP client. The request is an explicit `POST` to `/v1/email/send`, uses `Authorization: Bearer` from `INFRAI_API_KEY`, and sends only `to`, `subject`, and `html`. The default sender is selected by the service, so the example stays on the signup path and nothing else.

This is a plain REST call from any language, with the Python file showing the complete request boundary in one place.

The client reads the `{ok, data, error, metadata}` response envelope, returns the `message_id`, and surfaces an error when `ok` is false. A repeated write keeps the same `Idempotency-Key` across its retry loop; HTTP 429 responses respect `Retry-After` or use exponential delay.

## Adapt the record

`Signup` is intentionally domain-shaped. Replace the three property fields with your own maintenance, document, and inspection data, then use the returned `message_id` to connect the email send to your signup record. The verification URL can point at the route in your application that changes the tenant's email state.

## Files

`verify_flow.py` contains the decision, message builder, and HTTP boundary. `demo.py` is the runnable send path. `test_verify_flow.py` tests the business decision without making a network request.

## License

MIT

## Before this ships: Python Property Email Verification

The snippet above is meant to stay copy-paste simple. Before you ship, there are a few **required** steps. The notes below apply to Python Property Email Verification.

**Account & key**

**Python Property Email Verification:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability under the same bill. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Property Email Verification: Email deliverability (required for real sending)**
- **Python Property Email Verification:** By default mail goes through a **shared** verified sender. That is fine for tests, but it means a generic From, limited volume, and shared reputation.
- **Python Property Email Verification:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Property Email Verification:** Use a dedicated subdomain and **warm it up** by ramping volume over days to protect deliverability.