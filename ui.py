import tkinter as tk
import math
import time
import threading
import random

# DUM-E glass theme — transparent dark blue glass, cyan & blue only
BG_TOP = "#0b1836"
BG_BOTTOM = "#01040b"
PANEL_COLOR = "#0d1f40"
PANEL_EDGE = "#2a4d86"
CYAN = "#00eaff"
CYAN_SOFT = "#5fd4ff"
BLUE = "#2f7bff"
BLUE_SOFT = "#4d8dff"
RED = "#1a6bff"
TEXT_COLOR = "#d5f1ff"
DIM_COLOR = "#5d83b4"


def hex_mix(c1, c2, t):
    """Blend two hex colors; t in [0,1]."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


class FuturisticGUI:
    def __init__(self, root):
        self.root = root
        self.status = "Listening"
        self._color_cur = CYAN
        self._color_tgt = CYAN
        self.rot = 0.0
        self._closed = False
        self.on_command = None

        root.geometry("920x720")
        root.overrideredirect(True)
        root.resizable(False, False)
        try:
            # real translucency: desktop bleeds faintly through the dark glass
            root.attributes("-alpha", 0.94)
        except tk.TclError:
            pass
        root.configure(bg=BG_BOTTOM, highlightthickness=0, bd=0)

        self.canvas = tk.Canvas(root, bg=BG_BOTTOM, highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self._draw_background()
        self._build_hud()
        self._build_reactor()
        self._build_particles()
        self._build_chat()
        self._build_command_bar()
        self._build_status_bar()
        self._bind_drag()

        self.command_entry.focus_set()
        self._tick_border()
        self._tick_reactor()
        self._tick_particles()
        self._tick_status_dot()
        self._tick_clock()

    # ---------------- Glass background ----------------
    def _draw_background(self):
        c = self.canvas
        w, h = 920, 720
        img = tk.PhotoImage(width=w, height=h)
        for y in range(h):
            t = y / (h - 1)
            img.put(hex_mix(BG_TOP, BG_BOTTOM, t), to=(0, y, w, y + 1))
        self._bgimg = img
        c.create_image(0, 0, anchor="nw", image=img, tags="bg")

        # faint hologrid for depth
        grid = hex_mix(BLUE, BG_BOTTOM, 0.82)
        for gx in range(20, w, 60):
            c.create_line(gx, 0, gx, h, fill=grid, width=1, tags="bg")
        for gy in range(20, h, 60):
            c.create_line(0, gy, w, gy, fill=grid, width=1, tags="bg")
        # edge vignette
        c.create_rectangle(8, 8, 912, 712, outline="#0a1a3a", width=6, tags="bg")
        c.tag_lower("bg")

    # ---------------- Glow text + corner brackets ----------------
    def _glow_text(self, x, y, text, font, color, anchor="center", tags=""):
        c = self.canvas
        glow = hex_mix(color, BG_BOTTOM, 0.45)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1)):
            c.create_text(x + dx, y + dy, text=text, font=font,
                          fill=glow, anchor=anchor, tags=tags)
        c.create_text(x, y, text=text, font=font, fill=color, anchor=anchor, tags=tags)

    def _brackets(self, x, y, w, h, s=10, color=DIM_COLOR, tag="deco"):
        c = self.canvas
        for x0, y0, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1),
                               (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
            c.create_line(x0, y0, x0 + dx * s, y0, fill=color, width=1, tags=tag)
            c.create_line(x0, y0, x0, y0 + dy * s, fill=color, width=1, tags=tag)

    # ---------------- HUD header ----------------
    def _build_hud(self):
        self._glow_text(26, 20, "◆ DUM-E", ("Consolas", 17, "bold"), CYAN,
                        anchor="w", tags="title")
        self.canvas.create_text(28, 44, text="HOLO INTERFACE // DEEP UNIVERSAL MIND ELECTRIC",
                                font=("Consolas", 8), fill=DIM_COLOR, anchor="w", tags="title")

        self.close_btn = tk.Button(
            self.canvas, text="✕", font=("Consolas", 11, "bold"),
            fg=DIM_COLOR, bg=PANEL_COLOR, bd=0, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=PANEL_EDGE,
            activebackground=BLUE, activeforeground="#b0f0ff",
            cursor="hand2", command=self._close,
        )
        self.close_btn.place(x=886, y=8, width=26, height=26)

        # static clock frame — drawn fresh each tick so it tracks theme color
        self._brackets(598, 24, 286, 76, 10, hex_mix(CYAN, BG_BOTTOM, 0.5), "clockframe")

    # ---------------- Dragging ----------------
    def _bind_drag(self):
        for w in (self.canvas,):
            w.bind("<Button-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

    def _start_move(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_move(self, event):
        self.root.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def _close(self):
        self._closed = True
        self.root.destroy()

    # ---------------- Animated glass border ----------------
    def _tick_border(self):
        if self._closed:
            return
        t = (math.sin(self.rot * 1.2) + 1) / 2
        color = hex_mix(BLUE, CYAN, t)
        c = self.canvas
        c.delete("border")

        c.create_rectangle(2, 2, 918, 718, outline=color, width=1, tags="border")
        c.create_rectangle(6, 6, 914, 714, outline=hex_mix(color, BG_BOTTOM, 0.6), width=3, tags="border")

        # HUD corner brackets
        s = 24
        c.create_line(4, 4 + s, 4, 4, 4 + s, 4, fill=color, width=2, tags="border")
        c.create_line(916 - s, 4, 916, 4, 916, 4 + s, fill=color, width=2, tags="border")
        c.create_line(4, 716 - s, 4, 716, 4 + s, 716, fill=color, width=2, tags="border")
        c.create_line(916 - s, 716, 916, 716, 916, 716 - s, fill=color, width=2, tags="border")

        # header separator (left of clock module)
        c.create_line(24, 62, 590, 62, fill=hex_mix(color, BG_BOTTOM, 0.5), width=1, tags="border")
        # clock module border (animated to theme)
        c.create_rectangle(600, 26, 886, 100, outline=hex_mix(color, BG_BOTTOM, 0.25), width=1, tags="border")
        self._brackets(600, 26, 286, 74, 10, color, "border")
        # glass-top highlight on panels
        c.create_line(24, 336, 896, 336, fill=hex_mix(color, "#b0f0ff", 0.45), width=1, tags="border")
        c.create_line(24, 634, 734, 634, fill=hex_mix(color, "#b0f0ff", 0.45), width=1, tags="border")

        c.tag_lower("border")
        self.root.after(30, self._tick_border)

    # ---------------- 3D arc reactor ----------------
    def _build_reactor(self):
        self.rx, self.ry = 460, 208
        self.rr = 62

    def _tick_reactor(self):
        if self._closed:
            return
        self.rot += 0.045
        self._color_cur = hex_mix(self._color_cur, self._color_tgt, 0.10)
        col = self._color_cur
        c = self.canvas
        c.delete("reactor")

        pulse = math.sin(self.rot * 0.9) * 3.5
        r = self.rr + pulse
        cx, cy = self.rx, self.ry

        rings = [
            (r * 1.75, r * 0.62, 0.9, 22, 1.0),
            (r * 1.42, r * 0.86, -0.6, 16, 2.0),
            (r * 1.12, r * 1.0, 0.4, 12, 3.0),
        ]
        for rx, ry, spd, dashes, w in rings:
            bbox = (cx - rx, cy - ry, cx + rx, cy + ry)
            a = self.rot * spd * 40
            c.create_arc(bbox, start=a, extent=180, style=tk.ARC,
                         outline=hex_mix(col, BG_BOTTOM, 0.72), width=int(w) + 1, tags="reactor")
            c.create_arc(bbox, start=a + 180, extent=180, style=tk.ARC,
                         outline=hex_mix(col, BG_BOTTOM, 0.15), width=int(w) + 2, tags="reactor")
            step = 360.0 / dashes
            for i in range(dashes):
                da = self.rot * spd * 200 + i * step
                c.create_arc(bbox, start=da, extent=step * 0.55, style=tk.ARC,
                             outline=col, width=int(w) + 2, tags="reactor")

        bbox = (cx - r, cy - r, cx + r, cy + r)
        c.create_oval(bbox, fill=hex_mix(BG_TOP, col, 0.42), outline=col, width=2, tags="reactor")

        c.create_arc(cx - r * 1.05, cy - r * 1.0, cx + r * 0.75, cy + r * 0.9,
                     start=205, extent=115, style=tk.PIESLICE,
                     fill=hex_mix(col, "#b0f0ff", 0.62), outline="", tags="reactor")
        c.create_arc(cx - r * 0.75, cy - r * 0.9, cx + r * 1.05, cy + r * 1.0,
                     start=20, extent=115, style=tk.PIESLICE,
                     fill=hex_mix(BG_BOTTOM, col, 0.9), outline="", tags="reactor")

        c.create_oval(cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55,
                      fill=hex_mix(BG_TOP, col, 0.68), outline="", tags="reactor")
        c.create_oval(cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2,
                      fill=hex_mix(col, "#b0f0ff", 0.85), outline="", tags="reactor")
        c.create_oval(cx - r * 0.5, cy - r * 0.52, cx - r * 0.2, cy - r * 0.22,
                      fill="#b0f0ff", outline="", tags="reactor")

        for i in range(3):
            ang = math.radians(self.rot * 55 + i * 120)
            sx = cx + math.cos(ang) * r * 1.75
            sy = cy + math.sin(ang) * r * 0.62
            c.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill=col, outline="", tags="reactor")

        self.root.after(30, self._tick_reactor)

    def set_state(self, status: str):
        """status in: Listening, Thinking, Speaking, Busy"""
        self.status = status
        palette = {
            "Listening": CYAN,
            "Thinking": BLUE,
            "Speaking": CYAN_SOFT,
            "Busy": BLUE,
        }
        self._color_tgt = palette.get(status, CYAN)
        self.status_label.config(text=f"{status.upper()}...", fg=self._color_tgt)

    # ---------------- Glass droplets ----------------
    def _build_particles(self):
        self.particles = [
            [random.uniform(70, 850), random.uniform(100, 300),
             random.uniform(0.4, 1.2), random.uniform(1.2, 2.6), random.uniform(0, 6)]
            for _ in range(16)
        ]

    def _tick_particles(self):
        if self._closed:
            return
        c = self.canvas
        c.delete("particles")
        for i, p in enumerate(self.particles):
            p[1] -= p[2]
            p[4] += 0.08
            if p[1] < 90:
                p[0] = random.uniform(70, 850)
                p[1] = random.uniform(290, 330)
                p[2] = random.uniform(0.4, 1.2)
            drift = math.sin(p[4]) * 8
            col = hex_mix(CYAN, BG_BOTTOM, (p[1] - 90) / 240)
            c.create_oval(p[0] + drift - p[3], p[1] - p[3], p[0] + drift + p[3], p[1] + p[3],
                          fill=col, outline="", tags="particles")
        self.root.after(30, self._tick_particles)

    # ---------------- System console ----------------
    def _build_chat(self):
        panel = tk.Frame(self.canvas, bg=PANEL_COLOR,
                         highlightthickness=1, highlightbackground=PANEL_EDGE,
                         bd=0, relief=tk.FLAT)
        panel.place(x=24, y=336, width=872, height=284)
        self._brackets(24, 336, 872, 284, 12, hex_mix(CYAN, BG_BOTTOM, 0.4), "deco")

        tk.Label(panel, text="// SYSTEM CONSOLE", font=("Consolas", 8, "bold"),
                 fg=DIM_COLOR, bg=PANEL_COLOR).pack(anchor="w", padx=12, pady=(7, 0))

        self.chat = tk.Text(
            panel, wrap=tk.WORD, font=("Consolas", 11), bg=PANEL_COLOR, fg=TEXT_COLOR,
            bd=0, highlightthickness=0, insertbackground=CYAN,
        )
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 10))
        self.chat.tag_configure("user", foreground=CYAN, font=("Consolas", 11, "bold"))
        self.chat.tag_configure("assistant", foreground=TEXT_COLOR)
        self.chat.config(state=tk.DISABLED)
        for ev in ["<Button-1>", "<B1-Motion>", "<Double-Button-1>", "<Triple-Button-1>", "<Key>"]:
            self.chat.bind(ev, lambda e: "break")

    def add_message(self, message: str, sender="assistant"):
        tag = "user" if sender == "user" else "assistant"
        prefix = "YOU ▸" if sender == "user" else "DUM-E ▸"
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, f" {prefix}  ", tag)
        self.chat.insert(tk.END, f"{message}\n\n", "assistant")
        self.chat.see(tk.END)
        self.chat.config(state=tk.DISABLED)

    # ---------------- Command input ----------------
    def _build_command_bar(self):
        frame = tk.Frame(self.canvas, bg=PANEL_COLOR,
                         highlightthickness=1, highlightbackground=PANEL_EDGE,
                         bd=0, relief=tk.FLAT)
        frame.place(x=24, y=634, width=710, height=40)

        self.input_var = tk.StringVar()
        self.command_entry = tk.Entry(
            frame, textvariable=self.input_var, font=("Consolas", 12),
            bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=CYAN,
            bd=0, highlightthickness=0,
        )
        self.command_entry.place(x=10, y=0, width=692, height=40)
        self.command_entry.bind("<Return>", self._send_command)

        self.send_btn = tk.Button(
            self.canvas, text="EXECUTE", font=("Consolas", 10, "bold"),
            fg=CYAN, bg=PANEL_COLOR, bd=0, relief=tk.FLAT,
            highlightthickness=1, highlightbackground=hex_mix(CYAN, BG_BOTTOM, 0.45),
            activebackground=BLUE, activeforeground="#b0f0ff",
            cursor="hand2", command=self._send_command,
        )
        self.send_btn.place(x=746, y=634, width=150, height=40)

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
            self.canvas, text="LISTENING...", font=("Consolas", 11, "bold"),
            fg=CYAN, bg=BG_BOTTOM,
        )
        self.status_label.place(x=446, y=696, anchor="w")

    def _tick_status_dot(self):
        if self._closed:
            return
        pulse = (math.sin(self.rot * 1.7) + 1) / 2
        d = 3.5 + pulse * 2
        col = hex_mix(self._color_cur, "#b0f0ff", pulse * 0.55)
        self.canvas.delete("dot")
        self.canvas.create_oval(430 - d, 696 - d, 430 + d, 696 + d,
                                fill=col, outline="", tags="dot")
        self.root.after(40, self._tick_status_dot)

    # ---------------- Futuristic digital clock (top-right) ----------------
    def _tick_clock(self):
        if self._closed:
            return
        c = self.canvas
        c.delete("clock")
        now = time.localtime()
        t_ms = time.time()
        sep = ":" if int(t_ms * 2) % 2 == 0 else " "

        hh = f"{now.tm_hour:02d}"
        mm = f"{now.tm_min:02d}"
        ss = f"{now.tm_sec:02d}"
        cx, cy = 743, 62

        self.canvas.create_text(cx - 30, 25, text="LOCAL TIME // SYS-CLK",
                                font=("Consolas", 7, "bold"), fill=DIM_COLOR,
                                anchor="w", tags="clock")
        self._glow_text(cx - 14, cy, f"{hh}{sep}{mm}",
                        ("Consolas", 27, "bold"), CYAN, anchor="center", tags="clock")
        self.canvas.create_text(cx + 98, cy, text=ss,
                                font=("Consolas", 12, "bold"),
                                fill=CYAN_SOFT, anchor="center", tags="clock")
        self.canvas.create_text(cx, 88, text=time.strftime("%a %b %d %Y", now).upper(),
                                font=("Consolas", 8, "bold"), fill=DIM_COLOR,
                                anchor="center", tags="clock")

        # seconds progress bar (fills the current minute)
        frac = (t_ms % 60) / 60.0
        c.create_rectangle(604, 92, 882, 96, fill=hex_mix(PANEL_EDGE, BG_BOTTOM, 0.6),
                           outline="", tags="clock")
        c.create_rectangle(604, 92, 604 + (882 - 604) * frac, 96,
                           fill=hex_mix(CYAN, BLUE, frac), outline="", tags="clock")
        c.create_rectangle(604, 92, 882, 96, outline=hex_mix(CYAN, BG_BOTTOM, 0.6),
                           width=1, tags="clock")

        self.root.after(100, self._tick_clock)


if __name__ == "__main__":
    root = tk.Tk()
    gui = FuturisticGUI(root)
    gui.add_message("Holo interface online. Awaiting commands, Sir.", sender="assistant")
    root.mainloop()
