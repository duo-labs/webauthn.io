from django.test import TestCase
from django.urls import reverse
from django.http.response import HttpResponse


class TestViewIndex(TestCase):
    route = reverse("index")

    def tearDown(self) -> None:
        self.client.cookies.clear()

    def test_renders_page(self) -> None:
        response = self.client.get(self.route)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.headers.get("content-type"), "text/html; charset=utf-8")

    def test_debug_query_param_sets_debug_cookie(self) -> None:
        # The user can set the "?debug=true" query param to get the "debug" cookie
        self.client.get(self.route, QUERY_STRING="debug=true")

        cookie_debug = self.client.cookies.get("debug")
        self.assertIsNotNone(cookie_debug)
        assert cookie_debug  # for mypy
        self.assertEqual(cookie_debug.value, "true")
