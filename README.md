# Firefly Desk Keyboard

A native, remote-safe Windows on-screen keyboard. It types into the currently focused desktop application and does not require a browser or network connection.

## Start

Double-click `Launch Firefly Keyboard.cmd`.

The launcher politely closes the legacy Windows On-Screen Keyboard window so it cannot cover Firefly Keyboard. It does not disable or uninstall Windows OSK; you can reopen it normally at any time.

## Remote controls

- Click keys with the Fire TV/remote-desktop pointer.
- A repeated activation of the same key within 300 ms is discarded.
- `TOP/BOTTOM` moves the keyboard without dragging.
- `SIZE` cycles through three key sizes.
- `123` opens numbers and symbols.
- `PASTE` sends Ctrl+V to the active application.

## Identify the unknown remote button

Click `INSPECT`, press the unknown button once, and read the native `VK` and `SCAN` values. The inspector is off by default, keeps only three events in memory, and never saves them.

The browser previously reported `key="Unidentified"` and no `code`, so the exact button cannot be recovered from that web log. The native inspector operates one layer earlier, before Chromium discards the Windows key identity.
