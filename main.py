import os
import sys
import threading

import pystray  # type: ignore
from naneos.manager.naneos_device_manager import NaneosDeviceManager
from PIL import Image
from pystray import Menu
from pystray import MenuItem as Item

shutdown_event = threading.Event()


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

        base_items = [Item("Quit", on_quit)]

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

    menu = Menu(Item("Quit", on_quit))

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
