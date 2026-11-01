# Firefly Desk Keyboard

A native, remote-oriented Windows on-screen keyboard for a Fire TV/remote-desktop pointer, D-pad, and OK button. No server, administrator rights, or network connection required; uses Python/Tkinter and Win32 APIs already available on the host.

## Start and recovery

Double-click `Launch Firefly Keyboard.cmd`. It closes the legacy Windows On-Screen Keyboard window so that the two keyboards do not overlap, **without disabling or uninstalling Windows OSK**. You can reopen OSK normally if Firefly cannot receive input.

The close (×) control requires a second press within 2.5 seconds, preventing a remote pointer mistake from immediately shutting down the keyboard. If the keyboard fails to open, run `python firefly_keyboard.pyw` from a command prompt to see a Python error (the normal launcher uses `pythonw` and hides console output).

## Remote interaction

- Move with the D-pad or remote pointer; click/OK activates the highlighted key. A 75 ms guard limits duplicate navigation.
- Duplicate identical key actions inside 300 ms are suppressed. This can also suppress *intentional* rapid identical presses; the guard is still a heuristic, not reliable physical-event deduplication.
- Shift is **one-shot** for capitals, highlights when active, and preserves selection on redraw. Shift and Ctrl cancel each other's sticky state to avoid accidental Ctrl+C in a terminal.
- Ctrl is one-shot for shortcuts. Be deliberate with Ctrl+C/Ctrl+D in a running terminal because those have real effects. Shift+Ctrl combinations aren't currently provided.
- `TOP/BOTTOM` moves the keyboard. `SIZE` cycles three scale presets. `123` switches symbols.
- `PASTE` reads clipboard text directly when possible; otherwise attempts Ctrl+V. The target must accept the text. Click a destination text field before typing.

## Quick launch

Use the **APPS / DESKTOP** strip: `CMD`, `POWERSHELL`, `FILES` (Explorer), and `NOTEPAD` open those applications in your Windows session. `RUN` opens Windows' built-in Win+R dialog to start *other* installed apps without bloating Firefly with another launcher. Newly opened programs can take a moment to become the tracked target.

## Click anywhere (including behind Firefly)

Choose `LEFT CLICK` or `RIGHT CLICK` in the APPS / DESKTOP strip. The keyboard temporarily hides. Move the remote pointer to the desired location and click/OK **once**. Firefly converts that event into one left or right click, then restores itself.

- ESC cancels the armed click. If no click arrives, Firefly restores itself automatically after 20 seconds.
- The right-click mode converts the next physical left click or OK/Enter into a right click. It does **not** permanently remap the remote.
- Click injection needs an unlocked, interactive Windows desktop and is limited by Windows integrity/security boundaries. It cannot operate on UAC/secure login screens.

## Predictive text

The three WORDS keys offer word completions and explicit spelling suggestions. Predictions now rank candidates using the preceding word (locally learned bigrams), individual learned word frequency, and the small built-in common-words list, with local spelling-dictionary additions. **Suggestions are never auto-inserted.** Selecting one replaces the current word and appends a space.

Learned words and word-pair counts are stored locally in `%LOCALAPPDATA%\FireflyDeskKeyboard\language.json` when Firefly closes normally. No cloud service is used. **Do not type secrets through the keyboard unless you accept that its local learning model can record the typed words.** The current model is intentionally lightweight; for larger vocabulary and typo correction, see [SymSpellPy](https://github.com/mammothb/symspellpy) and [Presage](https://presage.sourceforge.io/) as research directions, not installed dependencies.

## Input diagnostics

Click `INSPECT`, press an unknown remote button once, and read its native `VK`/`SCAN` values. The inspector is off by default; it keeps only three recent events in memory and never saves the event log. A browser reporting `key="Unidentified"` cannot reconstruct keys that were already discarded before reaching Windows.

Input now prefers native `SendInput` for foreground targets, with a targeted Win32 message fallback for compatible controls. Posted-message success **does not prove** the application consumed a character, particularly in modern windowless UI frameworks. Windows can deny focus/injection into elevated or secure applications. Verify text in the actual target before using any potentially destructive shortcut or command.

## Useful upstream references

- [Microsoft SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput) and [MOUSEINPUT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput): native keyboard and mouse event injection.
- [Microsoft winappCli UI automation](https://github.com/microsoft/winappCli): target verification and transport tradeoffs; not required by Firefly.
- [Flow Launcher](https://github.com/Flow-Launcher/Flow.Launcher): mature launcher ideas if a fuller app-search workflow becomes necessary.
- [SymSpellPy](https://github.com/mammothb/symspellpy): frequency-aware typo correction for future predictor development.

## Limits

Only source-level review and basic sanity checks can be done without the actual interactive Windows/Fire TV session. Validate Shift → letter → Shift, Ctrl → Shift → C in a **non-destructive scratch editor**, launching CMD, and both one-shot click modes before relying on the revised program for critical work.
