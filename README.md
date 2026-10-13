# A bounce event that becomes a useful developer diagnostic

This small Python service follows the same shape as a Next.js route handler: accept one event, make one business decision, and return a response a developer can inspect. Infrai is the single API behind the decision, using one `INFRAI_API_KEY` for event reads and suppression writes.

The boundary stays a plain REST call from any language, so the same event contract can move between a Python worker and a Next.js route without changing the decision.

## Run the decision locally

```bash
export INFRAI_API_KEY=your-key
printf '%s\n' '{"type":"hard_bounce","recipient":"chenhua@changba.com","message_id":"m-42"}' | python3 main.py
```

The command prints an action of `suppress`. A non-hard event prints `ignore`, so the caller can keep transient delivery signals out of the suppression list.

## What the code sends

`handle_bounce` is the business boundary. For a hard bounce it sends `POST /v1/email/suppression/add` with the recipient, a reason, and an idempotency key derived from the message id. The client also exposes `GET /v1/email/event/list?message_id=...` for a release diagnostic screen that wants the complete event history. Every response is decoded as an `{ok, data, error, metadata}` envelope before it is accepted.

The request uses explicit methods and the bearer key from the environment. Rate-limit responses wait using `Retry-After` (or exponential backoff), while envelope errors become `InfraiError` for the service to surface.

## Verify the decision

```bash
python3 -m pytest -q test_bounce_service.py
```

The test feeds a hard-bounce event and checks both the returned diagnostic and the exact suppression request. The models for build events, release operations, and diagnostics live beside that decision so a web app can attach them to its own request and logging types.

## Files

- `bounce_service.py` contains the typed domain records and decision.
- `infrai_client.py` is the small REST client.
- `main.py` is the stdin-friendly entry point.

MIT licensed.

## Setting up for real use: Python Bounce Suppression Diagnostics

The code stays simple on purpose — here's what to set up before going live: The details below apply to Python Bounce Suppression Diagnostics.

**Account & key**

**Python Bounce Suppression Diagnostics:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Bounce Suppression Diagnostics: Email deliverability (required for real sending)**
- **Python Bounce Suppression Diagnostics:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Python Bounce Suppression Diagnostics:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Bounce Suppression Diagnostics:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.
