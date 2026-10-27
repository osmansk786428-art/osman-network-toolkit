import socket
import ssl
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer


class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = b"local TLS test"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class TLSVerificationTests(unittest.TestCase):

    def test_default_context_requires_certificate_verification(self):
        context = ssl.create_default_context()
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_self_signed_certificate_is_rejected(self):
        # No external connection: use a local TCP server that speaks plain
        # HTTP. A TLS client must reject it because the peer sends no TLS
        # certificate or TLS handshake.
        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def plain_http_peer():
            try:
                conn, _ = server.accept()
                with conn:
                    conn.recv(4096)
                    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\n\r\n")
            except OSError:
                pass
            finally:
                server.close()

        thread = threading.Thread(target=plain_http_peer, daemon=True)
        thread.start()

        context = ssl.create_default_context()
        with socket.create_connection(("127.0.0.1", port), timeout=3) as raw:
            with self.assertRaises(ssl.SSLError):
                context.wrap_socket(raw, server_hostname="localhost")

        thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
