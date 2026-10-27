import unittest
import ipaddress
import sys
import importlib.util
from pathlib import Path
from unittest.mock import patch

# Add project directory to Python path
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# Load Network-Toolkit.py
MODULE_PATH = PROJECT_DIR / "Network-Toolkit.py"

spec = importlib.util.spec_from_file_location(
    "network_toolkit", MODULE_PATH
)

toolkit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toolkit)


class TestNetworkToolkit(unittest.TestCase):

    # Domain tests
    def test_valid_domain(self):
        self.assertTrue(
            toolkit.valid_domain("example.com")
        )

    def test_invalid_domain(self):
        self.assertFalse(
            toolkit.valid_domain("not a domain")
        )

    # IP address tests
    def test_ipv4_address(self):
        self.assertEqual(
            str(ipaddress.ip_address("192.168.1.1")),
            "192.168.1.1"
        )

    def test_ipv6_address(self):
        self.assertEqual(
            str(ipaddress.ip_address("2001:db8::1")),
            "2001:db8::1"
        )

    def test_invalid_ip_address(self):
        with self.assertRaises(ValueError):
            ipaddress.ip_address("999.999.999.999")

    # Password generation test
    def test_sample_password_generation(self):
        with patch("builtins.input", return_value="16"):
            with patch("builtins.print"):
                toolkit.generate_sample_password()

    # IPv4 validator output
    def test_ipv4_validator_output(self):
        with patch(
            "builtins.input",
            return_value="192.168.1.10"
        ):
            with patch("builtins.print") as mock_print:
                toolkit.ipv4_ipv6_validator()

        output = "\n".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Valid IPv4", output)
        self.assertIn("192.168.1.10", output)

    # IPv6 validator output
    def test_ipv6_validator_output(self):
        with patch(
            "builtins.input",
            return_value="2001:4860:4860::8888"
        ):
            with patch("builtins.print") as mock_print:
                toolkit.ipv4_ipv6_validator()

        output = "\n".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Valid IPv6", output)
        self.assertIn("2001:4860:4860::8888", output)

    # Invalid IP validator output
    def test_invalid_ip_validator_output(self):
        with patch(
            "builtins.input",
            return_value="999.999.999.999"
        ):
            with patch("builtins.print") as mock_print:
                toolkit.ipv4_ipv6_validator()

        output = "\n".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Invalid IP", output)

    # IPv4 subnet /26
    def test_subnet_ipv4_26(self):
        with patch(
            "builtins.input",
            return_value="192.168.10.0/26"
        ):
            with patch.object(toolkit, "ok") as mock_ok:
                with patch.object(toolkit, "log"):
                    toolkit.subnet_practice()

        output = "\n".join(
            str(call.args[0])
            for call in mock_ok.call_args_list
        )

        self.assertIn("Network: 192.168.10.0/26", output)
        self.assertIn("Broadcast: 192.168.10.63", output)
        self.assertIn("First host: 192.168.10.1", output)
        self.assertIn("Last host: 192.168.10.62", output)
        self.assertIn("Usable hosts: 62", output)

    # IPv4 subnet /31
    def test_subnet_ipv4_31(self):
        with patch(
            "builtins.input",
            return_value="192.168.10.0/31"
        ):
            with patch.object(toolkit, "ok") as mock_ok:
                with patch.object(toolkit, "log"):
                    toolkit.subnet_practice()

        output = "\n".join(
            str(call.args[0])
            for call in mock_ok.call_args_list
        )

        self.assertIn(
            "Usable hosts: 2 (point-to-point /31)",
            output
        )

    # IPv6 subnet test
    def test_subnet_ipv6(self):
        with patch(
            "builtins.input",
            return_value="2001:db8::/126"
        ):
            with patch.object(toolkit, "ok") as mock_ok:
                with patch.object(toolkit, "log"):
                    toolkit.subnet_practice()

        output = "\n".join(
            str(call.args[0])
            for call in mock_ok.call_args_list
        )

        self.assertIn("IP version: IPv6", output)
        self.assertIn("Network: 2001:db8::/126", output)
        self.assertIn(
            "IPv6 does not use broadcast addresses",
            output
        )

    # Invalid CIDR test
    def test_subnet_invalid_cidr(self):
        with patch(
            "builtins.input",
            return_value="not-a-network"
        ):
            with patch.object(toolkit, "error") as mock_error:
                with patch.object(toolkit, "log"):
                    toolkit.subnet_practice()

        mock_error.assert_called_once()

        self.assertIn(
            "Invalid CIDR/network",
            mock_error.call_args.args[0]
        )

    # Password length test
    def test_password_generator_length(self):
        with patch("builtins.input", return_value="16"):
            with patch.object(toolkit, "ok") as mock_ok:
                with patch.object(toolkit, "warn"):
                    with patch.object(toolkit, "info"):
                        toolkit.generate_sample_password()

        message = mock_ok.call_args.args[0]
        password = message.split("Sample password: ", 1)[1]

        self.assertEqual(len(password), 16)

    # Default password length test
    def test_password_generator_default_length(self):
        with patch("builtins.input", return_value=""):
            with patch.object(toolkit, "ok") as mock_ok:
                with patch.object(toolkit, "warn"):
                    with patch.object(toolkit, "info"):
                        toolkit.generate_sample_password()

        message = mock_ok.call_args.args[0]
        password = message.split("Sample password: ", 1)[1]

        self.assertEqual(len(password), 16)

    # Reject passwords shorter than 8 characters
    def test_password_generator_rejects_short_length(self):
        with patch("builtins.input", return_value="7"):
            with patch.object(toolkit, "error") as mock_error:
                toolkit.generate_sample_password()

        mock_error.assert_called_once()

        self.assertIn(
            "between 8 and 64",
            mock_error.call_args.args[0]
        )

    # Reject non-numeric password length
    def test_password_generator_rejects_invalid_length(self):
        with patch("builtins.input", return_value="abc"):
            with patch.object(toolkit, "error") as mock_error:
                toolkit.generate_sample_password()

        mock_error.assert_called_once()

        self.assertIn(
            "must be a number",
            mock_error.call_args.args[0]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
