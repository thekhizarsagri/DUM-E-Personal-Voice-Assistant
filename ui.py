import tkinter as tk
import math
import time
import threading
import random

# DUM-E // Jarvis-class theme — blue, cyan, red only
BG_COLOR = "#04060c"
PANEL_COLOR = "#081018"
CYAN = "#00e5ff"
BLUE = "#2f6bff"
RED = "#ff2d55"
TEXT_COLOR = "#d0ecff"
DIM_COLOR = "#2c4a6b"


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

        root.geometry("920x700")
        root.overrideredirect(True)
        root.resizable(False, False)
        root.configure(bg=BG_COLOR, highlightthickness=0, bd=0)

        self.canvas = tk.Canvas(root, bg=BG_COLOR, highlightthickness=0, bd=0)
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

    # ---------------- Background depth grid ----------------
    def _draw_background(self):
        c = self.canvas
        c.delete("bg")
        for gx in range(20, 920, 60):
            c.create_line(gx, 0, gx, 700, fill="#08101c", width=1, tags="bg")
        for gy in range(20, 700, 60):
            c.create_line(0, gy, 920, gy, fill="#08101c", width=1, tags="bg")
        # vignette: darker edge frame
        c.create_rectangle(8, 8, 912, 692, outline="#0a1524", width=6, tags="bg")
        c.tag_lower("bg")

    # ---------------- HUD header ----------------
    def _build_hud(self):
        self.title = tk.Label(
            self.canvas, text="◆ DUM-E",
            font=("Consolas", 16, "bold"), fg=CYAN, bg=BG_COLOR,
        )
        self.title.place(x=22, y=14)

        self.subtitle = tk.Label(
            self.canvas, text="JARVIS-CLASS INTERFACE // DEEP UNIVERSAL MIND ELECTRIC",
            font=("Consolas", 8), fg=DIM_COLOR, bg=BG_COLOR,
        )
        self.subtitle.place(x=24, y=40)

        self.clock_label = tk.Label(
            self.canvas, text="", font=("Consolas", 13, "bold"),
            fg=TEXT_COLOR, bg=BG_COLOR,
        )
        self.clock_label.place(x=896, y=14, anchor="ne")

        self.date_label = tk.Label(
            self.canvas, text="", font=("Consolas", 8), fg=DIM_COLOR, bg=BG_COLOR,
        )
        self.date_label.place(x=896, y=40, anchor="ne")

        self.close_btn = tk.Button(
            self.canvas, text="✕", font=("Consolas", 12, "bold"),
            fg=DIM_COLOR, bg=BG_COLOR, bd=0, activebackground=RED,
            activeforeground="#fff", cursor="hand2", command=self._close,
        )
        self.close_btn.place(x=880, y=8)

    # ---------------- Dragging ----------------
    def _bind_drag(self):
        for w in (self.canvas, self.title, self.subtitle, self.clock_label, self.date_label):
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

    # ---------------- Animated border ----------------
    def _tick_border(self):
        if self._closed:
            return
        t = (math.sin(self.rot * 1.2) + 1) / 2
        color = hex_mix(BLUE, CYAN, t)
        c = self.canvas
        c.delete("border")

        c.create_rectangle(2, 2, 918, 698, outline=color, width=1, tags="border")
        # outer soft glow frame
        c.create_rectangle(6, 6, 914, 694, outline=hex_mix(color, BG_COLOR, 0.6), width=3, tags="border")

        # HUD corner brackets
        s = 22
        c.create_line(4, 4 + s, 4, 4, 4 + s, 4, fill=color, width=2, tags="border")
        c.create_line(916 - s, 4, 916, 4, 916, 4 + s, fill=color, width=2, tags="border")
        c.create_line(4, 696 - s, 4, 696, 4 + s, 696, fill=color, width=2, tags="border")
        c.create_line(916 - s, 696, 916, 696, 916, 696 - s, fill=color, width=2, tags="border")

        # header separator
        c.create_line(24, 62, 896, 62, fill=hex_mix(color, BG_COLOR, 0.55), width=1, tags="border")
        c.tag_lower("border")
        self.root.after(30, self._tick_border)

    # ---------------- 3D arc reactor ----------------
    def _build_reactor(self):
        self.rx, self.ry = 460, 195
        self.rr = 60

    def _tick_reactor(self):
        if self._closed:
            return
        self.rot += 0.045
        # smooth color transition toward target state color
        self._color_cur = hex_mix(self._color_cur, self._color_tgt, 0.10)
        col = self._color_cur
        c = self.canvas
        c.delete("reactor")

        pulse = math.sin(self.rot * 0.9) * 3.5
        r = self.rr + pulse
        cx, cy = self.rx, self.ry

        # ---- gyroscope rings (3D tilted ellipses) ----
        rings = [
            (r * 1.75, r * 0.62, 0.9, 22, 1.0),   # outer horizontal
            (r * 1.42, r * 0.86, -0.6, 16, 2.0),  # mid tilted
            (r * 1.12, r * 1.0, 0.4, 12, 3.0),    # near circle
        ]
        for rx, ry, spd, dashes, w in rings:
            bbox = (cx - rx, cy - ry, cx + rx, cy + ry)
            # back half dim, front half bright
            a = self.rot * spd * 40
            c.create_arc(bbox, start=a, extent=180, style=tk.ARC,
                         outline=hex_mix(col, BG_COLOR, 0.72), width=int(w) + 1, tags="reactor")
            c.create_arc(bbox, start=a + 180, extent=180, style=tk.ARC,
                         outline=hex_mix(col, BG_COLOR, 0.15), width=int(w) + 2, tags="reactor")
            # rotating bright dashes traveling along the ring
            step = 360.0 / dashes
            for i in range(dashes):
                da = self.rot * spd * 200 + i * step
                c.create_arc(bbox, start=da, extent=step * 0.55, style=tk.ARC,
                             outline=col, width=int(w) + 2, tags="reactor")

        # ---- 3D shaded core sphere ----
        bbox = (cx - r, cy - r, cx + r, cy + r)
        c.create_oval(bbox, fill=hex_mix(BG_COLOR, col, 0.42), outline=col, width=2, tags="reactor")

        # top-left highlight crescent (3D shading)
        c.create_arc(cx - r * 1.05, cy - r * 1.0, cx + r * 0.75, cy + r * 0.9,
                     start=205, extent=115, style=tk.PIESLICE,
                     fill=hex_mix(col, "#ffffff", 0.62), outline="", tags="reactor")
        # bottom-right shadow crescent
        c.create_arc(cx - r * 0.75, cy - r * 0.9, cx + r * 1.05, cy + r * 1.0,
                     start=20, extent=115, style=tk.PIESLICE,
                     fill=hex_mix(BG_COLOR, col, 0.9), outline="", tags="reactor")

        # inner glow + specular dot
        c.create_oval(cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55,
                      fill=hex_mix(BG_COLOR, col, 0.68), outline="", tags="reactor")
        c.create_oval(cx - r * 0.2, cy - r * 0.2, cx + r * 0.2, cy + r * 0.2,
                      fill=hex_mix(col, "#ffffff", 0.85), outline="", tags="reactor")
        c.create_oval(cx - r * 0.5, cy - r * 0.52, cx - r * 0.2, cy - r * 0.22,
                      fill="#ffffff", outline="", tags="reactor")

        # orbiting satellites on the outermost ring
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
            "Speaking": RED,
            "Busy": BLUE,
        }
        self._color_tgt = palette.get(status, CYAN)
        self.status_label.config(text=f"{status.upper()}...", fg=self._color_tgt)

    # ---------------- Hologram particles ----------------
    def _build_particles(self):
        self.particles = [
            [random.uniform(180, 740), random.uniform(360, 560),
             random.uniform(0.4, 1.4), random.uniform(1.5, 3.0), random.uniform(0, 6)]
            for _ in range(14)
        ]

    def _tick_particles(self):
        if self._closed:
            return
        c = self.canvas
        c.delete("particles")
        for i, p in enumerate(self.particles):
            p[1] -= p[2]
            p[4] += 0.08
            if p[1] < 330:
                p[0] = random.uniform(180, 740)
                p[1] = random.uniform(540, 620)
                p[2] = random.uniform(0.4, 1.4)
            drift = math.sin(p[4]) * 8
            col = hex_mix(CYAN, BG_COLOR, (p[1] - 300) / 300)
            c.create_oval(p[0] + drift - p[3], p[1] - p[3], p[0] + drift + p[3], p[1] + p[3],
                          fill=col, outline="", tags="particles")
        self.root.after(30, self._tick_particles)

    # ---------------- System console ----------------
    def _build_chat(self):
        panel = tk.Frame(self.canvas, bg=PANEL_COLOR,
                         highlightthickness=1, highlightbackground=hex_mix(BLUE, BG_COLOR, 0.5),
                         bd=0)
        panel.place(x=24, y=336, width=872, height=262)

        tk.Label(panel, text="// SYSTEM CONSOLE", font=("Consolas", 8, "bold"),
                 fg=DIM_COLOR, bg=PANEL_COLOR).pack(anchor="w", padx=10, pady=(6, 0))

        self.chat = tk.Text(
            panel, wrap=tk.WORD, font=("Consolas", 11), bg=PANEL_COLOR, fg=TEXT_COLOR,
            bd=0, highlightthickness=0, insertbackground=CYAN,
        )
        self.chat.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))
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
                         highlightthickness=1, highlightbackground=hex_mix(BLUE, BG_COLOR, 0.5),
                         bd=0)
        frame.place(x=24, y=612, width=720, height=36)

        self.input_var = tk.StringVar()
        self.command_entry = tk.Entry(
            frame, textvariable=self.input_var, font=("Consolas", 12),
            bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=CYAN,
            bd=0, highlightthickness=0,
        )
        self.command_entry.place(x=8, y=0, width=704, height=36)
        self.command_entry.bind("<Return>", self._send_command)

        self.send_btn = tk.Button(
            self.canvas, text="EXECUTE", font=("Consolas", 10, "bold"),
            fg=BG_COLOR, bg=CYAN, bd=0, cursor="hand2",
            activebackground=BLUE, activeforeground="#fff",
            command=self._send_command,
        )
        self.send_btn.place(x=756, y=612, width=140, height=36)

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
            fg=CYAN, bg=BG_COLOR,
        )
        self.status_label.place(x=478, y=664, anchor="w")

    def _tick_status_dot(self):
        if self._closed:
            return
        pulse = (math.sin(self.rot * 1.7) + 1) / 2
        d = 3.5 + pulse * 2
        col = hex_mix(self._color_cur, "#ffffff", pulse * 0.55)
        self.canvas.delete("dot")
        self.canvas.create_oval(462 - d, 664 - d, 462 + d, 664 + d,
                                fill=col, outline="", tags="dot")
        self.root.after(40, self._tick_status_dot)

    def _tick_clock(self):
        if self._closed:
            return
        self.clock_label.config(text=time.strftime("%H:%M:%S"))
        self.date_label.config(text=time.strftime("%a %b %d %Y"))
        self.root.after(1000, self._tick_clock)


if __name__ == "__main__":
    root = tk.Tk()
    gui = FuturisticGUI(root)
    gui.add_message("Jarvis-class interface online. Awaiting commands, Sir.", sender="assistant")
    root.mainloop()