# Firefly Desk Keyboard

A native, remote-oriented Windows on-screen keyboard for a Fire TV/remote-desktop pointer, D-pad, and OK button. No server, administrator rights, or network connection required; uses Python/Tkinter and Win32 APIs already available on the host.

## Critical: Illinois AnyWare / TV-remote safe mode (default)

This program is operating inside an **Illinois AnyWare remote session**, possibly controlled only by a TV remote. **Avoid losing access to the university desktop.** The regular `Launch Firefly Keyboard.cmd` starts in safe pointer mode:

- **Does not close Windows On-Screen Keyboard (OSK)**, even when an old launcher accidentally passes `--replace-osk`.
- **Does not install system-wide keyboard or mouse hooks** or block mouse/keyboard events elsewhere. The optional input inspector observes key state with a Tk timer; it cannot intercept the remote.
- **Does not intercept mouse clicks or hold a mouse button while you navigate**. The `MOUSE` panel uses an explicit countdown to capture the remote pointer over a target, then injects a click or a short atomic drag. Ordinary pointer clicks outside Firefly continue normally.
- Never auto-terminates an existing Firefly instance. A repeat launch returns to the existing window.
- Never forces foreground focus on pointer leave or to deliver text. Click the actual target text field first, then type.
- Shows a `SAFE · POINTER` indicator. If D-pad-only input does not behave like a pointer, the optional `--advanced-input` mode can **observe** directional keys by polling, but cannot swallow their underlying Windows events.

The **OSK** app shortcut starts Windows' built-in keyboard, independently of Firefly. The close (×) control requires two presses within 2.5 seconds to avoid accidental closure.

Startup and Tk callback errors are appended to `%LOCALAPPDATA%\FireflyDeskKeyboard\startup.log`. Launch `Debug Firefly Keyboard.cmd` to display failures in a console without replacing OSK. An application can still crash; safe mode minimizes its effects on the rest of the remote session, not guarantees a crash-free Windows runtime.

**Crash regression fix:** Previous versions created Python `WINFUNCTYPE` callbacks for Windows low-level keyboard/mouse hooks; these could re-enter Tk and are suspected in the reported `PyEval_RestoreThread` fatal error. **Both callback creation and hook installation have been removed completely.** Advanced mode (`--advanced-input`) now uses non-intercepting `GetAsyncKeyState` polling from Tk's event loop. No remote event is stolen. The tradeoff is that very short presses can be missed, and a mouse left-click cannot safely be converted into a right-click without also reaching the underlying app.

The Illinois AnyWare service may disconnect idle sessions after 15 minutes and log them off one hour after disconnection. Save critical work to a persistent university-supported location.

## Movable TV dock and transparency

The previous 34%-height cap was too aggressive: it made the keyboard unnecessarily cramped and removed useful screen-positioning control. The keyboard now defaults to a **comfortable height around 43% of the AnyWare work area**, with a **46% maximum** (including the title bar, always under half the vertical desktop). Its keys still scale with `SIZE`.

The title bar offers four separate controls:

- **MOVE ↑ / MOVE ↓**: shift the complete keyboard up/down **72 pixels per press**, with clamping so the entire window stays onscreen. These work even while collapsed.
- **TOP/BOTTOM**: jump immediately between the two work-area edges and reset the incremental offset.
- **HIDE / SHOW**: collapse to a thin, always-available control strip, then restore the full-size keyboard at its previous position.
- **APPS**: reveal CMD, PowerShell, Files, Notepad, Chrome, Run and OSK only while needed.

All movement uses normal window geometry, not global hooks, and doesn't affect the Windows fallback OSK.

Idle opacity remains **24%** (hover **88%**). Transparency is only visual: the overlay continues to capture pointer clicks within its bounds, so MOVE or HIDE is the reliable way to reach a control behind it.

## Menu debounce

Tool buttons now have **per-control debouncing** rather than only checking the last action. Each menu control is guarded for **700 ms**; MOVE UP/DOWN use **360 ms** to allow repeated position adjustments. `HIDE` and `SHOW` share a stable debounce identity, so a duplicated remote OK cannot immediately reverse the toggle. Normal letter typing retains its separate 300 ms guard.

Option controls also keep independent debounce history: toggles/actions such as `CTRL`, `SHIFT`, `123/ABC`, `PASTE`, `ENTER`, and word suggestions use **550 ms**. Repeatable editing/navigation options (`BACKSPACE`, arrows, Home/End, Page Up/Down and Delete) use **140 ms**, blocking a duplicated remote click while preserving deliberate rapid movement.

The remote's measured OK/Select signal is also guarded once at the Firefly-window level. A second left-button press within **120 ms** and 18 pixels of the first is discarded before any key command runs. This protects every Firefly control without installing a system-wide mouse hook or altering clicks in other Windows applications.

## D-pad snap navigation

The remote desktop converts D-pad taps into accelerated pointer motion instead of `VK_LEFT/RIGHT/UP/DOWN`. While the pointer is over Firefly, strongly horizontal or vertical motion is therefore treated as one neighboring-key step and the pointer is snapped to that key's center. A **160 ms** step guard plus a **240 ms quiet-period lock** keeps every follow-on event from the same accelerated tap pinned to that center, so the physical OK click cannot drift back to another key. Once the burst goes quiet, normal mouse hover immediately highlights the control underneath. Diagonal mouse motion is left alone, and capture/inspector mode remains observation-only except for hover highlighting.

## Map a TV remote

Run `python firefly_keyboard.pyw --capture-remote`. The red **REMOTE CAPTURE** row reports key DOWN/UP transitions as virtual-key numbers and names, plus pointer deltas when a remote button is translated into mouse movement. Move the pointer above/outside Firefly, then press each remote button once; clicking a Firefly key intentionally creates output that is annotated as likely application output rather than raw remote input. The observation-only session is appended locally to `%LOCALAPPDATA%\FireflyDeskKeyboard\remote-input-capture.log`; it installs no hooks, swallows no input, and sends nothing over the network. Very short client-side events can still be discarded before Windows exposes them.

## Remote interaction

- In **safe mode**, click/tap the visible Firefly keys using the remote-controlled pointer; the standard Windows input path handles remote clicks. The 300 ms identical-action guard mitigates accidentally doubled remote clicks, but can also suppress genuinely rapid repeated characters.
- `SHIFT` is **one-shot uppercase**: select SHIFT, then a letter. Shift updates its key labels **in place**, and capitalization is resolved when the letter is pressed. This fixes the earlier case where the label displayed uppercase but the command still sent lowercase. Shift and Ctrl cancel each other's sticky state to prevent unintended terminal shortcuts. `123` is still the symbol layout; physical held Shift+key combinations are not emulated by the Shift button.
- `TOP/BOTTOM`, `SIZE`, `123`, `PASTE`, and word suggestions are available without global hooks.
- If typing reports **Click the destination field first**, click the destination text field outside Firefly to establish focus. Safe mode does not silently move focus or send text to an unrelated app.
- `INSPECT` now works in safe mode without hooks: it samples native virtual-key press transitions. The client may still discard or translate remote buttons before they reach Windows. D-pad navigation by polling is opt-in; it cannot suppress original arrow-key actions in the target application.


## Quick launch

The **APPS** row opens `CMD`, `POWERSHELL`, `FILES`, `NOTEPAD`, `CHROME`, `RUN`, and **`OSK`** (Windows' On-Screen Keyboard). Chrome is resolved through Windows App Paths or typical install locations; if Chrome is not installed in the Illinois AnyWare image, Firefly reports that instead of failing. `RUN` opens Windows' native Run dialog.

On shared/managed university desktops, installed apps and their permissions can differ from a personal Windows PC.


## Right-click, left-click and drag without stealing the remote

Open the **MOUSE** menu in Firefly's title row. These functions are available in normal safe mode; they use Windows `SendInput` and **do not require global hooks**.

**Click anywhere:** Press `RIGHT • 4.5s` or `LEFT • 4.5s`, then move the TV-controlled pointer **off Firefly and over the exact target**. After 4.5 seconds Firefly sends one corresponding mouse click there. **CANCEL / CLEAR** aborts a pending countdown. Aiming at Firefly itself cancels the action instead of clicking a menu button accidentally.

**Drag between two desktop positions:** Press `DRAG FROM • 4.5s`, move the pointer to the drag start, and allow the countdown to capture it. Next press `DRAG TO • 4.5s`, move the pointer to the destination, and allow that countdown to capture the endpoint. Firefly inserts mouse-down, several moves and mouse-up in **one bounded SendInput batch**. It never intentionally keeps a button held between actions or while you move the TV remote. `CANCEL / CLEAR` discards a pending capture and its start position.

Because the drag is a short synthesized sequence and not a physically held mouse button, some applications (including Citrix-hosted ones) may not recognize every drag. Windows may also deny input to elevated or secure surfaces, and a successful SendInput call does not prove the application acted. **Try a harmless file selection or text selection before relying on it for any consequential operation.** The regular OSK and Citrix input path remain available if Firefly exits.





