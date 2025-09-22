import os
import sys
import threading

import pystray  # type: ignore
from filelock import FileLock, Timeout
from naneos.manager.naneos_device_manager import NaneosDeviceManager
from PIL import Image
from pystray import Menu
from pystray import MenuItem as Item

VERSION = "1.0.0"
shutdown_event = threading.Event()

lock_path = os.path.join(os.path.expanduser("~"), ".naneos_upload_tray.lock")
lock = FileLock(lock_path)

try:
    lock.acquire(timeout=0.1)
except Timeout:
    print("App is already running!")
    sys.exit(0)


def resource_path(rel_path: str) -> str:
    """Gibt den richtigen Pfad zu Ressourcen zurück (PyInstaller kompatibel)."""
    if hasattr(sys, "_MEIPASS"):  # beim PyInstaller-Build
        return os.path.join(sys._MEIPASS, rel_path)
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


def on_quit(icon, item):
    shutdown_event.set()

    manager.stop()
    manager.join()

    print("Quitting...")
    icon.stop()


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
    import multiprocessing

    multiprocessing.freeze_support()
    main()

    lock.release()
    try:
        os.remove(lock_path)
    except FileNotFoundError:
        pass
