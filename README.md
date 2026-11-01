# Firefly Desk Keyboard

A native, remote-oriented Windows on-screen keyboard for a Fire TV/remote-desktop pointer, D-pad, and OK button. No server, administrator rights, or network connection required; uses Python/Tkinter and Win32 APIs already available on the host.

## Critical: Illinois AnyWare / TV-remote safe mode (default)

This program is operating inside an **Illinois AnyWare remote session**, possibly controlled only by a TV remote. **Avoid losing access to the university desktop.** The regular `Launch Firefly Keyboard.cmd` starts in safe pointer mode:

- **Does not close Windows On-Screen Keyboard (OSK)**, even when an old launcher accidentally passes `--replace-osk`.
- **Does not install system-wide keyboard or mouse hooks**, capture remote arrow/OK events, or block the mouse elsewhere.
- **Does not hide itself for one-shot mouse clicks**. The experimental `LEFT CLICK` / `RIGHT CLICK` conversion controls are deliberately unavailable in safe mode. Normal pointer clicks outside Firefly continue normally.
- Never auto-terminates an existing Firefly instance. A repeat launch returns to the existing window.
- Never forces foreground focus on pointer leave or to deliver text. Click the actual target text field first, then type.
- Shows a `SAFE · POINTER` indicator. If D-pad-only input does not behave like a pointer, this safe default is intentionally less capable than hook mode. Do not enable advanced input unless another reliable recovery path exists.

The **OSK** app shortcut starts Windows' built-in keyboard, independently of Firefly. The close (×) control requires two presses within 2.5 seconds to avoid accidental closure.

Startup and Tk callback errors are appended to `%LOCALAPPDATA%\FireflyDeskKeyboard\startup.log`. Launch `Debug Firefly Keyboard.cmd` to display failures in a console without replacing OSK. An application can still crash; safe mode minimizes its effects on the rest of the remote session, not guarantees a crash-free Windows runtime.

**Advanced features** (`--advanced-input` in a manually invoked command) install global input hooks for remote navigation and one-shot right-click conversion. They are intentionally **opt-in** and not recommended when Firefly is the only feasible input method. Microsoft's documentation warns that low-level input hooks can time out and be removed silently.

The Illinois AnyWare service may disconnect idle sessions after 15 minutes and log them off one hour after disconnection. Save critical work to a persistent university-supported location.

## Remote interaction

- In **safe mode**, click/tap the visible Firefly keys using the remote-controlled pointer; the standard Windows input path handles remote clicks. The 300 ms identical-action guard mitigates accidentally doubled remote clicks, but can also suppress genuinely rapid repeated characters.
- `SHIFT` is one-shot uppercase; its selection survives redraw, and it cancels sticky Ctrl so that typing cannot unintentionally interrupt a terminal with Ctrl+C.
- `TOP/BOTTOM`, `SIZE`, `123`, `PASTE`, and word suggestions are available without global hooks.
- If typing reports **Click the destination field first**, click the destination text field outside Firefly to establish focus. Safe mode does not silently move focus or send text to an unrelated app.
- The `INSPECT` hook-based diagnostic and D-pad interception are disabled in safe mode; they require `--advanced-input`.


## Quick launch

The **APPS** row opens `CMD`, `POWERSHELL`, `FILES`, `NOTEPAD`, `CHROME`, `RUN`, and **`OSK`** (Windows' On-Screen Keyboard). Chrome is resolved through Windows App Paths or typical install locations; if Chrome is not installed in the Illinois AnyWare image, Firefly reports that instead of failing. `RUN` opens Windows' native Run dialog.

On shared/managed university desktops, installed apps and their permissions can differ from a personal Windows PC.


## Click anywhere (advanced only)

Native pointer clicks already work **outside** the Firefly overlay and do not need mouse hooks. Firefly's custom one-shot LEFT/RIGHT CLICK conversion behind the overlay is hidden in **safe mode** because it would otherwise intercept global remote input and briefly withdraw the keyboard.

If the Citrix touch client exposes gestures, Citrix documents touch-hold-release for right-click. That gesture may **not** be available through a physical Fire TV remote. Avoid enabling experimental hooks just to access right-click until a fallback input method exists.


## Predictive text

The three WORDS keys offer word completions and explicit spelling suggestions. Predictions now rank candidates using the preceding word (locally learned bigrams), individual learned word frequency, and the small built-in common-words list, with local spelling-dictionary additions. **Suggestions are never auto-inserted.** Selecting one replaces the current word and appends a space.

Learned words and word-pair counts are stored locally in `%LOCALAPPDATA%\FireflyDeskKeyboard\language.json` when Firefly closes normally. No cloud service is used. **Do not type secrets through the keyboard unless you accept that its local learning model can record the typed words.** The current model is intentionally lightweight; for larger vocabulary and typo correction, see [SymSpellPy](https://github.com/mammothb/symspellpy) and [Presage](https://presage.sourceforge.io/) as research directions, not installed dependencies.

## Input diagnostics

Safe mode preserves the existing Windows/remote-desktop event path and does not inspect or swallow global mouse/keyboard events. When advanced mode is deliberately enabled, `INSPECT` can capture native `VK` / `SCAN` codes, but a Citrix/Fire TV client may already have transformed or discarded the original remote button identity.

Text uses `SendInput` when Firefly's target is verified foreground, with targeted message fallback for compatible controls. A posted Win32 message does not prove a modern application accepted text. Always verify in the actual field, particularly in a terminal.


## Useful upstream references

- [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput) and [MOUSEINPUT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput): native keyboard and mouse event injection.
- [Microsoft winappCli UI automation](https://github.com/microsoft/winappCli): target verification and transport tradeoffs; not required by Firefly.
- [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher): mature launcher ideas if a fuller app-search workflow becomes necessary.
- [SymSpellPy](https://github.com/mammothb/symspellpy): frequency-aware typo correction for future predictor development.

## Limits

Only source-level review and basic sanity checks can be done without the actual interactive Windows/Fire TV session. Validate Shift → letter → Shift, Ctrl → Shift → C in a **non-destructive scratch editor**, launching CMD, and both one-shot click modes before relying on the revised program for critical work.
