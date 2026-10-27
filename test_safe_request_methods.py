import unittest
from unittest.mock import patch, MagicMock

from safe_network import safe_request, SafeNetworkError


def fake_response(status=200, headers=None, body=b"example body"):
    response = MagicMock()
    response.status = status
    response.reason = "OK"
    response.getheaders.return_value = list((headers or {}).items())
    response.getheader.return_value = None
    response.read.side_effect = (
        lambda size=-1: body if size < 0 else body[:size]
    )
    return response


class SafeRequestMethodTests(unittest.TestCase):

    @patch("safe_network.resolve_public_ips", return_value=["93.184.216.34"])
    @patch("safe_network.PinnedHTTPConnection")
    @patch("safe_network.parse_public_url",
           return_value=("http", "example.com", 80, "/"))
    def test_head_does_not_read_body(self, mock_parse, mock_conn, mock_dns):
        conn = mock_conn.return_value
        conn.getresponse.return_value = fake_response()

        result = safe_request("http://example.com", method="HEAD")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["body"], b"")
        conn.putrequest.assert_called_once_with("HEAD", "/", skip_host=True)
        conn.getresponse.return_value.read.assert_not_called()

    @patch("safe_network.resolve_public_ips", return_value=["93.184.216.34"])
    @patch("safe_network.PinnedHTTPConnection")
    @patch("safe_network.parse_public_url",
           return_value=("http", "example.com", 80, "/"))
    def test_get_reads_limited_amount(self, mock_parse, mock_conn, mock_dns):
        conn = mock_conn.return_value
        response = fake_response(body=b"abcdefghij")
        conn.getresponse.return_value = response

        result = safe_request(
            "http://example.com", method="GET", max_bytes=4
        )

        response.read.assert_called_once_with(4)
        self.assertEqual(result["body"], b"abcd")

    def test_rejects_unsupported_method(self):
        with self.assertRaises(SafeNetworkError):
            safe_request("https://example.com", method="POST")

    def test_rejects_invalid_max_bytes(self):
        with self.assertRaises(SafeNetworkError):
            safe_request("https://example.com", max_bytes=True)

    @patch("safe_network.resolve_public_ips", return_value=["93.184.216.34"])
    @patch("safe_network.PinnedHTTPConnection")
    @patch("safe_network.parse_public_url",
           return_value=("http", "example.com", 80, "/"))
    def test_redirect_is_not_followed(self, mock_parse, mock_conn, mock_dns):
        conn = mock_conn.return_value
        response = fake_response(
            status=302, headers={"Location": "http://127.0.0.1/"}
        )
        response.getheader.return_value = "http://127.0.0.1/"
        conn.getresponse.return_value = response

        result = safe_request("http://example.com", method="GET")

        self.assertTrue(result["redirect_blocked"])
        self.assertEqual(
            result["redirect_location"], "http://127.0.0.1/"
        )
        response.read.assert_not_called()
        conn.getresponse.assert_called_once()

if __name__ == "__main__":
    unittest.main(verbosity=2)
