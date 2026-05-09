"""Alarm clock state machine."""

import threading


class AlarmClock:
    """Manages alarm state: set, check, trigger, snooze, stop."""

    def __init__(self):
        self._alarm_hour = 7
        self._alarm_minute = 0
        self._enabled = False
        self._ringing = False
        self._snooze_count = 0
        self._on_trigger = None
        self._on_stop = None
        self._lock = threading.Lock()

    # -- read-only properties --

    @property
    def alarm_hour(self):
        return self._alarm_hour

    @property
    def alarm_minute(self):
        return self._alarm_minute

    @property
    def enabled(self):
        return self._enabled

    @property
    def ringing(self):
        return self._ringing

    @property
    def snooze_count(self):
        return self._snooze_count

    @property
    def status(self):
        """Return a status code the UI layer can format:
        'off' | 'on' | 'ringing' | 'snoozed'
        """
        if self._ringing:
            return 'ringing'
        if self._enabled:
            return 'snoozed' if self._snooze_count > 0 else 'on'
        return 'off'

    # -- callbacks --

    def set_on_trigger(self, callback):
        self._on_trigger = callback

    def set_on_stop(self, callback):
        self._on_stop = callback

    # -- commands --

    def set_alarm(self, hour, minute):
        """Set alarm time (24-hour format)."""
        with self._lock:
            self._alarm_hour = hour % 24
            self._alarm_minute = minute % 60

    def toggle(self):
        """Toggle alarm enabled state."""
        with self._lock:
            self._enabled = not self._enabled
            if not self._enabled:
                self._ringing = False
                self._snooze_count = 0

    def set_enabled(self, enabled):
        """Explicitly set enabled state."""
        with self._lock:
            self._enabled = enabled
            if not enabled:
                self._ringing = False
                self._snooze_count = 0

    def check(self, current_hour, current_minute, current_second):
        """Check if alarm should trigger. Returns True if triggered."""
        with self._lock:
            if not self._enabled or self._ringing:
                return False
            if (current_hour == self._alarm_hour
                    and current_minute == self._alarm_minute
                    and current_second <= 1):  # tolerant window
                self._ringing = True
                if self._on_trigger:
                    self._on_trigger()
                return True
            return False

    def snooze(self, current_hour=None, current_minute=None, minutes=5):
        """Snooze the alarm for N minutes.
        Accepts optional current time; falls back to system clock if omitted.
        """
        with self._lock:
            if not self._ringing:
                return
            self._ringing = False
            self._snooze_count += 1

            if current_hour is None or current_minute is None:
                import time
                now = time.localtime()
                current_hour = now.tm_hour
                current_minute = now.tm_min

            total_minutes = current_hour * 60 + current_minute + minutes
            self._alarm_hour = (total_minutes // 60) % 24
            self._alarm_minute = total_minutes % 60
            self._enabled = True
            if self._on_stop:
                self._on_stop()

    def stop(self):
        """Stop/dismiss the alarm completely."""
        with self._lock:
            self._ringing = False
            self._enabled = False
            self._snooze_count = 0
            if self._on_stop:
                self._on_stop()

    def get_display_time(self):
        """Get alarm time as formatted HH:MM string."""
        return f"{self._alarm_hour:02d}:{self._alarm_minute:02d}"
