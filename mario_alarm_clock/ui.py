"""Main UI for Mario Alarm Clock."""

import math
import tkinter as tk
from datetime import datetime
import mario_draw as md
import sounds
from alarm import AlarmClock

WIN_WIDTH = 520
WIN_HEIGHT = 680
GROUND_Y = 530

# Alarm status → display mapping (view logic stays in the view)
STATUS_LABELS = {
    'ringing': ('WAKE UP! ★', '#FF3333'),
    'on':      ('ON', '#00FF00'),
    'snoozed': ('ON (snoozed)', '#FFAA00'),
    'off':     ('OFF', '#FFD700'),
}


class MarioAlarmUI:
    """Main application UI with smooth animations and rich decorations."""

    def __init__(self, root):
        self.root = root
        self.root.title("Mario Alarm Clock")
        self.root.resizable(False, False)
        self.root.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.root.configure(bg=md.SKY_BLUE)

        self.alarm = AlarmClock()
        self.alarm.set_on_trigger(self._on_alarm_trigger)
        self.alarm.set_on_stop(self._on_alarm_stop)

        # Animation state
        self._animating = False
        self._anim_phase = 0.0
        self._anim_speed = 0.12
        self._anim_timer_id = None
        self._current_mario_y = 0
        self._mario_items = []
        self._qblock_items = []
        self._melody_cooldown = 0

        # Display cache for change detection
        self._last_status = ''
        self._last_alarm_display = ''

        self._build_ui()
        self._update_clock()

    # ─── build ──────────────────────────────────────────────────

    def _build_ui(self):
        self.canvas = tk.Canvas(self.root, width=WIN_WIDTH, height=WIN_HEIGHT,
                                bg=md.SKY_BLUE, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        md.draw_sky(self.canvas, WIN_WIDTH, WIN_HEIGHT)
        md.draw_hill(self.canvas, -30, GROUND_Y, 160, 70)
        md.draw_hill(self.canvas, 300, GROUND_Y, 200, 55)

        md.draw_cloud(self.canvas, 20, 30, 1.2)
        md.draw_cloud(self.canvas, 280, 55, 0.9)
        md.draw_cloud(self.canvas, 380, 20, 1.0)
        md.draw_cloud(self.canvas, 120, 75, 0.7)

        md.draw_ground(self.canvas, WIN_WIDTH, GROUND_Y)

        # Mario
        self.mario_x = 90
        self.mario_base_y = GROUND_Y - 16 * 6
        self._current_mario_y = self.mario_base_y
        self._mario_items = md.draw_mario(self.canvas, self.mario_x, self.mario_base_y)

        # Decorations
        md.draw_pipe(self.canvas, 400, GROUND_Y - 90, GROUND_Y)
        self._qblock_items = md.draw_question_block(self.canvas, 424, GROUND_Y - 140)

        for i in range(3):
            md.draw_brick_block(self.canvas, 35 + i * 40, GROUND_Y - 115)
        for i in range(3):
            md.draw_coin(self.canvas, 45 + i * 40, GROUND_Y - 140)

        md.draw_flag(self.canvas, 35, GROUND_Y, 110)
        md.draw_bush(self.canvas, 210, GROUND_Y - 20)

        self._draw_title_banner()
        self._draw_clock_panel()
        self._draw_alarm_section()
        self._draw_buttons()

    def _draw_title_banner(self):
        cx, y = WIN_WIDTH // 2, 18
        self.canvas.create_text(cx + 1, y + 1, text='★ MARIO ALARM ★',
                                font=('Arial', 18, 'bold'), fill='#C88000')
        self.canvas.create_text(cx, y, text='★ MARIO ALARM ★',
                                font=('Arial', 18, 'bold'), fill='#FFD700')
        self.canvas.create_text(cx, y + 22, text='超级马里奥闹钟',
                                font=('Arial', 9), fill='#FFFFFF')

    def _draw_clock_panel(self):
        cx, cy = WIN_WIDTH // 2, 62
        pw, ph = 220, 68

        self.canvas.create_rectangle(cx - pw // 2 + 2, cy + 2,
                                     cx + pw // 2 + 2, cy + ph + 2,
                                     fill='#0A0A18', outline='', width=0)
        self.canvas.create_rectangle(cx - pw // 2, cy,
                                     cx + pw // 2, cy + ph,
                                     fill='#1A1A2E', outline='#C88000', width=2)
        self.canvas.create_rectangle(cx - pw // 2 + 4, cy + 4,
                                     cx + pw // 2 - 4, cy + ph - 4,
                                     fill='', outline='#2A2A4E', width=1)

        md.draw_coin(self.canvas, cx - pw // 2 + 14, cy + 26, 18)
        self.clock_text = self.canvas.create_text(
            cx + 8, cy + 32, text='00:00:00',
            font=('Consolas', 32, 'bold'), fill='#FF3333')
        self.date_text = self.canvas.create_text(
            cx + 8, cy + 56, text='',
            font=('Consolas', 10), fill='#8888AA')

    def _draw_alarm_section(self):
        cx = WIN_WIDTH // 2
        base_y = 158

        self.canvas.create_text(cx, base_y + 10,
                                text='⏰ Alarm Time', font=('Arial', 11, 'bold'),
                                fill='#FFFFFF')

        self.hour_var = tk.StringVar(value=f'{self.alarm.alarm_hour:02d}')
        self.hour_sb = tk.Spinbox(
            self.root, from_=0, to=23, textvariable=self.hour_var,
            width=3, font=('Consolas', 15), justify='center',
            format='%02.0f', bg='#2A2A3E', fg='white',
            buttonbackground='#444466', relief='flat',
            readonlybackground='#2A2A3E')
        self.hour_sb.place(x=cx - 52, y=base_y + 28, width=50, height=32)

        self.canvas.create_text(cx + 2, base_y + 44, text=':',
                                font=('Consolas', 20, 'bold'), fill='#FFD700')

        self.minute_var = tk.StringVar(value=f'{self.alarm.alarm_minute:02d}')
        self.minute_sb = tk.Spinbox(
            self.root, from_=0, to=59, textvariable=self.minute_var,
            width=3, font=('Consolas', 15), justify='center',
            format='%02.0f', bg='#2A2A3E', fg='white',
            buttonbackground='#444466', relief='flat',
            readonlybackground='#2A2A3E')
        self.minute_sb.place(x=cx + 10, y=base_y + 28, width=50, height=32)

        self.alarm_time_text = self.canvas.create_text(
            cx, base_y + 80, text='Alarm: 07:00',
            font=('Consolas', 13), fill='#CCCCCC')

        self.alarm_status_text = self.canvas.create_text(
            cx, base_y + 102, text='OFF',
            font=('Arial', 14, 'bold'), fill='#FFD700')

    def _draw_buttons(self):
        cx = WIN_WIDTH // 2
        btn_w, btn_h = 90, 40
        h_gap = 26
        v_gap = 14
        base_y = 295

        left_x = cx - btn_w - h_gap // 2
        right_x = cx + h_gap // 2
        row1_y = base_y
        row2_y = base_y + btn_h + v_gap

        self.set_btn = self._make_btn(left_x, row1_y, btn_w, btn_h,
                                      'SET', md.BRICK_ORANGE, self._on_set_alarm)
        self.toggle_btn = self._make_btn(right_x, row1_y, btn_w, btn_h,
                                         'ON/OFF', '#0055C0', self._on_toggle)
        self.snooze_btn = self._make_btn(left_x, row2_y, btn_w, btn_h,
                                         'SNOOZE', md.PIPE_GREEN, self._on_snooze)
        self.stop_btn = self._make_btn(right_x, row2_y, btn_w, btn_h,
                                       'STOP', '#E52521', self._on_stop)

        md.draw_star(self.canvas, cx, row2_y - v_gap // 2, 8)

    def _make_btn(self, x, y, w, h, text, color, cmd):
        btn = tk.Button(
            self.root, text=text, command=cmd,
            font=('Arial', 11, 'bold'),
            bg=color, fg='white',
            activebackground=md.lighten_color(color, 0.35),
            relief='raised', bd=3, padx=0, pady=0)
        btn.place(x=x, y=y, width=w, height=h)
        return btn

    # ─── clock loop ─────────────────────────────────────────────

    def _update_clock(self):
        now = datetime.now()
        self.canvas.itemconfig(self.clock_text, text=now.strftime('%H:%M:%S'))
        self.canvas.itemconfig(self.date_text, text=now.strftime('%Y-%m-%d  %A'))

        self.alarm.check(now.hour, now.minute, now.second)
        self._refresh_alarm_display()
        self.root.after(250, self._update_clock)

    def _refresh_alarm_display(self):
        """Update alarm display only when content changed."""
        status = self.alarm.status
        if status != self._last_status:
            self._last_status = status
            label, color = STATUS_LABELS.get(status, ('OFF', '#FFD700'))
            self.canvas.itemconfig(self.alarm_status_text, text=label, fill=color)

        alarm_display = self.alarm.get_display_time()
        if alarm_display != self._last_alarm_display:
            self._last_alarm_display = alarm_display
            self.canvas.itemconfig(self.alarm_time_text,
                                   text=f'Alarm: {alarm_display}')

    # ─── animation loop (runs only when ringing) ─────────────────

    def _start_anim_timer(self):
        if self._anim_timer_id is None:
            self._anim_tick()

    def _stop_anim_timer(self):
        if self._anim_timer_id is not None:
            self.root.after_cancel(self._anim_timer_id)
            self._anim_timer_id = None

    def _anim_tick(self):
        if self._animating and self.alarm.ringing:
            self._do_bounce()
            self._do_flash()
            if self._melody_cooldown > 0:
                self._melody_cooldown -= 1
            self._anim_timer_id = self.root.after(33, self._anim_tick)
        else:
            self._anim_timer_id = None

    def _do_bounce(self):
        self._anim_phase += self._anim_speed
        sin_val = math.sin(self._anim_phase)
        offset = -48 * abs(sin_val)
        target_y = self.mario_base_y + offset

        delta = target_y - self._current_mario_y
        for item_id in self._mario_items:
            self.canvas.move(item_id, 0, delta)
        self._current_mario_y = target_y

        if self._melody_cooldown <= 0 and offset < -44:
            self._melody_cooldown = 30
            sounds.play_alarm_melody()

    def _do_flash(self):
        if not self._qblock_items:
            return
        bright = int(abs(math.sin(self._anim_phase * 3)) * 255)
        flash_color = f'#{bright:02x}{bright:02x}00'
        self.canvas.itemconfig(self._qblock_items[0], fill=flash_color)

    # ─── callbacks ──────────────────────────────────────────────

    def _on_set_alarm(self):
        try:
            h = int(self.hour_var.get()) % 24
            m = int(self.minute_var.get()) % 60
            self.alarm.set_alarm(h, m)
            self.alarm.set_enabled(True)
            self.alarm.stop()
            self._last_alarm_display = ''  # force refresh
            sounds.play_coin_sound()
        except ValueError:
            pass

    def _on_toggle(self):
        self.alarm.toggle()
        if self.alarm.enabled:
            sounds.play_jump_sound()
        else:
            sounds.stop_sound()
            self._stop_anim()

    def _on_snooze(self):
        if self.alarm.ringing:
            now = datetime.now()
            self.alarm.snooze(current_hour=now.hour, current_minute=now.minute)
            sounds.stop_sound()
            self._stop_anim()

    def _on_stop(self):
        self.alarm.stop()
        sounds.stop_sound()
        self._stop_anim()

    def _on_alarm_trigger(self):
        self._animating = True
        self._anim_phase = 0
        self._melody_cooldown = 0
        self._last_status = ''  # force status refresh
        self._start_anim_timer()
        sounds.play_alarm_melody()

    def _on_alarm_stop(self):
        self._stop_anim()

    def _stop_anim(self):
        self._animating = False
        self._melody_cooldown = 0
        self._stop_anim_timer()
        # Snap Mario back to base position
        if self._mario_items:
            dy = self.mario_base_y - self._current_mario_y
            for item_id in self._mario_items:
                self.canvas.move(item_id, 0, dy)
            self._current_mario_y = self.mario_base_y
        # Reset question block color
        if self._qblock_items:
            self.canvas.itemconfig(self._qblock_items[0], fill=md.QUESTION_YELLOW)
