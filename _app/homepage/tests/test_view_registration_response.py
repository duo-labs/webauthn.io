from django.test import TestCase
from django.urls import reverse
from django.http.response import HttpResponseBadRequest


class TestViewRegistrationVerification(TestCase):
    def setUp(self):
        self.route = reverse("registration-verification")
        self.client.get(reverse("index"))

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
