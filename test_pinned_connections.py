import unittest
from unittest.mock import MagicMock, patch

import safe_network as sn


class PinnedConnectionTests(unittest.TestCase):

    @patch("safe_network.socket.create_connection")
    def test_http_connect_uses_pinned_ip(self, mock_create):
        mock_socket = MagicMock()
        mock_create.return_value = mock_socket

        conn = sn.PinnedHTTPConnection(
            "example.com", "93.184.216.34", 80, 5
        )
        conn.connect()

        mock_create.assert_called_once_with(
            ("93.184.216.34", 80),
            5,
            None,
        )
        self.assertIs(conn.sock, mock_socket)
        conn.close()

    @patch("safe_network.socket.create_connection")
    def test_https_connect_pins_ip_and_uses_hostname_for_tls(
        self, mock_create
    ):
        raw_socket = MagicMock(name="raw_socket")
        tls_socket = MagicMock(name="tls_socket")
        mock_create.return_value = raw_socket

        mock_context = MagicMock(name="ssl_context")
        mock_context.wrap_socket.return_value = tls_socket

        conn = sn.PinnedHTTPSConnection(
            "example.com",
            "93.184.216.34",
            443,
            5,
            mock_context,
        )

        conn.connect()

        mock_create.assert_called_once_with(
            ("93.184.216.34", 443),
            5,
            None,
        )
        mock_context.wrap_socket.assert_called_once_with(
            raw_socket,
            server_hostname="example.com",
        )
        self.assertIs(conn.sock, tls_socket)
        conn.close()

    @patch("safe_network.socket.create_connection")
    def test_tls_failure_closes_raw_socket(self, mock_create):
        raw_socket = MagicMock(name="raw_socket")
        mock_create.return_value = raw_socket

        mock_context = MagicMock(name="ssl_context")
        mock_context.wrap_socket.side_effect = OSError("mock TLS failure")

        conn = sn.PinnedHTTPSConnection(
            "example.com",
            "93.184.216.34",
            443,
            5,
            mock_context,
        )

        with self.assertRaises(OSError):
            conn.connect()

        raw_socket.close.assert_called_once()

    @patch("safe_network.socket.create_connection")
    def test_http_connect_failure_propagates(self, mock_create):
        mock_create.side_effect = OSError("mock connection failure")

        conn = sn.PinnedHTTPConnection(
            "example.com", "93.184.216.34", 80, 5
        )

        with self.assertRaises(OSError):
            conn.connect()


if __name__ == "__main__":
    unittest.main(verbosity=2)
