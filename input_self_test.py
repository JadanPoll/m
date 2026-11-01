"""Visible local target used to verify Firefly's real Windows input path."""
import tkinter as tk
import sys
import ctypes
from ctypes import wintypes

EXPECTED = sys.argv[1] if len(sys.argv) > 1 else "firefly"
INITIAL = next((arg.split("=", 1)[1] for arg in sys.argv[2:] if arg.startswith("--initial=")), "")
CLIPBOARD = next((arg.split("=", 1)[1] for arg in sys.argv[2:] if arg.startswith("--clipboard=")), None)


def set_clipboard_text(text: str) -> None:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    encoded = (text + "\0").encode("utf-16-le")
    kernel32.GlobalAlloc.argtypes = (wintypes.UINT, ctypes.c_size_t)
    kernel32.GlobalAlloc.restype = wintypes.HANDLE
    kernel32.GlobalLock.argtypes = (wintypes.HANDLE,)
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = (wintypes.HANDLE,)
    user32.OpenClipboard.argtypes = (wintypes.HWND,)
    user32.SetClipboardData.argtypes = (wintypes.UINT, wintypes.HANDLE)
    user32.SetClipboardData.restype = wintypes.HANDLE
    handle = kernel32.GlobalAlloc(0x0002, len(encoded))
    pointer = kernel32.GlobalLock(handle)
    ctypes.memmove(pointer, encoded, len(encoded))
    kernel32.GlobalUnlock(handle)
    if not user32.OpenClipboard(None):
        raise RuntimeError("Could not open Windows clipboard")
    try:
        user32.EmptyClipboard()
        if not user32.SetClipboardData(13, handle):
            raise RuntimeError("Could not set Windows clipboard text")
        handle = None  # Clipboard now owns the allocation.
    finally:
        user32.CloseClipboard()
        if handle:
            kernel32.GlobalFree(handle)
root = tk.Tk()
root.title("Firefly Input Self-Test")
root.geometry("520x140+120+120")
root.attributes("-topmost", True)
value = tk.StringVar(value=INITIAL)
tk.Label(root, text="Waiting for Firefly keyboard input…", font=("Segoe UI", 13)).pack(pady=(18, 8))
entry = tk.Entry(root, textvariable=value, font=("Segoe UI", 16), width=34)
entry.pack()
if CLIPBOARD is not None:
    set_clipboard_text(CLIPBOARD)

def check(*_args):
    if value.get() == EXPECTED:
        print("PASS: Firefly delivered text through the Windows input path", flush=True)
        root.after(100, root.destroy)

value.trace_add("write", check)
root.after(150, lambda: (root.focus_force(), entry.focus_force(), entry.icursor("end")))
root.after(30000, lambda: (print(f"FAIL: received {value.get()!r}", flush=True), root.destroy()))
root.mainloop()


