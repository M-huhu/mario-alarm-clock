"""Mario-themed desktop alarm clock application.

A fun alarm clock with Mario pixel art, 8-bit sounds, and smooth animations.
"""

import tkinter as tk
from ui import MarioAlarmUI
import sounds


def main():
    # Initialize sound system
    sounds.init_sound()

    root = tk.Tk()
    app = MarioAlarmUI(root)

    root.protocol("WM_DELETE_WINDOW", lambda: (sounds.stop_sound(), root.destroy()))
    root.mainloop()


if __name__ == '__main__':
    main()
