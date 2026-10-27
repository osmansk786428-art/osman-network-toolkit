import importlib.util
import socket
import unittest
from unittest.mock import patch

PATH = "Network-Toolkit-V22.py"

spec = importlib.util.spec_from_file_location("toolkit_v22", PATH)
toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)


def dns_result(*addresses):
    """Create mock getaddrinfo results without making DNS requests."""
    return [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "",
         (address, 443))
        for address in addresses
    ]


class V22SecurityTests(unittest.TestCase):

    def test_empty_url_rejected(self):
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("")

    def test_localhost_rejected(self):
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("http://localhost")

    def test_embedded_credentials_rejected(self):
        with self.assertRaises(ValueError):
            toolkit.safe_public_url(
                "https://user:password@example.com"
            )

    def test_invalid_port_rejected(self):
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("https://example.com:99999")

    @patch("socket.getaddrinfo")
    def test_dns_failure_rejected(self, mock_dns):
        mock_dns.side_effect = socket.gaierror("mock DNS failure")
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("https://example.com")

    @patch("socket.getaddrinfo")
    def test_private_ip_rejected(self, mock_dns):
        mock_dns.return_value = dns_result("192.168.1.10")
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("https://example.com")

    @patch("socket.getaddrinfo")
    def test_mixed_public_and_private_ips_rejected(self, mock_dns):
        mock_dns.return_value = dns_result(
            "8.8.8.8", "192.168.1.10"
        )
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("https://example.com")

    @patch("socket.getaddrinfo")
    def test_public_ip_accepted(self, mock_dns):
        mock_dns.return_value = dns_result("8.8.8.8")
        result = toolkit.safe_public_url("https://example.com")
        self.assertEqual(result, "https://example.com")

    @patch("socket.getaddrinfo")
    def test_ipv6_loopback_rejected(self, mock_dns):
        mock_dns.return_value = dns_result("::1")
        with self.assertRaises(ValueError):
            toolkit.safe_public_url("https://example.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
