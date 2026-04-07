import asyncio
import json
import logging
import socket
import threading
import websockets

from PIL import Image, ImageDraw
from pynput.mouse import Button, Controller
from pystray import Icon, Menu, MenuItem

# ── SETUP ──────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("touchpad")

mouse = Controller()

WEBSOCKET_PORT = 8765
DISCOVERY_PORT = 8766

left_pressed = False
right_pressed = False
accumulated_dx = 0.0
accumulated_dy = 0.0

# Global reference to tray icon for updating it
tray_icon = None
connected = False


# ── HELPER ─────────────────────────────────────────
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


# ── TRAY ICON ───────────────────────────────────────
def create_tray_image(is_connected: bool) -> Image:
    """
    Creates a simple colored circle as the tray icon.
    Green = phone connected, grey = waiting for connection.
    """
    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    color = (34, 197, 94) if is_connected else (156, 163, 175)
    draw.ellipse([8, 8, size - 8, size - 8], fill=color)

    return image


def update_tray_status(is_connected: bool):
    """Update tray icon color based on connection status."""
    global tray_icon, connected
    connected = is_connected
    if tray_icon is not None:
        tray_icon.icon = create_tray_image(is_connected)
        tray_icon.title = (
            "Touchpad — Phone connected"
            if is_connected
            else "Touchpad — Waiting for phone"
        )


def on_quit(icon, item):
    """Called when user clicks Quit in tray menu."""
    icon.stop()


def run_tray():
    """Runs the tray icon in its own thread."""
    global tray_icon
    tray_icon = Icon(
        name="Touchpad",
        icon=create_tray_image(False),
        title="Touchpad — Waiting for phone",
        menu=Menu(
            MenuItem(
                text=f"PC IP: {get_local_ip()}:{WEBSOCKET_PORT}",
                action=None,
                enabled=False,
            ),
            Menu.SEPARATOR,
            MenuItem("Quit", on_quit),
        ),
    )
    # Show startup notification after 1 second
    # Delay needed because the tray icon needs to be running first
    def show_startup_notification():
        import time
        time.sleep(1)
        tray_icon.notify(
            "Ready to connect. Open the app on your phone.",
            "Touchpad Service Started"
        )

    notification_thread = threading.Thread(
        target=show_startup_notification,
        daemon=True
    )
    notification_thread.start()

    tray_icon.run()


# ── MESSAGE HANDLER ────────────────────────────────
async def handle_message(message: str):
    global left_pressed, right_pressed, accumulated_dx, accumulated_dy
    try:
        data = json.loads(message)
        event_type = data.get("type")

        if event_type == "move":
            accumulated_dx += data.get("dx", 0)
            accumulated_dy += data.get("dy", 0)

            move_x = int(accumulated_dx)
            move_y = int(accumulated_dy)

            if move_x != 0 or move_y != 0:
                mouse.move(move_x, move_y)
                accumulated_dx -= move_x
                accumulated_dy -= move_y

        elif event_type == "left_down":
            left_pressed = True
            mouse.press(Button.left)
            log.info("Left button down")

        elif event_type == "left_up":
            left_pressed = False
            mouse.release(Button.left)
            log.info("Left button up")

        elif event_type == "right_down":
            right_pressed = True
            mouse.press(Button.right)
            log.info("Right button down")

        elif event_type == "right_up":
            right_pressed = False
            mouse.release(Button.right)
            log.info("Right button up")

        elif event_type == "double_click":
            mouse.click(Button.left, 2)
            log.info("Double click")

        elif event_type == "scroll":
            dx = data.get("dx", 0)
            dy = data.get("dy", 0)
            mouse.scroll(dx * 0.20, dy * 0.20)

        elif event_type == "left_click":
            mouse.press(Button.left)
            mouse.release(Button.left)
            log.info("Left click")

        elif event_type == "right_click":
            mouse.press(Button.right)
            mouse.release(Button.right)
            log.info("Right click")

        else:
            log.warning(f"Unknown event type: {event_type}")

    except json.JSONDecodeError:
        log.error(f"Invalid message: {message}")


# ── WEBSOCKET HANDLER ──────────────────────────────
async def on_connect(websocket):
    global left_pressed, right_pressed, accumulated_dx, accumulated_dy
    client_ip = websocket.remote_address[0]
    log.info(f"Phone connected from {client_ip}")
    update_tray_status(True)

    try:
        async for message in websocket:
            await handle_message(message)

    except websockets.exceptions.ConnectionClosedOK:
        log.info("Phone disconnected cleanly")

    except websockets.exceptions.ConnectionClosedError:
        log.warning("Phone disconnected unexpectedly")

    finally:
        update_tray_status(False)
        accumulated_dx = 0.0
        accumulated_dy = 0.0
        if left_pressed:
            mouse.release(Button.left)
            left_pressed = False
            log.info("Released stuck left button on disconnect")
        if right_pressed:
            mouse.release(Button.right)
            right_pressed = False
            log.info("Released stuck right button on disconnect")


# ── UDP DISCOVERY SERVER ───────────────────────────
async def discovery_server(local_ip: str):
    loop = asyncio.get_event_loop()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", DISCOVERY_PORT))
    sock.setblocking(False)

    log.info(f"Discovery server listening on port {DISCOVERY_PORT}")

    while True:
        try:
            data, addr = await loop.run_in_executor(
                None, lambda: sock.recvfrom(1024)
            )
            message = data.decode("utf-8").strip()

            if message == "TOUCHPAD_DISCOVER":
                log.info(f"Discovery request from {addr[0]}")
                reply = json.dumps({
                    "ip": local_ip,
                    "port": WEBSOCKET_PORT
                })
                sock.sendto(reply.encode("utf-8"), addr)
                log.info(f"Replied with {local_ip}:{WEBSOCKET_PORT}")

        except BlockingIOError:
            await asyncio.sleep(0.1)

        except Exception as e:
            log.error(f"Discovery error: {e}")
            await asyncio.sleep(1)


# ── MAIN ───────────────────────────────────────────
async def main():
    local_ip = get_local_ip()

    log.info(f"TouchpadService started — {local_ip}:{WEBSOCKET_PORT}")

    await asyncio.gather(
        websockets.serve(on_connect, "0.0.0.0", WEBSOCKET_PORT),
        discovery_server(local_ip),
    )


def start_asyncio():
    """Run the asyncio event loop in a background thread."""
    asyncio.run(main())


if __name__ == "__main__":
    # Start asyncio server in background thread
    server_thread = threading.Thread(target=start_asyncio, daemon=True)
    server_thread.start()

    # Run tray icon on main thread — pystray requires this on Windows
    run_tray()