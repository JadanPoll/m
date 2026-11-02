# Desktop-wide OK duplicate filtering (optional, separate from Firefly)

**Why:** In the TV → Amazon Silk → browser remote desktop → Windows chain,
one physical remote OK can become a second Windows left click on release.
Firefly's in-window debounce cannot prevent a second click on File Explorer,
ordinary desktop controls, browsers, or other applications.

**Existing, independently maintained software:** [marvinlehmann/Mouse-Debouncer](https://github.com/marvinlehmann/Mouse-Debouncer)
(MIT; Windows tray executable; released builds at
[GitHub Releases](https://github.com/marvinlehmann/Mouse-Debouncer/releases)).
It filters a new mouse-down arriving too soon after the previous mouse-up,
and exposes `--left=220` (milliseconds) as a command-line option.
Another existing project, [nenning/DoubleClickFix](https://github.com/nenning/DoubleClickFix),
has richer diagnostics but recent builds require .NET 10.

## Opt-in, no automatic installation

1. While normal computer input is available, inspect/download the upstream
   `MouseDebouncer64.exe` release. Place it beside
   `Start Desktop OK Debounce.cmd` or under `tools/`.
2. Run **Start Desktop OK Debounce.cmd**. It intentionally does nothing if
   the executable is absent or already running.
3. Run **Stop Desktop OK Debounce.cmd** to terminate the optional helper and
   immediately restore ordinary Windows click input. Also use the helper's
   own tray Exit control. The keyboard NEVER launches this tool automatically.
4. If 220 ms suppresses deliberate clicks or fails to suppress remote
   duplicates, change the one `--left=220` argument in the Start script,
   after assessing the actual user experience. No setting is guaranteed
   correct for every browser or remote desktop.

## Safety and limits

- **Not tested on Illinois AnyWare.** It may be blocked by university policy,
  fail to receive remote input, or not operate on elevated/secure windows.
  Never make it the only method of controlling the machine.
- The helper uses a global Windows mouse hook. Firefly deliberately doesn't:
  earlier Python low-level hook callbacks were associated with serious crashes.
  This is a separately operated and independently compiled program.
- This intentionally affects the **entire guest Windows desktop**, not Silk's
  local UI. It cannot stop two actions if the browser's remote-desktop client
  has already handled them outside Windows input delivery.
- Fast intentional double-clicks (for example, opening folders) may also be
  filtered. The user can choose a deliberate click interval above the
  threshold, or configure single-click-to-open in Explorer. Do not confuse
  a stable input contract with pretending we can distinguish intent from two
  otherwise identical click pairs.
- Never auto-start on login. Stop and Start scripts remain visible and
  independent of the Firefly GUI, so a Firefly crash cannot remove the exit.

**Separate problems:** Firefly's FAST mode handles the *location and meaning*
of OK inside its own window. The global optional helper handles the *count*
of Windows mouse clicks in other applications. Neither solves the other's job.
