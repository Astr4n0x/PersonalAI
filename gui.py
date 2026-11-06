import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import math
import queue
import sys
import os

# ─── Color Palette ──────────────────────────────────────────────────────────
BG_DARK       = "#0a0c14"
BG_CARD       = "#10131f"
BG_CARD2      = "#141828"
ACCENT_BLUE   = "#4f8ef7"
ACCENT_CYAN   = "#00d4ff"
ACCENT_PURPLE = "#a855f7"
ACCENT_GREEN  = "#22c55e"
TEXT_PRIMARY  = "#e8eaf6"
TEXT_SECONDARY= "#8892b0"
TEXT_DIM      = "#4a5568"
USER_BUBBLE   = "#1e2a45"
AI_BUBBLE     = "#151c30"
BORDER_COLOR  = "#1e2640"
PULSE_COLOR   = "#4f8ef7"
SPEAKING_COLOR= "#a855f7"
IDLE_COLOR    = "#1e2640"

# ─── State Constants ─────────────────────────────────────────────────────────
STATE_IDLE     = "idle"
STATE_LISTENING= "listening"
STATE_THINKING = "thinking"
STATE_SPEAKING = "speaking"


class AnimatedOrb(tk.Canvas):
    """Central orb with dynamic ring animations for idle/listening/thinking/speaking."""

    def __init__(self, parent, size=180, **kwargs):
        super().__init__(parent, width=size, height=size,
                         bg=BG_DARK, highlightthickness=0, **kwargs)
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.state = STATE_IDLE
        self._angle = 0
        self._pulse = 0.0
        self._pulse_dir = 1
        self._wave_offsets = [0, 0.4, 0.8, 1.2]
        self._bar_phases = [i * (math.pi / 6) for i in range(12)]
        self._running = True
        self._after_id = None
        self._draw()

    def set_state(self, state: str):
        self.state = state

    def _draw(self):
        if not self._running:
            return
        self.delete("all")
        cx, cy = self.cx, self.cy
        t = time.time()

        if self.state == STATE_IDLE:
            self._draw_idle(cx, cy, t)
        elif self.state == STATE_LISTENING:
            self._draw_listening(cx, cy, t)
        elif self.state == STATE_THINKING:
            self._draw_thinking(cx, cy, t)
        elif self.state == STATE_SPEAKING:
            self._draw_speaking(cx, cy, t)

        self._after_id = self.after(33, self._draw)  # ~30 fps

    def _draw_idle(self, cx, cy, t):
        breath = 0.5 + 0.5 * math.sin(t * 1.2)
        r = 55 + 6 * breath
        alpha_hex = self._alpha_color(ACCENT_BLUE, 0.25 + 0.1 * breath)
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=alpha_hex, width=2)
        for i in range(3):
            rr = 38 - i * 8
            op = 0.15 + i * 0.1
            c = self._alpha_color(ACCENT_BLUE, op)
            self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                             fill=c, outline="")
        self.create_oval(cx - 10, cy - 10, cx + 10, cy + 10,
                         fill=ACCENT_BLUE, outline="")
        self.create_text(cx, cy + 72, text="STANDBY",
                         fill=TEXT_DIM, font=("Courier", 8, "bold"))

    def _draw_listening(self, cx, cy, t):
        for i in range(4):
            phase = (t * 1.8 + i * 0.6) % (2 * math.pi)
            r = 32 + 28 * (phase / (2 * math.pi))
            alpha = 1.0 - (phase / (2 * math.pi))
            c = self._alpha_color(ACCENT_CYAN, alpha * 0.8)
            self.create_oval(cx - r, cy - r, cx + r, cy + r,
                             outline=c, width=max(1, int(3 * alpha)))
        angle = (t * 180) % 360
        self._draw_arc_ring(cx, cy, 42, ACCENT_CYAN, angle, 240, 3)
        pulse = 0.7 + 0.3 * math.sin(t * 4)
        rr = int(22 * pulse)
        self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                         fill=ACCENT_CYAN, outline="")
        self.create_text(cx, cy + 72, text="LISTENING",
                         fill=ACCENT_CYAN, font=("Courier", 8, "bold"))

    def _draw_thinking(self, cx, cy, t):
        num_dots = 8
        for i in range(num_dots):
            angle = (t * 120 + i * (360 / num_dots)) * (math.pi / 180)
            r = 48
            dx = cx + r * math.cos(angle)
            dy = cy + r * math.sin(angle)
            size = 4 + 2 * math.sin(t * 3 + i)
            fade = 0.4 + 0.6 * ((i / num_dots))
            c = self._alpha_color(ACCENT_PURPLE, fade)
            self.create_oval(dx - size, dy - size, dx + size, dy + size,
                             fill=c, outline="")
        self._draw_arc_ring(cx, cy, 28, ACCENT_PURPLE, (t * 200) % 360, 270, 4)
        self.create_oval(cx - 16, cy - 16, cx + 16, cy + 16,
                         fill=ACCENT_PURPLE, outline="")
        self.create_text(cx, cy + 72, text="THINKING",
                         fill=ACCENT_PURPLE, font=("Courier", 8, "bold"))

    def _draw_speaking(self, cx, cy, t):
        num_bars = 16
        for i in range(num_bars):
            angle = i * (2 * math.pi / num_bars)
            base_r = 38
            wave = math.sin(t * 6 + i * 0.6) * 0.5 + 0.5
            bar_len = 10 + 22 * wave
            x1 = cx + base_r * math.cos(angle)
            y1 = cy + base_r * math.sin(angle)
            x2 = cx + (base_r + bar_len) * math.cos(angle)
            y2 = cy + (base_r + bar_len) * math.sin(angle)
            alpha = 0.5 + 0.5 * wave
            c = self._alpha_color(ACCENT_PURPLE, alpha)
            self.create_line(x1, y1, x2, y2, fill=c, width=2, capstyle=tk.ROUND)
        self._draw_arc_ring(cx, cy, 68, ACCENT_PURPLE, (t * -90) % 360, 120, 2)
        self._draw_arc_ring(cx, cy, 72, ACCENT_CYAN, (t * 90 + 60) % 360, 80, 1)
        pulse = 0.8 + 0.2 * math.sin(t * 8)
        rr = int(20 * pulse)
        self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr,
                         fill=ACCENT_PURPLE, outline="")
        self.create_text(cx, cy + 80, text="SPEAKING",
                         fill=ACCENT_PURPLE, font=("Courier", 8, "bold"))

    def _draw_arc_ring(self, cx, cy, r, color, start, extent, width):
        self.create_arc(cx - r, cy - r, cx + r, cy + r,
                        start=start, extent=extent,
                        outline=color, style=tk.ARC, width=width)

    @staticmethod
    def _alpha_color(hex_color: str, alpha: float) -> str:
        alpha = max(0.0, min(1.0, alpha))
        bg = BG_DARK.lstrip("#")
        fg = hex_color.lstrip("#")
        br, bg_g, bb = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
        fr, fg_g, fb = int(fg[0:2], 16), int(fg[2:4], 16), int(fg[4:6], 16)
        r = int(br + (fr - br) * alpha)
        g = int(bg_g + (fg_g - bg_g) * alpha)
        b = int(bb + (fb - bb) * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"

    def stop(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)


class TaskBadge(tk.Frame):
    """Animated task status badge shown below the orb."""

    TASK_MESSAGES = {
        "idle":          ("", IDLE_COLOR, TEXT_DIM),
        "listening":     ("🎙  Listening to you...", ACCENT_CYAN, BG_DARK),
        "thinking":      ("🧠  Processing your request...", ACCENT_PURPLE, BG_DARK),
        "general":       ("💬  Generating response...", ACCENT_BLUE, BG_DARK),
        "realtime":      ("🌐  Searching the web...", ACCENT_CYAN, BG_DARK),
        "stocks":        ("📈  Fetching stock market data...", ACCENT_GREEN, BG_DARK),
        "crypto":        ("₿   Fetching crypto prices...", "#f59e0b", BG_DARK),
        "weather":       ("🌤  Getting weather data...", "#38bdf8", BG_DARK),
        "open":          ("🚀  Opening application...", ACCENT_BLUE, BG_DARK),
        "close":         ("❌  Closing application...", "#ef4444", BG_DARK),
        "play":          ("▶️  Searching YouTube...", "#ef4444", BG_DARK),
        "youtube search":("🔍  Searching YouTube...", "#ef4444", BG_DARK),
        "google search": ("🔍  Searching Google...", ACCENT_BLUE, BG_DARK),
        "content":       ("✍️  Writing content...", ACCENT_PURPLE, BG_DARK),
        "generate image":("🎨  Generating image...", "#f97316", BG_DARK),
        "reminder":      ("⏰  Setting reminder...", ACCENT_GREEN, BG_DARK),
        "system":        ("⚙️  Executing system task...", TEXT_SECONDARY, BG_DARK),
        "speaking":      ("🔊  Speaking...", ACCENT_PURPLE, BG_DARK),
        "done":          ("✅  Done", ACCENT_GREEN, BG_DARK),
    }

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self._current_key = "idle"
        self._label = tk.Label(self, text="", bg=BG_DARK,
                               fg=TEXT_DIM, font=("Segoe UI", 10, "bold"),
                               padx=14, pady=6)
        self._label.pack()

    def set_task(self, key: str, custom_text: str = None):
        self._current_key = key
        if key in self.TASK_MESSAGES:
            text, fg, bg = self.TASK_MESSAGES[key]
        else:
            text, fg, bg = f"  {key.capitalize()}...", ACCENT_BLUE, BG_DARK
        if custom_text:
            text = custom_text
        if key == "idle":
            self._label.config(text="", fg=TEXT_DIM, bg=BG_DARK)
            self.config(bg=BG_DARK)
            return
        self._label.config(text=text, fg=fg, bg=BG_DARK)
        self.config(bg=BG_DARK)

    def clear(self):
        self.set_task("idle")


class ChatMessage(tk.Frame):
    """A single chat bubble (user or AI)."""

    def __init__(self, parent, role: str, text: str, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        is_user = role == "user"
        outer = tk.Frame(self, bg=BG_DARK)
        outer.pack(fill=tk.X, padx=16, pady=4)
        avatar_text = "YOU" if is_user else " AI"
        avatar_fg   = ACCENT_BLUE if is_user else ACCENT_PURPLE
        avatar = tk.Label(outer, text=avatar_text, bg=BG_DARK, fg=avatar_fg,
                          font=("Segoe UI", 7, "bold"), width=4)
        bubble_bg = USER_BUBBLE if is_user else AI_BUBBLE
        bubble = tk.Frame(outer, bg=bubble_bg,
                          highlightbackground=BORDER_COLOR,
                          highlightthickness=1)
        msg_label = tk.Label(bubble, text=text, bg=bubble_bg, fg=TEXT_PRIMARY,
                             font=("Segoe UI", 11), wraplength=480,
                             justify=tk.LEFT, padx=14, pady=10)
        msg_label.pack()
        if is_user:
            avatar.pack(side=tk.RIGHT, anchor=tk.N, padx=(6, 0), pady=6)
            bubble.pack(side=tk.RIGHT, anchor=tk.E)
        else:
            avatar.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 6), pady=6)
            bubble.pack(side=tk.LEFT, anchor=tk.W)


class TypingIndicator(tk.Frame):
    """Three-dot animated typing indicator."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BG_DARK, **kwargs)
        self._running = False
        self._after_id = None
        outer = tk.Frame(self, bg=BG_DARK)
        outer.pack(fill=tk.X, padx=16, pady=4)
        avatar = tk.Label(outer, text=" AI", bg=BG_DARK, fg=ACCENT_PURPLE,
                          font=("Segoe UI", 7, "bold"), width=4)
        avatar.pack(side=tk.LEFT, anchor=tk.N, padx=(0, 6), pady=6)
        bubble = tk.Frame(outer, bg=AI_BUBBLE,
                          highlightbackground=BORDER_COLOR,
                          highlightthickness=1)
        bubble.pack(side=tk.LEFT, anchor=tk.W)
        dot_frame = tk.Frame(bubble, bg=AI_BUBBLE, padx=16, pady=14)
        dot_frame.pack()
        self._canvas = tk.Canvas(dot_frame, width=48, height=16,
                                 bg=AI_BUBBLE, highlightthickness=0)
        self._canvas.pack()
        self.start()

    def start(self):
        self._running = True
        self._animate()

    def stop(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)

    def _animate(self):
        if not self._running:
            return
        self._canvas.delete("all")
        t = time.time() * 3
        for i in range(3):
            wave = math.sin(t + i * 1.1)
            y = 8 + 5 * wave
            alpha = 0.4 + 0.6 * (0.5 + 0.5 * wave)
            color = self._blend(ACCENT_PURPLE, alpha)
            x = 8 + i * 16
            self._canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline="")
        self._after_id = self.after(40, self._animate)

    @staticmethod
    def _blend(hex_color, alpha):
        bg = AI_BUBBLE.lstrip("#")
        fg = hex_color.lstrip("#")
        br, bg_g, bb = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
        fr, fg_g, fb = int(fg[0:2], 16), int(fg[2:4], 16), int(fg[4:6], 16)
        r = int(br + (fr - br) * alpha)
        g = int(bg_g + (fg_g - bg_g) * alpha)
        b = int(bb + (fb - bb) * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"


class JarvisGUI(tk.Tk):
    """Main Jarvis AI Chatbot GUI Window."""

    def __init__(self):
        super().__init__()
        self.title("Jarvis — AI Assistant")
        self.geometry("860x720")
        self.minsize(720, 580)
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.ui_queue: queue.Queue = queue.Queue()
        self._state = STATE_IDLE
        self._typing_widget = None
        self._build_ui()
        self._poll_queue()

    # ─── UI Construction ─────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=BG_CARD, height=56)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        logo_frame = tk.Frame(header, bg=BG_CARD)
        logo_frame.pack(side=tk.LEFT, padx=20, pady=8)
        logo_canvas = tk.Canvas(logo_frame, width=32, height=32,
                                bg=BG_CARD, highlightthickness=0)
        logo_canvas.pack(side=tk.LEFT)
        logo_canvas.create_oval(4, 4, 28, 28, fill=ACCENT_BLUE, outline="")
        logo_canvas.create_text(16, 16, text="J", fill="white",
                                font=("Segoe UI", 14, "bold"))
        tk.Label(logo_frame, text="JARVIS", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT, padx=8)
        tk.Label(logo_frame, text="AI Assistant", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._status_dot = tk.Canvas(header, width=12, height=12,
                                     bg=BG_CARD, highlightthickness=0)
        self._status_dot.pack(side=tk.RIGHT, padx=6, pady=22)
        self._status_label = tk.Label(header, text="Standby", bg=BG_CARD,
                                      fg=TEXT_DIM, font=("Segoe UI", 9))
        self._status_label.pack(side=tk.RIGHT, padx=(0, 4))
        self._update_status_dot()

        # Body
        body = tk.Frame(self, bg=BG_DARK)
        body.pack(fill=tk.BOTH, expand=True)

        # Left Panel
        left_panel = tk.Frame(body, bg=BG_CARD2, width=220)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        tk.Label(left_panel, text="STATUS", bg=BG_CARD2, fg=TEXT_DIM,
                 font=("Segoe UI", 8, "bold")).pack(pady=(24, 8))
        self.orb = AnimatedOrb(left_panel, size=180)
        self.orb.configure(bg=BG_CARD2)
        self.orb.pack(pady=10)
        self.task_badge = TaskBadge(left_panel)
        self.task_badge.pack(pady=8, padx=10, fill=tk.X)
        sep = tk.Frame(left_panel, bg=BORDER_COLOR, height=1)
        sep.pack(fill=tk.X, padx=16, pady=16)
        tk.Label(left_panel, text="CAPABILITIES", bg=BG_CARD2, fg=TEXT_DIM,
                 font=("Segoe UI", 8, "bold")).pack(pady=(0, 8))
        caps = [
            ("💬", "General Chat"),
            ("🌐", "Real-time Search"),
            ("📈", "Stock Market"),
            ("₿ ", "Crypto Prices"),
            ("🌤", "Weather"),
            ("🚀", "App Control"),
            ("▶️", "YouTube"),
            ("🎨", "Image Gen"),
        ]
        for icon, label in caps:
            row = tk.Frame(left_panel, bg=BG_CARD2)
            row.pack(fill=tk.X, padx=18, pady=2)
            tk.Label(row, text=icon, bg=BG_CARD2, font=("Segoe UI", 10)).pack(side=tk.LEFT)
            tk.Label(row, text=label, bg=BG_CARD2, fg=TEXT_SECONDARY,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=6)

        # Right Panel
        right_panel = tk.Frame(body, bg=BG_DARK)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_header = tk.Frame(right_panel, bg=BG_CARD, height=40)
        chat_header.pack(fill=tk.X)
        chat_header.pack_propagate(False)
        tk.Label(chat_header, text="Conversation", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=16, pady=10)

        # Chat scroll area
        chat_container = tk.Frame(right_panel, bg=BG_DARK)
        chat_container.pack(fill=tk.BOTH, expand=True)
        self._chat_canvas = tk.Canvas(chat_container, bg=BG_DARK,
                                      highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(chat_container, orient=tk.VERTICAL,
                                 command=self._chat_canvas.yview,
                                 bg=BG_DARK, troughcolor=BG_CARD)
        self._chat_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._messages_frame = tk.Frame(self._chat_canvas, bg=BG_DARK)
        self._chat_window = self._chat_canvas.create_window(
            (0, 0), window=self._messages_frame, anchor=tk.NW)
        self._messages_frame.bind("<Configure>", self._on_frame_configure)
        self._chat_canvas.bind("<Configure>", self._on_canvas_configure)
        self._chat_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._add_system_message(
            "Hello! I'm Jarvis, your AI assistant. "
            "Type a message or press the mic button to speak."
        )

        # Input bar
        input_bar = tk.Frame(right_panel, bg=BG_CARD, height=64)
        input_bar.pack(fill=tk.X, side=tk.BOTTOM)
        input_bar.pack_propagate(False)
        input_inner = tk.Frame(input_bar, bg=BG_CARD)
        input_inner.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)
        entry_frame = tk.Frame(input_inner, bg=BG_CARD2,
                               highlightbackground=BORDER_COLOR,
                               highlightthickness=1)
        entry_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self._entry = tk.Entry(entry_frame, bg=BG_CARD2, fg=TEXT_PRIMARY,
                               insertbackground=ACCENT_BLUE,
                               font=("Segoe UI", 11), bd=0, relief=tk.FLAT)
        self._entry.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self._entry.bind("<Return>", self._on_send)
        placeholder = "Type a message or use voice..."
        self._entry.insert(0, placeholder)
        self._entry.config(fg=TEXT_DIM)
        self._entry.bind("<FocusIn>",
            lambda e: (entry_frame.config(highlightbackground=ACCENT_BLUE),
                       self._clear_placeholder(placeholder)))
        self._entry.bind("<FocusOut>",
            lambda e: (entry_frame.config(highlightbackground=BORDER_COLOR),
                       self._restore_placeholder(placeholder)))
        send_btn = tk.Button(input_inner, text="Send  ↑",
                             bg=ACCENT_BLUE, fg="white",
                             font=("Segoe UI", 10, "bold"),
                             bd=0, padx=18, pady=6, relief=tk.FLAT,
                             cursor="hand2", activebackground="#3a7ce8",
                             activeforeground="white", command=self._on_send)
        send_btn.pack(side=tk.LEFT)
        self._mic_btn = tk.Button(input_inner, text="🎙",
                                  bg=BG_CARD, fg=ACCENT_CYAN,
                                  font=("Segoe UI", 14), bd=0, padx=10,
                                  pady=4, relief=tk.FLAT, cursor="hand2",
                                  activebackground=BG_CARD2,
                                  command=self._on_mic)
        self._mic_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Callback reference (set by main.py)
        self.on_user_input = None   # Callable[[str], None]

    # ─── Placeholder helpers ─────────────────────────────────────────────────

    def _clear_placeholder(self, placeholder):
        if self._entry.get() == placeholder:
            self._entry.delete(0, tk.END)
            self._entry.config(fg=TEXT_PRIMARY)

    def _restore_placeholder(self, placeholder):
        if not self._entry.get():
            self._entry.insert(0, placeholder)
            self._entry.config(fg=TEXT_DIM)

    # ─── Event Handlers ───────────────────────────────────────────────────────

    def _on_send(self, event=None):
        placeholder = "Type a message or use voice..."
        text = self._entry.get().strip()
        if not text or text == placeholder:
            return
        self._entry.delete(0, tk.END)
        self._entry.insert(0, placeholder)
        self._entry.config(fg=TEXT_DIM)
        self.add_user_message(text)
        if self.on_user_input:
            threading.Thread(target=self.on_user_input, args=(text,), daemon=True).start()

    def _on_mic(self):
        if self.on_user_input:
            def _listen_thread():
                self.set_state(STATE_LISTENING)
                self.set_task("listening")
                try:
                    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "services"))
                    from speach_rec import listen
                    text = listen()
                    if text:
                        self.add_user_message(text)
                        self.on_user_input(text)
                except Exception as e:
                    self.set_state(STATE_IDLE)
                    self.set_task("idle")
            threading.Thread(target=_listen_thread, daemon=True).start()

    def _on_frame_configure(self, event=None):
        self._chat_canvas.configure(scrollregion=self._chat_canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        self._chat_canvas.itemconfig(self._chat_window, width=event.width)

    def _on_mousewheel(self, event):
        self._chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ─── Public API (thread-safe via queue) ───────────────────────────────────

    def add_user_message(self, text: str):
        self.ui_queue.put(("user_msg", text))

    def add_ai_message(self, text: str):
        self.ui_queue.put(("ai_msg", text))

    def set_state(self, state: str):
        self.ui_queue.put(("state", state))

    def set_task(self, task: str, custom_text: str = None):
        self.ui_queue.put(("task", task, custom_text))

    def show_typing(self):
        self.ui_queue.put(("typing_show",))

    def hide_typing(self):
        self.ui_queue.put(("typing_hide",))

    # ─── Queue Processor ─────────────────────────────────────────────────────

    def _poll_queue(self):
        try:
            while True:
                item = self.ui_queue.get_nowait()
                cmd = item[0]
                if cmd == "user_msg":
                    self._render_user_message(item[1])
                elif cmd == "ai_msg":
                    self._render_ai_message(item[1])
                elif cmd == "state":
                    self._apply_state(item[1])
                elif cmd == "task":
                    custom = item[2] if len(item) > 2 else None
                    self.task_badge.set_task(item[1], custom)
                elif cmd == "typing_show":
                    self._show_typing()
                elif cmd == "typing_hide":
                    self._hide_typing()
        except queue.Empty:
            pass
        self.after(50, self._poll_queue)

    # ─── Rendering ───────────────────────────────────────────────────────────

    def _render_user_message(self, text: str):
        msg = ChatMessage(self._messages_frame, role="user", text=text)
        msg.pack(fill=tk.X, pady=2)
        self._scroll_to_bottom()

    def _render_ai_message(self, text: str):
        self._hide_typing()
        msg = ChatMessage(self._messages_frame, role="ai", text=text)
        msg.pack(fill=tk.X, pady=2)
        self._scroll_to_bottom()

    def _add_system_message(self, text: str):
        msg = ChatMessage(self._messages_frame, role="ai", text=text)
        msg.pack(fill=tk.X, pady=2)

    def _show_typing(self):
        if self._typing_widget is None:
            self._typing_widget = TypingIndicator(self._messages_frame)
            self._typing_widget.pack(fill=tk.X, pady=2)
            self._scroll_to_bottom()

    def _hide_typing(self):
        if self._typing_widget is not None:
            self._typing_widget.stop()
            self._typing_widget.destroy()
            self._typing_widget = None

    def _scroll_to_bottom(self):
        self.after(100, lambda: self._chat_canvas.yview_moveto(1.0))

    def _apply_state(self, state: str):
        self._state = state
        self.orb.set_state(state)
        colors = {
            STATE_IDLE:      (IDLE_COLOR,    "Standby",   TEXT_DIM),
            STATE_LISTENING: (ACCENT_CYAN,   "Listening", ACCENT_CYAN),
            STATE_THINKING:  (ACCENT_PURPLE, "Thinking",  ACCENT_PURPLE),
            STATE_SPEAKING:  (ACCENT_PURPLE, "Speaking",  ACCENT_PURPLE),
        }
        dot_color, label_text, label_color = colors.get(
            state, (IDLE_COLOR, "Standby", TEXT_DIM))
        self._status_dot.delete("all")
        self._status_dot.create_oval(1, 1, 11, 11, fill=dot_color, outline="")
        self._status_label.config(text=label_text, fg=label_color)

    def _update_status_dot(self):
        self._status_dot.delete("all")
        self._status_dot.create_oval(1, 1, 11, 11, fill=IDLE_COLOR, outline="")

    def on_closing(self):
        self.orb.stop()
        self.destroy()
