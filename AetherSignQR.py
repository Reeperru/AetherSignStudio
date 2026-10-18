import os
import re
import math
import zipfile
import segno
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageDraw, ImageFont, ImageTk

class AetherSignApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AetherSign QR — 3D WiFi Plaque Studio")
        self.root.geometry("1240x880")
        self.root.configure(bg="#121214")
        self.root.minsize(1000, 750)

        self.ui_ready = False

        # 3D Camera State (Yaw, Pitch, Zoom)
        self.cam_yaw = -0.45
        self.cam_pitch = 0.35
        self.cam_zoom = 2.2
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.cached_3d_quads = []

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # UI Colors
        self.bg_dark = "#121214"
        self.bg_card = "#1e1e24"
        self.accent = "#3b82f6"
        self.accent_hover = "#2563eb"
        self.text_main = "#f3f4f6"
        self.text_muted = "#9ca3af"

        # In-Memory Default 3D Print Palette Colors
        self.color_qr = "#111111"
        self.color_bg = "#FFFFFF"
        self.color_stand = "#111111"

        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

        # --- HEADER ---
        header_frame = tk.Frame(root, bg=self.bg_dark)
        header_frame.pack(fill="x", padx=25, pady=(16, 10))

        title_lbl = tk.Label(header_frame, text="AETHER-SIGN QR", font=("Segoe UI", 18, "bold"), fg=self.accent, bg=self.bg_dark)
        title_lbl.pack(anchor="w")
        
        sub_lbl = tk.Label(header_frame, text="Parametric multi-color 3D Wi-Fi sign & stand compiler — Advanced Shaded 3D Orbit Studio", font=("Segoe UI", 10), fg=self.text_muted, bg=self.bg_dark)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # --- THREE-COLUMN STUDIO BODY ---
        body_frame = tk.Frame(root, bg=self.bg_dark)
        body_frame.pack(fill="both", expand=True, padx=25, pady=5)
        body_frame.columnconfigure(0, weight=3)
        body_frame.columnconfigure(1, weight=2)
        body_frame.columnconfigure(2, weight=2)
        body_frame.rowconfigure(0, weight=1)

        # ==========================================
        # COLUMN 1 (LEFT): CONTROLS & PARAMETERS
        # ==========================================
        left_card = tk.Frame(body_frame, bg=self.bg_card, highlightbackground="#2d2d38", highlightthickness=1)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        inner_left = tk.Frame(left_card, bg=self.bg_card)
        inner_left.pack(fill="both", expand=True, padx=18, pady=14)

        # SSID Field
        self.lbl_ssid = tk.Label(inner_left, text="Network Name (SSID)", font=("Segoe UI", 9, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_ssid.pack(anchor="w", pady=(0, 2))
        self.ssid_entry = tk.Entry(inner_left, font=("Segoe UI", 10), bg="#272730", fg=self.text_main, insertbackground="white", relief="flat", highlightbackground="#3f3f46", highlightcolor=self.accent, highlightthickness=1)
        self.ssid_entry.pack(fill="x", ipady=4, pady=(0, 5))
        self.ssid_entry.bind("<KeyRelease>", lambda e: self.refresh_all_previews())

        # Password Field with Show/Hide Toggle
        self.lbl_pass = tk.Label(inner_left, text="Wi-Fi Password", font=("Segoe UI", 9, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_pass.pack(anchor="w", pady=(0, 2))
        pass_box = tk.Frame(inner_left, bg=self.bg_card)
        pass_box.pack(fill="x", pady=(0, 5))

        self.show_pass_var = tk.BooleanVar(value=False)
        self.pass_entry = tk.Entry(pass_box, font=("Segoe UI", 10), bg="#272730", fg=self.text_main, show="•", insertbackground="white", relief="flat", highlightbackground="#3f3f46", highlightcolor=self.accent, highlightthickness=1)
        self.pass_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.pass_entry.bind("<KeyRelease>", lambda e: self.refresh_all_previews())

        self.btn_toggle_pass = tk.Button(pass_box, text="Show", font=("Segoe UI", 8, "bold"), bg="#3f3f46", fg=self.text_main, relief="flat", cursor="hand2", command=self.toggle_password_visibility)
        self.btn_toggle_pass.pack(side="right", padx=(6, 0), ipady=2, ipadx=6)

        # Custom Sign Subtitle Field
        self.lbl_sub = tk.Label(inner_left, text="Text Under Icon (e.g. GUEST ACCESS)", font=("Segoe UI", 9, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_sub.pack(anchor="w", pady=(0, 2))
        self.subtitle_entry = tk.Entry(inner_left, font=("Segoe UI", 10), bg="#272730", fg=self.text_main, insertbackground="white", relief="flat", highlightbackground="#3f3f46", highlightcolor=self.accent, highlightthickness=1)
        self.subtitle_entry.pack(fill="x", ipady=4, pady=(0, 5))
        self.subtitle_entry.insert(0, "GUEST ACCESS")
        self.subtitle_entry.bind("<KeyRelease>", lambda e: self.refresh_all_previews())

        # Row: Protocol, Icon Glyph & Palette
        settings_row = tk.Frame(inner_left, bg=self.bg_card)
        settings_row.pack(fill="x", pady=(0, 5))

        sec_box = tk.Frame(settings_row, bg=self.bg_card)
        sec_box.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.lbl_protocol = tk.Label(sec_box, text="Protocol", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_protocol.pack(anchor="w", pady=(0, 2))
        self.sec_var = tk.StringVar(value="WPA")
        self.sec_dropdown = ttk.Combobox(sec_box, textvariable=self.sec_var, values=["WPA", "WEP", "nopass"], state="readonly", font=("Segoe UI", 9), width=7)
        self.sec_dropdown.pack(fill="x", ipady=2)
        self.sec_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_previews())

        glyph_box = tk.Frame(settings_row, bg=self.bg_card)
        glyph_box.pack(side="left", padx=4)
        self.lbl_glyph = tk.Label(glyph_box, text="Icon", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_glyph.pack(anchor="w", pady=(0, 2))
        self.glyph_var = tk.StringVar(value="WiFi")
        self.glyph_dropdown = ttk.Combobox(glyph_box, textvariable=self.glyph_var, values=["WiFi", "Home", "Coffee", "None"], state="readonly", font=("Segoe UI", 9), width=7)
        self.glyph_dropdown.pack(ipady=2)
        self.glyph_dropdown.bind("<<ComboboxSelected>>", lambda e: self.refresh_all_previews())

        qr_cbox = tk.Frame(settings_row, bg=self.bg_card)
        qr_cbox.pack(side="left", padx=3)
        self.lbl_color_qr = tk.Label(qr_cbox, text="QR", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_color_qr.pack(anchor="center", pady=(0, 2))
        self.btn_color_qr = tk.Button(qr_cbox, bg=self.color_qr, width=3, height=1, relief="flat", highlightbackground="#3f3f46", highlightthickness=1, cursor="hand2", command=lambda: self.pick_color("qr"))
        self.btn_color_qr.pack()

        bg_cbox = tk.Frame(settings_row, bg=self.bg_card)
        bg_cbox.pack(side="left", padx=3)
        self.lbl_color_bg = tk.Label(bg_cbox, text="BG", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_color_bg.pack(anchor="center", pady=(0, 2))
        self.btn_color_bg = tk.Button(bg_cbox, bg=self.color_bg, width=3, height=1, relief="flat", highlightbackground="#3f3f46", highlightthickness=1, cursor="hand2", command=lambda: self.pick_color("bg"))
        self.btn_color_bg.pack()

        stand_cbox = tk.Frame(settings_row, bg=self.bg_card)
        stand_cbox.pack(side="left", padx=(3, 0))
        self.lbl_color_stand = tk.Label(stand_cbox, text="Stand", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg=self.bg_card)
        self.lbl_color_stand.pack(anchor="center", pady=(0, 2))
        self.btn_color_stand = tk.Button(stand_cbox, bg=self.color_stand, width=3, height=1, relief="flat", highlightbackground="#3f3f46", highlightthickness=1, cursor="hand2", command=lambda: self.pick_color("stand"))
        self.btn_color_stand.pack()

        # Geometry & Structural Options Box
        self.lbl_engine_head = tk.Label(inner_left, text="Aesthetic & Structural Engine", font=("Segoe UI", 9, "bold"), fg=self.accent, bg=self.bg_card)
        self.lbl_engine_head.pack(anchor="w", pady=(2, 2))

        geom_box = tk.Frame(inner_left, bg="#272730", highlightbackground="#3f3f46", highlightthickness=1)
        geom_box.pack(fill="x", pady=(0, 6), ipady=4, ipadx=8)

        # Plaque Size Preset Row
        size_row = tk.Frame(geom_box, bg="#272730")
        size_row.pack(fill="x", padx=6, pady=(3, 2))
        self.lbl_size = tk.Label(size_row, text="Sign Size:", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg="#272730")
        self.lbl_size.pack(side="left", padx=(0, 6))

        self.size_var = tk.StringVar(value="Standard")
        self.size_radios = []
        for s_val, s_label in [("Compact", "Compact (65mm)"), ("Standard", "Standard (80mm)"), ("Display", "Display (100mm)")]:
            rb = tk.Radiobutton(size_row, text=s_label, variable=self.size_var, value=s_val, font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main, command=self.refresh_all_previews)
            rb.pack(side="left", padx=3)
            self.size_radios.append(rb)

        # Plaque Thickness Mode
        thick_row = tk.Frame(geom_box, bg="#272730")
        thick_row.pack(fill="x", padx=6, pady=(2, 2))
        self.lbl_thick = tk.Label(thick_row, text="Thickness:", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg="#272730")
        self.lbl_thick.pack(side="left", padx=(0, 6))

        self.thick_var = tk.StringVar(value="2.0")
        self.thick_radios = []
        for val, label in [("1.4", "1.4mm Light"), ("2.0", "2.0mm Std"), ("2.8", "2.8mm Rigid")]:
            rb = tk.Radiobutton(thick_row, text=label, variable=self.thick_var, value=val, font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main)
            rb.pack(side="left", padx=3)
            self.thick_radios.append(rb)

        # Stand Width Matcher Mode
        stand_w_row = tk.Frame(geom_box, bg="#272730")
        stand_w_row.pack(fill="x", padx=6, pady=(2, 2))
        self.lbl_stand_mode = tk.Label(stand_w_row, text="Stand Style:", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg="#272730")
        self.lbl_stand_mode.pack(side="left", padx=(0, 6))

        self.stand_style_var = tk.StringVar(value="minimal")
        self.rb_min = tk.Radiobutton(stand_w_row, text="Minimalist (Wings)", variable=self.stand_style_var, value="minimal", font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main, command=self.refresh_all_previews)
        self.rb_min.pack(side="left", padx=3)

        self.rb_full = tk.Radiobutton(stand_w_row, text="Full Width (Flush)", variable=self.stand_style_var, value="full", font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main, command=self.refresh_all_previews)
        self.rb_full.pack(side="left", padx=3)

        # Corner Radius Slider
        radius_row = tk.Frame(geom_box, bg="#272730")
        radius_row.pack(fill="x", padx=6, pady=(2, 2))
        self.lbl_radius = tk.Label(radius_row, text="Corner Radius: 6mm", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg="#272730")
        self.lbl_radius.pack(side="left", padx=(0, 8))

        self.radius_slider = tk.Scale(radius_row, from_=0, to=12, orient="horizontal", bg="#272730", fg=self.text_main, highlightthickness=0, troughcolor="#1e1e24", activebackground=self.accent, command=self.on_radius_change, length=140)
        self.radius_slider.set(6)
        self.radius_slider.pack(side="right", fill="x", expand=True)

        # Surface Style & Stand Angle Row
        opt_split_row = tk.Frame(geom_box, bg="#272730")
        opt_split_row.pack(fill="x", padx=6, pady=(2, 3))

        self.lbl_style = tk.Label(opt_split_row, text="Print Style:", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg="#272730")
        self.lbl_style.pack(side="left", padx=(0, 4))

        self.surface_style_var = tk.StringVar(value="raised")
        self.rb_raised = tk.Radiobutton(opt_split_row, text="Raised", variable=self.surface_style_var, value="raised", font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main, command=self.refresh_all_previews)
        self.rb_raised.pack(side="left", padx=2)

        self.rb_flush = tk.Radiobutton(opt_split_row, text="Flush Inlay", variable=self.surface_style_var, value="flush", font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main, command=self.refresh_all_previews)
        self.rb_flush.pack(side="left", padx=2)

        self.lbl_stand_tilt = tk.Label(opt_split_row, text="Tilt:", font=("Segoe UI", 8, "bold"), fg=self.text_main, bg="#272730")
        self.lbl_stand_tilt.pack(side="left", padx=(10, 4))

        self.angle_var = tk.StringVar(value="65")
        self.angle_radios = []
        for ang in ["55°", "65°", "75°"]:
            rb = tk.Radiobutton(opt_split_row, text=ang, variable=self.angle_var, value=ang.replace("°", ""), font=("Segoe UI", 8), fg=self.text_main, bg="#272730", selectcolor="#1e1e24", activebackground="#272730", activeforeground=self.text_main, command=self.refresh_all_previews)
            rb.pack(side="left", padx=2)
            self.angle_radios.append(rb)

        # Destination Directory
        tk.Label(inner_left, text="Export Destination Directory", font=("Segoe UI", 9, "bold"), fg=self.text_main, bg=self.bg_card).pack(anchor="w", pady=(0, 2))
        dir_frame = tk.Frame(inner_left, bg=self.bg_card)
        dir_frame.pack(fill="x", pady=(0, 6))

        self.dir_path_var = tk.StringVar(value=os.getcwd())
        dir_entry = tk.Entry(dir_frame, textvariable=self.dir_path_var, font=("Segoe UI", 8), bg="#272730", fg=self.text_muted, relief="flat", highlightbackground="#3f3f46", highlightthickness=1)
        dir_entry.pack(side="left", fill="x", expand=True, ipady=4)

        browse_btn = tk.Button(dir_frame, text="Browse", font=("Segoe UI", 8), bg="#3f3f46", fg=self.text_main, activebackground="#52525b", activeforeground="white", relief="flat", cursor="hand2", command=self.browse_output_dir)
        browse_btn.pack(side="right", padx=(6, 0), ipady=2, ipadx=6)

        # Components to Generate
        chk_frame = tk.Frame(inner_left, bg=self.bg_card)
        chk_frame.pack(fill="x", pady=(0, 6))

        self.gen_plaque_var = tk.BooleanVar(value=True)
        self.gen_stand_var = tk.BooleanVar(value=True)

        self.chk_plaque = tk.Checkbutton(chk_frame, text="Plaque (.3mf)", variable=self.gen_plaque_var, font=("Segoe UI", 9), fg=self.text_main, bg=self.bg_card, selectcolor="#272730", activebackground=self.bg_card, activeforeground=self.text_main, command=self.update_ui_states)
        self.chk_plaque.pack(side="left", padx=(0, 20))

        self.chk_stand = tk.Checkbutton(chk_frame, text="Stand (.3mf)", variable=self.gen_stand_var, font=("Segoe UI", 9), fg=self.text_main, bg=self.bg_card, selectcolor="#272730", activebackground=self.bg_card, activeforeground=self.text_main, command=self.update_ui_states)
        self.chk_stand.pack(side="left")

        # Action Button
        self.gen_btn = tk.Button(inner_left, text="Compile Selected Models", font=("Segoe UI", 10, "bold"), bg=self.accent, fg="white", activebackground=self.accent_hover, activeforeground="white", relief="flat", cursor="hand2", command=self.generate_files)
        self.gen_btn.pack(fill="x", ipady=8, pady=(2, 2))

        self.status_lbl = tk.Label(inner_left, text="Ready", font=("Segoe UI", 9), fg=self.text_muted, bg=self.bg_card, anchor="w")
        self.status_lbl.pack(fill="x", pady=(2, 0))

        # ==========================================
        # COLUMN 2 (MIDDLE): 2D TOP-DOWN SCANNABLE VIEW
        # ==========================================
        mid_card = tk.Frame(body_frame, bg=self.bg_card, highlightbackground="#2d2d38", highlightthickness=1)
        mid_card.grid(row=0, column=1, sticky="nsew", padx=6)

        inner_mid = tk.Frame(mid_card, bg=self.bg_card)
        inner_mid.pack(fill="both", expand=True, padx=14, pady=14)

        tk.Label(inner_mid, text="2D Top-Down Scan Test", font=("Segoe UI", 10, "bold"), fg=self.text_main, bg=self.bg_card).pack(anchor="center", pady=(0, 6))

        self.preview_canvas = tk.Label(inner_mid, bg=self.bg_card)
        self.preview_canvas.pack(anchor="center", pady=6)

        tk.Label(inner_mid, text="Point your phone camera here to test-scan credentials.", font=("Segoe UI", 8), fg=self.text_muted, bg=self.bg_card, wraplength=220, justify="center").pack(anchor="center", pady=(6, 0))

        # ==========================================
        # COLUMN 3 (RIGHT): 3D INTERACTIVE ORBIT VIEW
        # ==========================================
        right_card = tk.Frame(body_frame, bg=self.bg_card, highlightbackground="#2d2d38", highlightthickness=1)
        right_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        inner_right = tk.Frame(right_card, bg=self.bg_card)
        inner_right.pack(fill="both", expand=True, padx=14, pady=14)

        top_v_row = tk.Frame(inner_right, bg=self.bg_card)
        top_v_row.pack(fill="x", pady=(0, 6))
        tk.Label(top_v_row, text="3D Orbit View", font=("Segoe UI", 10, "bold"), fg=self.text_main, bg=self.bg_card).pack(side="left")
        tk.Button(top_v_row, text="Reset", font=("Segoe UI", 8), bg="#272730", fg=self.text_muted, relief="flat", cursor="hand2", command=self.reset_3d_camera).pack(side="right", ipadx=4, ipady=1)

        self.view3d = tk.Canvas(inner_right, bg="#16161a", highlightthickness=1, highlightbackground="#2d2d38", cursor="fleur")
        self.view3d.pack(fill="both", expand=True)

        # Bind 3D Mouse Orbit & Zoom & Window Resize tracking
        self.view3d.bind("<ButtonPress-1>", self.on_3d_mouse_down)
        self.view3d.bind("<B1-Motion>", self.on_3d_mouse_drag)
        self.view3d.bind("<MouseWheel>", self.on_3d_mouse_wheel)
        self.view3d.bind("<Configure>", lambda e: self.render_3d_viewport())

        tk.Label(inner_right, text="Click + Drag to Rotate • Scroll to Zoom", font=("Segoe UI", 8), fg=self.text_muted, bg=self.bg_card, justify="center").pack(anchor="center", pady=(6, 0))

        # Mark UI ready and run initial state + both previews
        self.ui_ready = True
        self.update_ui_states()

    def refresh_all_previews(self):
        if not getattr(self, "ui_ready", False):
            return
        self.update_qr_preview()
        self.rebuild_3d_scene()

    # ==========================================
    # INTERACTIVE 3D VIEWPORT ENGINE (WITH SHADING)
    # ==========================================
    def reset_3d_camera(self):
        self.cam_yaw = -0.45
        self.cam_pitch = 0.35
        self.cam_zoom = 2.2
        self.render_3d_viewport()

    def on_3d_mouse_down(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def on_3d_mouse_drag(self, event):
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.cam_yaw += dx * 0.012
        self.cam_pitch = max(-1.4, min(1.4, self.cam_pitch + dy * 0.012))
        self.render_3d_viewport()

    def on_3d_mouse_wheel(self, event):
        if event.delta > 0:
            self.cam_zoom = min(5.0, self.cam_zoom * 1.12)
        else:
            self.cam_zoom = max(1.0, self.cam_zoom * 0.88)
        self.render_3d_viewport()

    def shade_hex(self, hex_str, factor):
        h = hex_str.lstrip('#')
        if len(h) != 6:
            return "#888888"
        r = min(255, max(0, int(int(h[0:2], 16) * factor)))
        g = min(255, max(0, int(int(h[2:4], 16) * factor)))
        b = min(255, max(0, int(int(h[4:6], 16) * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def rebuild_3d_scene(self):
        if not getattr(self, "ui_ready", False):
            return

        ssid = self.ssid_entry.get().strip() or "WIFI"
        pwd = self.pass_entry.get().strip()
        sec = self.sec_var.get().strip()
        sub = self.subtitle_entry.get().strip().upper()
        glyph = self.glyph_var.get()
        size_mode = self.size_var.get()
        stand_style = self.stand_style_var.get()
        thickness = float(self.thick_var.get())
        angle_deg = float(self.angle_var.get())
        is_flush = (self.surface_style_var.get() == "flush")

        do_plaque = self.gen_plaque_var.get()
        do_stand = self.gen_stand_var.get()

        size_presets = {
            "Compact": (65.0, 108.0, 54.0, 18.0),
            "Standard": (80.0, 134.0, 68.0, 22.0),
            "Display": (100.0, 168.0, 84.0, 26.0)
        }
        p_w, p_h, p_pad, p_tab = size_presets[size_mode]
        stand_w = p_w if stand_style == "full" else (min(65.0, p_w - 12.0) if size_mode != "Compact" else 50.0)

        boxes = []

        def make_local_box(x0, y0, z0, x1, y1, z1):
            return [
                (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
            ]

        tilt_rad = math.radians(90.0 - angle_deg) if do_stand else 0.0
        cos_t, sin_t = math.cos(tilt_rad), math.sin(tilt_rad)

        def transform_plaque_pts(pts):
            out = []
            for x, y, z in pts:
                cx = x - p_w / 2.0
                cy = y - 10.0
                cz = z
                ry = cy * cos_t - cz * sin_t
                rz = cy * sin_t + cz * cos_t
                out.append((cx, ry - 35.0, rz))
            return out

        if do_stand:
            sw_half = stand_w / 2.0
            boxes.append((make_local_box(-sw_half, -48.0, -14.0, sw_half, -35.0, 8.0), self.color_stand))
            boxes.append((make_local_box(-sw_half, -48.0, 8.0, sw_half, -42.0, 28.0), self.color_stand))

        if do_plaque:
            z_mid = 0.2 if is_flush else 0.8
            z_top = 0.3 if is_flush else 1.5

            boxes.append((transform_plaque_pts(make_local_box(0, 0, 0, p_w, p_h, thickness)), self.color_qr))

            pad_x = (p_w - p_pad) / 2.0
            pad_y = p_tab + 14.0
            boxes.append((transform_plaque_pts(make_local_box(pad_x, pad_y, thickness, pad_x + p_pad, pad_y + p_pad, thickness + z_mid)), self.color_bg))

            bw = 1.8
            boxes.append((transform_plaque_pts(make_local_box(0, p_tab, thickness, p_w, p_tab + bw, thickness + z_mid)), self.color_bg))
            boxes.append((transform_plaque_pts(make_local_box(0, p_h - bw, thickness, p_w, p_h, thickness + z_mid)), self.color_bg))
            boxes.append((transform_plaque_pts(make_local_box(0, p_tab, thickness, bw, p_h, thickness + z_mid)), self.color_bg))
            boxes.append((transform_plaque_pts(make_local_box(p_w - bw, p_tab, thickness, p_w, p_h, thickness + z_mid)), self.color_bg))

            if glyph != "None":
                boxes.append((transform_plaque_pts(make_local_box(p_w/2 - 7, pad_y + p_pad + 13, thickness, p_w/2 + 7, pad_y + p_pad + 19, thickness + z_mid)), self.color_bg))
            if sub:
                sub_w = min(p_w - 14, len(sub) * 3.8)
                boxes.append((transform_plaque_pts(make_local_box(p_w/2 - sub_w/2, pad_y + p_pad + 4, thickness, p_w/2 + sub_w/2, pad_y + p_pad + 9, thickness + z_mid)), self.color_bg))

            ssid_w = min(p_w - 12, len(ssid) * 4.2)
            boxes.append((transform_plaque_pts(make_local_box(p_w/2 - ssid_w/2, p_tab + 5, thickness, p_w/2 + ssid_w/2, p_tab + 10, thickness + z_mid)), self.color_bg))

            try:
                wifi_str = f"WIFI:S:{ssid};T:{sec};P:{pwd};;"
                qr = segno.make(wifi_str, error='l')
                matrix = qr.matrix
                grid_size = len(matrix)
                qr_size = p_pad - 8.0
                mod = qr_size / grid_size
                qx0, qy0 = pad_x + 4.0, pad_y + 4.0

                for r_idx, row in enumerate(matrix):
                    y0 = qy0 + (grid_size - 1 - r_idx) * mod
                    c_idx = 0
                    while c_idx < grid_size:
                        if row[c_idx]:
                            start_c = c_idx
                            while c_idx < grid_size and row[c_idx]:
                                c_idx += 1
                            x0 = qx0 + start_c * mod
                            x1 = qx0 + c_idx * mod
                            boxes.append((transform_plaque_pts(make_local_box(x0, y0, thickness + z_mid, x1, y0 + mod, thickness + z_top)), self.color_qr))
                        else:
                            c_idx += 1
            except Exception:
                pass

        self.cached_3d_boxes = boxes
        self.render_3d_viewport()

    def render_3d_viewport(self):
        self.view3d.delete("all")
        w = int(self.view3d.winfo_width())
        h = int(self.view3d.winfo_height())
        if w <= 10:
            w, h = 305, 420
        cx, cy = w / 2.0, h / 2.0 + 25.0

        cyaw, syaw = math.cos(self.cam_yaw), math.sin(self.cam_yaw)
        cpitch, spitch = math.cos(self.cam_pitch), math.sin(self.cam_pitch)

        def project(pt):
            x, y, z = pt
            x1 = x * cyaw - z * syaw
            z1 = x * syaw + z * cyaw
            y2 = y * cpitch - z1 * spitch
            z2 = y * spitch + z1 * cpitch
            fov = 420.0
            dist = 260.0 - z2
            if dist < 10.0:
                dist = 10.0
            scale = (fov / dist) * self.cam_zoom
            return (cx + x1 * scale, cy - y2 * scale, z2)

        faces_to_draw = []
        # Calculate real-time shaded faces with depth outlines
        box_faces = [
            (0, 1, 2, 3, 0.70),
            (4, 5, 6, 7, 1.00),
            (0, 1, 5, 4, 0.60),
            (2, 3, 7, 6, 0.90),
            (0, 3, 7, 4, 0.80),
            (1, 2, 6, 5, 0.85)
        ]

        for verts, base_hex in self.cached_3d_boxes:
            p_verts = [project(v) for v in verts]
            for f0, f1, f2, f3, shade in box_faces:
                v0, v1, v2, v3 = p_verts[f0], p_verts[f1], p_verts[f2], p_verts[f3]
                avg_z = (v0[2] + v1[2] + v2[2] + v3[2]) * 0.25
                shaded_col = self.shade_hex(base_hex, shade)
                outline_col = self.shade_hex(base_hex, shade * 0.75)
                faces_to_draw.append((avg_z, [v0[0], v0[1], v1[0], v1[1], v2[0], v2[1], v3[0], v3[1]], shaded_col, outline_col))

        faces_to_draw.sort(key=lambda item: item[0])
        for _, poly_coords, col, out_col in faces_to_draw:
            self.view3d.create_polygon(poly_coords, fill=col, outline=out_col, width=1)

    def on_radius_change(self, val):
        self.lbl_radius.config(text=f"Corner Radius: {val}mm")
        if getattr(self, "ui_ready", False):
            self.refresh_all_previews()

    # --- DYNAMIC WIDGET GREYING / STATE MANAGEMENT ---
    def update_ui_states(self):
        do_plaque = self.gen_plaque_var.get()
        do_stand = self.gen_stand_var.get()

        plaque_state = "normal" if do_plaque else "disabled"
        plaque_color = self.text_main if do_plaque else "#52525b"

        self.ssid_entry.config(state=plaque_state)
        self.pass_entry.config(state=plaque_state)
        self.subtitle_entry.config(state=plaque_state)
        self.sec_dropdown.config(state="readonly" if do_plaque else "disabled")
        self.glyph_dropdown.config(state="readonly" if do_plaque else "disabled")
        self.btn_toggle_pass.config(state=plaque_state)
        self.btn_color_qr.config(state=plaque_state)
        self.btn_color_bg.config(state=plaque_state)
        self.rb_raised.config(state=plaque_state)
        self.rb_flush.config(state=plaque_state)
        self.radius_slider.config(state=plaque_state)
        for rb in self.size_radios:
            rb.config(state=plaque_state)
        for rb in self.thick_radios:
            rb.config(state=plaque_state)

        self.lbl_ssid.config(fg=plaque_color)
        self.lbl_pass.config(fg=plaque_color)
        self.lbl_sub.config(fg=plaque_color)
        self.lbl_protocol.config(fg=plaque_color)
        self.lbl_glyph.config(fg=plaque_color)
        self.lbl_color_qr.config(fg=plaque_color)
        self.lbl_color_bg.config(fg=plaque_color)
        self.lbl_style.config(fg=plaque_color)
        self.lbl_thick.config(fg=plaque_color)
        self.lbl_size.config(fg=plaque_color)
        self.lbl_radius.config(fg=plaque_color)

        stand_state = "normal" if do_stand else "disabled"
        stand_color = self.text_main if do_stand else "#52525b"

        self.btn_color_stand.config(state=stand_state)
        self.lbl_color_stand.config(fg=stand_color)
        self.lbl_stand_tilt.config(fg=stand_color)
        self.lbl_stand_mode.config(fg=stand_color)
        self.rb_min.config(state=stand_state)
        self.rb_full.config(state=stand_state)
        for rb in self.angle_radios:
            rb.config(state=stand_state)

        if getattr(self, "ui_ready", False):
            self.refresh_all_previews()

    def toggle_password_visibility(self):
        if self.show_pass_var.get():
            self.pass_entry.config(show="•")
            self.btn_toggle_pass.config(text="Show")
            self.show_pass_var.set(False)
        else:
            self.pass_entry.config(show="")
            self.btn_toggle_pass.config(text="Hide")
            self.show_pass_var.set(True)

    def pick_color(self, target):
        initial = getattr(self, f"color_{target}")
        display_name = "QR Color" if target == "qr" else ("Background Color" if target == "bg" else "Stand Color")
        chosen = colorchooser.askcolor(color=initial, title=f"Choose {display_name}")[1]
        if chosen:
            setattr(self, f"color_{target}", chosen.upper())
            getattr(self, f"btn_color_{target}").config(bg=chosen)
            self.refresh_all_previews()

    def hex_to_3mf_rgba(self, hex_code):
        hex_clean = hex_code.lstrip('#').upper()
        if len(hex_clean) == 6:
            return f"#{hex_clean}FF"
        return "#FFFFFFFF"

    def browse_output_dir(self):
        selected = filedialog.askdirectory(initialdir=self.dir_path_var.get())
        if selected:
            self.dir_path_var.set(selected)

    def sanitize_filename(self, text):
        clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', text)
        return clean.strip('_') or "WiFi"

    # ==========================================
    # LIVE 2D TOP-DOWN SCANNABLE PREVIEW
    # ==========================================
    def update_qr_preview(self):
        if not getattr(self, "ui_ready", False):
            return
        ssid = self.ssid_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        sec = self.sec_var.get().strip()
        sub = self.subtitle_entry.get().strip().upper()
        glyph = self.glyph_var.get()
        radius = int(self.radius_slider.get())

        if not ssid:
            blank_img = Image.new("RGBA", (220, 280), (39, 39, 48, 255))
            draw = ImageDraw.Draw(blank_img)
            draw.text((65, 130), "Awaiting SSID...", fill="#6b7280")
            self.tk_qr_img = ImageTk.PhotoImage(blank_img)
            self.preview_canvas.config(image=self.tk_qr_img)
            self.preview_canvas.image = self.tk_qr_img
            return

        try:
            wifi_str = f"WIFI:S:{ssid};T:{sec};P:{pwd};;"
            qr = segno.make(wifi_str, error='l')
            matrix = qr.matrix
            grid_size = len(matrix)
            
            card_w, card_h = 220, 280
            img = Image.new("RGBA", (card_w, card_h), (30, 30, 36, 255))
            draw = ImageDraw.Draw(img)

            draw.rounded_rectangle([0, 0, card_w, card_h], radius=radius * 2, fill=self.color_qr)

            cx, cy = card_w // 2, 20
            if glyph == "WiFi":
                for r in [12, 8, 4]:
                    draw.arc([cx - r, cy - r, cx + r, cy + r], start=220, end=320, fill=self.color_bg, width=2)
                draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=self.color_bg)
            elif glyph == "Home":
                draw.polygon([(cx, cy - 8), (cx - 9, cy), (cx + 9, cy)], fill=self.color_bg)
                draw.rectangle([cx - 6, cy, cx + 6, cy + 7], fill=self.color_bg)
            elif glyph == "Coffee":
                draw.rounded_rectangle([cx - 6, cy - 4, cx + 6, cy + 7], radius=2, fill=self.color_bg)
                draw.arc([cx + 4, cy - 2, cx + 10, cy + 5], start=270, end=90, fill=self.color_bg, width=2)

            if sub:
                sub_font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), sub, font=sub_font)
                tw = bbox[2] - bbox[0]
                draw.text(((card_w - tw) // 2, 34), sub, fill=self.color_bg, font=sub_font)

            pad_size = 160
            px0 = (card_w - pad_size) // 2
            py0 = 50
            draw.rounded_rectangle([px0, py0, px0 + pad_size, py0 + pad_size], radius=max(2, radius), fill=self.color_bg)

            scale = 3
            border = 2
            qr_draw_size = (grid_size + 2 * border) * scale
            qr_offset_x = (card_w - qr_draw_size) // 2
            qr_offset_y = py0 + (pad_size - qr_draw_size) // 2

            for r_idx, row in enumerate(matrix):
                for c_idx, is_dark in enumerate(row):
                    if is_dark:
                        x0 = qr_offset_x + (c_idx + border) * scale
                        y0 = qr_offset_y + (r_idx + border) * scale
                        draw.rectangle([x0, y0, x0 + scale, y0 + scale], fill=self.color_qr)

            ssid_txt = ssid.upper()
            bbox = draw.textbbox((0, 0), ssid_txt)
            tw = bbox[2] - bbox[0]
            draw.text(((card_w - tw) // 2, 222), ssid_txt, fill=self.color_bg)

            draw.line([0, 246, card_w, 246], fill="#3f3f46", width=1)
            draw.text((card_w // 2 - 32, 255), "STAND TAB", fill="#6b7280")

            self.tk_qr_img = ImageTk.PhotoImage(img)
            self.preview_canvas.config(image=self.tk_qr_img)
            self.preview_canvas.image = self.tk_qr_img
        except Exception as err:
            err_img = Image.new("RGBA", (220, 280), (39, 39, 48, 255))
            draw = ImageDraw.Draw(err_img)
            draw.text((10, 120), f"Preview Error:\n{err}", fill="#ef4444")
            self.tk_qr_img = ImageTk.PhotoImage(err_img)
            self.preview_canvas.config(image=self.tk_qr_img)
            self.preview_canvas.image = self.tk_qr_img

    # --- COMPILATION PIPELINE ---
    def generate_files(self):
        ssid = self.ssid_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        sub = self.subtitle_entry.get().strip().upper()
        sec = self.sec_var.get().strip()
        export_dir = self.dir_path_var.get().strip()
        radius = float(self.radius_slider.get())
        thickness = float(self.thick_var.get())
        size_mode = self.size_var.get()
        stand_style = self.stand_style_var.get()

        do_plaque = self.gen_plaque_var.get()
        do_stand = self.gen_stand_var.get()

        if not do_plaque and not do_stand:
            messagebox.showwarning("Selection Required", "Please select at least one component (Plaque or Stand) to generate!")
            return

        if do_plaque and not ssid:
            messagebox.showerror("Input Required", "Network SSID cannot be empty to generate the plaque!")
            return

        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Folder Error", f"Cannot access export folder: {e}")
                return

        clean_prefix = self.sanitize_filename(ssid) if ssid else "WiFi"
        generated_files = []

        size_presets = {
            "Compact": (65.0, 108.0, 54.0, 18.0),
            "Standard": (80.0, 134.0, 68.0, 22.0),
            "Display": (100.0, 168.0, 84.0, 26.0)
        }
        p_w, p_h, p_pad, p_tab = size_presets[size_mode]

        if stand_style == "full":
            stand_width = p_w
        else:
            stand_width = min(65.0, p_w - 12.0) if size_mode != "Compact" else 50.0

        try:
            if do_plaque:
                self.status_lbl.config(text=f"Compiling {size_mode} Plaque...", fg="#f59e0b")
                self.root.update_idletasks()
                plaque_filename = os.path.join(export_dir, f"{clean_prefix}_Plaque_{size_mode}.3mf")
                self.build_plaque_3mf(ssid, pwd, sub, sec, plaque_filename, radius, thickness, p_w, p_h, p_pad, p_tab)
                generated_files.append(os.path.basename(plaque_filename))

            if do_stand:
                angle_val = float(self.angle_var.get())
                self.status_lbl.config(text=f"Compiling {int(angle_val)}° Stand 3MF...", fg="#f59e0b")
                self.root.update_idletasks()
                stand_filename = os.path.join(export_dir, f"{clean_prefix}_Stand_{int(angle_val)}deg_{stand_style}.3mf")
                self.build_stand_3mf(stand_filename, angle_val, thickness, stand_width, p_tab)
                generated_files.append(os.path.basename(stand_filename))

            file_list_str = "\n".join([f"• {f}" for f in generated_files])
            self.status_lbl.config(text="✅ Selected models compiled successfully!", fg="#10b981")
            messagebox.showinfo("Compilation Complete", f"Generated successfully:\n\n{file_list_str}\n\nDestination: {export_dir}")
        except Exception as e:
            self.status_lbl.config(text="❌ Error during compilation.", fg="#ef4444")
            messagebox.showerror("Error", str(e))

    # ==========================================
    # 3D GEOMETRY COMPILERS
    # ==========================================
    def add_box(self, vertices, triangles, x0, y0, z0, x1, y1, z1):
        b = len(vertices)
        vertices.extend([
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
        ])
        for t in [
            (0,2,1), (0,3,2), (4,5,6), (4,6,7),
            (0,1,5), (0,5,4), (2,3,7), (2,7,6),
            (3,0,4), (3,4,7), (1,2,6), (1,6,5)
        ]:
            triangles.append((b + t[0], b + t[1], b + t[2]))

    def add_cylinder(self, vertices, triangles, cx, cy, z0, z1, radius, segments=16):
        b = len(vertices)
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            x = cx + radius * math.cos(ang)
            y = cy + radius * math.sin(ang)
            vertices.append((x, y, z0))
            vertices.append((x, y, z1))
        
        c0 = len(vertices)
        vertices.append((cx, cy, z0))
        c1 = len(vertices)
        vertices.append((cx, cy, z1))

        for i in range(segments):
            nxt = (i + 1) % segments
            b0 = b + i * 2
            t0 = b0 + 1
            b1 = b + nxt * 2
            t1 = b1 + 1
            triangles.append((c0, b1, b0))
            triangles.append((c1, t0, t1))
            triangles.append((b0, b1, t1))
            triangles.append((b0, t1, t0))

    def add_glyph(self, vertices, triangles, glyph_type, cx, cy, z0, z1, scale_factor=1.0):
        if glyph_type == "WiFi":
            self.add_cylinder(vertices, triangles, cx, cy, z0, z1, 1.2 * scale_factor, segments=12)
            for r_in, r_out in [(3.2 * scale_factor, 4.4 * scale_factor), (6.4 * scale_factor, 7.6 * scale_factor)]:
                segments = 14
                for i in range(segments):
                    ang0 = math.radians(45 + (90 / segments) * i)
                    ang1 = math.radians(45 + (90 / segments) * (i + 1))
                    x0_in, y0_in = cx + r_in * math.cos(ang0), cy + r_in * math.sin(ang0)
                    x1_in, y1_in = cx + r_in * math.cos(ang1), cy + r_in * math.sin(ang1)
                    x0_out, y0_out = cx + r_out * math.cos(ang0), cy + r_out * math.sin(ang0)
                    x1_out, y1_out = cx + r_out * math.cos(ang1), cy + r_out * math.sin(ang1)

                    b = len(vertices)
                    vertices.extend([
                        (x0_in, y0_in, z0), (x1_in, y1_in, z0), (x1_out, y1_out, z0), (x0_out, y0_out, z0),
                        (x0_in, y0_in, z1), (x1_in, y1_in, z1), (x1_out, y1_out, z1), (x0_out, y0_out, z1)
                    ])
                    for t in [(0,2,1), (0,3,2), (4,5,6), (4,6,7), (0,1,5), (0,5,4), (2,3,7), (2,7,6), (3,0,4), (3,4,7), (1,2,6), (1,6,5)]:
                        triangles.append((b + t[0], b + t[1], b + t[2]))
        elif glyph_type == "Home":
            sf = scale_factor
            self.add_box(vertices, triangles, cx - 6.0*sf, cy - 6.0*sf, z0, cx + 6.0*sf, cy + 2.0*sf, z1)
            self.add_box(vertices, triangles, cx - 8.0*sf, cy + 2.0*sf, z0, cx + 8.0*sf, cy + 4.0*sf, z1)
            self.add_box(vertices, triangles, cx - 4.0*sf, cy + 4.0*sf, z0, cx + 4.0*sf, cy + 7.0*sf, z1)
        elif glyph_type == "Coffee":
            sf = scale_factor
            self.add_box(vertices, triangles, cx - 5.0*sf, cy - 4.0*sf, z0, cx + 5.0*sf, cy + 5.0*sf, z1)
            self.add_box(vertices, triangles, cx + 5.0*sf, cy - 2.0*sf, z0, cx + 8.0*sf, cy + 3.0*sf, z1)

    def add_3d_text(self, vertices, triangles, text, center_x, center_y, max_w, target_h, z0, z1):
        img_w, img_h = 1400, 200
        img = Image.new("L", (img_w, img_h), 0)
        draw = ImageDraw.Draw(img)
        
        font = None
        for font_name in ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf", "arial.ttf"]:
            try:
                font = ImageFont.truetype(font_name, 72)
                break
            except IOError:
                continue
        if font is None:
            font = ImageFont.load_default()

        draw.text((100, 40), text, fill=255, font=font)
        bbox = img.getbbox()
        if bbox is None:
            return
        cropped = img.crop(bbox)
        cw, ch = cropped.size

        scale = min(max_w / cw, target_h / ch)
        real_w = cw * scale
        real_h = ch * scale
        start_x = center_x - (real_w / 2.0)
        start_y = center_y - (real_h / 2.0)

        pixels = cropped.load()
        for row in range(ch):
            y0 = start_y + (ch - 1 - row) * scale
            y1 = y0 + scale
            col = 0
            while col < cw:
                if pixels[col, row] > 128:
                    run_start = col
                    while col < cw and pixels[col, row] > 128:
                        col += 1
                    x0 = start_x + run_start * scale
                    x1 = start_x + col * scale
                    self.add_box(vertices, triangles, x0, y0, z0, x1, y1, z1)
                else:
                    col += 1

    def get_rounded_rect_pts(self, x_off, y_off, width, height, radius, segments=10):
        if radius <= 0.0:
            return [
                (x_off, y_off),
                (x_off + width, y_off),
                (x_off + width, y_off + height),
                (x_off, y_off + height)
            ]
        pts = []
        corners = [
            (x_off + width - radius, y_off + height - radius, 0.0),
            (x_off + radius, y_off + height - radius, math.pi * 0.5),
            (x_off + radius, y_off + radius, math.pi),
            (x_off + width - radius, y_off + radius, math.pi * 1.5)
        ]
        for cx, cy, start_ang in corners:
            for i in range(segments + 1):
                ang = start_ang + (math.pi * 0.5) * (i / segments)
                pts.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
        return pts

    def add_rounded_plate(self, vertices, triangles, x_off, y_off, width, height, radius, z0, z1):
        pts_2d = self.get_rounded_rect_pts(x_off, y_off, width, height, radius)
        n = len(pts_2d)
        base_idx = len(vertices)
        cx, cy = x_off + width / 2.0, y_off + height / 2.0
        vertices.append((cx, cy, z0))
        vertices.append((cx, cy, z1))

        for px, py in pts_2d:
            vertices.append((px, py, z0))
            vertices.append((px, py, z1))

        for i in range(n):
            nxt = (i + 1) % n
            b_cur = base_idx + 2 + i * 2
            t_cur = b_cur + 1
            b_nxt = base_idx + 2 + nxt * 2
            t_nxt = b_nxt + 1
            triangles.append((base_idx, b_nxt, b_cur))
            triangles.append((base_idx + 1, t_cur, t_nxt))
            triangles.append((b_cur, b_nxt, t_nxt))
            triangles.append((b_cur, t_nxt, t_cur))

    def add_beveled_tab(self, vertices, triangles, width, tab_height, z0, z1, chamfer=0.6):
        ch = min(chamfer, tab_height * 0.3, (z1 - z0) * 0.3)
        self.add_box(vertices, triangles, 0.0, ch, z0, width, tab_height, z1)
        self.add_box(vertices, triangles, ch, 0.0, z0 + ch, width - ch, ch, z1 - ch)

    def add_raised_border(self, vertices, triangles, x_off, y_off, width, height, radius, border_w, z0, z1):
        outer_pts = self.get_rounded_rect_pts(x_off, y_off, width, height, radius)
        inner_pts = self.get_rounded_rect_pts(x_off + border_w, y_off + border_w, width - 2*border_w, height - 2*border_w, max(0.0, radius - border_w))
        n = len(outer_pts)
        base_idx = len(vertices)

        for i in range(n):
            ox, oy = outer_pts[i]
            ix, iy = inner_pts[i]
            vertices.extend([(ox, oy, z0), (ox, oy, z1), (ix, iy, z0), (ix, iy, z1)])

        for i in range(n):
            nxt = (i + 1) % n
            o_b0, o_t0, i_b0, i_t0 = base_idx + i*4, base_idx + i*4 + 1, base_idx + i*4 + 2, base_idx + i*4 + 3
            o_b1, o_t1, i_b1, i_t1 = base_idx + nxt*4, base_idx + nxt*4 + 1, base_idx + nxt*4 + 2, base_idx + nxt*4 + 3
            triangles.extend([(o_t0, o_t1, i_t1), (o_t0, i_t1, i_t0)])
            triangles.extend([(o_b0, i_b1, o_b1), (o_b0, i_b0, i_b1)])
            triangles.extend([(o_b0, o_b1, o_t1), (o_b0, o_t1, o_t0)])
            triangles.extend([(i_b0, i_t1, i_b1), (i_b0, i_t0, i_t1)])

    def mesh_to_xml(self, obj_id, name, vertices, triangles, pid=None, pindex=None):
        pid_attr = f' pid="{pid}"' if pid is not None else ""
        pindex_attr = f' pindex="{pindex}"' if pindex is not None else ""
        lines = [f'    <object id="{obj_id}" name="{name}" type="model"{pid_attr}{pindex_attr}>', '      <mesh>', '        <vertices>']
        for vx, vy, vz in vertices:
            lines.append(f'          <vertex x="{vx:.4f}" y="{vy:.4f}" z="{vz:.4f}" />')
        lines.append('        </vertices>\n        <triangles>')
        for v1, v2, v3 in triangles:
            lines.append(f'          <triangle v1="{v1}" v2="{v2}" v3="{v3}"{pid_attr}{pindex_attr} />')
        lines.extend(['        </triangles>', '      </mesh>', '    </object>'])
        return "\n".join(lines)

    def build_plaque_3mf(self, ssid, pwd, sub, sec, output_path, corner_radius, base_thick, p_w, p_h, p_pad, p_tab):
        QR_QUIET_ZONE, BORDER_WIDTH = 4.0, 1.6
        scale_ratio = p_w / 80.0

        qr_rgba = self.hex_to_3mf_rgba(self.color_qr)
        bg_rgba = self.hex_to_3mf_rgba(self.color_bg)

        is_flush = (self.surface_style_var.get() == "flush")
        if is_flush:
            z_base_0, z_base_1 = 0.0, base_thick + 0.4
            z_mid_0, z_mid_1 = 0.0, 0.4
            z_top_0, z_top_1 = 0.0, 0.4
        else:
            z_base_0, z_base_1 = 0.0, base_thick
            z_mid_0, z_mid_1 = base_thick, base_thick + 0.6
            z_top_0, z_top_1 = base_thick + 0.6, base_thick + 1.2

        black_base_v, black_base_t = [], []
        self.add_rounded_plate(black_base_v, black_base_t, 0.0, p_tab, p_w, p_h - p_tab, corner_radius, z_base_0, z_base_1)
        self.add_beveled_tab(black_base_v, black_base_t, p_w, p_tab, z_base_0, z_base_1, chamfer=0.6)

        white_mid_v, white_mid_t = [], []
        pad_x = (p_w - p_pad) / 2.0
        pad_y = p_tab + (16.0 * scale_ratio)
        pad_radius = max(0.0, min(corner_radius, 4.0))
        self.add_rounded_plate(white_mid_v, white_mid_t, pad_x, pad_y, p_pad, p_pad, pad_radius, z_mid_0, z_mid_1)

        glyph = self.glyph_var.get()
        if glyph != "None":
            self.add_glyph(white_mid_v, white_mid_t, glyph, p_w / 2.0, pad_y + p_pad + (17.5 * scale_ratio), z_mid_0, z_mid_1, scale_factor=scale_ratio)
            if sub:
                self.add_3d_text(white_mid_v, white_mid_t, sub, p_w / 2.0, pad_y + p_pad + (7.5 * scale_ratio), 52.0 * scale_ratio, 6.0 * scale_ratio, z_mid_0, z_mid_1)
        else:
            if sub:
                self.add_3d_text(white_mid_v, white_mid_t, sub, p_w / 2.0, pad_y + p_pad + (11.5 * scale_ratio), 60.0 * scale_ratio, 7.5 * scale_ratio, z_mid_0, z_mid_1)

        self.add_3d_text(white_mid_v, white_mid_t, ssid.upper(), p_w / 2.0, p_tab + (8.0 * scale_ratio), 66.0 * scale_ratio, 6.2 * scale_ratio, z_mid_0, z_mid_1)
        self.add_raised_border(white_mid_v, white_mid_t, 0.0, p_tab, p_w, p_h - p_tab, corner_radius, BORDER_WIDTH, z_mid_0, z_mid_1)

        black_qr_v, black_qr_t = [], []
        wifi_str = f"WIFI:S:{ssid};T:{sec};P:{pwd};;"
        qr = segno.make(wifi_str, error='l')
        matrix = qr.matrix
        grid_size = len(matrix)

        qr_size = p_pad - (2.0 * QR_QUIET_ZONE)
        mod_size = qr_size / grid_size
        qr_start_x = pad_x + QR_QUIET_ZONE
        qr_start_y = pad_y + QR_QUIET_ZONE

        for r_idx, row in enumerate(matrix):
            for c_idx, is_dark in enumerate(row):
                if is_dark:
                    x0 = qr_start_x + c_idx * mod_size
                    y0 = qr_start_y + (grid_size - 1 - r_idx) * mod_size
                    self.add_box(black_qr_v, black_qr_t, x0, y0, z_top_0, x0 + mod_size, y0 + mod_size, z_top_1)

        obj1_xml = self.mesh_to_xml(2, "Main_Backplate", black_base_v, black_base_t, pid=1, pindex=0)
        obj2_xml = self.mesh_to_xml(3, "Background_Pad_and_Text", white_mid_v, white_mid_t, pid=1, pindex=1)
        obj3_xml = self.mesh_to_xml(4, "QR_Code_Blocks", black_qr_v, black_qr_t, pid=1, pindex=0)

        model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">
  <resources>
    <m:colorgroup id="1">
      <m:color color="{qr_rgba}" />
      <m:color color="{bg_rgba}" />
    </m:colorgroup>
{obj1_xml}
{obj2_xml}
{obj3_xml}
    <object id="5" name="WiFi_QR_Plaque" type="model">
      <components>
        <component objectid="2" />
        <component objectid="3" />
        <component objectid="4" />
      </components>
    </object>
  </resources>
  <build>
    <item objectid="5" />
  </build>
</model>"""

        model_settings_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="5">
    <metadata key="name" value="WiFi_QR_Plaque"/>
    <metadata key="extruder" value="1"/>
    <part id="2" subtype="normal_part">
      <metadata key="name" value="Main_Backplate"/>
      <metadata key="extruder" value="1"/>
      <metadata key="paint_color" value="{qr_rgba}"/>
    </part>
    <part id="3" subtype="normal_part">
      <metadata key="name" value="Background_Pad_and_Text"/>
      <metadata key="extruder" value="2"/>
      <metadata key="paint_color" value="{bg_rgba}"/>
    </part>
    <part id="4" subtype="normal_part">
      <metadata key="name" value="QR_Code_Blocks"/>
      <metadata key="extruder" value="1"/>
      <metadata key="paint_color" value="{qr_rgba}"/>
    </part>
  </object>
</config>"""

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />
  <Default Extension="config" ContentType="text/xml" />
</Types>"""

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
            zf.writestr("3D/3dmodel.model", model_xml)
            zf.writestr("Metadata/model_settings.config", model_settings_xml)

    def build_stand_3mf(self, output_path, angle_deg, plaque_thick, stand_width, tab_depth):
        STAND_DEPTH, CLEARANCE = 46.0, 0.20
        slot_w = plaque_thick + CLEARANCE
        slot_depth = min(12.0, tab_depth * 0.65)

        rad = math.radians(angle_deg)
        tx, ty = -math.cos(rad), -math.sin(rad)
        nx, ny = math.sin(rad), -math.cos(rad)

        s_fx, s_fy = 6.0, 14.5
        s_fbx, s_fby = s_fx + tx * slot_depth, s_fy + ty * slot_depth
        s_bbx, s_bby = s_fbx + nx * slot_w, s_fby + ny * slot_w
        s_top_bx = s_bbx - tx * ((16.0 - s_bby) / (-ty))
        s_top_by = 16.0

        tris_2d = [
            ((0, 0), (s_fbx, s_fby), (s_fx, s_fy)),
            ((0, 0), (s_fx, s_fy), (0, 11.5)),
            ((0, 0), (17.0, 0), (s_bbx, s_bby)),
            ((0, 0), (s_bbx, s_bby), (s_fbx, s_fby)),
            ((17.0, 0), (17.0, 16.0), (s_top_bx, s_top_by)),
            ((17.0, 0), (s_top_bx, s_top_by), (s_bbx, s_bby)),
            ((17.0, 0), (STAND_DEPTH, 0), (STAND_DEPTH, 4.0)),
            ((17.0, 0), (STAND_DEPTH, 4.0), (17.0, 16.0)),
        ]
        perimeter = [
            (0, 0), (STAND_DEPTH, 0), (STAND_DEPTH, 4.0), (17.0, 16.0),
            (s_top_bx, s_top_by), (s_bbx, s_bby), (s_fbx, s_fby), (s_fx, s_fy), (0, 11.5)
        ]

        vertices = []
        triangles = []
        z0, z1 = 0.0, stand_width

        vert_map = {}
        def get_v_idx(x, y, z):
            pt = (round(x, 4), round(y, 4), round(z, 4))
            if pt not in vert_map:
                vert_map[pt] = len(vertices)
                vertices.append(pt)
            return vert_map[pt]

        for pA, pB, pC in tris_2d:
            iA = get_v_idx(pA[0], pA[1], z0)
            iB = get_v_idx(pB[0], pB[1], z0)
            iC = get_v_idx(pC[0], pC[1], z0)
            triangles.append((iA, iC, iB))

            iA1 = get_v_idx(pA[0], pA[1], z1)
            iB1 = get_v_idx(pB[0], pB[1], z1)
            iC1 = get_v_idx(pC[0], pC[1], z1)
            triangles.append((iA1, iB1, iC1))

        for i in range(len(perimeter)):
            pA = perimeter[i]
            pB = perimeter[(i + 1) % len(perimeter)]
            v_a0 = get_v_idx(pA[0], pA[1], z0)
            v_b0 = get_v_idx(pB[0], pB[1], z0)
            v_a1 = get_v_idx(pA[0], pA[1], z1)
            v_b1 = get_v_idx(pB[0], pB[1], z1)

            triangles.append((v_a0, v_b0, v_b1))
            triangles.append((v_a0, v_b1, v_a1))

        stand_rgba = self.hex_to_3mf_rgba(self.color_stand)
        obj_xml = self.mesh_to_xml(2, "Stand_Base", vertices, triangles, pid=1, pindex=0)

        model_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">
  <resources>
    <m:colorgroup id="1">
      <m:color color="{stand_rgba}" />
    </m:colorgroup>
{obj_xml}
  </resources>
  <build>
    <item objectid="2" />
  </build>
</model>"""

        model_settings_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<config>
  <object id="2">
    <metadata key="name" value="WiFi_Stand_Base"/>
    <metadata key="extruder" value="1"/>
    <metadata key="paint_color" value="{stand_rgba}"/>
  </object>
</config>"""

        content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />
  <Default Extension="config" ContentType="text/xml" />
</Types>"""

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
            zf.writestr("3D/3dmodel.model", model_xml)
            zf.writestr("Metadata/model_settings.config", model_settings_xml)

if __name__ == "__main__":
    root = tk.Tk()
    app = AetherSignApp(root)
    root.mainloop()