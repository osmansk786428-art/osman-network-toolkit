#!/usr/bin/env python3
"""Educational HTTP client with public-IP pinning and redirect blocking."""

import http.client
import ipaddress
import socket
import ssl
import urllib.parse


class SafeNetworkError(Exception):
    """Raised when a URL or network connection fails a security check."""


def resolve_public_ips(host, port):
    """Resolve a hostname and reject the entire result if any IP is non-global."""
    try:
        records = socket.getaddrinfo(
            host, port, type=socket.SOCK_STREAM
        )
    except OSError as exc:
        raise SafeNetworkError("DNS resolution failed.") from exc

    addresses = set()

    for record in records:
        address = record[4][0].split("%")[0]
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise SafeNetworkError("DNS returned an invalid IP address.") from exc

        if not ip.is_global:
            raise SafeNetworkError(
                "Blocked: hostname resolves to a private or non-global IP."
            )

        addresses.add(str(ip))

    if not addresses:
        raise SafeNetworkError("DNS returned no usable IP addresses.")

    return sorted(addresses)


def parse_public_url(raw_url):
    """Parse an HTTP(S) URL and validate its hostname and port."""
    raw_url = raw_url.strip()

    if not raw_url:
        raise SafeNetworkError("URL cannot be empty.")

    if "://" not in raw_url:
        raw_url = "https://" + raw_url

    try:
        parsed = urllib.parse.urlsplit(raw_url)
        port = parsed.port
    except ValueError as exc:
        raise SafeNetworkError("Malformed URL or invalid port.") from exc

    if parsed.scheme not in ("http", "https"):
        raise SafeNetworkError("Only HTTP and HTTPS are allowed.")

    if not parsed.hostname or parsed.username or parsed.password:
        raise SafeNetworkError("A valid hostname without credentials is required.")

    host = parsed.hostname.rstrip(".")
    if not host or "%" in host or not host.isascii():
        raise SafeNetworkError("Invalid hostname.")

    # This educational client accepts public DNS names, not IP literals.
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise SafeNetworkError("Enter a public hostname, not an IP literal.")

    if any(not label or len(label) > 63 for label in host.split(".")):
        raise SafeNetworkError("Invalid hostname labels.")

    if len(host) > 253:
        raise SafeNetworkError("Hostname is too long.")

    import re
    if not all(
        re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
        for label in host.split(".")
    ):
        raise SafeNetworkError("Invalid hostname syntax.")

    port = port or (443 if parsed.scheme == "https" else 80)
    if not 1 <= port <= 65535:
        raise SafeNetworkError("Port is out of range.")

    path = urllib.parse.urlunsplit(("", "", parsed.path or "/", parsed.query, ""))
    return parsed.scheme, host, port, path


class PinnedHTTPConnection(http.client.HTTPConnection):
    """Connect to a previously validated IP, not a fresh DNS lookup."""

    def __init__(self, hostname, address, port, timeout):
        self.pinned_address = address
        super().__init__(hostname, port=port, timeout=timeout)

    def connect(self):
        self.sock = socket.create_connection(
            (self.pinned_address, self.port),
            self.timeout,
            self.source_address,
        )


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Pin TCP to a validated IP while verifying TLS against the hostname."""

    def __init__(self, hostname, address, port, timeout, context):
        self.pinned_address = address
        super().__init__(
            hostname,
            port=port,
            timeout=timeout,
            context=context,
        )

    def connect(self):
        raw_socket = socket.create_connection(
            (self.pinned_address, self.port),
            self.timeout,
            self.source_address,
        )
        try:
            self.sock = self._context.wrap_socket(
                raw_socket,
                server_hostname=self.host,
            )
        except Exception:
            raw_socket.close()
            raise



def safe_request(raw_url, method="GET", timeout=8, max_bytes=65536):
    """Send one pinned HTTP(S) GET or HEAD request without following redirects."""
    method = method.upper() if isinstance(method, str) else ""

    if method not in ("GET", "HEAD"):
        raise SafeNetworkError("Only GET and HEAD methods are allowed.")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise SafeNetworkError("Timeout must be positive.")
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 1:
        raise SafeNetworkError("max_bytes must be a positive integer.")

    scheme, host, port, path = parse_public_url(raw_url)
    addresses = resolve_public_ips(host, port)
    last_error = None

    for address in addresses:
        connection = None
        try:
            if scheme == "https":
                connection = PinnedHTTPSConnection(
                    host, address, port, timeout,
                    ssl.create_default_context(),
                )
            else:
                connection = PinnedHTTPConnection(host, address, port, timeout)

            connection.connect()
            connection.putrequest(method, path, skip_host=True)

            host_header = host
            default_port = 443 if scheme == "https" else 80
            if port != default_port:
                host_header = f"{host}:{port}"

            connection.putheader("Host", host_header)
            connection.putheader("User-Agent", "OsmanCyberLab-SafeClient/1.0")
            connection.putheader("Connection", "close")
            connection.endheaders()

            response = connection.getresponse()
            status = response.status
            reason = response.reason
            headers = dict(response.getheaders())
            redirect = status in (301, 302, 303, 307, 308)
            location = response.getheader("Location", "") if redirect else None

            body = b""
            if method == "GET" and not redirect:
                body = response.read(max_bytes)

            response.close()
            return {
                "status": status,
                "reason": reason,
                "headers": headers,
                "body": body,
                "redirect_blocked": redirect,
                "redirect_location": location,
            }

        except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
            last_error = exc
        finally:
            if connection is not None:
                connection.close()

    raise SafeNetworkError(
        f"Could not connect to a validated public IP: {last_error}"
    ) from last_error

def safe_get(raw_url, timeout=8, max_bytes=65536):
    """Backward-compatible GET wrapper."""
    return safe_request(
        raw_url, method="GET", timeout=timeout, max_bytes=max_bytes
    )
