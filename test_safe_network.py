import unittest
import socket
from unittest.mock import patch

import safe_network as sn


def dns_result(*addresses):
    return [
        (
            socket.AF_INET6 if ":" in address else socket.AF_INET,
            socket.SOCK_STREAM,
            6,
            "",
            (address, 443, 0, 0) if ":" in address else (address, 443),
        )
        for address in addresses
    ]


class SafeNetworkTests(unittest.TestCase):

    def test_empty_url_rejected(self):
        with self.assertRaises(sn.SafeNetworkError):
            sn.parse_public_url("")

    def test_credentials_rejected(self):
        with self.assertRaises(sn.SafeNetworkError):
            sn.parse_public_url("https://user:pass@example.com")

    def test_unsupported_scheme_rejected(self):
        with self.assertRaises(sn.SafeNetworkError):
            sn.parse_public_url("ftp://example.com")

    def test_invalid_port_rejected(self):
        with self.assertRaises(sn.SafeNetworkError):
            sn.parse_public_url("https://example.com:99999")

    @patch("safe_network.socket.getaddrinfo")
    def test_private_ip_rejected(self, mock_dns):
        mock_dns.return_value = dns_result("192.168.1.10")
        with self.assertRaises(sn.SafeNetworkError):
            sn.resolve_public_ips("example.com", 443)

    @patch("safe_network.socket.getaddrinfo")
    def test_mixed_public_private_rejected(self, mock_dns):
        mock_dns.return_value = dns_result("8.8.8.8", "192.168.1.10")
        with self.assertRaises(sn.SafeNetworkError):
            sn.resolve_public_ips("example.com", 443)

    @patch("safe_network.socket.getaddrinfo")
    def test_loopback_ipv6_rejected(self, mock_dns):
        mock_dns.return_value = dns_result("::1")
        with self.assertRaises(sn.SafeNetworkError):
            sn.resolve_public_ips("example.com", 443)

    @patch("safe_network.socket.getaddrinfo")
    def test_dns_failure_rejected(self, mock_dns):
        mock_dns.side_effect = socket.gaierror("mock DNS failure")
        with self.assertRaises(sn.SafeNetworkError):
            sn.resolve_public_ips("example.com", 443)

    def test_non_positive_timeout_rejected(self):
        with self.assertRaises(sn.SafeNetworkError):
            sn.safe_get("https://example.com", timeout=0)

    def test_invalid_max_bytes_rejected(self):
        with self.assertRaises(sn.SafeNetworkError):
            sn.safe_get("https://example.com", max_bytes=0)

    @patch("safe_network.resolve_public_ips")
    @patch("safe_network.PinnedHTTPSConnection")
    def test_redirect_is_reported_not_followed(
        self, mock_connection_class, mock_resolve
    ):
        mock_resolve.return_value = ["8.8.8.8"]

        connection = mock_connection_class.return_value
        response = connection.getresponse.return_value
        response.status = 302
        response.reason = "Found"
        response.getheaders.return_value = [
            ("Location", "http://127.0.0.1/private")
        ]
        response.getheader.return_value = "http://127.0.0.1/private"

        result = sn.safe_get("https://example.com")

        self.assertTrue(result["redirect_blocked"])
        self.assertEqual(result["status"], 302)
        self.assertEqual(
            result["redirect_location"],
            "http://127.0.0.1/private",
        )
        connection.getresponse.assert_called_once()
        connection.close.assert_called_once()

    @patch("safe_network.resolve_public_ips")
    @patch("safe_network.PinnedHTTPSConnection")
    def test_successful_response_returns_body(
        self, mock_connection_class, mock_resolve
    ):
        mock_resolve.return_value = ["8.8.8.8"]

        connection = mock_connection_class.return_value
        response = connection.getresponse.return_value
        response.status = 200
        response.reason = "OK"
        response.getheaders.return_value = [("Content-Type", "text/plain")]
        response.read.return_value = b"mock response"

        result = sn.safe_get("https://example.com")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["body"], b"mock response")
        self.assertFalse(result["redirect_blocked"])
        connection.getresponse.assert_called_once()

    def test_url_path_and_query_preserved(self):
        scheme, host, port, path = sn.parse_public_url(
            "https://example.com/test?q=hello"
        )
        self.assertEqual(scheme, "https")
        self.assertEqual(host, "example.com")
        self.assertEqual(port, 443)
        self.assertEqual(path, "/test?q=hello")


if __name__ == "__main__":
    unittest.main(verbosity=2)
