# Touchpad Service

Backend service for PocketMouse. This application allows a mobile device to control a computer's mouse by acting as a wireless touchpad.

---

## Quick Start

### Option 1 — Use the prebuilt executable (recommended)

1. Go to the Releases section of this repository
2. Download the latest `.exe` file
3. Run the executable (no installation required)
4. Ensure your computer and phone are on the same Wi-Fi network
5. Open the PocketMouse app and connect

The application will run in the system tray.

---

### Option 2 — Run from source

#### Requirements

* Python 3.9 or higher

#### Install dependencies

```bash id="q7z2l1"
pip install websockets pynput pystray pillow
```

#### Run

```bash id="x92kdl"
python touchpad_service.py
```

---

## Overview

Touchpad Service runs locally on your computer and listens for input events sent from a mobile client over a WebSocket connection. These events are translated into native mouse actions using the system input API.

The service also includes a UDP-based discovery mechanism, allowing the mobile app to automatically detect the host machine on the same network.

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

## Network Configuration

| Purpose          | Port |
| ---------------- | ---- |
| WebSocket server | 8765 |
| UDP discovery    | 8766 |

If connection issues occur, ensure these ports are allowed through your firewall.

---

## Discovery Protocol

Client sends:

```id="l2k9q3"
TOUCHPAD_DISCOVER
```

Server responds with:

```json id="z81a9x"
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

## Distribution

Prebuilt executables are available in the Releases section.

You can also build the executable yourself using PyInstaller.

---

## License

MIT License

---

## Contributing

Contributions and suggestions are welcome.
