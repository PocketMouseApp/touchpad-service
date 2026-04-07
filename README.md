# Touchpad Service

Backend service for PocketMouse. This application allows a mobile device to control a computer's mouse by acting as a wireless touchpad.

---

## Overview

Touchpad Service runs locally on your computer and listens for input events sent from a mobile client over a WebSocket connection. These events are translated into native mouse actions using the system input API.

The service also includes a lightweight UDP-based discovery mechanism, allowing the mobile app to automatically detect the host machine on the same network.

---

## Features

* Real-time cursor movement
* Left, right, and middle mouse button support
* Click, double-click, and scroll input
* Automatic device discovery over local network
* System tray integration with connection status
* No external servers or cloud dependencies

---

## Privacy

This application does not collect, store, or transmit any personal data.

* All communication happens locally within your network
* No data is sent to external servers
* The source code is publicly available for inspection

---

## Architecture

Mobile client (Flutter) communicates with this service over WebSocket. The service processes incoming events and executes corresponding mouse actions on the host system.

---

## Getting Started

### Requirements

* Python 3.9 or higher

### Installation

Install dependencies:

```bash
pip install websockets pynput pystray pillow pyinstaller
```

### Running the service

```bash
python touchpad_service.py
```

Once started, the application will run in the system tray and display the local IP address and port.

---

## Usage

1. Ensure your computer and mobile device are connected to the same network
2. Launch the Touchpad Service
3. Open the PocketMouse app on your phone
4. The app will automatically discover and connect to the service

---

## Network Configuration

| Purpose          | Port |
| ---------------- | ---- |
| WebSocket server | 8765 |
| UDP discovery    | 8766 |

If connection issues occur, ensure these ports are allowed through your firewall.

---

## Discovery Protocol

The mobile client sends a UDP message:

```
TOUCHPAD_DISCOVER
```

The service responds with:

```json
{
  "ip": "<local_ip>",
  "port": 8765
}
```

---

## Supported Events

* `move`
* `left_down`
* `left_up`
* `right_down`
* `right_up`
* `left_click`
* `right_click`
* `double_click`
* `scroll`

---

## System Tray

The application runs in the system tray and provides:

* Connection status indicator
* Local IP address and port
* Option to exit the application

---

## Distribution

Prebuilt executables are available in the Releases section for users who prefer not to run the application from source.

---

## Contributing

Contributions and suggestions are welcome.
