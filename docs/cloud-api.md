# WhatsApp Business Cloud API

## Pieces

- **Meta app** with the WhatsApp product enabled.
- **Phone number id** used in API calls.
- **Temporary or system user token** for authentication.
- **App secret** used to sign webhook payloads.
- **Verify token** you choose; it proves the webhook URL belongs to you.

## Webhook verification

Meta calls `GET /webhook` with `hub.mode`, `hub.verify_token` and
`hub.challenge`. Reply with the challenge when the token matches.

## Webhook payloads

Each `POST` carries an `X-Hub-Signature-256` header: `sha256=` plus the HMAC of the
raw body keyed with the app secret. Verify it before trusting the JSON.

## Operational notes

- Answer `200` quickly; process asynchronously.
- Deduplicate by message id; Meta can retry.
- Store the raw body for debugging, but never log message content in production
  without a retention policy.
