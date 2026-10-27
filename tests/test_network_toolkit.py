import unittest
import ipaddress
import sys
from pathlib import Path
from unittest.mock import patch

# Add project directory to Python path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import importlib.util

MODULE_PATH = PROJECT_DIR / "Network-Toolkit.py"

spec = importlib.util.spec_from_file_location(
    "network_toolkit", MODULE_PATH
)
toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)


class TestNetworkToolkit(unittest.TestCase):

    def test_valid_domain(self):
        self.assertTrue(toolkit.valid_domain("example.com"))

    def test_invalid_domain(self):
        self.assertFalse(toolkit.valid_domain("not a domain"))

    def test_ipv4_address(self):
        self.assertEqual(str(ipaddress.ip_address("192.168.1.1")),
                         "192.168.1.1")

    def test_ipv6_address(self):
        self.assertEqual(str(ipaddress.ip_address("2001:db8::1")),
                         "2001:db8::1")

    def test_invalid_ip_address(self):
        with self.assertRaises(ValueError):
            ipaddress.ip_address("999.999.999.999")

    def test_sample_password_generation(self):
        with patch("builtins.input", return_value="16"):
            with patch("builtins.print"):
                toolkit.generate_sample_password()


if __name__ == "__main__":
    unittest.main(verbosity=2)
