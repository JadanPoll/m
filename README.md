# Firefly Desk Keyboard

A native, remote-oriented Windows on-screen keyboard for a Fire TV/remote-desktop pointer, D-pad, and OK button. No server, administrator rights, or network connection required; uses Python/Tkinter and Win32 APIs already available on the host.

## Critical: Illinois AnyWare / TV-remote safe mode (default)

This program is operating inside an **Illinois AnyWare remote session**, possibly controlled only by a TV remote. **Avoid losing access to the university desktop.** The regular `Launch Firefly Keyboard.cmd` starts in safe pointer mode:

- **Does not close Windows On-Screen Keyboard (OSK)**, even when an old launcher accidentally passes `--replace-osk`.
- **Does not install system-wide keyboard or mouse hooks** or block mouse/keyboard events elsewhere. The optional input inspector observes key state with a Tk timer; it cannot intercept the remote.
- **Does not hide itself for one-shot mouse clicks**. The experimental `LEFT CLICK` / `RIGHT CLICK` conversion controls are deliberately unavailable in safe mode. Normal pointer clicks outside Firefly continue normally.
- Never auto-terminates an existing Firefly instance. A repeat launch returns to the existing window.
- Never forces foreground focus on pointer leave or to deliver text. Click the actual target text field first, then type.
- Shows a `SAFE · POINTER` indicator. If D-pad-only input does not behave like a pointer, the optional `--advanced-input` mode can **observe** directional keys by polling, but cannot swallow their underlying Windows events.

The **OSK** app shortcut starts Windows' built-in keyboard, independently of Firefly. The close (×) control requires two presses within 2.5 seconds to avoid accidental closure.

Startup and Tk callback errors are appended to `%LOCALAPPDATA%\FireflyDeskKeyboard\startup.log`. Launch `Debug Firefly Keyboard.cmd` to display failures in a console without replacing OSK. An application can still crash; safe mode minimizes its effects on the rest of the remote session, not guarantees a crash-free Windows runtime.

**Crash regression fix:** Previous versions created Python `WINFUNCTYPE` callbacks for Windows low-level keyboard/mouse hooks; these could re-enter Tk and are suspected in the reported `PyEval_RestoreThread` fatal error. **Both callback creation and hook installation have been removed completely.** Advanced mode (`--advanced-input`) now uses non-intercepting `GetAsyncKeyState` polling from Tk's event loop. No remote event is stolen. The tradeoff is that very short presses can be missed, and a mouse left-click cannot safely be converted into a right-click without also reaching the underlying app.

The Illinois AnyWare service may disconnect idle sessions after 15 minutes and log them off one hour after disconnection. Save critical work to a persistent university-supported location.

## Restored screen layout and transparency

The idle keyboard is **24% opaque** again, becoming **88% opaque** when the remote pointer enters it. The keyboard now sizes itself from Tk's requested height after the app and prediction strips have been built, rather than reusing the old pre-shortcut 380px/49%-of-screen calculation. `SIZE` and `TOP/BOTTOM` also refit the window so **CTRL, HOME, END, PAGE, arrow, DELETE and PASTE** below ENTER remain visible when the AnyWare work area allows the full layout.

## Remote interaction

- In **safe mode**, click/tap the visible Firefly keys using the remote-controlled pointer; the standard Windows input path handles remote clicks. The 300 ms identical-action guard mitigates accidentally doubled remote clicks, but can also suppress genuinely rapid repeated characters.
- `SHIFT` is one-shot uppercase; its selection survives redraw, and it cancels sticky Ctrl so that typing cannot unintentionally interrupt a terminal with Ctrl+C.
- `TOP/BOTTOM`, `SIZE`, `123`, `PASTE`, and word suggestions are available without global hooks.
- If typing reports **Click the destination field first**, click the destination text field outside Firefly to establish focus. Safe mode does not silently move focus or send text to an unrelated app.
- `INSPECT` now works in safe mode without hooks: it samples native virtual-key press transitions. The client may still discard or translate remote buttons before they reach Windows. D-pad navigation by polling is opt-in; it cannot suppress original arrow-key actions in the target application.


## Quick launch

The **APPS** row opens `CMD`, `POWERSHELL`, `FILES`, `NOTEPAD`, `CHROME`, `RUN`, and **`OSK`** (Windows' On-Screen Keyboard). Chrome is resolved through Windows App Paths or typical install locations; if Chrome is not installed in the Illinois AnyWare image, Firefly reports that instead of failing. `RUN` opens Windows' native Run dialog.

On shared/managed university desktops, installed apps and their permissions can differ from a personal Windows PC.


## Click anywhere (advanced only)

Native pointer clicks already work **outside** the Firefly overlay and do not need mouse hooks. Firefly's one-shot LEFT/RIGHT CLICK controls are hidden in **safe mode**. In advanced polling mode, keyboard Enter/Space can trigger an injected click at the pointer position while the overlay is hidden; a normal pointer left-click passes through unchanged and does **not** generate a second click. Right-click conversion of a left-click is therefore not available without event interception.

If the Citrix touch client exposes gestures, Citrix documents touch-hold-release for right-click. That gesture may **not** be available through a physical Fire TV remote. Avoid relying on experimental pointer-click conversion as your only way to operate AnyWare.


## Predictive text

The three WORDS keys offer word completions and explicit spelling suggestions. The predictor now prioritizes **real prefix completions** (never the already-typed prefix), ranks by learned preceding-word context and word frequency, and considers common transposition typos when completions are scarce. **Suggestions are never auto-inserted.**

When a suggestion *completes* the existing prefix, Firefly sends only the missing suffix plus space, preserving already typed letters. When the suggestion is a correction, it sends a single ordered Windows input batch of Backspaces and replacement characters. **Neither case silently clears the predictor or learns the suggestion if SendInput reports failure.** This also avoids posting individual WM_CHAR messages to modern applications that may ignore them. Because Windows can accept input without the target consuming it, verify the result in the actual text field.

Learned words and word-pair counts are stored locally in `%LOCALAPPDATA%\FireflyDeskKeyboard\language.json` when Firefly closes normally. No cloud service is used. **Do not type secrets through the keyboard unless you accept that its local learning model can record the typed words.** The current model is intentionally lightweight; for larger vocabulary and typo correction, see [SymSpellPy](https://github.com/mammothb/symspellpy) and [Presage](https://presage.sourceforge.io/) as research directions, not installed dependencies.

## Input diagnostics

Safe mode preserves the Windows/remote-desktop event path and never consumes global mouse or keyboard events. `INSPECT` samples **virtual-key codes only** from the Tk event loop, without installing hooks. It cannot recover hardware scan codes or an event Citrix/Fire TV already transformed or discarded. Microsoft's `GetAsyncKeyState` API explicitly cautions that its recent-press bit is unreliable, so very brief taps may be missed.

Text uses `SendInput` when Firefly's target is verified foreground, with targeted message fallback for compatible controls. A posted Win32 message does not prove a modern application accepted text. Always verify in the actual field, particularly in a terminal.


## Useful upstream references

- [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput) and [MOUSEINPUT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput): native keyboard and mouse event injection.
- [Microsoft winappCli UI automation](https://github.com/microsoft/winappCli): target verification and transport tradeoffs; not required by Firefly.
- [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher): mature launcher ideas if a fuller app-search workflow becomes necessary.
- [SymSpellPy](https://github.com/mammothb/symspellpy): frequency-aware typo correction for future predictor development.

## Limits

Only source-level review and a Windows import CI smoke workflow (where available) can be done without the actual interactive Windows/Fire TV session. A passing import alone does not establish safety or absence of thread-state crashes. Validate Shift → letter → Shift, Ctrl → Shift → C in a **non-destructive scratch editor**, launching CMD, and both one-shot click modes before relying on the revised program for critical work.
