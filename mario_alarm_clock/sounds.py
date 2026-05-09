"""8-bit style sound generation with rich waveforms and Mario-inspired melodies.

All note-playing runs in background threads to avoid blocking the tkinter GUI.
"""

import threading
import numpy as np
import pygame

_sample_rate = 44100
_initialized = False


def init_sound():
    """Initialize pygame mixer for sound playback."""
    global _initialized
    if _initialized:
        return
    pygame.mixer.init(frequency=_sample_rate, size=-16, channels=2, buffer=512)
    _initialized = True


def _make_tone(frequency, duration_ms, volume=0.3, wave_type='mix'):
    """Generate a rich tone as a pygame Sound object."""
    samples = int(_sample_rate * duration_ms / 1000)
    t = np.arange(samples, dtype=np.float32) / _sample_rate

    sin_wave = np.sin(2 * np.pi * frequency * t)
    if wave_type == 'square':
        wave = np.sign(sin_wave)
    elif wave_type == 'sine':
        wave = sin_wave
    else:  # 'mix' — square fundamental + sine warmth
        wave = np.sign(sin_wave) * 0.8 + sin_wave * 0.15
        wave += np.sin(2 * np.pi * frequency * 2 * t) * 0.05

    # ADSR envelope with overflow protection
    attack_ms = min(8, duration_ms * 0.15)
    decay_ms = min(30, duration_ms * 0.3)
    release_ms = min(50, duration_ms * 0.4)
    sustain_level = 0.7

    a = max(1, int(_sample_rate * attack_ms / 1000))
    d = max(1, int(_sample_rate * decay_ms / 1000))
    r = max(1, int(_sample_rate * release_ms / 1000))
    total_env = a + d + r
    if total_env > samples:
        scale = samples / total_env
        a = max(1, int(a * scale))
        d = max(1, int(d * scale))
        r = max(1, int(r * scale))

    s_start = a + d
    r_start = max(s_start + 1, samples - r)

    envelope = np.ones(samples, dtype=np.float32) * sustain_level
    envelope[:a] = np.linspace(0, 1, a)
    if d > 0 and s_start > a:
        envelope[a:s_start] = np.linspace(1, sustain_level, s_start - a)
    if r > 0 and r_start < samples:
        envelope[r_start:] = np.linspace(sustain_level, 0, samples - r_start)

    wave = wave * envelope * volume
    wave = (wave * 32767).astype(np.int16)
    wave_2d = np.column_stack((wave, wave))
    return pygame.sndarray.make_sound(wave_2d)


def _play_notes(notes, base_duration_ms=100, volume=0.25, gap_ms=15):
    """Play a sequence of (frequency, duration_multiplier) tuples synchronously.

    This is called from background threads to avoid blocking the GUI.
    """
    for freq, mult in notes:
        tone = _make_tone(freq, int(base_duration_ms * mult), volume=volume)
        tone.play()
        pygame.time.wait(int(base_duration_ms * mult) + gap_ms)


def _play_notes_async(notes, base_duration_ms=100, volume=0.25, gap_ms=15):
    """Play notes in a background daemon thread — non-blocking."""
    threading.Thread(
        target=_play_notes,
        args=(notes, base_duration_ms, volume, gap_ms),
        daemon=True
    ).start()


def play_alarm_melody():
    """Play Mario-inspired alarm melody (non-blocking)."""
    init_sound()
    melody = [
        (523, 1.0), (659, 1.0), (784, 1.0), (1047, 1.5),
        (784, 0.5), (1047, 0.5), (1319, 2.0),
    ]
    arp = [
        (1319, 0.4), (1175, 0.4), (1047, 0.4), (988, 0.4), (784, 0.6),
    ]

    def _play_both():
        _play_notes(melody, base_duration_ms=90, volume=0.22, gap_ms=20)
        _play_notes(arp, base_duration_ms=70, volume=0.18, gap_ms=10)

    threading.Thread(target=_play_both, daemon=True).start()


def play_jump_sound():
    """Play Mario jump sound — rising sweep (non-blocking)."""
    init_sound()
    notes = [(400, 0.5), (500, 0.5), (600, 0.5), (700, 0.5), (800, 0.5)]
    _play_notes_async(notes, base_duration_ms=50, volume=0.18, gap_ms=0)


def play_coin_sound():
    """Play coin collect sound — bright double ding (non-blocking)."""
    init_sound()
    notes = [(988, 0.8), (1319, 1.2)]
    _play_notes_async(notes, base_duration_ms=75, volume=0.21, gap_ms=5)


def stop_sound():
    """Stop all sounds immediately."""
    pygame.mixer.stop()
