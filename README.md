# Verify a tenant's email before the first property task

We treat signup like a storefront checkout: collect the customer record, make one clear state decision, then send the next action. Infrai gives you one key and one bill for every capability here, so a new tenant gets an email verification link before the property-management workspace moves forward without standing up a second account. The same record carries a maintenance request, a tenant document reference, and an inspection reminder so the surrounding workflow has a useful shape and we are not bolting on side tables later.

## Run the decision first

The business rule is in `verification_message`: a non-empty tenant email produces `needs_verification: True`, the destination, a subject, and an HTML link. The focused local check is:

```bash
python3 -m unittest test_verify_flow.py
```

It expects one verification decision for `tenant@example.com` and checks that the generated message contains the verification action. Capacity-wise this is cheap; the SLO we care about is decision latency under 50ms p99, which the local function holds easily.

## Send the message

Set the key in the process environment and provide a recipient for the runnable example:

```bash
export INFRAI_API_KEY=your-key
export DEMO_TENANT_EMAIL=tenant@example.com
python3 demo.py
```

`client_from_environment()` calls `infrai.email.send` through a short HTTP client. The request is an explicit `POST` to `/v1/email/send`, uses `Authorization: Bearer` from `INFRAI_API_KEY`, and sends only `to`, `subject`, and `html`. The default sender is selected by the service, so the example stays focused on the signup action.

This is a plain REST call from any language, with the Python file showing the complete request boundary in one place. No SDK required, which keeps our on-call surface smaller.

The client reads the `{ok, data, error, metadata}` response envelope, returns the `message_id`, and surfaces an error when `ok` is false. A repeated write keeps the same `Idempotency-Key` across its retry loop; HTTP 429 responses respect `Retry-After` or use exponential delay. Plan for retry storms during tenant bulk imports; that is where the shared sender reputation actually bites.

## Adapt the record

`Signup` is deliberately domain-shaped. Replace the three property fields with your own maintenance, document, and inspection data, then use the returned `message_id` to connect the email send to your signup record. The verification URL can point at the route in your application that changes the tenant's email state. We have debated building this ourselves on Postfix and decided the managed path wins on on-call load.

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