import hashlib
import hmac
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import webhook


class VerificationTests(unittest.TestCase):
    def test_valid_challenge(self):
        params = {"hub.mode": "subscribe", "hub.verify_token": "t", "hub.challenge": "42"}
        self.assertEqual(webhook.verify_challenge(params, "t"), "42")

    def test_wrong_token(self):
        params = {"hub.mode": "subscribe", "hub.verify_token": "x", "hub.challenge": "42"}
        self.assertIsNone(webhook.verify_challenge(params, "t"))

    def test_wrong_mode(self):
        params = {"hub.mode": "unsubscribe", "hub.verify_token": "t", "hub.challenge": "42"}
        self.assertIsNone(webhook.verify_challenge(params, "t"))


class SignatureTests(unittest.TestCase):
    def signature(self, body, secret):
        return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

    def test_valid_signature(self):
        body = b'{"a":1}'
        self.assertTrue(webhook.verify_signature(body, self.signature(body, "s"), "s"))

    def test_invalid_signature(self):
        self.assertFalse(webhook.verify_signature(b"{}", "sha256=deadbeef", "s"))

    def test_missing_header(self):
        self.assertFalse(webhook.verify_signature(b"{}", None, "s"))

    def test_wrong_prefix(self):
        self.assertFalse(webhook.verify_signature(b"{}", "sha1=abc", "s"))


class ParsingTests(unittest.TestCase):
    def test_parse_messages(self):
        payload = {"entry": [{"changes": [{"value": {"messages": [
            {"id": "1", "from": "123", "type": "text", "text": {"body": "hi"},
             "timestamp": "1700000000"}
        ]}}]}]}
        messages = webhook.parse_messages(payload)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["text"], "hi")
        self.assertEqual(messages[0]["from"], "123")

    def test_parse_empty(self):
        self.assertEqual(webhook.parse_messages({}), [])

    def test_parse_status_only_payload(self):
        payload = {"entry": [{"changes": [{"value": {"statuses": [{"id": "1"}]}}]}]}
        self.assertEqual(webhook.parse_messages(payload), [])


if __name__ == "__main__":
    unittest.main()
