# whatsapp-bot-study

Study notes and reference code for the **official** WhatsApp Business Cloud API:
webhook verification, signature checking and parsing inbound messages. This is a
learning repository for the documented business API — it does not automate
personal WhatsApp accounts.

## Features

- `docs/cloud-api.md`: setup flow, tokens, phone number ids and webhook rules.
- `webhook.py`: `GET` verification challenge, `POST` signature verification
  (HMAC-SHA256 over the raw body) and message parsing.
- No outbound sending implemented, so nothing can be used to spam anyone.
- Tests cover the verification handshake, signatures and parsing.

## Installation

```bash
git clone https://github.com/victor-harden/whatsapp-bot-study.git
cd whatsapp-bot-study
```

## Usage

```bash
export WHATSAPP_VERIFY_TOKEN=dev-token
export WHATSAPP_APP_SECRET=dev-secret
python3 webhook.py serve --port 8080
```

Send the verification request Meta expects:

```bash
curl "localhost:8080/webhook?hub.mode=subscribe&hub.verify_token=dev-token&hub.challenge=123"
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Scope

Educational repository using the documented Cloud API. Do not automate personal
accounts; that violates the platform terms.

## License

MIT — see [LICENSE](LICENSE).
