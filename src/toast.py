import tkinter as tk


def toast(
    message: str,
    title: str | None = None,
    duration_ms: int = 5000,
    corner: str = "bottom-right",
    alpha: float = 0.8,
    image_path: str | None = None,  # <--- optionales Bild
):
    """Einfacher Toast mit optionalem Bild, blockiert bis er wieder verschwindet."""
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    try:
        root.attributes("-alpha", alpha)
    except tk.TclError:
        pass  # not supported on some systems

    frame = tk.Frame(root, bg="black")
    frame.pack(padx=0, pady=0)

    text_frame = tk.Frame(frame, bg="black")
    text_frame.pack(side="top")

    if title:
        tk.Label(
            text_frame, text=title, bg="black", fg="white", font=("Helvetica", 50, "bold")
        ).pack(side="top")

    tk.Label(text_frame, text=message, bg="black", fg="white", font=("Helvetica", 40)).pack(
        side="top"
    )

    # Bild laden (falls vorhanden)
    img_label = None
    if image_path:
        try:
            img = tk.PhotoImage(file=image_path)
            img_label = tk.Label(frame, image=img, bg="black")
            img_label.image = img  # type: ignore
            img_label.pack(side="top", expand=True, fill="both", pady=10)
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")

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
