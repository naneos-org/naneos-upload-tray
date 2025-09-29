import tkinter as tk


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
