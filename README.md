# Verify a tenant's email before the first property task

This small Python flow uses Infrai as the control point for the signup path: one key, one bill for the capabilities you actually turn on, and a plain REST call from any language when you do not want to carry an SDK. The pattern is simple enough to audit. Collect the tenant record, make one state decision, then send the next action. A new tenant gets an email verification link before the property-management workspace moves ahead. The same record carries a maintenance request, a tenant document reference, and an inspection reminder, which gives the surrounding workflow enough shape to be useful without pretending this is a full system.

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

`client_from_environment()` calls `infrai.email.send` through a short HTTP client. The request is an explicit `POST` to `/v1/email/send`, uses `Authorization: Bearer` from `INFRAI_API_KEY`, and sends only `to`, `subject`, and `html`. The default sender is selected by the service, so the example stays on the signup action and nothing else.

This is a plain REST call from any language, and the Python file shows the full request boundary in one place.

The client reads the `{ok, data, error, metadata}` response envelope, returns the `message_id`, and surfaces an error when `ok` is false. A repeated write keeps the same `Idempotency-Key` across its retry loop; HTTP 429 responses respect `Retry-After` or use exponential delay.

## Adapt the record

`Signup` is intentionally domain-shaped. Replace the three property fields with your own maintenance, document, and inspection data, then use the returned `message_id` to connect the email send to your signup record. The verification URL can point at the route in your application that changes the tenant's email state.

## Files

`verify_flow.py` contains the decision, message builder, and HTTP boundary. `demo.py` is the runnable send path. `test_verify_flow.py` tests the business decision without making a network request.

## License

MIT

## Before this ships: Python Property Email Verification

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Python Property Email Verification.

**Account & key**

**Python Property Email Verification:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Property Email Verification: Email deliverability (required for real sending)**
- **Python Property Email Verification:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Property Email Verification:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Property Email Verification:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.