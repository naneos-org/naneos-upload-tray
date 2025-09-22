import threading

import pystray  # type: ignore
from naneos.manager.naneos_device_manager import NaneosDeviceManager
from PIL import Image
from pystray import Menu
from pystray import MenuItem as Item

shutdown_event = threading.Event()


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

    icon = pystray.Icon("Naneos Icon", icon=Image.open("img/naneos_icon.png"), menu=menu)

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
    main()
