# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Mario-themed desktop alarm clock — a single-window tkinter app with pixel-art Mario decorations, 8-bit sounds via pygame, and alarm/snooze/stop functionality.

## Running the app

```bash
pip install pygame numpy
cd mario_alarm_clock
python main.py
```

On Windows, the full Python path may be needed:
```
E:\app\mypython\python.exe main.py
```

`启动闹钟.bat` launches the app via `pythonw.exe` (no console window).

## Architecture

```
main.py       → entry point, inits sound + tkinter Tk, wires WM_DELETE_WINDOW
ui.py         → MarioAlarmUI class — builds canvas, clock loop, animation, button callbacks
alarm.py      → AlarmClock state machine — set/toggle/check/snooze/stop, thread-safe via threading.Lock
sounds.py     → pygame-based 8-bit tone generation, all playback in background daemon threads
mario_draw.py → pure drawing functions for tkinter Canvas (Mario sprite, blocks, pipe, clouds, etc.)
```

**Data flow:** `main.py` creates `MarioAlarmUI(root)`, which owns an `AlarmClock` instance. The clock loop (`_update_clock`, fires every 250ms via `root.after`) calls `alarm.check(h, m, s)` each tick. When the alarm triggers, `AlarmClock` fires `_on_trigger` / `_on_stop` callbacks back into the UI layer.

## Key design decisions

- **All visuals are programmatic** — no image assets. Mario is a 16x14 pixel grid drawn as tkinter Canvas rectangles (`mario_draw.py:7-84`).
- **Sound is procedural** — square/sine/mix waveforms generated via numpy, shaped with ADSR envelopes (`sounds.py:23-66`). No copyrighted audio.
- **Sound plays on background threads** — `_play_notes_async` spawns daemon threads so the GUI never blocks (`sounds.py:80-86`).
- **AlarmClock is a plain state machine** — no tkinter dependency. UI reads `.status` (returns `'off'|'on'|'ringing'|'snoozed'`) and renders accordingly.
- **Animation loop only runs while ringing** — `_anim_tick` self-terminates when `alarm.ringing` goes false, avoiding idle work (`ui.py:232-240`).
- **Change detection on display updates** — `_refresh_alarm_display` compares cached strings before touching canvas items, avoiding redundant tkinter calls (`ui.py:207-219`).
- **Thread safety on alarm state** — all AlarmClock mutations use `threading.Lock` because the alarm check runs on the tkinter timer thread and sound callbacks run on background threads (`alarm.py`).

## Python environment

The system Python is at `E:\app\mypython\python.exe`. The Windows `python` shim (`WindowsApps/python.exe`) is a Microsoft Store stub — always use the full path or ensure PATH precedence.
