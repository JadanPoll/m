"""Firefly Desk Keyboard — remote-safe Windows on-screen keyboard.

Runs with the Python included on this PC. No installation or network access.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import difflib
import json
import os
import subprocess
import struct
import sys
import time
import tkinter as tk
import zlib


APP_TITLE = "Firefly Desk Keyboard"
GUARD_MS = 300
NAV_GUARD_MS = 75
BG = "#07111f"
PANEL = "#0d1a2b"
KEY = "#17304c"
KEY_ALT = "#22445f"
INK = "#f5f8ff"
MUTED = "#91a4bd"
CYAN = "#57d9ff"
LIME = "#b7f34a"
RED = "#ff6e78"
ALPHA_IDLE = 0.24
ALPHA_ACTIVE = 0.88

COMMON_WORDS = tuple("""
the to and a of in is it you that for on with this I be are as have at or
from by not was but we they your can all will my one about would there their
what so up out if who get which go me when make like time no just him know
take people into year good some could them see other than then now look only
come its over think also back after use two how our work first well way even
new want because these give day most us hello help helpful here home thanks thank
please yes okay sorry today tomorrow tonight where why when firefly keyboard
remote desktop click paste control copy cut select search open close send
message write read next previous left right top bottom recommend word words
""".split())

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32

ULONG_PTR = wintypes.WPARAM
LRESULT = wintypes.LPARAM

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_PRIOR = 0x21
VK_NEXT = 0x22
VK_END = 0x23
VK_HOME = 0x24
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_DELETE = 0x2E
VK_CONTROL = 0x11
VK_V = 0x56
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOOLWINDOW = 0x00000080
GWL_EXSTYLE = -20
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SW_RESTORE = 9
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
HC_ACTION = 0
LLKHF_INJECTED = 0x10
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
LLMHF_INJECTED = 0x00000001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
WM_CHAR = 0x0102
WM_PASTE = 0x0302
WM_CLOSE = 0x0010
CF_UNICODETEXT = 13
SRCCOPY = 0x00CC0020
DIB_RGB_COLORS = 0
SPI_GETWORKAREA = 0x0030
GA_ROOT = 2


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", wintypes.DWORD), ("u", INPUT_UNION)]


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT), ("mouseData", wintypes.DWORD),
                ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG),
                ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class GUITHREADINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("hwndActive", wintypes.HWND), ("hwndFocus", wintypes.HWND),
                ("hwndCapture", wintypes.HWND), ("hwndMenuOwner", wintypes.HWND),
                ("hwndMoveSize", wintypes.HWND), ("hwndCaret", wintypes.HWND),
                ("rcCaret", RECT)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG), ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]


user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
user32.SetWindowsHookExW.argtypes = (ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD)
user32.SetWindowsHookExW.restype = wintypes.HANDLE
user32.CallNextHookEx.argtypes = (wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
user32.CallNextHookEx.restype = LRESULT
user32.UnhookWindowsHookEx.argtypes = (wintypes.HANDLE,)
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.OpenClipboard.argtypes = (wintypes.HWND,)
user32.OpenClipboard.restype = wintypes.BOOL
user32.GetClipboardData.argtypes = (wintypes.UINT,)
user32.GetClipboardData.restype = wintypes.HANDLE
user32.CloseClipboard.argtypes = ()
user32.CloseClipboard.restype = wintypes.BOOL
user32.VkKeyScanW.argtypes = (wintypes.WCHAR,)
user32.VkKeyScanW.restype = ctypes.c_short
kernel32.GlobalLock.argtypes = (wintypes.HANDLE,)
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = (wintypes.HANDLE,)
kernel32.GlobalUnlock.restype = wintypes.BOOL


def send_input(item: INPUT) -> bool:
    return user32.SendInput(1, ctypes.byref(item), ctypes.sizeof(INPUT)) == 1


def send_mouse_click(right: bool = False) -> bool:
    """Deliver a single mouse click using the supported Win32 SendInput API."""
    down = MOUSEEVENTF_RIGHTDOWN if right else MOUSEEVENTF_LEFTDOWN
    up = MOUSEEVENTF_RIGHTUP if right else MOUSEEVENTF_LEFTUP
    events = (INPUT * 2)(
        INPUT(type=0, mi=MOUSEINPUT(0, 0, 0, down, 0, 0)),
        INPUT(type=0, mi=MOUSEINPUT(0, 0, 0, up, 0, 0)),
    )
    return user32.SendInput(2, events, ctypes.sizeof(INPUT)) == 2


def send_unicode(text: str) -> bool:
    sent = True
    for char in text:
        units = char.encode("utf-16-le")
        for i in range(0, len(units), 2):
            unit = units[i] | (units[i + 1] << 8)
            sent = send_input(INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(0, unit, KEYEVENTF_UNICODE, 0, 0))) and sent
            sent = send_input(INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(0, unit, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, 0, 0))) and sent
    return sent


def send_vk(vk: int) -> bool:
    down = send_input(INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, 0, 0, 0, 0)))
    up = send_input(INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, 0)))
    return down and up


def send_ctrl_chord(vk: int) -> bool:
    events = (INPUT * 4)(
        INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(VK_CONTROL, 0, 0, 0, 0)),
        INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, 0, 0, 0, 0)),
        INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(vk, 0, KEYEVENTF_KEYUP, 0, 0)),
        INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, 0)),
    )
    return user32.SendInput(4, events, ctypes.sizeof(INPUT)) == 4


def paste_clipboard() -> bool:
    return send_ctrl_chord(VK_V)


def read_clipboard_text() -> str | None:
    """Read Unicode clipboard text without Tk's RDP-fragile clipboard bridge."""
    if not user32.OpenClipboard(None):
        return None
    try:
        handle = user32.GetClipboardData(CF_UNICODETEXT)
        if not handle:
            return None
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            return None
        try:
            return ctypes.wstring_at(pointer)
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def direct_text(hwnd: int, text: str) -> None:
    for char in text:
        units = char.encode("utf-16-le")
        for i in range(0, len(units), 2):
            unit = units[i] | (units[i + 1] << 8)
            user32.PostMessageW(hwnd, WM_CHAR, unit, 1)


def direct_vk(hwnd: int, vk: int) -> None:
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 1)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0xC0000001)


def direct_ctrl_chord(hwnd: int, vk: int) -> None:
    user32.PostMessageW(hwnd, WM_KEYDOWN, VK_CONTROL, 1)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, 1)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, 0xC0000001)
    user32.PostMessageW(hwnd, WM_KEYUP, VK_CONTROL, 0xC0000001)


def close_windows_osk() -> None:
    """Politely close only the legacy Windows OSK window when replacing it."""
    hwnd = user32.FindWindowW(None, "On-Screen Keyboard")
    if hwnd:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)


def close_existing_firefly() -> None:
    """Replace an older overlay instead of stacking multiple keyboards."""
    hwnd = user32.FindWindowW(None, APP_TITLE)
    if hwnd:
        # The first close arms the accidental-close guard; the second confirms
        # this deliberate same-app replacement.
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        time.sleep(0.36)
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
        time.sleep(0.12)


class FireflyKeyboard:
    def __init__(self) -> None:
        previous_foreground = user32.GetForegroundWindow()
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.configure(bg=BG)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", ALPHA_IDLE)
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.scale = 0.82
        self.dock_top = False
        self.shifted = False
        self.ctrl_held = False
        self.symbols = False
        self.last_action = ("", 0.0)
        self.blocked = 0
        self.inspecting = False
        self.preview_hover = "--hover-preview" in sys.argv
        self.preview_idle = "--idle-preview" in sys.argv
        self.pointer_inside = False
        self.header_buttons: list[tk.Button] = []
        self.quick_buttons: list[tk.Button] = []
        self.suggestion_buttons: list[tk.Button] = []
        self.suggestions: list[str] = []
        self.current_word = ""
        self.previous_word = ""
        self.learned_words: dict[str, int] = {}
        self.next_words: dict[str, dict[str, int]] = {}
        local_data = os.environ.get("LOCALAPPDATA", os.path.dirname(__file__))
        self.learning_path = os.path.join(local_data, "FireflyDeskKeyboard", "language.json")
        self.nav_buttons: list[tk.Button] = []
        self.nav_selected: tk.Button | None = None
        self.hook = None
        self.hook_proc = HOOKPROC(self._keyboard_hook)
        self.nav_hook = None
        self.nav_hook_proc = HOOKPROC(self._navigation_hook)
        self.mouse_hook = None
        self.mouse_hook_proc = HOOKPROC(self._mouse_navigation_hook)
        self.last_mouse_point: tuple[int, int] | None = None
        self.mouse_motion_accum = [0, 0]
        self.last_mouse_motion_at = 0.0
        self.last_nav_action = ("", 0.0)
        self.remote_nav_until = 0.0
        self.pointer_mode: str | None = None
        self.pointer_suppress_up = False
        self.pointer_suppress_until = 0.0
        self.pointer_suppress_key: int | None = None
        self.close_armed_until = 0.0
        self.event_rows: list[str] = []
        self.last_native_at = 0
        self.last_external_hwnd = previous_foreground
        self.target_var = tk.StringVar(value="Target: detecting…")
        self.guard_var = tk.StringVar(value=f"{GUARD_MS} ms guard · 0 blocked")
        self.inspect_var = tk.StringVar(value="Inspector off — click INSPECT, then press the unknown remote button")
        self._load_language_model()
        self._configure_window()
        self._build()
        self.root.after(150, self._apply_no_activate)
        self.root.after(180, self._install_navigation_hook)
        self.root.after(190, self._install_mouse_hook)
        self.root.after(250, self._update_target)
        self.root.after(300, self._poll_pointer)
        self.root.protocol("WM_DELETE_WINDOW", self.request_close)

    def _configure_window(self) -> None:
        work = RECT()
        user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(work), 0)
        work_w, work_h = work.right - work.left, work.bottom - work.top
        height = min(work_h, max(380, int(work_h * 0.49)))
        # Keep Win32 and Tk in the same DPI coordinate space. Explicitly making
        # this process DPI-aware gives Remote Desktop's 1536x863 viewport a
        # 2048x1152 work area, which places most of the keyboard off-screen.
        # Account for the native title bar as well as the requested client area.
        self.root.update_idletasks()
        hwnd = user32.GetAncestor(self.root.winfo_id(), GA_ROOT) or self.root.winfo_id()
        outer = RECT()
        client = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(outer))
        user32.GetClientRect(hwnd, ctypes.byref(client))
        frame_w = max(0, (outer.right - outer.left) - (client.right - client.left))
        frame_h = max(0, (outer.bottom - outer.top) - (client.bottom - client.top))
        y = work.top if self.dock_top else work.bottom - height - frame_h
        self.root.geometry(f"{work_w - frame_w}x{height}+{work.left}+{y}")
        self.root.minsize(780, 340)

    def _apply_no_activate(self) -> None:
        self.root.update_idletasks()
        hwnd = user32.GetAncestor(self.root.winfo_id(), GA_ROOT) or self.root.winfo_id()
        self.hwnd = hwnd
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE)

    def _build(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()
        self.header_buttons = []
        self.quick_buttons = []
        self.suggestion_buttons = []
        self.nav_buttons = []
        self.nav_selected = None
        title = tk.Frame(self.root, bg=BG, padx=16, pady=10)
        title.pack(fill="x")
        tk.Label(title, text="●", fg=LIME, bg=BG, font=("Segoe UI", 15, "bold")).pack(side="left")
        tk.Label(title, text="  FIREFLY DESK KEYBOARD", fg=INK, bg=BG,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(title, textvariable=self.target_var, fg=MUTED, bg=BG,
                 font=("Segoe UI", 10)).pack(side="left", padx=22)
        self._tool_button(title, "×", self.request_close, RED, 4).pack(side="right", padx=3)
        self._tool_button(title, "TOP/BOTTOM", self.toggle_dock, CYAN, 12).pack(side="right", padx=3)
        self._tool_button(title, "SIZE", self.toggle_size, CYAN, 7).pack(side="right", padx=3)
        self.inspect_button = self._tool_button(title, "INSPECT", self.toggle_inspector, LIME, 10)
        self.inspect_button.pack(side="right", padx=3)

        status = tk.Frame(self.root, bg=PANEL, padx=16, pady=7)
        status.pack(fill="x", padx=12)
        tk.Label(status, textvariable=self.guard_var, fg=LIME, bg=PANEL,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(status, textvariable=self.inspect_var, fg=CYAN, bg=PANEL,
                 anchor="e", font=("Segoe UI", 9)).pack(side="right")

        quick = tk.Frame(self.root, bg=BG, padx=12, pady=3)
        quick.pack(fill="x")
        tk.Label(quick, text="APPS / DESKTOP", fg=CYAN, bg=BG,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 8))
        shortcuts = [
            ("CMD", lambda: self._launch_app("cmd")),
            ("POWERSHELL", lambda: self._launch_app("powershell")),
            ("FILES", lambda: self._launch_app("explorer")),
            ("NOTEPAD", lambda: self._launch_app("notepad")),
            ("LEFT CLICK", lambda: self._arm_desktop_click("left")),
            ("RIGHT CLICK", lambda: self._arm_desktop_click("right")),
        ]
        for label, command in shortcuts:
            button = tk.Button(
                quick, text=label,
                command=lambda name=label, callback=command: self.activate("quick:" + name, callback),
                bg=KEY_ALT, fg=INK, activebackground=LIME, activeforeground=BG,
                relief="flat", bd=0, padx=5, pady=4, font=("Segoe UI", 9, "bold"), takefocus=0,
            )
            self.quick_buttons.append(button)
            self._register_nav_button(button, "quick:" + label)
            button.pack(side="left", expand=True, fill="x", padx=3)

        suggest = tk.Frame(self.root, bg=BG, padx=12, pady=5)
        suggest.pack(fill="x")
        tk.Label(suggest, text="WORDS", fg=CYAN, bg=BG,
                 font=("Segoe UI", 9, "bold"), width=7).pack(side="left")
        for index in range(3):
            button = tk.Button(
                suggest, text="…",
                command=lambda i=index: self.activate(
                    f"suggest:{i}", lambda: self._accept_suggestion(i)
                ),
                bg=KEY_ALT, fg=INK, activebackground=LIME, activeforeground=BG,
                relief="flat", bd=0, pady=4, font=("Segoe UI", 11, "bold"),
                takefocus=0,
            )
            self.suggestion_buttons.append(button)
            self._register_nav_button(button, f"suggest:{index}")
            button.pack(side="left", expand=True, fill="x", padx=4)
        self._update_suggestions()

        self.keyboard = tk.Frame(self.root, bg=BG, padx=10, pady=9)
        self.keyboard.pack(fill="both", expand=True)
        self._build_keys()

    def _launch_app(self, name: str) -> None:
        """Launch only the explicitly listed programs, never a user-supplied command."""
        commands = {
            "cmd": ["cmd.exe"],
            "powershell": ["powershell.exe", "-NoLogo"],
            "explorer": ["explorer.exe"],
            "notepad": ["notepad.exe"],
        }
        if name not in commands:
            return
        self.ctrl_held = False
        self.shifted = False
        try:
            flags = subprocess.CREATE_NEW_CONSOLE if name in ("cmd", "powershell") else 0
            subprocess.Popen(commands[name], creationflags=flags, cwd=os.path.expanduser("~"))
            self.guard_var.set("Opened " + name + " — click a field to type")
        except (OSError, ValueError) as error:
            self.guard_var.set("Could not open " + name + ": " + str(error)[:90])
        self._build_keys()

    def _arm_desktop_click(self, side: str) -> None:
        """Hide the overlay for one click anywhere, including beneath Firefly."""
        self.pointer_mode = side
        self.pointer_suppress_key = None
        self.root.withdraw()
        self.guard_var.set(side.upper() + " click armed — click/OK anywhere; ESC cancels")
        self.root.after(20000, self._cancel_pointer_click_if_pending)

    def _cancel_pointer_click_if_pending(self) -> None:
        if self.pointer_mode is not None:
            self.pointer_mode = None
            self._restore_after_click("Desktop click timed out — keyboard restored")

    def _restore_after_click(self, message: str) -> None:
        self.root.deiconify()
        self._apply_no_activate()
        self.guard_var.set(message)

    def _complete_desktop_click(self, side: str, point: tuple[int, int]) -> None:
        # Position is the physical remote event point, not a stale Tk selection.
        user32.SetCursorPos(*point)
        success = send_mouse_click(right=side == "right")
        self._restore_after_click(
            side.upper() + " click sent" if success else "Click failed (Windows input permission)"
        )

    def _tool_button(self, parent, text, command, color, width):
        button = tk.Button(parent, text=text, command=lambda: self.activate("tool:" + text, command),
                           bg=PANEL, fg=color, activebackground=KEY_ALT, activeforeground=INK,
                           relief="flat", bd=0, width=width, padx=5, pady=5,
                           font=("Segoe UI", 9, "bold"), takefocus=0)
        self.header_buttons.append(button)
        self._register_nav_button(button)
        return button

    def _register_nav_button(self, button: tk.Button, identity: str | None = None) -> tk.Button:
        # Stable semantic identity survives recreating keys on Shift/Ctrl changes.
        button._firefly_identity = identity or ("label:" + str(button.cget("text")))
        self.nav_buttons.append(button)
        button.configure(highlightthickness=0)
        button.bind("<Enter>", lambda _event, item=button: self._select_nav_button(item), add="+")
        return button

    def _load_language_model(self) -> None:
        try:
            with open(self.learning_path, "r", encoding="utf-8") as file:
                saved = json.load(file)
            self.learned_words = {
                str(word).lower(): int(count)
                for word, count in saved.get("words", {}).items()
            }
            self.next_words = {
                str(previous).lower(): {
                    str(word).lower(): int(count) for word, count in choices.items()
                }
                for previous, choices in saved.get("next", {}).items()
            }
        except (OSError, ValueError, TypeError):
            pass

        # Include words the user has already added to Windows' spelling
        # dictionary. Microsoft documents these as UTF-16 text files.
        spelling = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Spelling")
        for language in ("en-US", "neutral"):
            path = os.path.join(spelling, language, "default.dic")
            try:
                with open(path, "r", encoding="utf-16") as file:
                    for line in file:
                        word = line.strip().lower()
                        if word.isalpha() and len(word) > 1:
                            self.learned_words[word] = max(1, self.learned_words.get(word, 0))
            except (OSError, UnicodeError):
                pass

    def _save_language_model(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.learning_path), exist_ok=True)
            with open(self.learning_path, "w", encoding="utf-8") as file:
                json.dump({"words": self.learned_words, "next": self.next_words}, file)
        except OSError:
            pass

    def _learn_word(self, word: str) -> None:
        learned = word.strip("'").lower()
        if len(learned) < 2 or not learned.replace("'", "").isalpha():
            return
        self.learned_words[learned] = self.learned_words.get(learned, 0) + 1
        if self.previous_word:
            choices = self.next_words.setdefault(self.previous_word, {})
            choices[learned] = choices.get(learned, 0) + 1
        self.previous_word = learned

    def _update_suggestions(self) -> None:
        prefix = self.current_word.lower()
        common_rank = {word.lower(): index for index, word in enumerate(COMMON_WORDS)}
        vocabulary = set(common_rank) | set(self.learned_words)

        if prefix:
            completions = [word for word in vocabulary if word.startswith(prefix) and word != prefix]
            completions.sort(
                key=lambda word: (-self.learned_words.get(word, 0), common_rank.get(word, 99999), len(word))
            )
            corrections = difflib.get_close_matches(prefix, vocabulary, n=5, cutoff=0.65)
            strong_correction = (
                corrections
                and not completions
                and difflib.SequenceMatcher(None, prefix, corrections[0]).ratio() >= 0.66
            )
            choices = (corrections[:1] if strong_correction else []) + completions[:2] + [prefix] + corrections
        else:
            learned_next = self.next_words.get(self.previous_word, {})
            choices = sorted(learned_next, key=lambda word: -learned_next[word]) + ["the", "I", "you"]

        unique = []
        for word in choices:
            if word and word.lower() not in {item.lower() for item in unique}:
                shown = word.capitalize() if self.current_word[:1].isupper() else word
                unique.append(shown)
            if len(unique) == 3:
                break
        self.suggestions = unique
        for index, button in enumerate(self.suggestion_buttons):
            available = index < len(unique)
            button.configure(
                text=unique[index] if available else "—",
                state="normal" if available else "disabled",
                disabledforeground=MUTED,
            )

    def _track_text(self, text: str) -> None:
        for char in text:
            if char.isalpha() or (char == "'" and self.current_word):
                self.current_word += char
            else:
                if self.current_word:
                    self._learn_word(self.current_word)
                self.current_word = ""
        self._update_suggestions()

    def _accept_suggestion(self, index: int) -> None:
        if index >= len(self.suggestions):
            return
        suggestion = self.suggestions[index]
        typed = self.current_word

        def replace(hwnd: int) -> None:
            for _ in typed:
                direct_vk(hwnd, VK_BACK)
            self.root.after(
                70,
                lambda: self._send_to_target(
                    lambda: False,
                    lambda target: direct_text(target, suggestion + " "),
                ),
            )

        self._send_to_target(lambda: False, replace)
        self._learn_word(suggestion)
        self.current_word = ""
        self._update_suggestions()

    def _layout(self):
        if self.symbols:
            return [
                [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"), ("0", "0")],
                [("!", "!"), ("@", "@"), ("#", "#"), ("$", "$"), ("%", "%"), ("&", "&"), ("*", "*"), ("(", "("), (")", ")")],
                [("ABC", "MODE"), ("-", "-"), ("_", "_"), ("+", "+"), ("=", "="), ("/", "/"), ("\\", "\\"), ("'", "'"), ('"', '"'), ("⌫", "BACK")],
            ]
        rows = ["qwertyuiop", "asdfghjkl"]
        return [
            [(c.upper() if self.shifted else c, c.upper() if self.shifted else c) for c in rows[0]],
            [(c.upper() if self.shifted else c, c.upper() if self.shifted else c) for c in rows[1]],
            [("⇧", "SHIFT")] + [(c.upper() if self.shifted else c, c.upper() if self.shifted else c) for c in "zxcvbnm"] + [("⌫", "BACK")],
        ]

    def _build_keys(self) -> None:
        # Rebuilding buttons must never redirect a remote OK press to another
        # control (notably CLOSE). Keep the selected action, not widget identity.
        selected_id = getattr(self.nav_selected, "_firefly_identity", None)
        for child in self.keyboard.winfo_children():
            child.destroy()
        self.nav_buttons = list(self.header_buttons) + list(self.quick_buttons) + list(self.suggestion_buttons)
        self.nav_selected = None
        font_size = max(13, int(19 * self.scale))
        # One text line keeps all four key rows plus navigation visible in the
        # compact remote-desktop dock. The surrounding frames provide the
        # touch target height by expanding into the available space.
        key_height = 1
        for row_num, row in enumerate(self._layout()):
            frame = tk.Frame(self.keyboard, bg=BG)
            frame.pack(fill="both", expand=True, pady=4)
            for col, (label, action) in enumerate(row):
                frame.grid_columnconfigure(col, weight=2 if action in ("SHIFT", "BACK", "MODE") else 1, uniform="keys")
                button = tk.Button(frame, text=label, command=lambda a=action: self.activate(a, lambda: self.key_action(a)),
                                   bg=LIME if action == "SHIFT" and self.shifted else (KEY_ALT if action in ("SHIFT", "BACK", "MODE") else KEY),
                                   fg=BG if action == "SHIFT" and self.shifted else (CYAN if action in ("SHIFT", "BACK", "MODE") else INK),
                                   activebackground=LIME, activeforeground=BG, relief="flat", bd=0,
                                   height=key_height, font=("Segoe UI", font_size, "bold"), takefocus=0)
                key_id = "key:" + (action.lower() if len(action) == 1 and action.isalpha() else action)
                self._register_nav_button(button, key_id)
                button.grid(row=0, column=col, sticky="nsew", padx=4)
            frame.grid_rowconfigure(0, weight=1)

        frame = tk.Frame(self.keyboard, bg=BG)
        frame.pack(fill="both", expand=True, pady=4)
        bottom = [
            ("123" if not self.symbols else "ABC", "MODE", 1, KEY_ALT),
            ("ESC", "VK:27", 1, KEY_ALT), ("TAB", "VK:9", 1, KEY_ALT),
            (",", ",", 1, KEY), ("SPACE", " ", 5, KEY), (".", ".", 1, KEY),
            ("←", "VK:37", 1, KEY_ALT), ("→", "VK:39", 1, KEY_ALT),
            ("ENTER", "VK:13", 2, LIME),
        ]
        for col, (label, action, weight, color) in enumerate(bottom):
            frame.grid_columnconfigure(col, weight=weight)
            fg = BG if color == LIME else (CYAN if color == KEY_ALT else INK)
            button = tk.Button(frame, text=label, command=lambda a=action: self.activate(a, lambda: self.key_action(a)),
                               bg=color, fg=fg, activebackground=LIME, activeforeground=BG,
                               relief="flat", bd=0, height=key_height,
                               font=("Segoe UI", max(11, int(15 * self.scale)), "bold"), takefocus=0)
            key_id = "key:" + (action.lower() if len(action) == 1 and action.isalpha() else action)
            self._register_nav_button(button, key_id)
            button.grid(row=0, column=col, sticky="nsew", padx=4)
        frame.grid_rowconfigure(0, weight=1)

        utility = tk.Frame(self.keyboard, bg=BG)
        utility.pack(fill="x", pady=(4, 0))
        utilities = [("CTRL●" if self.ctrl_held else "CTRL", "CTRL"),
                     ("HOME", VK_HOME), ("END", VK_END), ("PG▲", VK_PRIOR), ("PG▼", VK_NEXT),
                     ("▲", VK_UP), ("▼", VK_DOWN), ("DELETE", VK_DELETE), ("PASTE", "PASTE")]
        for label, action in utilities:
            active_modifier = action == "CTRL" and self.ctrl_held
            button = tk.Button(utility, text=label, command=lambda a=action: self.activate(str(a), lambda: self.key_action(a)),
                               bg=LIME if active_modifier else PANEL,
                               fg=BG if active_modifier else MUTED,
                               activebackground=KEY_ALT, activeforeground=INK,
                               relief="flat", bd=0, padx=13, pady=6,
                               font=("Segoe UI", 9, "bold"), takefocus=0)
            self._register_nav_button(button, "key:" + str(action))
            button.pack(side="left", expand=True, fill="x", padx=3)
        restored = next((item for item in self.nav_buttons
                         if getattr(item, "_firefly_identity", None) == selected_id), None)
        if restored is not None:
            self._select_nav_button(restored)
        elif self.pointer_inside and time.monotonic() >= self.remote_nav_until:
            self.root.after_idle(self._select_pointer_button)

    def _select_nav_button(self, button: tk.Button) -> None:
        if self.nav_selected and self.nav_selected.winfo_exists():
            self.nav_selected.configure(highlightthickness=0)
        self.nav_selected = button
        button.configure(highlightthickness=3, highlightbackground=LIME, highlightcolor=LIME)

    def _button_at_point(self, x: int, y: int) -> tk.Button | None:
        widget = self.root.winfo_containing(x, y)
        while widget is not None and not isinstance(widget, tk.Button):
            widget = getattr(widget, "master", None)
        if isinstance(widget, tk.Button) and widget in self.nav_buttons:
            return widget
        return None

    def _select_pointer_button(self) -> None:
        if time.monotonic() < self.remote_nav_until and self.nav_selected:
            return
        x, y = self.root.winfo_pointerxy()
        button = self._button_at_point(x, y)
        if button:
            self._select_nav_button(button)
        elif self.nav_buttons:
            index = min(len(self.header_buttons), len(self.nav_buttons) - 1)
            self._select_nav_button(self.nav_buttons[index])

    def _handle_mouse_motion(self, point: tuple[int, int], direction: str | None) -> None:
        if direction:
            self._navigate(direction)
            return
        if time.monotonic() < self.remote_nav_until:
            return
        button = self._button_at_point(*point)
        if button:
            self._select_nav_button(button)

    def _invoke_pointer_button(self, point: tuple[int, int]) -> None:
        if time.monotonic() < self.remote_nav_until and self.nav_selected:
            button = self.nav_selected
        else:
            button = self._button_at_point(*point) or self.nav_selected
        if button and button.winfo_exists():
            self._select_nav_button(button)
            button.invoke()

    def _focus_navigation(self) -> None:
        if not self.pointer_inside:
            return
        self.root.update_idletasks()
        hwnd = getattr(self, "hwnd", user32.GetAncestor(self.root.winfo_id(), GA_ROOT) or self.root.winfo_id())
        style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, (style & ~WS_EX_NOACTIVATE) | WS_EX_TOOLWINDOW)
        user32.SetForegroundWindow(hwnd)
        self.root.focus_force()

    def _set_pointer_inside(self, inside: bool) -> None:
        if inside == self.pointer_inside:
            return
        self.pointer_inside = inside
        if inside:
            self.last_mouse_point = self.root.winfo_pointerxy()
            self.mouse_motion_accum = [0, 0]
            self.root.attributes("-alpha", ALPHA_ACTIVE)
            self._select_pointer_button()
            self.guard_var.set("REMOTE DIRECTIONS navigate · CLICK/OK presses")
        else:
            self.last_mouse_point = None
            self.mouse_motion_accum = [0, 0]
            self.root.attributes("-alpha", ALPHA_IDLE)
            self._apply_no_activate()
            target = self.last_external_hwnd
            if target and user32.IsWindow(target):
                user32.SetForegroundWindow(target)

    def _poll_pointer(self) -> None:
        try:
            if self.preview_idle:
                inside = False
            elif self.preview_hover:
                inside = True
            else:
                x, y = self.root.winfo_pointerxy()
                left, top = self.root.winfo_rootx(), self.root.winfo_rooty()
                inside = left <= x < left + self.root.winfo_width() and top <= y < top + self.root.winfo_height()
            self._set_pointer_inside(inside)
            self.root.after(120, self._poll_pointer)
        except tk.TclError:
            pass

    def _move_nav(self, direction: str) -> None:
        buttons = [
            button for button in self.nav_buttons
            if button.winfo_exists() and button.winfo_ismapped() and str(button.cget("state")) != "disabled"
        ]
        if not buttons:
            return
        if self.nav_selected not in buttons:
            self._select_pointer_button()
            return
        current = self.nav_selected
        cx = current.winfo_rootx() + current.winfo_width() / 2
        cy = current.winfo_rooty() + current.winfo_height() / 2
        choices = []
        for button in buttons:
            if button is current:
                continue
            bx = button.winfo_rootx() + button.winfo_width() / 2
            by = button.winfo_rooty() + button.winfo_height() / 2
            dx, dy = bx - cx, by - cy
            if direction == "Left" and dx < -2:
                score = -dx + abs(dy) * 3
            elif direction == "Right" and dx > 2:
                score = dx + abs(dy) * 3
            elif direction == "Up" and dy < -2:
                score = -dy + abs(dx) * 3
            elif direction == "Down" and dy > 2:
                score = dy + abs(dx) * 3
            else:
                continue
            choices.append((score, button))
        if choices:
            self._select_nav_button(min(choices, key=lambda item: item[0])[1])

    def _navigate(self, direction: str) -> None:
        now = time.perf_counter() * 1000
        last_direction, last_at = self.last_nav_action
        if direction == last_direction and now - last_at < NAV_GUARD_MS:
            return
        self.last_nav_action = (direction, now)
        self.remote_nav_until = time.monotonic() + 1.4
        self._move_nav(direction)

    def _on_navigation_key(self, event):
        if not self.pointer_inside:
            return None
        key = event.keysym
        if key in ("Left", "Right", "Up", "Down"):
            self._navigate(key)
            return "break"
        if key in ("Return", "KP_Enter", "space") and self.nav_selected:
            self.nav_selected.invoke()
            return "break"
        return None

    def _install_navigation_hook(self) -> None:
        if not self.nav_hook:
            self.nav_hook = user32.SetWindowsHookExW(
                WH_KEYBOARD_LL, self.nav_hook_proc, kernel32.GetModuleHandleW(None), 0
            )

    def _install_mouse_hook(self) -> None:
        if not self.mouse_hook:
            self.mouse_hook = user32.SetWindowsHookExW(
                WH_MOUSE_LL, self.mouse_hook_proc, kernel32.GetModuleHandleW(None), 0
            )

    def _mouse_navigation_hook(self, n_code, w_param, l_param):
        """Capture one desktop click, or navigate Firefly while the pointer is inside."""
        if n_code == HC_ACTION:
            data = ctypes.cast(l_param, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            # Injected clicks must always reach Windows, never be reinterpreted.
            if data.flags & LLMHF_INJECTED:
                return user32.CallNextHookEx(self.mouse_hook or 0, n_code, w_param, l_param)
            if self.pointer_suppress_up and w_param == WM_LBUTTONUP:
                self.pointer_suppress_up = False
                return 1
            if time.monotonic() < self.pointer_suppress_until and w_param in (
                WM_LBUTTONDOWN, WM_LBUTTONDBLCLK, WM_LBUTTONUP
            ):
                return 1
            point = (int(data.pt.x), int(data.pt.y))
            if self.pointer_mode is not None and w_param in (WM_LBUTTONDOWN, WM_LBUTTONDBLCLK):
                side = self.pointer_mode
                self.pointer_mode = None
                self.pointer_suppress_up = True
                self.pointer_suppress_until = time.monotonic() + 0.25
                self.root.after(0, lambda which=side, at=point: self._complete_desktop_click(which, at))
                return 1
            if not self.pointer_inside:
                return user32.CallNextHookEx(self.mouse_hook or 0, n_code, w_param, l_param)
            if w_param == WM_MOUSEMOVE:
                previous = self.last_mouse_point
                self.last_mouse_point = point
                direction = None
                if previous:
                    dx, dy = point[0] - previous[0], point[1] - previous[1]
                    now = time.monotonic()
                    if now - self.last_mouse_motion_at > 0.45:
                        self.mouse_motion_accum = [0, 0]
                    self.last_mouse_motion_at = now
                    self.mouse_motion_accum[0] += dx
                    self.mouse_motion_accum[1] += dy
                    ax, ay = self.mouse_motion_accum
                    if max(abs(ax), abs(ay)) >= 2:
                        if abs(ax) >= abs(ay):
                            direction = "Right" if ax > 0 else "Left"
                        else:
                            direction = "Down" if ay > 0 else "Up"
                        self.mouse_motion_accum = [0, 0]
                self.root.after(
                    0,
                    lambda value=direction, position=point: self._handle_mouse_motion(position, value),
                )
            elif w_param in (WM_LBUTTONDOWN, WM_LBUTTONDBLCLK):
                self.root.after(0, lambda position=point: self._invoke_pointer_button(position))
                return 1
            elif w_param == WM_LBUTTONUP:
                return 1
        return user32.CallNextHookEx(self.mouse_hook or 0, n_code, w_param, l_param)

    def _handle_navigation_vk(self, vk: int) -> None:
        directions = {VK_LEFT: "Left", VK_RIGHT: "Right", VK_UP: "Up", VK_DOWN: "Down"}
        if vk in directions:
            direction = directions[vk]
            self._navigate(direction)
        elif vk in (VK_RETURN, VK_SPACE) and self.nav_selected:
            self.nav_selected.invoke()

    def _navigation_hook(self, n_code, w_param, l_param):
        if n_code == HC_ACTION:
            data = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            if not (data.flags & LLKHF_INJECTED):
                if self.pointer_suppress_key == data.vkCode and w_param in (WM_KEYUP, WM_SYSKEYUP):
                    self.pointer_suppress_key = None
                    return 1
                if self.pointer_mode is not None and data.vkCode in (VK_RETURN, VK_SPACE, VK_ESCAPE):
                    if w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
                        self.pointer_suppress_key = data.vkCode
                        if data.vkCode == VK_ESCAPE:
                            self.pointer_mode = None
                            self.root.after(0, lambda: self._restore_after_click("Desktop click cancelled"))
                        else:
                            side = self.pointer_mode
                            self.pointer_mode = None
                            point = self.root.winfo_pointerxy()
                            self.root.after(0, lambda which=side, at=point: self._complete_desktop_click(which, at))
                    return 1
            if not self.pointer_inside:
                return user32.CallNextHookEx(self.nav_hook or 0, n_code, w_param, l_param)
            navigation_keys = (VK_LEFT, VK_RIGHT, VK_UP, VK_DOWN, VK_RETURN, VK_SPACE)
            # Never consume Firefly's own injected key events. This allows the
            # on-screen arrow/Enter buttons to reach the target application.
            if data.vkCode in navigation_keys and not (data.flags & LLKHF_INJECTED):
                if w_param in (WM_KEYDOWN, WM_SYSKEYDOWN):
                    vk = int(data.vkCode)
                    self.root.after(0, lambda value=vk: self._handle_navigation_vk(value))
                return 1
        return user32.CallNextHookEx(self.nav_hook or 0, n_code, w_param, l_param)

    def _run_navigation_self_test(self) -> None:
        """Exercise remote Right + Enter through the real hook callback path."""
        self.pointer_inside = True
        first = next((button for button in self.nav_buttons if button.cget("text") == "q"), None)
        if not first:
            return
        self._select_nav_button(first)
        for vk in (VK_RIGHT, VK_RETURN):
            event = KBDLLHOOKSTRUCT(vkCode=vk, scanCode=0, flags=0, time=0, dwExtraInfo=0)
            self._navigation_hook(HC_ACTION, WM_KEYDOWN, ctypes.addressof(event))

    def _run_mouse_navigation_self_test(self) -> None:
        """Exercise remote pointer-right + click through the real mouse hook."""
        self.preview_hover = True
        self.pointer_inside = True
        first = next((button for button in self.nav_buttons if button.cget("text") == "q"), None)
        if not first:
            return
        self._select_nav_button(first)
        self.last_mouse_point = (100, 100)
        for x in (102, 104, 106):
            move = MSLLHOOKSTRUCT(pt=POINT(x, 100), mouseData=0, flags=0, time=0, dwExtraInfo=0)
            self._mouse_navigation_hook(HC_ACTION, WM_MOUSEMOVE, ctypes.addressof(move))
        click = MSLLHOOKSTRUCT(pt=POINT(106, 100), mouseData=0, flags=0, time=0, dwExtraInfo=0)
        self.root.after(
            100,
            lambda: self._mouse_navigation_hook(
                HC_ACTION, WM_LBUTTONDOWN, ctypes.addressof(click)
            ),
        )

    def _run_hover_click_self_test(self) -> None:
        """Exercise one remote click on the key physically under the pointer."""
        self.preview_hover = True
        self.pointer_inside = True
        self.root.update_idletasks()
        button = next((item for item in self.nav_buttons if item.cget("text") == "w"), None)
        if not button:
            return
        point = POINT(
            button.winfo_rootx() + button.winfo_width() // 2,
            button.winfo_rooty() + button.winfo_height() // 2,
        )
        click = MSLLHOOKSTRUCT(pt=point, mouseData=0, flags=0, time=0, dwExtraInfo=0)
        self._mouse_navigation_hook(HC_ACTION, WM_LBUTTONDOWN, ctypes.addressof(click))

    def _run_fast_navigation_self_test(self) -> None:
        """Exercise four rapid same-direction remote taps: q -> t."""
        self.preview_hover = True
        self.pointer_inside = True
        first = next((item for item in self.nav_buttons if item.cget("text") == "q"), None)
        if not first:
            return
        self._select_nav_button(first)
        for index in range(4):
            self.root.after(index * 90, lambda: self._navigate("Right"))
        self.root.after(430, lambda: self.nav_selected.invoke() if self.nav_selected else None)

    def _run_suggestion_self_test(self) -> None:
        self.current_word = "hel"
        self._update_suggestions()
        self._accept_suggestion(0)

    def _run_unknown_word_self_test(self) -> None:
        self.current_word = "xylophonic"
        self._update_suggestions()
        self._accept_suggestion(0)

    def _run_long_suggestion_self_test(self) -> None:
        self.current_word = "recommen"
        self._update_suggestions()
        self._accept_suggestion(0)

    def _run_correction_self_test(self) -> None:
        self.current_word = "teh"
        self._update_suggestions()
        self._accept_suggestion(0)

    def _run_paste_self_test(self) -> None:
        self.key_action("PASTE")

    def _run_ctrl_self_test(self) -> None:
        self.ctrl_held = True
        self.key_action("a")
        self.root.after(180, lambda: self.key_action("x"))

    def activate(self, signature: str, action) -> None:
        now = time.perf_counter() * 1000
        last_sig, last_at = self.last_action
        if signature == last_sig and now - last_at < GUARD_MS:
            self.blocked += 1
            self.guard_var.set(f"{GUARD_MS} ms guard · {self.blocked} duplicate{'s' if self.blocked != 1 else ''} blocked")
            return
        self.last_action = (signature, now)
        action()

    def key_action(self, action) -> None:
        if action == "SHIFT":
            # Never leave a latent Ctrl chord that could send Ctrl+C/Ctrl+D
            # to cmd/PowerShell when the user intended uppercase letters.
            self.ctrl_held = False
            self.shifted = not self.shifted
            self._build_keys()
        elif action == "MODE":
            self.symbols = not self.symbols
            self.shifted = False
            self._build_keys()
        elif action == "CTRL":
            self.shifted = False
            self.ctrl_held = not self.ctrl_held
            self._build_keys()
        elif action == "BACK":
            self._send_vk_action(VK_BACK)
            self.current_word = self.current_word[:-1]
            self._update_suggestions()
        elif action == "PASTE":
            self.ctrl_held = False
            clipboard_text = read_clipboard_text()
            if clipboard_text is None:
                self._send_to_target(paste_clipboard, lambda hwnd: direct_ctrl_chord(hwnd, VK_V))
            else:
                # Text injection is reliable in remote/RDP targets where a
                # synthetic Ctrl+V may be swallowed before reaching the editor.
                self._send_to_target(
                    lambda: False,
                    lambda hwnd, value=clipboard_text: direct_text(hwnd, value),
                )
                self._track_text(clipboard_text)
            self._build_keys()
        elif isinstance(action, int):
            self._send_vk_action(action)
        elif isinstance(action, str) and action.startswith("VK:"):
            vk = int(action.split(":", 1)[1])
            self._send_vk_action(vk)
            if vk in (VK_RETURN, VK_TAB, VK_ESCAPE):
                if self.current_word:
                    self._learn_word(self.current_word)
                self.current_word = ""
                self._update_suggestions()
        else:
            text = str(action)
            reset_layout = self.shifted
            if self.ctrl_held and len(text) == 1:
                vk = user32.VkKeyScanW(text) & 0xFF
                self._send_to_target(
                    lambda value=vk: send_ctrl_chord(value),
                    lambda hwnd, value=vk: direct_ctrl_chord(hwnd, value),
                )
                self.ctrl_held = False
                reset_layout = True
            else:
                self._send_to_target(lambda: False, lambda hwnd: direct_text(hwnd, text))
                self._track_text(text)
            if self.shifted:
                self.shifted = False
            if reset_layout:
                self._build_keys()

    def _send_vk_action(self, vk: int) -> None:
        if self.ctrl_held:
            self._send_to_target(
                lambda: send_ctrl_chord(vk),
                lambda hwnd: direct_ctrl_chord(hwnd, vk),
            )
            self.ctrl_held = False
            self._build_keys()
        else:
            self._send_to_target(lambda: False, lambda hwnd: direct_vk(hwnd, vk))

    def _focused_control(self, target: int) -> int:
        thread_id = user32.GetWindowThreadProcessId(target, None)
        info = GUITHREADINFO(cbSize=ctypes.sizeof(GUITHREADINFO))
        if thread_id and user32.GetGUIThreadInfo(thread_id, ctypes.byref(info)):
            return info.hwndFocus or target
        return target

    def _send_to_target(self, callback, fallback) -> None:
        """Restore the target focus, inject input, then use a direct fallback."""
        target = self.last_external_hwnd
        if target and user32.IsWindow(target):
            focused = self._focused_control(target)
            if user32.IsIconic(target):
                user32.ShowWindow(target, SW_RESTORE)
            target_thread = user32.GetWindowThreadProcessId(target, None)
            current_thread = kernel32.GetCurrentThreadId()
            attached = bool(target_thread and target_thread != current_thread and
                            user32.AttachThreadInput(current_thread, target_thread, True))
            try:
                user32.SetForegroundWindow(target)
                if focused and focused != target:
                    user32.SetFocus(focused)
                if not callback():
                    fallback(focused or target)
                self.guard_var.set(f"Sent to {self._target_title(target)} · {self.blocked} blocked")
            finally:
                if attached:
                    user32.AttachThreadInput(current_thread, target_thread, False)
        else:
            self.guard_var.set("No target yet — click a text field in another window")

    def _target_title(self, hwnd: int) -> str:
        title = ctypes.create_unicode_buffer(128)
        user32.GetWindowTextW(hwnd, title, 128)
        return title.value.strip()[:28] or "target"

    def toggle_size(self) -> None:
        self.scale = {1.0: 1.22, 1.22: 0.82}.get(self.scale, 1.0)
        self._build()
        self._apply_no_activate()

    def toggle_dock(self) -> None:
        self.dock_top = not self.dock_top
        self._configure_window()
        self._apply_no_activate()

    def _update_target(self) -> None:
        hwnd = user32.GetForegroundWindow()
        own_hwnd = getattr(self, "hwnd", user32.GetAncestor(self.root.winfo_id(), GA_ROOT) or self.root.winfo_id())
        title = ctypes.create_unicode_buffer(256)
        if hwnd:
            user32.GetWindowTextW(hwnd, title, 256)
            foreground_title = title.value.strip()
            if hwnd != own_hwnd and foreground_title not in (APP_TITLE, "On-Screen Keyboard", "Magnifier"):
                self.last_external_hwnd = hwnd
        title = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(self.last_external_hwnd, title, 256)
        target = title.value.strip() or "Desktop application"
        self.target_var.set("Target: " + target[:54])
        self.root.after(500, self._update_target)

    def toggle_inspector(self) -> None:
        if self.inspecting:
            self.inspecting = False
            if self.hook:
                user32.UnhookWindowsHookEx(self.hook)
                self.hook = None
            self.inspect_button.configure(text="INSPECT", fg=LIME)
            self.inspect_var.set("Inspector off — no input is being recorded")
        else:
            self.inspecting = True
            self.event_rows.clear()
            self.last_native_at = 0
            self.hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self.hook_proc, kernel32.GetModuleHandleW(None), 0)
            self.inspect_button.configure(text="INSPECTING", fg=RED)
            self.inspect_var.set("Press the unknown remote button once… (events are temporary and never saved)")

    def _keyboard_hook(self, n_code, w_param, l_param):
        if n_code == HC_ACTION and self.inspecting:
            data = ctypes.cast(l_param, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            now = int(time.perf_counter() * 1000)
            gap = 0 if not self.last_native_at else now - self.last_native_at
            self.last_native_at = now
            kind = {WM_KEYDOWN: "DOWN", WM_KEYUP: "UP", WM_SYSKEYDOWN: "SYS↓", WM_SYSKEYUP: "SYS↑"}.get(w_param, hex(w_param))
            injected = " injected" if data.flags & LLKHF_INJECTED else " hardware"
            row = f"{kind}  VK=0x{data.vkCode:02X} ({data.vkCode})  SCAN=0x{data.scanCode:02X}  flags=0x{data.flags:02X}  +{gap}ms{injected}"
            self.event_rows.append(row)
            self.event_rows = self.event_rows[-3:]
            self.root.after(0, lambda: self.inspect_var.set("  |  ".join(self.event_rows)))
        return user32.CallNextHookEx(self.hook or 0, n_code, w_param, l_param)

    def save_screenshot_bmp(self, path: str) -> None:
        """Capture this window to BMP and PNG without external packages."""
        self.root.update()
        hwnd = self.root.winfo_id()
        rect = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        width, height = rect.right - rect.left, rect.bottom - rect.top
        src_dc = user32.GetWindowDC(hwnd)
        mem_dc = gdi32.CreateCompatibleDC(src_dc)
        bitmap = gdi32.CreateCompatibleBitmap(src_dc, width, height)
        old = gdi32.SelectObject(mem_dc, bitmap)
        gdi32.BitBlt(mem_dc, 0, 0, width, height, src_dc, 0, 0, SRCCOPY)
        header = BITMAPINFOHEADER()
        header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        header.biWidth = width
        header.biHeight = -height
        header.biPlanes = 1
        header.biBitCount = 32
        header.biCompression = 0
        size = width * height * 4
        pixels = ctypes.create_string_buffer(size)
        gdi32.GetDIBits(mem_dc, bitmap, 0, height, pixels, ctypes.byref(header), DIB_RGB_COLORS)
        file_header = struct.pack("<2sIHHI", b"BM", 14 + 40 + size, 0, 0, 54)
        info_header = struct.pack("<IiiHHIIiiII", 40, width, -height, 1, 32, 0, size, 0, 0, 0, 0)
        with open(path, "wb") as f:
            f.write(file_header)
            f.write(info_header)
            f.write(pixels.raw)
        rgba = bytearray()
        raw = pixels.raw
        for y in range(height):
            rgba.append(0)  # PNG filter: none
            row_start = y * width * 4
            for x in range(width):
                i = row_start + x * 4
                b, g, r = raw[i], raw[i + 1], raw[i + 2]
                rgba.extend((r, g, b, 255))
        def chunk(kind: bytes, data: bytes) -> bytes:
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        png_path = os.path.splitext(path)[0] + ".png"
        with open(png_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n")
            f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
            f.write(chunk(b"IDAT", zlib.compress(bytes(rgba), 7)))
            f.write(chunk(b"IEND", b""))
        gdi32.SelectObject(mem_dc, old)
        gdi32.DeleteObject(bitmap)
        gdi32.DeleteDC(mem_dc)
        user32.ReleaseDC(hwnd, src_dc)

    def close(self) -> None:
        self._save_language_model()
        if self.hook:
            user32.UnhookWindowsHookEx(self.hook)
        if self.nav_hook:
            user32.UnhookWindowsHookEx(self.nav_hook)
        if self.mouse_hook:
            user32.UnhookWindowsHookEx(self.mouse_hook)
        self.root.destroy()

    def request_close(self) -> None:
        now = time.monotonic()
        if now < self.close_armed_until:
            self.close()
            return
        self.close_armed_until = now + 2.5
        self.guard_var.set("Close protected — press × again within 2.5 seconds")

    def run(self) -> None:
        if "--screenshot" in sys.argv:
            out = os.path.join(os.path.dirname(__file__), "firefly-keyboard-preview.bmp")
            self.root.after(900, lambda: self.save_screenshot_bmp(out))
        if "--self-test" in sys.argv:
            self.root.after(650, lambda: self._send_to_target(
                lambda: False,
                lambda hwnd: direct_text(hwnd, "firefly"),
            ))
            self.root.after(1800, self.close)
        if "--nav-self-test" in sys.argv:
            self.root.after(650, self._run_navigation_self_test)
            self.root.after(2200, self.close)
        if "--mouse-nav-self-test" in sys.argv:
            self.root.after(650, self._run_mouse_navigation_self_test)
            self.root.after(2400, self.close)
        if "--hover-click-self-test" in sys.argv:
            self.root.after(650, self._run_hover_click_self_test)
            self.root.after(2200, self.close)
        if "--fast-nav-self-test" in sys.argv:
            self.root.after(650, self._run_fast_navigation_self_test)
            self.root.after(2500, self.close)
        if "--suggestion-self-test" in sys.argv:
            self.root.after(650, self._run_suggestion_self_test)
            self.root.after(2200, self.close)
        if "--unknown-word-self-test" in sys.argv:
            self.root.after(650, self._run_unknown_word_self_test)
            self.root.after(2200, self.close)
        if "--long-suggestion-self-test" in sys.argv:
            self.root.after(650, self._run_long_suggestion_self_test)
            self.root.after(2200, self.close)
        if "--correction-self-test" in sys.argv:
            self.root.after(650, self._run_correction_self_test)
            self.root.after(2200, self.close)
        if "--paste-self-test" in sys.argv:
            self.root.after(650, self._run_paste_self_test)
            self.root.after(2400, self.close)
        if "--ctrl-self-test" in sys.argv:
            self.root.after(650, self._run_ctrl_self_test)
            self.root.after(2600, self.close)
        self.root.mainloop()


if __name__ == "__main__":
    close_existing_firefly()
    if "--replace-osk" in sys.argv:
        close_windows_osk()
    FireflyKeyboard().run()





