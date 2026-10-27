"""Adapter for Network Toolkit V22 using pinned, redirect-blocking requests."""

from safe_network import safe_request


def fetch_headers(url, timeout=8):
    """Fetch response headers using HEAD without downloading a body."""
    result = safe_request(url, method="HEAD", timeout=timeout, max_bytes=1)

    return {
        "url": url,
        "status": result["status"],
        "headers": result["headers"],
        "redirect_blocked": result["redirect_blocked"],
        "redirect_location": result["redirect_location"],
    }


def fetch_status(url, timeout=10):
    """Fetch status information using GET."""
    result = safe_request(url, method="GET", timeout=timeout, max_bytes=1)
    headers = result["headers"]

    return {
        "url": url,
        "status": result["status"],
        "content_type": headers.get(
            "Content-Type", headers.get("content-type", "Unknown")
        ),
        "redirect_blocked": result["redirect_blocked"],
        "redirect_location": result["redirect_location"],
    }


def fetch_security_headers(url, timeout=10):
    """Fetch security headers using GET without following redirects."""
    result = safe_request(url, method="GET", timeout=timeout, max_bytes=1)

    return {
        "url": url,
        "status": result["status"],
        "headers": result["headers"],
        "redirect_blocked": result["redirect_blocked"],
        "redirect_location": result["redirect_location"],
    }
