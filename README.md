# Naneos-Upload-Tray

Naneos Manager running in the system tray.
This gets compiled and can be used by our customers.

## Pyinstaller

First you need to install pyinstaller as dev dependency.
```bash
uv add --dev pyinstaller
```

On Mac you can build the executable the following way:
```bash
uv run pyinstaller --onedir --noconsole --name naneos_upload_tray main.py --add-data "img:img"
```
This works when running the terminal application. For the app file I need to add some rights and sign it with an apple developer key.

On Windows it should work in the following way:
```bash
uv run pyinstaller --onefile --noconsole --name naneos_upload_tray main.py --add-data "img;img"
```