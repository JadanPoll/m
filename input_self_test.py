"""Visible local target used to verify Firefly's real Windows input path."""
import tkinter as tk
import sys

EXPECTED = sys.argv[1] if len(sys.argv) > 1 else "firefly"
root = tk.Tk()
root.title("Firefly Input Self-Test")
root.geometry("520x140+120+120")
root.attributes("-topmost", True)
value = tk.StringVar()
tk.Label(root, text="Waiting for Firefly keyboard input…", font=("Segoe UI", 13)).pack(pady=(18, 8))
entry = tk.Entry(root, textvariable=value, font=("Segoe UI", 16), width=34)
entry.pack()

def check(*_args):
    if value.get() == EXPECTED:
        print("PASS: Firefly delivered text through the Windows input path", flush=True)
        root.after(100, root.destroy)

value.trace_add("write", check)
root.after(150, lambda: (root.focus_force(), entry.focus_force()))
root.after(30000, lambda: (print(f"FAIL: received {value.get()!r}", flush=True), root.destroy()))
root.mainloop()
