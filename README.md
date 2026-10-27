# 🐺 OSMAN CYBER LAB

## Network Toolkit V22 — Premium Wolf Edition

An educational Python networking toolkit designed for Termux and compatible Python environments.

## ✨ Features

- HTTP response status checker
- HTTP response header inspection
- Security-header inspection
- Safe HTTP request adapter
- Public destination validation
- DNS resolution checks
- Private and loopback address rejection
- HTTPS certificate verification
- Redirect detection without automatic redirect following
- Bounded response-body reading
- Automated regression test suite

## 📋 Requirements

- Python 3
- Termux or another compatible Python environment
- Internet access for live HTTP checks

No third-party Python package is required for the standard-library-based components.

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/osmansk786428-art/osman-network-toolkit.git
cd osman-network-toolkit
```

## ▶️ Run the Toolkit

From the project directory, run:

```bash
python Network-Toolkit-V22.py
```

## 🧪 Run the Regression Tests

Run the following command from the directory containing the test files:

```bash
python -m unittest -v \
  test_network_toolkit.py \
  test_network_toolkit_extra.py \
  test_pinned_connections.py \
  test_safe_http_adapter.py \
  test_safe_network.py \
  test_safe_request_methods.py \
  test_tls_verification.py \
  test_v22_security.py \
  test_v22_ui.py
```

## 🔐 Security Notes and Limitations

- Security safeguards reduce certain risks but do not guarantee complete protection.
- Security-header checks are informational and are not a complete security audit.
- HTTPS certificate verification should remain enabled.
- Passing the test suite does not prove the software is vulnerability-free.

Use this toolkit only on systems you own or are authorized to test.

## 📁 Main Project Files

| File | Purpose |
|---|---|
| `Network-Toolkit-V22.py` | Main terminal toolkit |
| `safe_network.py` | Validated network requests |
| `safe_http_adapter.py` | HTTP inspection adapter |
| `test_*.py` | Automated regression tests |

## 📌 Project Status

- Version: V22 release candidate
- Branch: `main`
- Test modules: 9
- Latest recorded test result: 68 tests passed
- Independent security audit: Not performed

## 👨‍💻 Author

**OSMAN CYBER LAB**

Educational networking and cybersecurity project.

## 📄 License

No license has been specified. Do not assume unrestricted reuse or redistribution.
