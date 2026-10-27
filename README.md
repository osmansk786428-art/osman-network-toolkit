# 🐺 OSMAN CYBER LAB

## Network Toolkit V22 — Premium Wolf Edition

> **An educational Python networking toolkit for Termux and compatible Python environments.**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Termux%20%7C%20Linux-green.svg)](https://termux.dev/)
[![Version](https://img.shields.io/badge/Version-V22-orange.svg)](https://github.com/osmansk786428-art/osman-network-toolkit/releases/tag/V22.0.0)
[![Security](https://img.shields.io/badge/Security-Educational-red.svg)](#security-notes-and-limitations)

---

## 📚 Table of Contents

- [✨ Features](#-features)
- [📋 Requirements](#-requirements)
- [📥 Download the Project](#-download-the-project)
- [🚀 Installation](#-installation)
- [▶️ Run the Toolkit](#️-run-the-toolkit)
- [🧪 Run the Tests](#-run-the-tests)
- [📁 Project Structure](#-project-structure)
- [🔐 Security Notes and Limitations](#-security-notes-and-limitations)
- [📌 Project Status](#-project-status)
- [👨‍💻 Author](#-author)
- [📄 License](#-license)

---

## ✨ Features

The toolkit provides educational networking and HTTP inspection features.

- [x] HTTP response status checker
- [x] HTTP response header inspection
- [x] Security-header inspection
- [x] Safe HTTP request adapter
- [x] Public destination validation
- [x] DNS resolution checks
- [x] Private and loopback address rejection
- [x] HTTPS certificate verification
- [x] Redirect detection without automatic redirect following
- [x] Bounded response-body reading
- [x] Automated regression test suite

---

## 📋 Requirements

| Requirement | Description |
|---|---|
| **Python** | Python 3 |
| **Platform** | Termux or another compatible Python environment |
| **Internet** | Required for live HTTP checks |
| **Additional packages** | No third-party package required for the standard-library-based components |

> **Note:** The toolkit's live network features require an internet connection.

---

## 📥 Download the Project

### Option 1 — Download from GitHub

1. Open the [OSMAN CYBER LAB repository](https://github.com/osmansk786428-art/osman-network-toolkit).
2. Open the **Releases** section.
3. Select the **V22.0.0** release.
4. Download the source-code ZIP archive.
5. Extract the archive.
6. Open a terminal in the extracted project directory.

### Option 2 — Download using Termux

```bash
mkdir -p ~/downloads
cd ~/downloads

curl -fL \
  https://github.com/osmansk786428-art/osman-network-toolkit/archive/refs/tags/V22.0.0.zip \
  -o osman-network-toolkit-22.0.0.zip
### 1. ZIP File Verify

```bash
unzip -t osman-network-toolkit-22.0.0.zip
```

### 2. ZIP File Extract

```bash
unzip osman-network-toolkit-22.0.0.zip
```

### 3. Extracted Folder-e Jaow

```bash
cd osman-network-toolkit-22.0.0
```

### 4. Required Packages Install

```bash
pkg install curl unzip git python -y
```

### 5. GitHub Repository Clone

```bash
git clone https://github.com/osmansk786428-art/osman-network-toolkit.git
```

### 6. Project Folder-e Jaow

```bash
cd osman-network-toolkit
```

### 7. Python Version Check

```bash
python --version
```

### 8. Network Toolkit V22 Run

```bash
python Network-Toolkit-V22.py
```

### 9. Python Syntax Check

```bash
python -m py_compile \
  Network-Toolkit.py \
  Network-Toolkit-V22.py \
  safe_network.py \
  safe_http_adapter.py
```

### 10. V22 Regression Tests Run

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

### 11. Legacy Tests Run

```bash
python -m unittest discover -s tests -v
```
