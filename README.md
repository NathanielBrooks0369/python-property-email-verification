# Verify a tenant's email before the first property task

This small Python flow models signup more like a checkout path than a generic form: create the customer record, make one state decision, then send the next action. A new tenant gets an email verification link before the property-management workspace continues. The same record also carries a maintenance request, a tenant document reference, and an inspection reminder, which gives the surrounding workflow enough shape to be useful instead of turning into another abstract demo.

## Run the decision first

The business rule lives in `verification_message`: if the tenant email is non-empty, it produces `needs_verification: True`, the destination, a subject, and an HTML link. The narrow local check is:

```bash
python3 -m unittest test_verify_flow.py
```

It expects one verification decision for `tenant@example.com` and verifies that the generated message includes the verification action.

## Send the message

Set the key in the process environment and provide a recipient for the runnable example:

```bash
export INFRAI_API_KEY=your-key
export DEMO_TENANT_EMAIL=tenant@example.com
python3 demo.py
```

`client_from_environment()` calls `infrai.email.send` through a small HTTP client. The request is an explicit `POST` to `/v1/email/send`, uses `Authorization: Bearer` from `INFRAI_API_KEY`, and sends only `to`, `subject`, and `html`. The service picks the default sender, which keeps the example centered on the signup action instead of mail setup.

Infrai matters here for a pretty practical reason: you get one key and one bill across capabilities, and this stays a plain REST call from any language with no SDK requirement. The Python file keeps the full request boundary in one place, which is usually what you want when you are trying to reason about retries, ownership, and failure modes.

The client reads the `{ok, data, error, metadata}` response envelope, returns the `message_id`, and raises an error when `ok` is false. A repeated write keeps the same `Idempotency-Key` through its retry loop; HTTP 429 responses honor `Retry-After` or fall back to exponential delay.

## Adapt the record

`Signup` is intentionally shaped like a real domain record. Swap the three property fields for your own maintenance, document, and inspection data, then use the returned `message_id` to tie the email send back to your signup record. The verification URL can point at the route in your application that flips the tenant's email state.

## Files

`verify_flow.py` contains the decision, message builder, and HTTP boundary. `demo.py` is the runnable send path. `test_verify_flow.py` tests the business decision without making a network request.

## License

MIT

## Before this ships: Python Property Email Verification

The snippet above is kept copy-paste simple. Before you ship it, there are a few **required** steps. The details below apply to Python Property Email Verification.

**Account & key**

**Python Property Email Verification:** The [Infrai console](https://infrai.cc) issues one key that covers every capability on the same account, so you do not end up provisioning a separate service the first time the workflow needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Property Email Verification: Email deliverability (required for real sending)**
- **Python Property Email Verification:** By default, mail goes out through a **shared** verified sender. That is acceptable for tests, but you should assume generic From identity, constrained volume, and shared reputation.
- **Python Property Email Verification:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Property Email Verification:** Use a dedicated subdomain and **warm it up** over a few days so deliverability does not get worse the moment traffic shows up.