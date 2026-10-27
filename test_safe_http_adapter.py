import unittest
from unittest.mock import patch

import safe_http_adapter as adapter
from safe_network import SafeNetworkError


def fake_result(status=200, headers=None, redirect=False, location=None):
    return {
        "status": status,
        "reason": "OK",
        "headers": headers or {},
        "body": b"",
        "redirect_blocked": redirect,
        "redirect_location": location,
    }


class SafeHTTPAdapterTests(unittest.TestCase):

    @patch("safe_http_adapter.safe_request")
    def test_fetch_headers_uses_head(self, mock_request):
        mock_request.return_value = fake_result(
            200, {"Content-Type": "text/html"}
        )
        result = adapter.fetch_headers("https://example.com")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["headers"]["Content-Type"], "text/html")
        mock_request.assert_called_once_with(
            "https://example.com", method="HEAD", timeout=8, max_bytes=1
        )

    @patch("safe_http_adapter.safe_request")
    def test_fetch_status_uses_get(self, mock_request):
        mock_request.return_value = fake_result(
            200, {"Content-Type": "application/json"}
        )
        result = adapter.fetch_status("https://example.com")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["content_type"], "application/json")
        mock_request.assert_called_once_with(
            "https://example.com", method="GET", timeout=10, max_bytes=1
        )

    @patch("safe_http_adapter.safe_request")
    def test_security_headers_uses_get(self, mock_request):
        mock_request.return_value = fake_result(
            200, {"Content-Security-Policy": "default-src 'self'"}
        )
        result = adapter.fetch_security_headers("https://example.com")

        self.assertIn("Content-Security-Policy", result["headers"])
        mock_request.assert_called_once_with(
            "https://example.com", method="GET", timeout=10, max_bytes=1
        )

    @patch("safe_http_adapter.safe_request")
    def test_redirect_is_reported(self, mock_request):
        mock_request.return_value = fake_result(
            302,
            {"Location": "http://127.0.0.1/"},
            redirect=True,
            location="http://127.0.0.1/",
        )
        result = adapter.fetch_status("https://example.com")

        self.assertTrue(result["redirect_blocked"])
        self.assertEqual(
            result["redirect_location"], "http://127.0.0.1/"
        )
        mock_request.assert_called_once()

    @patch("safe_http_adapter.safe_request")
    def test_network_error_propagates(self, mock_request):
        mock_request.side_effect = SafeNetworkError("Blocked destination")

        with self.assertRaises(SafeNetworkError):
            adapter.fetch_headers("https://example.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
