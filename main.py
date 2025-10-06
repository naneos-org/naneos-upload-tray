import os
import sys
import threading

import pystray  # type: ignore
from func_timeout import FunctionTimedOut, func_timeout  # type: ignore
from naneos.manager.naneos_device_manager import NaneosDeviceManager
from PIL import Image
from pystray import Menu
from pystray import MenuItem as Item
from wakepy import keep

from src.single_instance import SingleInstance
from src.toast import toast

VERSION = "1.0.3"

shutdown_event = threading.Event()


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

        seconds_left = manager.get_seconds_until_next_upload()
        if seconds_left is not None:
            seconds_item = [
                Item(f"Next upload in: {seconds_left:.0f} seconds", None, enabled=False)
            ]

        base_items = [Item(f"Tool-Version: {VERSION}", None, enabled=False), Item("Quit", on_quit)]

        icon.menu = Menu(*(usb_items + ble_items + seconds_item + base_items))
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
            duration_ms=3000,
            corner="center",
        )
        print("Another instance is already running. Exiting.")
        sys.exit(0)

    if sys.platform == "darwin":
        toast(
            "Tool is running as tray icon.\nYou can find it in the menu bar (top right).",
            title="Naneos Upload Tray",
            duration_ms=4000,
            corner="center",
            image_path=resource_path("img/screenshot_mac.png"),
        )
    elif sys.platform == "win32":
        toast(
            "Tool is running as tray icon.\nYou can find it in the system tray (bottom right).",
            title="Naneos Upload Tray",
            duration_ms=4000,
            corner="center",
            image_path=resource_path("img/screenshot_windows.png"),
        )

    with keep.running():
        main()
