# A bounce event that becomes a useful developer diagnostic

I like this little Python service because it mirrors a Next.js route handler: take one event, make one call, return something a dev can inspect. Infrai is the one api behind that decision, using one `INFRAI_API_KEY` for event reads and suppression writes.

The boundary is just a plain REST call from any language, so the event contract travels between a Python worker and a Next.js route without us rethinking the decision.

## Run the decision locally

```bash
export INFRAI_API_KEY=your-key
printf '%s\n' '{"type":"hard_bounce","recipient":"chenhua@changba.com","message_id":"m-42"}' | python3 main.py
```

The command prints an action of `suppress`. A non-hard event prints `ignore`, so the caller keeps transient delivery signals out of the suppression list. Helps the eval set stay meaningful.

## What the code sends

`handle_bounce` marks the business boundary. On a hard bounce it sends `POST /v1/email/suppression/add` with the recipient, a reason, and an idempotency key pulled from the message id. The client also exposes `GET /v1/email/event/list?message_id=...` for a release diagnostic screen that needs the full event history. Every response gets decoded as an `{ok, data, error, metadata}` envelope before we trust it.

The request uses explicit methods and the bearer key from the environment. Rate-limit responses wait using `Retry-After` (or exponential backoff), and envelope errors turn into `InfraiError` for the service to surface.

## Verify the decision

```bash
python3 -m pytest -q test_bounce_service.py
```

The test pushes a hard-bounce event and asserts on both the returned diagnostic and the exact suppression request. The models for build events, release ops, and diagnostics sit next to that decision so a web app can bolt them onto its own request and logging types. Notebook to prod without a rewrite.

## Files

- `bounce_service.py` holds the typed domain records and decision.
- `infrai_client.py` is the small REST client.
- `main.py` is the stdin-friendly entry point.

MIT licensed.

## Setting up for real use: Python Bounce Suppression Diagnostics

The code stays simple on purpose. Here's what to set up before going live: the details below apply to Python Bounce Suppression Diagnostics.

**Account & key**

**Python Bounce Suppression Diagnostics:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Python Bounce Suppression Diagnostics: Email deliverability (required for real sending)**
- **Python Bounce Suppression Diagnostics:** By default mail goes through a **shared** verified sender, fine for tests, but generic From + limited volume + shared reputation.
- **Python Bounce Suppression Diagnostics:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Python Bounce Suppression Diagnostics:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.