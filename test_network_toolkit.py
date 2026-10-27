import ast
import ipaddress
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
import socket

SOURCE = Path(__file__).with_name("Network-Toolkit-V21.py")


class NetworkToolkitTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if not SOURCE.exists():
            raise FileNotFoundError(
                f"Toolkit not found: {SOURCE}"
            )

        # Check syntax without running the interactive menu.
        source_text = SOURCE.read_text(encoding="utf-8")
        ast.parse(source_text, filename=str(SOURCE))

        spec = importlib.util.spec_from_file_location(
            "network_toolkit_v21", SOURCE
        )
        cls.toolkit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.toolkit)

    def test_python_syntax(self):
        self.assertTrue(SOURCE.exists())

    def test_valid_domain_accepts_example(self):
        self.assertTrue(
            self.toolkit.valid_domain("example.com")
        )

    def test_valid_domain_rejects_invalid_names(self):
        for domain in ("", "localhost", "-bad.com", "bad..com"):
            with self.subTest(domain=domain):
                self.assertFalse(
                    self.toolkit.valid_domain(domain)
                )

    def test_valid_domain_accepts_subdomain(self):
        self.assertTrue(
            self.toolkit.valid_domain("www.example.com")
        )

    def test_ipv4_calculation(self):
        network = ipaddress.ip_network(
            "192.168.1.10/24", strict=False
        )
        self.assertEqual(str(network), "192.168.1.0/24")
        self.assertEqual(str(network.network_address), "192.168.1.0")
        self.assertEqual(str(network.broadcast_address), "192.168.1.255")
        self.assertEqual(network.num_addresses, 256)
        self.assertEqual(network.num_addresses - 2, 254)

    def test_ipv6_network(self):
        network = ipaddress.ip_network("2001:db8::1/64", strict=False)
        self.assertEqual(network.version, 6)
        self.assertEqual(network.prefixlen, 64)

    def test_ip_address_validation(self):
        self.assertEqual(
            ipaddress.ip_address("192.168.1.10").version, 4
        )
        self.assertEqual(
            ipaddress.ip_address("2001:4860:4860::8888").version, 6
        )

    def test_invalid_ip_is_rejected(self):
        with self.assertRaises(ValueError):
            ipaddress.ip_address("999.999.1.1")

    def test_private_and_public_ip_classification(self):
        self.assertTrue(
            ipaddress.ip_address("192.168.1.10").is_private
        )
        self.assertTrue(
            ipaddress.ip_address("127.0.0.1").is_loopback
        )
        self.assertTrue(
            ipaddress.ip_address("8.8.8.8").is_global
        )

    def test_url_rejects_empty_input(self):
        with self.assertRaises(ValueError):
            self.toolkit.safe_public_url("")

    def test_url_rejects_non_http_scheme(self):
        with self.assertRaises(ValueError):
            self.toolkit.safe_public_url("ftp://example.com")

    def test_url_rejects_localhost(self):
        with self.assertRaises(ValueError):
            self.toolkit.safe_public_url("http://localhost")

    def test_url_rejects_private_resolved_address(self):
        fake_result = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("192.168.1.10", 443))
        ]

        with patch.object(
            self.toolkit.socket,
            "getaddrinfo",
            return_value=fake_result
        ):
            with self.assertRaises(ValueError):
                self.toolkit.safe_public_url("https://example.com")

    def test_url_accepts_public_resolved_address(self):
        fake_result = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("93.184.216.34", 443))
        ]

        with patch.object(
            self.toolkit.socket,
            "getaddrinfo",
            return_value=fake_result
        ):
            result = self.toolkit.safe_public_url("example.com")
            self.assertEqual(result, "https://example.com")


    def test_url_rejects_embedded_credentials(self):
        with self.assertRaises(ValueError):
            self.toolkit.safe_public_url(
                "https://user:password@example.com"
            )

    def test_url_rejects_invalid_port(self):
        with self.assertRaises(ValueError):
            self.toolkit.safe_public_url("https://example.com:99999")

    def test_url_rejects_dns_failure(self):
        with patch.object(
            self.toolkit.socket,
            "getaddrinfo",
            side_effect=socket.gaierror("mock DNS failure")
        ):
            with self.assertRaises(ValueError):
                self.toolkit.safe_public_url("https://example.com")

    def test_url_rejects_mixed_public_and_private_dns(self):
        fake_result = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("93.184.216.34", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "",
             ("192.168.1.10", 443))
        ]

        with patch.object(
            self.toolkit.socket,
            "getaddrinfo",
            return_value=fake_result
        ):
            with self.assertRaises(ValueError):
                self.toolkit.safe_public_url("https://example.com")

    def test_url_rejects_ipv6_private_dns(self):
        fake_result = [
            (socket.AF_INET6, socket.SOCK_STREAM, 6, "",
             ("fc00::1", 443, 0, 0))
        ]

        with patch.object(
            self.toolkit.socket,
            "getaddrinfo",
            return_value=fake_result
        ):
            with self.assertRaises(ValueError):
                self.toolkit.safe_public_url("https://example.com")


if __name__ == "__main__":
    unittest.main(verbosity=2)
