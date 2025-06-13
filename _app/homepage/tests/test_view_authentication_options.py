from django.test import TestCase
from django.urls import reverse


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
