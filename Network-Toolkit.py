#!/usr/bin/env python3
# ==============================================================
# 🐺 OSMAN CYBER LAB — NETWORK TOOLKIT ULTRA V5
# PREMIUM WOLF COLOR EDITION
# Termux / Android / Desktop Python | Standard library + Colorama
# Use only on systems and networks you own or have permission to test.
# ==============================================================

import ipaddress
import socket
import platform
import subprocess
import json
import urllib.request
import urllib.error
import urllib.parse
import datetime
import re
import os
import sys
import string
import secrets

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    # The toolkit still works without colorama; install it for colors:
    # python -m pip install colorama
    class _NoColor:
        def __getattr__(self, _name):
            return ""
    Fore = Back = Style = _NoColor()

APP_NAME = "OSMAN CYBER LAB"
VERSION = "NETWORK TOOLKIT ULTRA V5 — PREMIUM WOLF EDITION"
REPORT_FILE = "network_report.txt"
report_log = []

# Premium Wolf palette
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
    p, cy, g, r, y, w = (C[k] for k in ("purple", "cyan", "green", "red", "yellow", "white"))
    print(p + "╔══════════════════════════════════════════════════════════╗")
    print("║" + " " * 18 + "🐺 OSMAN CYBER LAB" + " " * 17 + "║")
    print("║" + " " * 12 + "NETWORK TOOLKIT ULTRA V5" + " " * 14 + "║")
    print("║" + " " * 14 + "PREMIUM WOLF EDITION" + " " * 15 + "║")
    print("╚══════════════════════════════════════════════════════════╝" + C["reset"])
    print(f"{cy}  ◆ {w}Purple • Cyan • Neon Green • Red • Gold{C['reset']}")
    print(f"{C['dim']}  Educational networking tools | Offline-friendly{C['reset']}")
    print(f"{y}  Use network tests only with permission.{C['reset']}")
    print(p + "═" * 58 + C["reset"])


def log(title, details):
    entry = f"[{now()}] {title}\n{details}\n"
    report_log.append(entry)
    try:
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except OSError:
        pass


def pause():
    input(f"\n{C['yellow']}Press Enter to return to the menu...{C['reset']}")


def ask(prompt):
    try:
        return input(f"{C['cyan']}{prompt}{C['reset']}")
    except (EOFError, KeyboardInterrupt):
        print(f"\n{C['yellow']}Operation cancelled.{C['reset']}")
        sys.exit(0)


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
        0 < len(label) <= 63
        and re.fullmatch(
            r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?",
            label
        )
        for label in labels
    )


def safe_public_url(raw):
    raw = raw.strip()
    if not raw:
        raise ValueError("URL cannot be empty.")
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Use only http:// or https:// URLs.")
    if not parsed.hostname or not valid_domain(parsed.hostname):
        raise ValueError("Enter a valid domain or hostname.")
    if parsed.username or parsed.password:
        raise ValueError("URLs must not contain a username or password.")
    try:
        infos = socket.getaddrinfo(
            parsed.hostname,
            parsed.port or (443 if parsed.scheme == "https" else 80),
            type=socket.SOCK_STREAM
        )
    except socket.gaierror as exc:
        raise ValueError(f"DNS lookup failed: {exc}")
    ips = {item[4][0] for item in infos}
    if not ips:
        raise ValueError("Could not resolve hostname to an IP address.")
    for ip in ips:
        if not ipaddress.ip_address(ip).is_global:
            raise ValueError(
                "Requests to private, local, and non-global targets are blocked."
            )
    return parsed.geturl()

def check_ip_address():
    heading("PUBLIC IP LOOKUP")
    info("Internet access is required for public IP lookup.")
    try:
        req = urllib.request.Request(
            "https://api.ipify.org?format=json",
            headers={"User-Agent": "OsmanCyberLab/5.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        ip = data.get("ip", "Unknown")
        ok(f"Public IP: {ip}")
        try:
            info(f"Type: IPv{ipaddress.ip_address(ip).version}")
        except ValueError:
            pass
        log("Public IP Lookup", f"Public IP: {ip}")
    except Exception as exc:
        error(f"Lookup failed: {exc}")
        warn("An internet connection may be required.")
        log("Public IP Lookup", f"Failed: {exc}")


def network_calculator():
    heading("NETWORK CALCULATOR")
    raw = ask("Enter an IPv4/IPv6 network (e.g. 192.168.1.10/24): ")
    try:
        net = ipaddress.ip_network(raw, strict=False)
        details = [
            f"Input: {raw}", f"Network: {net}", f"IP version: IPv{net.version}",
            f"Netmask: {getattr(net, 'netmask', 'Not applicable')}",
            f"Prefix length: /{net.prefixlen}", f"Total addresses: {net.num_addresses}",
        ]
        if net.version == 4:
            details += [
                f"Broadcast: {net.broadcast_address}",
                f"Network address: {net.network_address}",
                f"Usable host count (traditional): {max(0, net.num_addresses - 2) if net.prefixlen < 31 else net.num_addresses}",
            ]
            if net.prefixlen < 31:
                details += [f"First host: {net.network_address + 1}", f"Last host: {net.broadcast_address - 1}"]
        for item in details:
            ok(item)
        log("Network Calculator", "\n".join(details))
    except ValueError as exc:
        error(f"Invalid network: {exc}")


def view_report():
    heading("SAVED REPORT")
    try:
        with open(REPORT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        print(content if content.strip() else f"{C['yellow']}No report is available yet.{C['reset']}")
    except FileNotFoundError:
        warn("No report has been generated yet.")
    except OSError as exc:
        error(f"Could not read report: {exc}")


def ip_range_generator():
    heading("IP RANGE GENERATOR")
    raw = ask("Enter a network/prefix (e.g. 192.168.1.0/29): ")
    try:
        net = ipaddress.ip_network(raw, strict=False)
        limit = 256
        if net.num_addresses > limit:
            warn(f"Network- {net.num_addresses} address ;  {limit}   ।")
        addresses = []
        for idx, addr in enumerate(net):
            if idx >= limit:
                break
            addresses.append(str(addr))
        ok(f"Network: {net} | Displayed: {len(addresses)}")
        for addr in addresses:
            print(f"  {C['cyan']}• {addr}{C['reset']}")
        log("IP Range Generator", f"Network: {net}\nDisplayed addresses: {len(addresses)}\n" + "\n".join(addresses))
    except ValueError as exc:
        error(f"Invalid network: {exc}")


def ip_subnet_validator():
    heading("IP & SUBNET VALIDATOR")
    raw = ask("Enter an IP address or CIDR (e.g. 192.168.1.10/24): ").strip()

    if not raw:
        error("Input cannot be empty.")
        return

    if "/" in raw:
        try:
            net = ipaddress.ip_network(raw, strict=False)
            addr = ipaddress.ip_interface(raw).ip
            rows = [
                f"Valid IPv{addr.version} address: {addr}",
                f"Compressed: {addr.compressed}",
                f"Private: {addr.is_private}",
                f"Global/Public-routable: {addr.is_global}",
                f"Loopback: {addr.is_loopback}",
                f"Network: {net}",
                f"Prefix: /{net.prefixlen}",
                f"Netmask: {net.netmask}",
                f"Broadcast: {net.broadcast_address}",
                f"Total addresses: {net.num_addresses}",
            ]
            for row in rows:
                ok(row)
            log("IP and Subnet Validation", "\\n".join(rows))
        except ValueError as exc:
            error(f"Invalid IP/CIDR: {exc}")
        return

    try:
        addr = ipaddress.ip_address(raw)
        rows = [
            f"Valid IPv{addr.version} address: {addr}",
            f"Compressed: {addr.compressed}",
            f"Private: {addr.is_private}",
            f"Global/Public-routable: {addr.is_global}",
            f"Loopback: {addr.is_loopback}",
            f"Multicast: {addr.is_multicast}",
            f"Link-local: {addr.is_link_local}",
            f"Reserved: {addr.is_reserved}",
        ]
        for row in rows:
            ok(row)
        log("IP Validator", "\\n".join(rows))
    except ValueError as exc:
        error(f"Invalid IP address or CIDR: {exc}")
def private_public_detector():
    heading("PRIVATE / PUBLIC IP DETECTOR")
    raw = ask("Enter an IP address: ")
    try:
        addr = ipaddress.ip_address(raw)
        if addr.is_loopback:
            kind = "Loopback (local address for this device)"
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
        log("Private/Public IP Detector", f"Address: {addr}\nClassification: {kind}")
    except ValueError:
        error("Invalid IP address. Example: 192.168.1.10 or 2001:4860:4860::8888")


def dns_lookup():
    heading("DNS LOOKUP")
    host = ask("Enter a domain/hostname (e.g. example.com): ").strip().rstrip(".")
    if not valid_domain(host):
        error("Invalid domain/hostname.")
        return
    try:
        results = socket.getaddrinfo(host, None)
        addresses = sorted({item[4][0] for item in results})
        if addresses:
            ok(f"DNS results for {host}:")
            for addr in addresses:
                print(f"  {C['cyan']}• {addr}{C['reset']}")
            log("DNS Lookup", f"Host: {host}\n" + "\n".join(addresses))
        else:
            warn("No addresses were found.")
    except socket.gaierror as exc:
        error(f"DNS lookup failed: {exc}")
        warn("Internet or DNS service may be unavailable.")
        log("DNS Lookup", f"Host: {host}\nFailed: {exc}")


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
        info("127.0.0.1 is the loopback address; it is not your Wi-Fi/LAN IP.")
    log("My Network Information", "\n".join(rows))


def connectivity_test():
    heading("TCP CONNECTIVITY TEST")
    host = ask("Hostname/domain (e.g. example.com): ").strip()
    if not valid_domain(host):
        error("Enter a valid hostname.")
        return
    port_raw = ask("Port [443]: ") or "443"
    try:
        port = int(port_raw)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        error("Port  1  65535-   ।")
        return
    start = datetime.datetime.now()
    try:
        with socket.create_connection((host, port), timeout=5):
            elapsed = (datetime.datetime.now() - start).total_seconds()
            ok(f"TCP connection successful: {host}:{port}")
            ok(f"Elapsed: {elapsed:.3f} seconds")
            log("Connectivity Test", f"Target: {host}:{port}\nResult: Connected\nElapsed: {elapsed:.3f} seconds")
    except OSError as exc:
        error(f"Connection failed: {exc}")
        log("Connectivity Test", f"Target: {host}:{port}\nResult: Failed\nError: {exc}")


def wifi_information():
    heading("WI-FI INFORMATION")
    info("Termux:API and Android permissions may be required.")

    try:
        result = subprocess.run(
            ["termux-wifi-connectioninfo"],
            capture_output=True,
            text=True,
            timeout=8
        )

        if result.returncode != 0:
            error("Could not read Wi-Fi information.")
            details = (result.stderr or result.stdout).strip()
            if details:
                print(details)
            warn("Check the Termux:API app and Android permissions.")
            log("Wi-Fi Information", f"Command failed: {details}")
            return

        data = json.loads(result.stdout)

        ssid = data.get("ssid")
        ip = data.get("ip")
        state = str(data.get("supplicant_state", "")).upper()

        disconnected = (
            ssid in (None, "", "<unknown ssid>")
            or ip in (None, "", "0.0.0.0")
            or state in ("UNINITIALIZED", "DISCONNECTED", "INACTIVE")
        )

        if disconnected:
            warn("Wi-Fi Status: DISCONNECTED or information unavailable")
            print(f"{C['cyan']}SSID: {C['white']}Not connected / unavailable{C['reset']}")
            print(f"{C['cyan']}Wi-Fi IP: {C['white']}Unavailable{C['reset']}")
            info("Mobile data status is not checked by this feature.")
        else:
            ok("Wi-Fi Status: CONNECTED")
            keys = [
                "ssid", "bssid", "ip", "rssi",
                "link_speed_mbps", "frequency_mhz",
                "network_id", "supplicant_state"
            ]
            for key in keys:
                print(
                    f"{C['cyan']}{key}: "
                    f"{C['white']}{data.get(key, 'Unavailable')}"
                    f"{C['reset']}"
                )

        log("Wi-Fi Information", json.dumps(data, indent=2, ensure_ascii=False))

    except FileNotFoundError:
        error("termux-wifi-connectioninfo was not found.")
        info("Install the Termux package with: pkg install termux-api")
        info("A compatible Termux:API Android app is also required.")
        log("Wi-Fi Information", "Termux:API command not found")

    except subprocess.TimeoutExpired:
        error("The Wi-Fi command timed out.")
        log("Wi-Fi Information", "Command timeout")

    except json.JSONDecodeError:
        error("The Wi-Fi command did not return valid JSON.")
        log("Wi-Fi Information", "Invalid JSON output")

    except Exception as exc:
        error(f"Wi-Fi info error: {exc}")
        log("Wi-Fi Information", f"Error: {exc}")


def http_header_checker():
    heading("HTTP HEADER CHECKER")
    raw = ask("Public website URL (e.g. https://example.com): ")
    try:
        url = safe_public_url(raw)
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "OsmanCyberLab/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=8) as response:
                status, headers = response.status, response.headers
        except urllib.error.HTTPError as exc:
            status, headers = exc.code, exc.headers
        ok(f"URL: {url}")
        ok(f"HTTP Status: {status}")
        for key, value in headers.items():
            print(f"{C['cyan']}{key}: {C['white']}{value}{C['reset']}")
        details = f"URL: {url}\nHTTP Status: {status}\n" + "\n".join(f"{k}: {v}" for k, v in headers.items())
        log("HTTP Header Checker", details)
        info("This checks HTTP response headers only; it is not a full security audit.")
    except Exception as exc:
        error(f"Request failed: {exc}")
        log("HTTP Header Checker", f"URL: {raw}\nFailed: {exc}")


def export_report():
    heading("EXPORT NETWORK REPORT")
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"network_report_export_{stamp}.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{APP_NAME}\n")
            f.write(f"{VERSION}\n")
            f.write(f"Exported: {now()}\n")
            f.write("=" * 58 + "\n\n")
            if report_log:
                f.write("\n".join(report_log))
            else:
                try:
                    with open(REPORT_FILE, "r", encoding="utf-8") as source:
                        f.write(source.read())
                except FileNotFoundError:
                    f.write("No report entries yet.\n")
        ok(f"Export saved: {os.path.abspath(filename)}")
        info("Show the current folder with: pwd")
    except OSError as exc:
        error(f"Export failed: {exc}")


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
    score = 0
    for label, passed in checks.items():
        (ok if passed else warn)(label)
        score += int(passed)
    grade = "Weak" if len(password) < 8 or score <= 2 else ("Strong" if len(password) >= 12 and score >= 5 else "Moderate")
    print(f"\n{C['purple']}Estimated strength: {grade} ({score}/6 checks){C['reset']}")
    info("This is an approximate local check. The password is not transmitted or saved in a report.")


def ipv4_ipv6_validator():
    heading("IPV4 / IPV6 VALIDATOR")
    raw = ask("Enter an IP address: ")
    try:
        addr = ipaddress.ip_address(raw)
        ok(f"Valid IPv{addr.version}")
        ok(f"Canonical form: {addr.compressed}")
        ok(f"Private: {addr.is_private}")
        ok(f"Global: {addr.is_global}")
        ok(f"Loopback: {addr.is_loopback}")
        log("IPv4/IPv6 Validator", f"Address: {addr}\nVersion: IPv{addr.version}\nPrivate: {addr.is_private}\nGlobal: {addr.is_global}")
    except ValueError:
        error("Invalid IP. IPv4 example: 192.168.1.10")
        info("IPv6 example: 2001:4860:4860::8888")


def subnet_practice():
    heading("ADVANCED SUBNET PRACTICE")
    info("Offline practice; no network scan is performed.")
    raw = ask("Network/CIDR (e.g. 192.168.10.0/26): ")
    try:
        net = ipaddress.ip_network(raw, strict=False)
        rows = [
            f"Network: {net}", f"IP version: IPv{net.version}",
            f"Prefix: /{net.prefixlen}", f"Total addresses: {net.num_addresses}",
            f"Network address: {net.network_address}",
        ]
        if net.version == 4:
            rows += [f"Broadcast: {net.broadcast_address}", f"Netmask: {net.netmask}",
                     f"Wildcard: {ipaddress.IPv4Address(int(net.hostmask))}"]
            if net.prefixlen <= 30:
                rows += [f"First host: {net.network_address + 1}",
                         f"Last host: {net.broadcast_address - 1}",
                         f"Usable hosts: {max(0, net.num_addresses - 2)}"]
            elif net.prefixlen == 31:
                rows += ["Usable hosts: 2 (point-to-point /31)"]
            else:
                rows += ["Usable hosts: 1 address (/32)"]
        else:
            rows += ["Broadcast: IPv6 does not use broadcast addresses", f"Netmask: {net.netmask}"]
        for row in rows:
            ok(row)
        log("Advanced Subnet Practice", "\n".join(rows))
    except ValueError as exc:
        error(f"Invalid CIDR/network: {exc}")


def offline_practice_mode():
    while True:
        print(f"\n{C['purple']}╔════ OFFLINE NETWORKING PRACTICE ════╗{C['reset']}")
        options = [
            ("1", "Private IPv4 examples"),
            ("2", "Public IPv4 examples"),
            ("3", "Loopback examples"),
            ("4", "CIDR quick quiz"),
            ("5", "Exit practice mode"),
        ]
        for key, label in options:
            print(f"{C['cyan']} [{key}] {C['white']}{label}{C['reset']}")
        choice = ask("Choose: ")
        if choice == "1":
            print(f"{C['green']}Private IPv4 ranges:{C['reset']}")
            print("  10.0.0.0/8\n  172.16.0.0/12\n  192.168.0.0/16")
            info("Example: 192.168.1.20 is private.")
        elif choice == "2":
            print(f"{C['green']}Example public addresses for learning:{C['reset']}")
            print("  8.8.8.8 (Google Public DNS)\n  1.1.1.1 (Cloudflare DNS)")
            info("A public address may still be unreachable due to routing or firewall rules.")
        elif choice == "3":
            print(f"{C['green']}Loopback addresses:{C['reset']}")
            print("  IPv4: 127.0.0.1\n  IPv6: ::1")
            info("These are loopback addresses used by this device.")
        elif choice == "4":
            print("Question: 192.168.1.0/24 contains how many IPv4 addresses?")
            answer = ask("Answer: ")
            if answer.strip() == "256":
                ok("Correct! /24 has 256 total addresses; traditionally 254 usable hosts.")
            else:
                warn("Correct answer: 256 total addresses; typically 254 usable hosts.")
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
        warn("This sample password is displayed on screen; do not use it for sensitive accounts.")
        info("The sample password is not saved to the report.")
    except ValueError:
        error("Length must be a number.")



def ssl_certificate_checker():
    heading("SSL/TLS CERTIFICATE CHECKER")

    host = ask("Domain name (e.g. example.com): ").strip()
    host = host.removeprefix("https://").removeprefix("http://")
    host = host.split("/")[0].split(":")[0].strip()

    if not valid_domain(host):
        error("Enter a valid domain name.")
        return

    import ssl

    context = ssl.create_default_context()
    info("Connecting with certificate verification enabled...")

    try:
        with socket.create_connection((host, 443), timeout=8) as raw_socket:
            with context.wrap_socket(raw_socket, server_hostname=host) as tls_socket:
                cert = tls_socket.getpeercert()
                cipher = tls_socket.cipher()
                version = tls_socket.version()

        subject = dict(item[0] for item in cert.get("subject", ()))
        issuer = dict(item[0] for item in cert.get("issuer", ()))
        expires = cert.get("notAfter", "Unknown")
        expiry_date = datetime.datetime.strptime(
            expires, "%b %d %H:%M:%S %Y %Z"
        ) if expires != "Unknown" else None

        ok(f"TLS connection verified for {host}")
        info(f"TLS version: {version or 'Unknown'}")
        info(f"Cipher: {cipher[0] if cipher else 'Unknown'}")
        info(f"Certificate subject: {subject.get('commonName', 'Not provided')}")
        info(f"Certificate issuer: {issuer.get('commonName', 'Not provided')}")
        info(f"Certificate expires: {expires}")

        if expiry_date:
            remaining = expiry_date.replace(tzinfo=datetime.timezone.utc) - datetime.datetime.now(datetime.timezone.utc)
            if remaining.total_seconds() < 0:
                warn("Certificate expiry date is in the past.")
            else:
                ok(f"Approximate time until expiry: {remaining.days} days")

        log("SSL/TLS Certificate Check", {
            "host": host,
            "tls_version": version,
            "cipher": cipher[0] if cipher else None,
            "issuer": issuer.get("commonName", "Not provided"),
            "expires": expires,
        })

    except (OSError, ssl.SSLError, ValueError) as exc:
        error(f"TLS check failed: {exc}")
        info("Check the domain, internet connection, and server certificate.")

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
        "19": ssl_certificate_checker,
    }
    while True:
        banner()
        menu = [
            ("1", "Check Public IP Address", "cyan"),
            ("2", "Network Calculator", "green"),
            ("3", "View Saved Report", "blue"),
            ("4", "IP Range Generator", "cyan"),
            ("5", "IP & Subnet Validator", "green"),
            ("6", "Private/Public IP Detector", "yellow"),
            ("7", "DNS Lookup", "cyan"),
            ("8", "My Network Information", "blue"),
            ("9", "Connectivity Test (TCP)", "green"),
            ("10", "Wi-Fi Information (Termux:API)", "cyan"),
            ("11", "HTTP Header Checker (public sites)", "yellow"),
            ("12", "Export Network Report", "blue"),
            ("13", "Exit", "red"),
            ("14", "Password Strength Checker", "purple"),
            ("15", "IPv4 / IPv6 Validator", "cyan"),
            ("16", "Advanced Subnet Practice", "green"),
            ("17", "Offline Networking Practice", "purple"),
            ("18", "Generate Sample Password", "yellow"),
            ("19", "SSL/TLS Certificate Checker", "cyan"),
        ]
        for key, label, color in menu:
            print(f" {C[color]}[{key:>2}]{C['reset']} {C['white']}{label}{C['reset']}")
        print(C["purple"] + "═" * 58 + C["reset"])
        choice = ask("Choose option: ")
        if choice == "13":
            print(f"\n{C['purple']}🐺 OSMAN CYBER LAB is shutting down. Keep learning!{C['reset']}")
            break
        action = actions.get(choice)
        if action:
            action()
            pause()
        else:
            error("Invalid option. Please choose a number from 1 to 19.")
            pause()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['yellow']}OSMAN CYBER LAB has been closed.{C['reset']}")
