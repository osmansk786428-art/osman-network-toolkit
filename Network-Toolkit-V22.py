#!/usr/bin/env python3
# ==============================================================
# OSMAN CYBER LAB — NETWORK TOOLKIT ULTRA V22
# PREMIUM WOLF EDITION | Termux / Android / Desktop Python
# Use only on systems and networks you own or have permission to test.
# ==============================================================

import datetime
import ipaddress
import json
import os
import platform
import re
import secrets
import socket
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import ssl

from safe_http_adapter import (
    fetch_headers,
    fetch_status,
    fetch_security_headers,
)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, _name):
            return ""
    Fore = Style = _NoColor()

APP_NAME = "OSMAN CYBER LAB"
VERSION = "NETWORK TOOLKIT ULTRA V22 — PREMIUM WOLF EDITION"
REPORT_FILE = "network_report.txt"
report_log = []

C = {
    "purple": Fore.MAGENTA + Style.BRIGHT,
    "cyan": Fore.CYAN + Style.BRIGHT,
    "green": Fore.GREEN + Style.BRIGHT,
    "red": Fore.RED + Style.BRIGHT,
    "yellow": Fore.YELLOW + Style.BRIGHT,
    "blue": Fore.BLUE + Style.BRIGHT,
    "white": Fore.WHITE + Style.BRIGHT,
    "dim": Style.DIM,
    "reset": Style.RESET_ALL,
}


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def ok(text):
    print(f"{C['green']}[+] {text}{C['reset']}")


def info(text):
    print(f"{C['cyan']}[i] {text}{C['reset']}")


def warn(text):
    print(f"{C['yellow']}[!] {text}{C['reset']}")


def error(text):
    print(f"{C['red']}[-] {text}{C['reset']}")


def heading(text):
    print(f"\n{C['purple']}╔══ {text} ══╗{C['reset']}")


def banner():
    os.system("clear" if os.name != "nt" else "cls")
    print(C["purple"] + "╔══════════════════════════════════════════════════════════╗")
    print("║                  🐺 OSMAN CYBER LAB                     ║")
    print("║             NETWORK TOOLKIT ULTRA V22                  ║")
    print("║               PREMIUM WOLF EDITION                     ║")
    print("╚══════════════════════════════════════════════════════════╝" + C["reset"])
    print(f"{C['cyan']}◆ Purple • Cyan • Neon Green • Red • Gold{C['reset']}")
    print(f"{C['dim']}Educational networking tools | Standard library{C['reset']}")
    warn("Use network tests only with permission.")


def log(title, details):
    """Add a report entry; accepts text or structured data."""
    entry = {
        "timestamp": now(),
        "title": str(title),
        "details": details if isinstance(details, (dict, list, int, float, bool)) or details is None else str(details),
    }
    report_log.append(entry)
    try:
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{entry['timestamp']}] {entry['title']}\n")
            f.write(json.dumps(entry["details"], ensure_ascii=False, indent=2) if isinstance(entry["details"], (dict, list)) else str(entry["details"]))
            f.write("\n\n")
    except OSError:
        pass


def pause():
    try:
        input(f"\n{C['yellow']}Press Enter to return to the menu...{C['reset']}")
    except (EOFError, KeyboardInterrupt):
        print()
        return


def ask(prompt):
    try:
        return input(f"{C['cyan']}{prompt}{C['reset']}")
    except (EOFError, KeyboardInterrupt):
        print(f"\n{C['yellow']}Operation cancelled.{C['reset']}")
        raise SystemExit(0)


def valid_domain(value):
    value = value.strip().rstrip(".")
    if not value or len(value) > 253:
        return False
    try:
        value.encode("ascii")
    except UnicodeEncodeError:
        return False
    labels = value.split(".")
    if len(labels) < 2:
        return False
    return all(
        0 < len(label) <= 63 and
        re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?", label)
        for label in labels
    )


def safe_public_url(raw):
    """Validate HTTP(S) URL and block hostnames resolving to non-global IPs."""
    raw = raw.strip()
    if not raw:
        raise ValueError("URL cannot be empty.")
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Use only http:// or https:// URLs.")
    if not parsed.hostname or not valid_domain(parsed.hostname):
        raise ValueError("Enter a valid public domain name.")
    if parsed.username or parsed.password:
        raise ValueError("URLs must not contain a username or password.")
    try:
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError as exc:
        raise ValueError("Invalid port number.") from exc
    try:
        infos = socket.getaddrinfo(parsed.hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS lookup failed: {exc}") from exc
    addresses = {item[4][0].split("%")[0] for item in infos}
    if not addresses:
        raise ValueError("Could not resolve hostname.")
    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            raise ValueError("Requests to private, local, and non-global targets are blocked.")
    return parsed.geturl()


def check_ip_address():
    heading("PUBLIC IP LOOKUP")
    info("Internet access is required.")
    try:
        request = urllib.request.Request(
            "https://api.ipify.org?format=json",
            headers={"User-Agent": "OsmanCyberLab/21.0"}
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        ip = data.get("ip", "Unknown")
        ok(f"Public IP: {ip}")
        try:
            info(f"Type: IPv{ipaddress.ip_address(ip).version}")
        except ValueError:
            pass
        log("Public IP Lookup", {"ip": ip})
    except Exception as exc:
        error(f"Lookup failed: {exc}")
        log("Public IP Lookup", {"error": str(exc)})


def network_calculator():
    heading("NETWORK CALCULATOR")
    raw = ask("Enter IPv4/IPv6 network (e.g. 192.168.1.10/24): ").strip()
    try:
        net = ipaddress.ip_network(raw, strict=False)
        rows = [
            f"Input: {raw}", f"Network: {net}", f"IP version: IPv{net.version}",
            f"Prefix length: /{net.prefixlen}", f"Total addresses: {net.num_addresses}",
            f"Network address: {net.network_address}",
        ]
        if net.version == 4:
            rows += [f"Netmask: {net.netmask}", f"Broadcast: {net.broadcast_address}"]
            if net.prefixlen <= 30:
                rows += [f"First host: {net.network_address + 1}",
                         f"Last host: {net.broadcast_address - 1}",
                         f"Usable hosts (traditional): {net.num_addresses - 2}"]
            elif net.prefixlen == 31:
                rows.append("Usable hosts: 2 (point-to-point /31)")
            else:
                rows.append("Usable hosts: 1 address (/32)")
        else:
            rows.append(f"Netmask: {net.netmask}")
        for row in rows:
            ok(row)
        log("Network Calculator", rows)
    except ValueError as exc:
        error(f"Invalid network: {exc}")


def view_report():
    heading("SAVED REPORT")
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print(content if content.strip() else "No report entries yet.")
    except FileNotFoundError:
        warn("No report has been generated yet.")
    except OSError as exc:
        error(f"Could not read report: {exc}")


def ip_range_generator():
    heading("IP RANGE GENERATOR")
    raw = ask("Enter a network/prefix (e.g. 192.168.1.0/29): ").strip()
    try:
        net = ipaddress.ip_network(raw, strict=False)
        limit = 256
        addresses = [str(addr) for idx, addr in enumerate(net) if idx < limit]
        if net.num_addresses > limit:
            warn(f"Network contains {net.num_addresses} addresses; showing first {limit}.")
        ok(f"Network: {net} | Displayed: {len(addresses)}")
        for addr in addresses:
            print(f"  {C['cyan']}• {addr}{C['reset']}")
        log("IP Range Generator", {"network": str(net), "displayed": addresses})
    except ValueError as exc:
        error(f"Invalid network: {exc}")


def ip_subnet_validator():
    heading("IP & SUBNET VALIDATOR")
    raw = ask("Enter IP or CIDR (e.g. 192.168.1.10/24): ").strip()
    if not raw:
        error("Input cannot be empty.")
        return
    try:
        if "/" in raw:
            interface = ipaddress.ip_interface(raw)
            net = interface.network
            addr = interface.ip
            rows = [
                f"Valid IPv{addr.version} address: {addr}",
                f"Compressed: {addr.compressed}",
                f"Private: {addr.is_private}",
                f"Global/Public-routable: {addr.is_global}",
                f"Loopback: {addr.is_loopback}",
                f"Network: {net}", f"Prefix: /{net.prefixlen}",
                f"Netmask: {net.netmask}", f"Total addresses: {net.num_addresses}",
            ]
            if net.version == 4:
                rows.append(f"Broadcast: {net.broadcast_address}")
        else:
            addr = ipaddress.ip_address(raw)
            rows = [
                f"Valid IPv{addr.version} address: {addr}",
                f"Compressed: {addr.compressed}", f"Private: {addr.is_private}",
                f"Global/Public-routable: {addr.is_global}",
                f"Loopback: {addr.is_loopback}", f"Multicast: {addr.is_multicast}",
                f"Link-local: {addr.is_link_local}", f"Reserved: {addr.is_reserved}",
            ]
        for row in rows:
            ok(row)
        log("IP and Subnet Validation", rows)
    except ValueError as exc:
        error(f"Invalid IP/CIDR: {exc}")


def private_public_detector():
    heading("PRIVATE / PUBLIC IP DETECTOR")
    raw = ask("Enter an IP address: ").strip()
    try:
        addr = ipaddress.ip_address(raw)
        if addr.is_loopback:
            kind = "Loopback (this device)"
        elif addr.is_private:
            kind = "Private IP"
        elif addr.is_global:
            kind = "Public / globally routable IP"
        elif addr.is_link_local:
            kind = "Link-local IP"
        elif addr.is_multicast:
            kind = "Multicast IP"
        elif addr.is_reserved:
            kind = "Reserved IP"
        else:
            kind = "Special-use / non-global IP"
        ok(f"Address: {addr}")
        ok(f"Classification: {kind}")
        log("Private/Public IP Detector", {"address": str(addr), "classification": kind})
    except ValueError:
        error("Invalid IP address. Example: 192.168.1.10")


def dns_lookup():
    heading("DNS LOOKUP")
    host = ask("Enter a domain/hostname (e.g. example.com): ").strip().rstrip(".")
    if not valid_domain(host):
        error("Invalid domain/hostname.")
        return
    try:
        results = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        addresses = sorted({item[4][0] for item in results})
        if addresses:
            ok(f"DNS results for {host}:")
            for address in addresses:
                print(f"  {C['cyan']}• {address}{C['reset']}")
            log("DNS Lookup", {"host": host, "addresses": addresses})
        else:
            warn("No addresses were found.")
    except socket.gaierror as exc:
        error(f"DNS lookup failed: {exc}")
        log("DNS Lookup", {"host": host, "error": str(exc)})


def my_network_information():
    heading("DEVICE NETWORK INFORMATION")
    host = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(host)
    except socket.gaierror:
        local_ip = "Unavailable"
    rows = [
        f"Hostname: {host}", f"OS: {platform.system() or 'Unknown'}",
        f"OS release: {platform.release() or 'Unknown'}",
        f"Python: {platform.python_version()}", f"Host-resolved address: {local_ip}",
    ]
    for row in rows:
        ok(row)
    if local_ip == "127.0.0.1":
        info("127.0.0.1 is loopback, not necessarily your Wi-Fi/LAN IP.")
    log("Device Network Information", rows)


def connectivity_test():
    heading("TCP CONNECTIVITY TEST")
    host = ask("Hostname/domain (e.g. example.com): ").strip()
    if not valid_domain(host):
        error("Enter a valid hostname.")
        return
    try:
        port = int(ask("Port [443]: ") or "443")
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        error("Port must be a number from 1 to 65535.")
        return
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=5):
            elapsed = time.perf_counter() - started
        ok(f"TCP connection successful: {host}:{port}")
        ok(f"Elapsed: {elapsed:.3f} seconds")
        log("TCP Connectivity Test", {"target": f"{host}:{port}", "connected": True, "elapsed_seconds": round(elapsed, 3)})
    except OSError as exc:
        error(f"Connection failed: {exc}")
        log("TCP Connectivity Test", {"target": f"{host}:{port}", "connected": False, "error": str(exc)})


def wifi_information():
    heading("WI-FI INFORMATION")
    info("Termux:API package, companion app, and Android permissions may be required.")
    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"], capture_output=True,
            text=True, timeout=8, check=False
        )
        if result.returncode != 0:
            details = (result.stderr or result.stdout).strip()
            error("Could not read Wi-Fi information.")
            if details:
                print(details)
            log("Wi-Fi Information", {"error": details or "Command failed"})
            return
        data = json.loads(result.stdout)
        ssid, ip = data.get("ssid"), data.get("ip")
        state = str(data.get("supplicant_state", "")).upper()
        disconnected = (
            ssid in (None, "", "<unknown ssid>") or
            ip in (None, "", "0.0.0.0") or
            state in ("UNINITIALIZED", "DISCONNECTED", "INACTIVE")
        )
        if disconnected:
            warn("Wi-Fi disconnected or information unavailable.")
        else:
            ok("Wi-Fi status: CONNECTED")
        for key in ("ssid", "bssid", "ip", "rssi", "link_speed_mbps", "frequency_mhz", "network_id", "supplicant_state"):
            if key in data:
                print(f"{C['cyan']}{key}: {C['white']}{data[key]}{C['reset']}")
        log("Wi-Fi Information", data)
    except FileNotFoundError:
        error("termux-wifi-connectioninfo was not found.")
        info("Install with: pkg install termux-api; also install the Termux:API Android app.")
        log("Wi-Fi Information", {"error": "Termux API command not found"})
    except subprocess.TimeoutExpired:
        error("Wi-Fi command timed out.")
        log("Wi-Fi Information", {"error": "Command timeout"})
    except (json.JSONDecodeError, OSError) as exc:
        error(f"Wi-Fi info error: {exc}")
        log("Wi-Fi Information", {"error": str(exc)})


def http_header_checker():
    heading("HTTP HEADER CHECKER")
    raw = ask("Public website URL (e.g. https://example.com): ")
    try:
        result = fetch_headers(raw, timeout=8)
        status = result["status"]
        headers = result["headers"]

        ok(f"HTTP Status: {status}")
        info(f"Checked URL: {result['url']}")

        if result["redirect_blocked"]:
            warn("Redirect detected; it was NOT followed.")
            info(f"Redirect destination: {result['redirect_location'] or 'Not provided'}")

        for key, value in headers.items():
            print(f"{C['cyan']}{key}: {C['white']}{value}{C['reset']}")

        log("HTTP Header Checker", {
            "url": result["url"],
            "status": status,
            "headers": headers,
            "redirect_blocked": result["redirect_blocked"],
            "redirect_location": result["redirect_location"],
        })
        info("Response headers only; this is not a full security audit.")
    except Exception as exc:
        error(f"Request failed: {exc}")
        log("HTTP Header Checker", {"url": raw, "error": str(exc)})


def http_status_checker():
    heading("HTTP STATUS & RESPONSE TIME")
    raw = ask("Public website URL (e.g. https://example.com): ")
    try:
        started = time.perf_counter()
        result = fetch_status(raw, timeout=10)
        elapsed = time.perf_counter() - started

        ok(f"HTTP status: {result['status']}")
        info(f"Checked URL: {result['url']}")
        info(f"Response time: {elapsed:.3f} seconds")
        info(f"Content-Type: {result['content_type']}")

        if result["redirect_blocked"]:
            warn("Redirect detected; it was NOT followed.")
            info(f"Redirect destination: {result['redirect_location'] or 'Not provided'}")

        log("HTTP Status Checker", {
            "url": result["url"],
            "status": result["status"],
            "response_time_seconds": round(elapsed, 3),
            "content_type": result["content_type"],
            "redirect_blocked": result["redirect_blocked"],
            "redirect_location": result["redirect_location"],
        })
    except Exception as exc:
        error(f"Request failed: {exc}")
        log("HTTP Status Checker", {"url": raw, "error": str(exc)})


def export_report():
    heading("EXPORT TXT REPORT")
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"network_report_export_{stamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{APP_NAME}\n{VERSION}\nExported: {now()}\n")
            f.write("=" * 58 + "\n\n")
            if report_log:
                for entry in report_log:
                    f.write(f"[{entry['timestamp']}] {entry['title']}\n")
                    details = entry["details"]
                    f.write(json.dumps(details, indent=2, ensure_ascii=False) if isinstance(details, (dict, list)) else str(details))
                    f.write("\n\n")
            else:
                try:
                    with open(REPORT_FILE, "r", encoding="utf-8") as source:
                        f.write(source.read())
                except FileNotFoundError:
                    f.write("No report entries yet.\n")
        ok(f"Export saved: {os.path.abspath(filename)}")
    except OSError as exc:
        error(f"Export failed: {exc}")


def export_json_report():
    heading("EXPORT JSON SECURITY REPORT")
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"network_security_report_{stamp}.json"
    data = {
        "application": APP_NAME,
        "version": VERSION,
        "generated_at": now(),
        "report_type": "Network Security and Diagnostics",
        "entries": report_log[:],
    }
    if not data["entries"]:
        try:
            with open(REPORT_FILE, "r", encoding="utf-8") as source:
                old_text = source.read().strip()
            if old_text:
                data["entries"].append({"timestamp": None, "title": "Imported existing text report", "details": old_text})
        except FileNotFoundError:
            pass
        except OSError as exc:
            error(f"Could not read existing report: {exc}")
            return
    try:
        with open(filename, "w", encoding="utf-8") as output:
            json.dump(data, output, indent=2, ensure_ascii=False)
        ok(f"JSON report saved: {os.path.abspath(filename)}")
        info(f"Records exported: {len(data['entries'])}")
    except (OSError, TypeError, ValueError) as exc:
        error(f"JSON report export failed: {exc}")


def password_strength_checker():
    heading("PASSWORD STRENGTH CHECKER")
    warn("Do not enter your real password; use a sample only.")
    password = ask("Sample password: ")
    if not password:
        error("Password cannot be empty.")
        return
    checks = {
        "At least 12 characters": len(password) >= 12,
        "Contains lowercase letters": bool(re.search(r"[a-z]", password)),
        "Contains uppercase letters": bool(re.search(r"[A-Z]", password)),
        "Contains digits": bool(re.search(r"\d", password)),
        "Contains symbols": bool(re.search(r"[^A-Za-z0-9]", password)),
        "Not a common/simple pattern": not bool(re.fullmatch(r"(?:password|admin|qwerty|letmein|123456+|abc123).*", password.lower())),
    }
    score = sum(checks.values())
    for label, passed in checks.items():
        (ok if passed else warn)(label)
    grade = "Weak" if len(password) < 8 or score <= 2 else ("Strong" if len(password) >= 12 and score >= 5 else "Moderate")
    print(f"\n{C['purple']}Estimated strength: {grade} ({score}/6 checks){C['reset']}")
    info("Approximate local check; the password is not transmitted or logged.")


def ipv4_ipv6_validator():
    heading("IPV4 / IPV6 VALIDATOR")
    raw = ask("Enter an IP address: ").strip()
    try:
        addr = ipaddress.ip_address(raw)
        rows = [f"Valid IPv{addr.version}", f"Canonical form: {addr.compressed}",
                f"Private: {addr.is_private}", f"Global: {addr.is_global}",
                f"Loopback: {addr.is_loopback}"]
        for row in rows:
            ok(row)
        log("IPv4/IPv6 Validator", rows)
    except ValueError:
        error("Invalid IP. IPv4 example: 192.168.1.10")
        info("IPv6 example: 2001:4860:4860::8888")


def subnet_practice():
    heading("ADVANCED SUBNET PRACTICE")
    info("Offline practice; no network scan is performed.")
    raw = ask("Network/CIDR (e.g. 192.168.10.0/26): ").strip()
    try:
        net = ipaddress.ip_network(raw, strict=False)
        rows = [f"Network: {net}", f"IP version: IPv{net.version}",
                f"Prefix: /{net.prefixlen}", f"Total addresses: {net.num_addresses}",
                f"Network address: {net.network_address}"]
        if net.version == 4:
            rows += [f"Broadcast: {net.broadcast_address}", f"Netmask: {net.netmask}",
                     f"Wildcard: {ipaddress.IPv4Address(int(net.hostmask))}"]
            if net.prefixlen <= 30:
                rows += [f"First host: {net.network_address + 1}",
                         f"Last host: {net.broadcast_address - 1}",
                         f"Usable hosts: {net.num_addresses - 2}"]
            elif net.prefixlen == 31:
                rows.append("Usable hosts: 2 (point-to-point /31)")
            else:
                rows.append("Usable hosts: 1 address (/32)")
        else:
            rows += ["Broadcast: IPv6 does not use broadcast addresses", f"Netmask: {net.netmask}"]
        for row in rows:
            ok(row)
        log("Advanced Subnet Practice", rows)
    except ValueError as exc:
        error(f"Invalid CIDR/network: {exc}")


def offline_practice_mode():
    while True:
        heading("OFFLINE NETWORKING PRACTICE")
        options = [
            ("1", "Private IPv4 examples"), ("2", "Public IPv4 examples"),
            ("3", "Loopback examples"), ("4", "CIDR quick quiz"), ("5", "Exit practice mode"),
        ]
        for key, label in options:
            print(f" {C['cyan']}[{key}]{C['reset']} {label}")
        choice = ask("Choose: ").strip()
        if choice == "1":
            print("Private IPv4 ranges:\n  10.0.0.0/8\n  172.16.0.0/12\n  192.168.0.0/16")
            info("Example: 192.168.1.20 is private.")
        elif choice == "2":
            print("Example public addresses:\n  8.8.8.8 (Google Public DNS)\n  1.1.1.1 (Cloudflare DNS)")
        elif choice == "3":
            print("IPv4: 127.0.0.1\nIPv6: ::1")
        elif choice == "4":
            answer = ask("How many IPv4 addresses are in 192.168.1.0/24? ")
            if answer.strip() == "256":
                ok("Correct: 256 total addresses.")
            else:
                warn("Answer: 256 total addresses; traditionally 254 usable hosts.")
        elif choice == "5":
            break
        else:
            error("Enter a valid option.")


def generate_sample_password():
    heading("GENERATE SAMPLE PASSWORD")
    try:
        length = int(ask("Length [16]: ") or "16")
        if not 8 <= length <= 64:
            error("Enter a length between 8 and 64.")
            return
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        ok(f"Sample password: {password}")
        warn("Displayed on screen; do not use it for sensitive accounts.")
        info("The generated password is not saved to reports.")
    except ValueError:
        error("Length must be a number.")


def ssl_certificate_checker():
    heading("SSL/TLS CERTIFICATE CHECKER")
    host = ask("Domain name (e.g. example.com): ").strip()
    host = host.removeprefix("https://").removeprefix("http://").split("/")[0].split(":")[0].strip()
    if not valid_domain(host):
        error("Enter a valid domain name.")
        return
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=8) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
                cert = tls_socket.getpeercert()
                cipher = tls_socket.cipher()
                version = tls_socket.version()
        subject = dict(item[0] for item in cert.get("subject", ()))
        issuer = dict(item[0] for item in cert.get("issuer", ()))
        expires = cert.get("notAfter", "Unknown")
        ok(f"TLS certificate verified for {host}")
        info(f"TLS version: {version or 'Unknown'}")
        info(f"Cipher: {cipher[0] if cipher else 'Unknown'}")
        info(f"Subject: {subject.get('commonName', 'Not provided')}")
        info(f"Issuer: {issuer.get('commonName', 'Not provided')}")
        info(f"Expires: {expires}")
        days_left = None
        if expires != "Unknown":
            expiry = datetime.datetime.strptime(expires, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
            days_left = (expiry - datetime.datetime.now(datetime.timezone.utc)).days
            if days_left < 0:
                warn("Certificate expiry date is in the past.")
            else:
                ok(f"Approximate time until expiry: {days_left} days")
        log("SSL/TLS Certificate Check", {"host": host, "tls_version": version, "cipher": cipher[0] if cipher else None, "issuer": issuer.get("commonName", "Not provided"), "expires": expires, "days_left": days_left})
    except (OSError, ssl.SSLError, ValueError) as exc:
        error(f"TLS check failed: {exc}")
        log("SSL/TLS Certificate Check", {"host": host, "error": str(exc)})


def security_headers_checker():
    heading("SECURITY HEADERS CHECKER")
    target = ask("Public website URL (e.g. https://example.com): ").strip()

    headers_to_check = {
        "Strict-Transport-Security": "Helps enforce HTTPS on supported browsers.",
        "Content-Security-Policy": "Helps restrict which resources a page can load.",
        "X-Content-Type-Options": "Helps prevent MIME-type sniffing.",
        "X-Frame-Options": "Can help reduce clickjacking risks.",
        "Referrer-Policy": "Controls referrer information shared.",
        "Permissions-Policy": "Controls access to selected browser features.",
    }

    try:
        result = fetch_security_headers(target, timeout=10)
        response_headers = result["headers"]
        status = result["status"]

        if status >= 400:
            warn(f"Website returned HTTP status {status}; checking available headers.")

        if result["redirect_blocked"]:
            warn("Redirect detected; it was NOT followed.")
            info(f"Redirect destination: {result['redirect_location'] or 'Not provided'}")

    except Exception as exc:
        error(f"Request failed: {exc}")
        log("Security Headers Check", {"url": target, "error": str(exc)})
        return

    ok(f"HTTP response: {status}")
    info(f"Checked URL: {result['url']}")
    present, missing = 0, 0

    for header, description in headers_to_check.items():
        value = next(
            (v for k, v in response_headers.items()
             if k.lower() == header.lower()),
            None,
        )
        if value:
            present += 1
            ok(f"{header}: PRESENT")
            print(f"    Value: {value}")
        else:
            missing += 1
            warn(f"{header}: NOT FOUND")
        print(f"    Purpose: {description}")

    info(f"Summary: {present} present, {missing} not found.")
    warn("A missing header alone is not proof of a vulnerability.")

    log("Security Headers Check", {
        "url": result["url"],
        "status": status,
        "present_headers": present,
        "missing_headers": missing,
        "redirect_blocked": result["redirect_blocked"],
        "redirect_location": result["redirect_location"],
    })


def main():
    actions = {
        "1": check_ip_address, "2": network_calculator, "3": view_report,
        "4": ip_range_generator, "5": ip_subnet_validator,
        "6": private_public_detector, "7": dns_lookup,
        "8": my_network_information, "9": connectivity_test,
        "10": wifi_information, "11": http_header_checker,
        "12": export_report, "14": password_strength_checker,
        "15": ipv4_ipv6_validator, "16": subnet_practice,
        "17": offline_practice_mode, "18": generate_sample_password,
        "19": ssl_certificate_checker, "20": security_headers_checker,
        "21": http_status_checker, "22": export_json_report,
    }
    menu = [
        ("1", "Check Public IP Address", "cyan"),
        ("2", "Network Calculator", "green"),
        ("3", "View Saved Report", "blue"),
        ("4", "IP Range Generator (max 256 displayed)", "cyan"),
        ("5", "IP & Subnet Validator", "green"),
        ("6", "Private/Public IP Detector", "yellow"),
        ("7", "DNS Lookup", "cyan"),
        ("8", "My Network Information", "blue"),
        ("9", "TCP Connectivity Test", "green"),
        ("10", "Wi-Fi Information (Termux:API)", "cyan"),
        ("11", "HTTP Header Checker", "yellow"),
        ("12", "Export TXT Report", "blue"),
        ("13", "Exit", "red"),
        ("14", "Password Strength Checker", "purple"),
        ("15", "IPv4 / IPv6 Validator", "cyan"),
        ("16", "Advanced Subnet Practice", "green"),
        ("17", "Offline Networking Practice", "purple"),
        ("18", "Generate Sample Password", "yellow"),
        ("19", "SSL/TLS Certificate Checker", "cyan"),
        ("20", "Security Headers Checker", "green"),
        ("21", "HTTP Status & Response Time", "yellow"),
        ("22", "Export JSON Security Report", "cyan"),
    ]
    # V22 PREMIUM UI: grouped menu; original actions remain unchanged.
    categories = [
        ("NETWORK TOOLS", {"1", "2", "4", "5", "6", "7", "8", "9", "10"}),
        ("REPORTS & EXPORT", {"3", "12", "22"}),
        ("WEB & SECURITY", {"11", "19", "20", "21"}),
        ("VALIDATION & PRACTICE", {"15", "16", "17"}),
        ("PASSWORD TOOLS", {"14", "18"}),
    ]

    while True:
        banner()
        width = max(24, min(58, __import__("shutil").get_terminal_size((40, 20)).columns - 2))
        divider = "═" * width

        for title, keys in categories:
            print(f"\n{C['purple']}▸ {title}{C['reset']}")
            for key, label, color in menu:
                if key in keys:
                    print(f"  {C[color]}[{key:>2}]{C['reset']} {C['white']}{label}{C['reset']}")

        for key, label, color in menu:
            if key == "13":
                print(f"\n{C['red']}  [{key:>2}] {label}{C['reset']}")

        print(f"{C['purple']}{divider}{C['reset']}")
        choice = ask("Choose option: ").strip()
        if choice == "13":
            print(f"\n{C['purple']}🐺 OSMAN CYBER LAB is shutting down. Keep learning!{C['reset']}")
            break
        action = actions.get(choice)
        if action:
            try:
                action()
            except KeyboardInterrupt:
                print()
                warn("Operation cancelled.")
            except Exception as exc:
                error(f"Unexpected error: {exc}")
                log("Unexpected Error", {"option": choice, "error": str(exc)})
            pause()
        else:
            error("Invalid option. Choose a listed menu number.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['yellow']}OSMAN CYBER LAB has been closed.{C['reset']}")
