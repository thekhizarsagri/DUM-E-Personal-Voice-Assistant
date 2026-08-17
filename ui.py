import tkinter as tk
import math
import time
import threading

# Futuristic DUM-E theme
BG_COLOR = "#07080d"
PANEL_COLOR = "#0c0f18"
ACCENT = "#00ffe1"
ACCENT2 = "#7b2ff7"
TEXT_COLOR = "#e8f6ff"
DIM_COLOR = "#5a6b7d"


def hex_mix(c1, c2, t):
    """Blend two hex colors; t in [0,1]."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


class FuturisticGUI:
    def __init__(self, root):
        self.root = root
        self.status = "Listening"
        self.state_color = ACCENT
        self.phase = 0.0
        self._closed = False
        self.on_command = None

        root.geometry("920x680")
        root.overrideredirect(True)
        root.resizable(False, False)
        root.configure(bg=BG_COLOR, highlightthickness=0, bd=0)

        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._build_title_bar()
        self._build_orb()
        self._build_chat()
        self._build_command_bar()
        self._build_status_bar()

        # start animations
        self._tick_border()
        self._tick_orb()
        self._tick_clock()

    # ---------------- Title bar ----------------
    def _build_title_bar(self):
        self.title = tk.Label(
            self.canvas,
            text="◆  DUM-E  //  Deep Universal Mind Electric",
            font=("Consolas", 11, "bold"),
            fg=ACCENT,
            bg=BG_COLOR,
        )
        self.title.place(x=16, y=12)

        self.clock_label = tk.Label(
            self.canvas, text="", font=("Consolas", 11), fg=DIM_COLOR, bg=BG_COLOR
        )
        self.clock_label.place(x=800, y=14, anchor="ne")

        self.close_btn = tk.Button(
            self.canvas, text="✕", font=("Consolas", 12, "bold"),
            fg=DIM_COLOR, bg=BG_COLOR, bd=0, activebackground="#ff2d55",
            activeforeground="#fff", cursor="hand2", command=self._close,
        )
        self.close_btn.place(x=884, y=8)

        self.canvas.tag_bind(self.canvas.create_text(0, 0, text=""), "<Button-1>", self._start_move)
        self.title.bind("<Button-1>", self._start_move)
        self.title.bind("<B1-Motion>", self._do_move)
        self.clock_label.bind("<Button-1>", self._start_move)
        self.clock_label.bind("<B1-Motion>", self._do_move)
        self.canvas.bind("<Button-1>", self._start_move)
        self.canvas.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_move(self, event):
        self.root.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def _close(self):
        self._closed = True
        self.root.destroy()

    # ---------------- Glowing border ----------------
    def _tick_border(self):
        if self._closed:
            return
        t = (math.sin(self.phase * 1.6) + 1) / 2
        color = hex_mix(ACCENT, ACCENT2, t)
        self.canvas.delete("border")
        self.canvas.create_rectangle(3, 3, 917, 677, outline=color, width=2, tags="border")
        self.canvas.tag_lower("border")
        self.root.after(40, self._tick_border)

    # ---------------- Animated orb ----------------
    def _build_orb(self):
        self.orb_x, self.orb_y = 460, 200
        self.orb_r = 58

    def _tick_orb(self):
        if self._closed:
            return
        self.phase += 0.08
        pulse = math.sin(self.phase) * 6
        r = self.orb_r + pulse

        # outer glow rings
        self.canvas.delete("orb")
        for i, ring_r in enumerate([r * 1.9, r * 1.55, r * 1.25]):
            alpha = 1.0 - (i / 3.0)
            ring_color = hex_mix(self.state_color, BG_COLOR, 0.55 * alpha + 0.15)
            self.canvas.create_oval(
                self.orb_x - ring_r, self.orb_y - ring_r,
                self.orb_x + ring_r, self.orb_y + ring_r,
                outline=ring_color, width=2, tags="orb",
            )

        # core orb with gradient fill
        core = hex_mix(BG_COLOR, self.state_color, 0.35)
        self.canvas.create_oval(
            self.orb_x - r, self.orb_y - r, self.orb_x + r, self.orb_y + r,
            fill=core, outline=self.state_color, width=3, tags="orb",
        )
        # center highlight
        self.canvas.create_oval(
            self.orb_x - r * 0.45, self.orb_y - r * 0.45,
            self.orb_x + r * 0.45, self.orb_y + r * 0.45,
            fill=hex_mix(self.state_color, "#ffffff", 0.85), outline="", tags="orb",
        )

        self.root.after(45, self._tick_orb)

    def set_state(self, status: str):
        """status in: Listening, Thinking, Speaking, Busy"""
        self.status = status
        palette = {
            "Listening": ACCENT,
            "Thinking": "#ffb300",
            "Speaking": "#ff2d55",
            "Busy": ACCENT2,
        }
        self.state_color = palette.get(status, ACCENT)
        self.status_label.config(text=f"{status}...", fg=self.state_color)

    # ---------------- Chat area ----------------
    def _build_chat(self):
        self.chat = tk.Text(
            self.canvas,
            wrap=tk.WORD, font=("Consolas", 12), bg=PANEL_COLOR, fg=TEXT_COLOR,
            bd=0, highlightthickness=0, insertbackground=TEXT_COLOR,
        )
        self.chat.place(x=24, y=330, width=872, height=250)
        self.chat.tag_configure("user", foreground=ACCENT, font=("Consolas", 12, "bold"))
        self.chat.tag_configure("assistant", foreground=TEXT_COLOR)
        self.chat.config(state=tk.DISABLED)
        for ev in ["<Button-1>", "<B1-Motion>", "<Double-Button-1>", "<Triple-Button-1>", "<Key>"]:
            self.chat.bind(ev, lambda e: "break")

    def add_message(self, message: str, sender="assistant"):
        tag = "user" if sender == "user" else "assistant"
        prefix = "YOU" if sender == "user" else "DUM-E"
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, f" {prefix} ▸  ", tag)
        self.chat.insert(tk.END, f"{message}\n\n", "assistant")
        self.chat.see(tk.END)
        self.chat.config(state=tk.DISABLED)

    # ---------------- Command input ----------------
    def _build_command_bar(self):
        self.input_var = tk.StringVar()
        self.command_entry = tk.Entry(
            self.canvas, textvariable=self.input_var, font=("Consolas", 12),
            bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=ACCENT,
            bd=0, highlightthickness=0,
        )
        self.command_entry.place(x=24, y=598, width=720, height=30)
        self.command_entry.bind("<Return>", self._send_command)

        self.send_btn = tk.Button(
            self.canvas, text="SEND", font=("Consolas", 10, "bold"),
            fg=BG_COLOR, bg=ACCENT, bd=0, cursor="hand2",
            activebackground=ACCENT2, activeforeground="#fff",
            command=self._send_command,
        )
        self.send_btn.place(x=756, y=598, width=140, height=30)

    def _send_command(self, _event=None):
        text = self.input_var.get().strip()
        if not text:
            return
        self.add_message(text, sender="user")
        self.input_var.set("")
        if self.on_command:
            threading.Thread(target=self.on_command, args=(text,), daemon=True).start()

    # ---------------- Status bar ----------------
    def _build_status_bar(self):
        self.status_label = tk.Label(
            self.canvas, text="Listening...", font=("Consolas", 12, "bold"),
            fg=ACCENT, bg=BG_COLOR,
        )
        self.status_label.place(x=460, y=650, anchor="center")

    def _tick_clock(self):
        if self._closed:
            return
        self.clock_label.config(text=time.strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)


if __name__ == "__main__":
    root = tk.Tk()
    gui = FuturisticGUI(root)
    root.mainloop()