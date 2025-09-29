import atexit
import os
import socket
import sys
import threading
import tkinter as tk

import pystray  # type: ignore
from func_timeout import FunctionTimedOut, func_timeout  # type: ignore
from naneos.manager.naneos_device_manager import NaneosDeviceManager
from PIL import Image
from pystray import Menu
from pystray import MenuItem as Item
from wakepy import keep

VERSION = "1.0.1"
# Is it possible to take the version from the pyproject.toml
DEFAULT_LOCK_PORT = 52721  # fix port for single instance lock
shutdown_event = threading.Event()


class SingleInstance:
    def __init__(self):
        self.port = DEFAULT_LOCK_PORT
        self.sock = None

    def acquire(self) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", self.port))
            s.listen(1)
        except OSError:
            return False
        self.sock = s
        atexit.register(self.release)
        return True

    def release(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


def resource_path(rel_path: str) -> str:
    """Gibt den richtigen Pfad zu Ressourcen zurück (PyInstaller kompatibel)."""
    if hasattr(sys, "_MEIPASS"):  # beim PyInstaller-Build
        return os.path.join(sys._MEIPASS, rel_path)  # type: ignore
    return os.path.join(os.path.dirname(__file__), rel_path)


def refresh_menu():
    """Erzeugt das Menü neu und weist es dem Icon zu"""
    global icon, manager

    while not shutdown_event.is_set():
        ble_items = []
        usb_items = []
        ble_devices = manager.get_connected_ble_devices()
        usb_devices = manager.get_connected_serial_devices()

        if ble_devices:
            ble_items = [Item(f"BLE: {dev}", None, enabled=False) for dev in ble_devices]
        if usb_devices:
            usb_items = [Item(f"USB: {dev}", None, enabled=False) for dev in usb_devices]

        base_items = [Item(f"Tool-Version: {VERSION}", None, enabled=False), Item("Quit", on_quit)]

        icon.menu = Menu(*(usb_items + ble_items + base_items))
        icon.update_menu()

        shutdown_event.wait(timeout=1.0)


def _graceful_shutdown(icon):
    shutdown_event.set()

    try:
        manager.stop()
    except Exception as e:
        print(f"[on_quit] manager.stop() Error: {e}", file=sys.stderr)

    try:
        manager.join(timeout=9)
    except Exception as e:
        print(f"[on_quit] manager.join() Error: {e}", file=sys.stderr)

    print("Quitting...")

    try:
        icon.stop()
    except Exception as e:
        print(f"[on_quit] icon.stop() Error: {e}", file=sys.stderr)


def on_quit(icon, item):
    print("Quit menu item clicked.")
    try:
        func_timeout(10, _graceful_shutdown, args=(icon,))
        os._exit(0)
    except FunctionTimedOut:
        print("[on_quit] Shutdown > 10s, hard shutdown.", file=sys.stderr)
        os._exit(1)


def toast(
    message: str,
    title: str | None = None,
    duration_ms: int = 3000,
    corner: str = "bottom-right",
    alpha: float = 0.8,
):
    """Einfacher Toast, blockiert bis er wieder verschwindet."""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    try:
        root.attributes("-alpha", alpha)
    except tk.TclError:
        pass  # not supported on some systems

    frame = tk.Frame(root, bg="black")
    frame.pack()

    if title:
        tk.Label(frame, text=title, bg="black", fg="white", font=("Helvetica", 50, "bold")).pack(
            anchor="w", padx=12, pady=(10, 0)
        )
    tk.Label(frame, text=message, bg="black", fg="white", font=("Helvetica", 40)).pack(
        anchor="w", padx=12, pady=(4, 10)
    )

    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    m = 20
    if corner == "bottom-right":
        x, y = sw - w - m, sh - h - m
    elif corner == "bottom-left":
        x, y = m, sh - h - m
    elif corner == "top-right":
        x, y = sw - w - m, m
    elif corner == "center":
        x, y = (sw - w) // 2, (sh - h) // 2
    else:  # top-left
        x, y = m, m
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.after(duration_ms, root.destroy)
    root.mainloop()


def main():
    global icon, manager

    menu = Menu([Item(f"Tool-Version: {VERSION}", None, enabled=False), Item("Quit", on_quit)])

    icon_path = resource_path("img/naneos_icon.png")
    icon = pystray.Icon("Naneos Icon", icon=Image.open(icon_path), menu=menu)

    manager = NaneosDeviceManager(gathering_interval_seconds=15)
    manager.start()

    refresh_thread = threading.Thread(target=refresh_menu)
    refresh_thread.start()

    try:
        icon.run()
    finally:
        shutdown_event.set()
        refresh_thread.join(timeout=5.0)


if __name__ == "__main__":
    instance = SingleInstance()
    if not instance.acquire():
        toast(
            "Another instance is already running.",
            title="Naneos Upload Tray",
            duration_ms=2500,
            corner="center",
        )
        print("Another instance is already running. Exiting.")
        sys.exit(0)

    toast(
        "Tool is running as tray icon.",
        title="Naneos Upload Tray",
        duration_ms=2500,
        corner="center",
    )

    with keep.running():
        main()
