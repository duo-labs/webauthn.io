from django.test import TestCase
from django.urls import reverse
from django.http.response import HttpResponseBadRequest


class TestViewAuthenticationOptions(TestCase):
    def setUp(self):
        self.route = reverse("authentication-options")
        self.client.get(reverse("index"))

    def test_handles_hints(self):

        options = self.client.post(
            self.route,
            {
                "user_verification": "preferred",
                "hints": ["security-key", "hybrid", "client-device"],
            },
            content_type="application/json",
        )

        options_json = options.json()

        self.assertEqual(options_json.get("hints"), ["security-key", "hybrid", "client-device"])

    def test_returns_400_bad_argument(self):
        options = self.client.post(
            self.route,
            {},
        )

        options_json = options.json()

        self.assertEquals(options.status_code, HttpResponseBadRequest.status_code)
        self.assertEquals(
            options_json,
            {"error": "Could not parse request: Expecting value: line 1 column 1 (char 0)"},
        )
