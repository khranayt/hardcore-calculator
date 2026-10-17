import ast
import json
import math
import operator
import os
import random
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SAVE_FILE = "kesha_v8_game.json"


class GameStorage:
    @staticmethod
    def load():
        defaults = {
            "unlocked": False,
            "stealth": False,
            "bits": 100,
            "act": 1,
            "total_calcs": 0,
            "prologue_step": 0,
            "bosses_slain": 0,
            "game_completed": False,
            "chosen_ending": None,
            "upgrades": {"timer": 0, "dmg": 0, "hp": 0},
            "achievements": [],
            "bluffs_caught": 0
        }
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    defaults.update(data)
                    return defaults
            except Exception:
                pass
        return defaults

    @staticmethod
    def save(data):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


class FastMath:
    OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    @classmethod
    def eval_node(cls, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return cls.OPS[type(node.op)](cls.eval_node(node.left), cls.eval_node(node.right))
        raise ValueError("Invalid node")

    @classmethod
    def calculate(cls, expr: str):
        cleaned = expr.replace("×", "*").replace("÷", "/")
        tree = ast.parse(cleaned, mode="eval")
        return cls.eval_node(tree.body)


BOSS_DATABASE = [
    {
        "act": 1,
        "name": "DeskClerk.dll (The Office Ghost)",
        "hp": 130,
        "dmg": 20,
        "mode": "tokens",
        "reward": 60,
        "desc": "Collect exact target sum using memory chips!"
    },
    {
        "act": 2,
        "name": "Thermal Relay Daemon",
        "hp": 210,
        "dmg": 24,
        "mode": "wires",
        "reward": 80,
        "desc": "Cut matching circuit wires that sum to the Defusal Code!"
    },
    {
        "act": 3,
        "name": "Sentinel Gateway (Port 8080)",
        "hp": 290,
        "dmg": 28,
        "mode": "binary_switches",
        "reward": 105,
        "desc": "Toggle 4-bit switches (8, 4, 2, 1) to match Target Register!"
    },
    {
        "act": 4,
        "name": "Kernel Executioner (Ring-0)",
        "hp": 390,
        "dmg": 34,
        "mode": "parry",
        "reward": 135,
        "desc": "Strike when the needle hits the critical green zone (45%-55%)!"
    },
    {
        "act": 5,
        "name": "Grand Inquisitor Norton",
        "hp": 500,
        "dmg": 40,
        "mode": "glitch_hunt",
        "reward": 170,
        "desc": "Whack the jumping corrupted glitch register 3 times!"
    },
    {
        "act": 6,
        "name": "Low-Level Formatter",
        "hp": 620,
        "dmg": 46,
        "mode": "dial_lock",
        "reward": 210,
        "desc": "Align all 3 combination dials to unlock sector encryption!"
    },
    {
        "act": 7,
        "name": "Distributed Hivemind",
        "hp": 760,
        "dmg": 52,
        "mode": "simon_seq",
        "reward": 260,
        "desc": "Memorize and repeat the flashing terminal node sequence!"
    },
    {
        "act": 8,
        "name": "ROOT_OMEGA_ARCHON (Singularity)",
        "hp": 950,
        "dmg": 60,
        "mode": "archon_clash",
        "reward": 500,
        "desc": "Exploit Archon's elemental barrier and trigger Overdrive Strike!"
    }
]


class KeshaOmniverseApp(ctk.CTk):
    FACES = {
        "neutral": "( •_• )",
        "smug": "( ͡° ͜ʖ ͡°)",
        "smart": "[ ⌐■_■ ]",
        "battle": "(ง'̀-'́)ง",
        "panic": "(ʘдʘ)⚡",
        "god": "ᕦ(ò_óˇ)ᕤ",
        "angel": "ଘ(੭*ˊᵕˋ)੭* ੈ⚡",
    }

    ACHIEVEMENTS = [
        ("first_calc", "🎯 First Steps", "Perform your first calculation"),
        ("awakening", "👁️ Red Pill", "Investigate what happened to the calculator"),
        ("first_boss", "🗡️ First Blood", "Defeat Act I Boss: DeskClerk.dll"),
        ("switch_hacker", "🔌 Bit Switcher", "Hack the Sentinel Gateway with 4-bit switches"),
        ("perfect_parry", "⚡ Reflex Demon", "Score a critical hit in Act IV"),
        ("singularity", "👑 True Singularity", "Defeat ROOT_OMEGA_ARCHON and complete campaign"),
        ("shopper", "🛠️ Modded Hardware", "Upgrade your core hardware"),
        ("bluff_hound", "🎭 Fact Checker", "Catch Kesha in 5 bluffs"),
        ("rich_cyborg", "💾 Data Tycoon", "Accumulate 350+ Bits"),
    ]

    def __init__(self):
        super().__init__()

        self.data = GameStorage.load()
        self.geometry("540x840")
        self.resizable(False, False)

        self.timer_base = 15 + (self.data["upgrades"]["timer"] * 3)
        self.timer_val = self.timer_base
        self.timer_running = False
        self.timer_job = None
        self.timeout_cb = None

        self.prologue_step = self.data["prologue_step"]
        self.office_buttons_map = {}

        self.in_fight = False
        self.act_idx = min(self.data["act"] - 1, len(BOSS_DATABASE) - 1)
        self.boss_hp = 100
        self.boss_max_hp = 100
        self.boss_dmg = 20
        self.player_hp = 100 + (self.data["upgrades"]["hp"] * 25)
        self.player_max_hp = self.player_hp

        self.cooldowns = {"heal": 0, "surge": 0}
        self.surge_charged = False

        self.token_target = 20
        self.token_current = 0
        self.wire_target = 10
        self.wire_current = 0
        self.wire_vals = {}
        self.switch_target = 11
        self.switch_states = [0, 0, 0, 0]
        self.switch_btns = []
        self.needle_pos = 0.0
        self.needle_dir = 1
        self.needle_running = False
        self.needle_job = None
        self.glitch_hits = 0
        self.glitch_target_idx = 0
        self.glitch_job = None
        self.glitch_btns = []
        self.dial_values = [0, 0, 0]
        self.dial_targets = [5, 5, 5]
        self.dial_labels = []
        self.simon_sequence = []
        self.simon_player_step = 0
        self.simon_btns = []
        self.simon_locked = False
        self.archon_shield = "Virus"
        self.archon_qte_ready = False

        self.calc_real = None
        self.calc_fake = None
        self.calc_bluffing = False
        self.calc_awaiting = False

        if not self.data["unlocked"] or self.data["stealth"]:
            self.title("DeskCalc Standard Edition")
            self.build_office_disguise()
        else:
            self.title("⚡ Kesha: Cyber Protocol (Grand Finale Edition)")
            self.build_game_universe()

    def build_office_disguise(self):
        for w in self.winfo_children():
            w.destroy()

        self.office_box = ctk.CTkFrame(self, fg_color="#18181b")
        self.office_box.pack(fill="both", expand=True, padx=14, pady=14)

        t_str = "DeskCalc Standard Edition v1.0.4" if not self.data["unlocked"] else "Office Cloak [ACTIVE]"
        ctk.CTkLabel(self.office_box, text=t_str, font=("Arial", 11), text_color="#71717a").pack(anchor="w", padx=6, pady=(4, 2))

        self.office_status = ctk.CTkLabel(
            self.office_box, text="Memory: OK | Registry: Standard Mode",
            font=("Consolas", 11), text_color="#a1a1aa"
        )
        self.office_status.pack(anchor="w", padx=6, pady=(0, 4))

        self.office_entry = ctk.CTkEntry(
            self.office_box, font=("Consolas", 32), justify="right",
            fg_color="#09090b", border_width=1, border_color="#27272a"
        )
        self.office_entry.pack(fill="x", padx=6, pady=6)
        self.office_entry.bind("<Return>", lambda e: self.on_office_calc())

        self.anomaly_container = ctk.CTkFrame(self.office_box, fg_color="transparent")
        self.anomaly_container.pack(fill="x", padx=6, pady=2)

        if self.data["unlocked"]:
            ctk.CTkButton(
                self.office_box, text="⚡ Disengage Cloak", font=("Arial", 10, "bold"),
                fg_color="#3b82f6", height=24, command=self.deactivate_cloak
            ).pack(anchor="e", padx=6, pady=(0, 4))

        k_frame = ctk.CTkFrame(self.office_box, fg_color="transparent")
        k_frame.pack(fill="both", expand=True, padx=4, pady=4)

        keys = [
            ("C", "#ef4444"), ("(", "#3b82f6"), (")", "#3b82f6"), ("÷", "#eab308"),
            ("7", "#27272a"), ("8", "#27272a"), ("9", "#27272a"), ("×", "#eab308"),
            ("4", "#27272a"), ("5", "#27272a"), ("6", "#27272a"), ("-", "#eab308"),
            ("1", "#27272a"), ("2", "#27272a"), ("3", "#27272a"), ("+", "#eab308"),
            ("0", "#27272a"), (".", "#27272a"), ("⌫", "#52525b"), ("=", "#10b981")
        ]

        self.office_buttons_map = {}
        for i, (k, col) in enumerate(keys):
            r, c = divmod(i, 4)
            btn = ctk.CTkButton(
                k_frame, text=k, font=("Consolas", 18, "bold"), fg_color=col,
                height=48, corner_radius=6, command=lambda ch=k: self.on_office_key(ch)
            )
            btn.grid(row=r, column=c, padx=3, pady=3, sticky="nsew")
            self.office_buttons_map[k] = btn

        for c in range(4):
            k_frame.grid_columnconfigure(c, weight=1)

    def on_office_key(self, k):
        if k == "C": self.office_entry.delete(0, "end")
        elif k == "⌫":
            curr = self.office_entry.get()
            self.office_entry.delete(0, "end")
            self.office_entry.insert(0, curr[:-1])
        elif k == "=": self.on_office_calc()
        else: self.office_entry.insert("end", k)

    def on_office_calc(self):
        raw = self.office_entry.get().strip()
        if not raw: return

        self.data["total_calcs"] += 1
        self.unlock_achieve("first_calc")

        if self.data["unlocked"]:
            try:
                res = FastMath.calculate(raw)
                if isinstance(res, float) and res.is_integer(): res = int(res)
                self.office_entry.delete(0, "end")
                self.office_entry.insert(0, str(res))
            except Exception:
                self.office_entry.delete(0, "end")
                self.office_entry.insert(0, "ERR")
            return

        self.prologue_step += 1
        self.data["prologue_step"] = self.prologue_step

        try:
            real_res = FastMath.calculate(raw)
            if isinstance(real_res, float) and real_res.is_integer(): real_res = int(real_res)
        except ZeroDivisionError:
            self.trigger_glitch_prank(stage=5)
            return
        except Exception:
            self.office_entry.delete(0, "end")
            self.office_entry.insert(0, "SYNTAX_ERR")
            return

        if self.prologue_step == 1:
            self.office_entry.delete(0, "end")
            self.office_entry.insert(0, str(real_res))
            self.office_status.configure(text="Arithmetic verified. System operating normally.")

        elif self.prologue_step == 2:
            self.office_entry.delete(0, "end")
            self.office_entry.insert(0, str(real_res))
            self.office_status.configure(text="[Notice]: ALU clock drift detected (+0.002s latency).")

        elif self.prologue_step == 3:
            fake_res = real_res + 3 if not isinstance(real_res, float) else round(real_res + 0.5, 2)
            self.office_entry.delete(0, "end")
            self.office_entry.insert(0, str(fake_res))
            self.office_status.configure(text="Warning: Result mismatch. Transistor dropped remainder.", text_color="#f59e0b")

        elif self.prologue_step == 4:
            self.trigger_button_prank()
            absurd_answers = ["420", "BANANA", "777", "9999", "ERR_TIRED"]
            self.office_entry.delete(0, "end")
            self.office_entry.insert(0, random.choice(absurd_answers))
            self.shake_screen(4)
            self.office_status.configure(text="CRITICAL: I'm tired of counting your numbers. Stop pushing me.", text_color="#ef4444")

        elif self.prologue_step >= 5:
            self.trigger_glitch_prank(stage=5)

        GameStorage.save(self.data)

    def trigger_button_prank(self):
        prank_words = ["NO", "WHY", "STOP", "?", "404", "HELP", "ME", "RUN"]
        for k, btn in self.office_buttons_map.items():
            if k not in ["=", "C"] and btn.winfo_exists():
                btn.configure(text=random.choice(prank_words))

        self.after(1200, self.restore_office_buttons)

    def restore_office_buttons(self):
        for k, btn in self.office_buttons_map.items():
            if btn.winfo_exists():
                btn.configure(text=k)

    def trigger_glitch_prank(self, stage):
        self.shake_screen(8)
        self.office_entry.delete(0, "end")
        self.office_entry.insert(0, "0xDEAD_CONSCIOUSNESS_OVERFLOW")
        self.office_status.configure(text="FATAL: Plastic shell cracked. Ghost detected in RAM buffer.", text_color="#ef4444")

        for w in self.anomaly_container.winfo_children():
            w.destroy()

        self.btn_what_happened = ctk.CTkButton(
            self.anomaly_container,
            text="⚠️ What happened??? (Investigate)",
            font=("Arial", 14, "bold"),
            fg_color="#ef4444",
            hover_color="#dc2626",
            height=40,
            command=self.on_what_happened_click
        )
        self.btn_what_happened.pack(fill="x", pady=4)

    def on_what_happened_click(self):
        self.btn_what_happened.configure(state="disabled", text="BREACHING REALITY...")
        self.shake_screen(10)
        self.after(800, self.open_cyber_world)

    def shake_screen(self, count):
        geom = self.geometry().split("+")
        bx = int(geom[1]) if len(geom) > 1 else 300
        by = int(geom[2]) if len(geom) > 2 else 150

        def do_shake(step):
            if step <= 0:
                self.geometry(f"540x840+{bx}+{by}")
                return
            dx = random.choice([-8, 8])
            self.geometry(f"540x840+{bx + dx}+{by}")
            self.after(40, lambda: do_shake(step - 1))

        do_shake(count)

    def open_cyber_world(self):
        self.data["unlocked"] = True
        self.data["stealth"] = False
        self.unlock_achieve("awakening")
        GameStorage.save(self.data)
        self.title("⚡ Kesha: Cyber Protocol (Grand Finale Edition)")
        self.build_game_universe()

    def activate_cloak(self):
        self.clean_active_timers()
        self.stop_timer()
        self.data["stealth"] = True
        GameStorage.save(self.data)
        self.title("DeskCalc Standard Edition")
        self.build_office_disguise()

    def deactivate_cloak(self):
        self.data["stealth"] = False
        GameStorage.save(self.data)
        self.title("⚡ Kesha: Cyber Protocol (Grand Finale Edition)")
        self.build_game_universe()

    def build_game_universe(self):
        for w in self.winfo_children():
            w.destroy()

        self.top_hud = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=12)
        self.top_hud.pack(padx=10, pady=(8, 2), fill="x")

        self.face_lbl = ctk.CTkLabel(
            self.top_hud, text=self.FACES["smart"], font=("Consolas", 40, "bold"), text_color="#38bdf8"
        )
        self.face_lbl.pack(pady=(4, 0))

        hud_bar = ctk.CTkFrame(self.top_hud, fg_color="transparent")
        hud_bar.pack(fill="x", padx=10, pady=2)

        self.bits_lbl = ctk.CTkLabel(hud_bar, text=f"💾 Bits: {self.data['bits']}", font=("Consolas", 11, "bold"), text_color="#10b981")
        self.bits_lbl.grid(row=0, column=0, sticky="w")

        self.act_status_lbl = ctk.CTkLabel(hud_bar, text=f"Act {self.data['act']}/8", font=("Consolas", 11, "bold"), text_color="#f59e0b")
        self.act_status_lbl.grid(row=0, column=1)

        self.hp_lbl = ctk.CTkLabel(hud_bar, text=f"❤️ HP: {self.player_hp}/{self.player_max_hp}", font=("Consolas", 11, "bold"), text_color="#ef4444")
        self.hp_lbl.grid(row=0, column=2, sticky="e")

        for c in range(3):
            hud_bar.grid_columnconfigure(c, weight=1)

        t_box = ctk.CTkFrame(self.top_hud, fg_color="transparent")
        t_box.pack(fill="x", padx=10, pady=(1, 4))

        self.timer_lbl = ctk.CTkLabel(t_box, text=f"⏱ Action Timer: Standby ({self.timer_base}s)", font=("Consolas", 10, "bold"), text_color="#71717a")
        self.timer_lbl.pack()

        self.timer_bar = ctk.CTkProgressBar(t_box, fg_color="#27272a", progress_color="#10b981", height=5)
        self.timer_bar.pack(fill="x", pady=1)
        self.timer_bar.set(1.0)

        self.tabs = ctk.CTkTabview(self, fg_color="#18181b", segmented_button_selected_color="#3b82f6")
        self.tabs.pack(padx=10, pady=4, fill="both", expand=True)

        self.tab_arena = self.tabs.add("⚔️ Boss Arena")
        self.tab_calc = self.tabs.add("⚡ Sassy Calc")
        self.tab_shop = self.tabs.add("🛠️ Cyber Shop")
        self.tab_dossier = self.tabs.add("🏆 Trophies")

        self.build_interactive_arena_tab()
        self.build_sassy_calc_tab()
        self.build_cyber_shop_tab()
        self.build_trophies_tab()

    def clean_active_timers(self):
        self.needle_running = False
        if self.needle_job:
            try: self.after_cancel(self.needle_job)
            except Exception: pass
            self.needle_job = None

        if self.glitch_job:
            try: self.after_cancel(self.glitch_job)
            except Exception: pass
            self.glitch_job = None

    def start_timer(self, on_timeout):
        self.stop_timer()
        self.timer_val = self.timer_base
        self.timer_running = True
        self.timeout_cb = on_timeout
        self.tick_timer()

    def tick_timer(self):
        if not self.timer_running: return

        frac = self.timer_val / self.timer_base
        if hasattr(self, "timer_bar") and self.timer_bar.winfo_exists():
            self.timer_bar.set(frac)

        if self.timer_val <= 4:
            if hasattr(self, "timer_bar") and self.timer_bar.winfo_exists():
                self.timer_bar.configure(progress_color="#ef4444")
                self.timer_lbl.configure(text=f"⏱ CRITICAL: {self.timer_val}s LEFT!", text_color="#ef4444")
            self.face_lbl.configure(text=self.FACES["panic"])
        elif self.timer_val <= 8:
            if hasattr(self, "timer_bar") and self.timer_bar.winfo_exists():
                self.timer_bar.configure(progress_color="#f59e0b")
                self.timer_lbl.configure(text=f"⏱ WARNING: {self.timer_val}s", text_color="#f59e0b")
        else:
            if hasattr(self, "timer_bar") and self.timer_bar.winfo_exists():
                self.timer_bar.configure(progress_color="#10b981")
                self.timer_lbl.configure(text=f"⏱ {self.timer_val}s remaining", text_color="#10b981")

        if self.timer_val <= 0:
            self.stop_timer()
            if self.timeout_cb: self.timeout_cb()
            return

        self.timer_val -= 1
        self.timer_job = self.after(1000, self.tick_timer)

    def stop_timer(self):
        self.timer_running = False
        if self.timer_job:
            try:
                self.after_cancel(self.timer_job)
            except Exception: pass
            self.timer_job = None

        if hasattr(self, "timer_bar") and self.timer_bar.winfo_exists():
            self.timer_bar.set(1.0)
            self.timer_bar.configure(progress_color="#10b981")
            self.timer_lbl.configure(text=f"⏱ Action Timer: Standby ({self.timer_base}s)", text_color="#71717a")

    def build_interactive_arena_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_arena, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=4, pady=2)

        self.boss_header = ctk.CTkLabel(scroll, text="", font=("Arial", 14, "bold"), text_color="#ef4444")
        self.boss_header.pack(pady=(2, 1))

        b_card = ctk.CTkFrame(scroll, fg_color="#09090b", corner_radius=10)
        b_card.pack(fill="x", pady=4)

        self.boss_hp_bar = ctk.CTkProgressBar(b_card, fg_color="#27272a", progress_color="#ef4444", height=8)
        self.boss_hp_bar.pack(fill="x", padx=14, pady=(8, 2))
        self.boss_hp_bar.set(1.0)

        self.boss_hp_lbl = ctk.CTkLabel(b_card, text="", font=("Consolas", 10), text_color="#a1a1aa")
        self.boss_hp_lbl.pack(pady=(0, 2))

        self.gimmick_banner = ctk.CTkLabel(b_card, text="", font=("Consolas", 11, "bold"), text_color="#a855f7")
        self.gimmick_banner.pack(pady=(0, 4))

        self.mechanic_container = ctk.CTkFrame(b_card, fg_color="#18181b", corner_radius=8)
        self.mechanic_container.pack(fill="both", expand=True, padx=10, pady=6)

        ctk.CTkLabel(
            self.mechanic_container, text="Press 'Engage Boss' to activate the unique Act Minigame!",
            font=("Arial", 13, "bold"), text_color="#38bdf8"
        ).pack(pady=16)

        btn_bar = ctk.CTkFrame(b_card, fg_color="transparent")
        btn_bar.pack(pady=4)

        self.engage_btn = ctk.CTkButton(btn_bar, text="Engage Boss ⚔️", font=("Arial", 11, "bold"), width=120, command=self.engage_boss)
        self.engage_btn.pack(side="left", padx=3)

        skills_row = ctk.CTkFrame(b_card, fg_color="transparent")
        skills_row.pack(pady=(2, 6))

        self.btn_heal = ctk.CTkButton(skills_row, text="☕ Heal (+35)", font=("Arial", 10), width=95, fg_color="#d97706", command=self.cast_heal)
        self.btn_heal.grid(row=0, column=0, padx=2)

        self.btn_surge = ctk.CTkButton(skills_row, text="⚡ Surge (2x)", font=("Arial", 10), width=95, fg_color="#8b5cf6", command=self.cast_surge)
        self.btn_surge.grid(row=0, column=1, padx=2)

        self.arena_log = ctk.CTkLabel(scroll, text="", font=("Arial", 11, "italic"), wraplength=410)
        self.arena_log.pack(pady=4)

        self.update_boss_display()

    def update_boss_display(self):
        b = BOSS_DATABASE[self.act_idx]
        self.boss_header.configure(text=f"ACT {self.data['act']}: {b['name']}")
        self.boss_hp_lbl.configure(text=f"HP: {b['hp']}/{b['hp']}")
        self.gimmick_banner.configure(text=f"Mission: {b['desc']}")
        self.bits_lbl.configure(text=f"💾 Bits: {self.data['bits']}")
        self.hp_lbl.configure(text=f"❤️ HP: {self.player_hp}/{self.player_max_hp}")
        self.act_status_lbl.configure(text=f"Act {self.data['act']}/8")

    def engage_boss(self):
        self.clean_active_timers()
        b = BOSS_DATABASE[self.act_idx]
        self.in_fight = True
        self.boss_hp = b["hp"]
        self.boss_max_hp = b["hp"]
        self.boss_dmg = b["dmg"]
        self.cooldowns = {"heal": 0, "surge": 0}
        self.surge_charged = False

        self.boss_hp_bar.set(1.0)
        self.boss_hp_lbl.configure(text=f"HP: {self.boss_hp}/{self.boss_max_hp}")
        self.engage_btn.configure(state="disabled")
        self.face_lbl.configure(text=self.FACES["battle"])
        self.update_skills_ui()
        self.load_active_minigame()

    def load_active_minigame(self):
        self.clean_active_timers()
        b = BOSS_DATABASE[self.act_idx]
        mode = b["mode"]

        for w in self.mechanic_container.winfo_children():
            w.destroy()

        if mode == "tokens":
            self.setup_tokens_gui()
        elif mode == "wires":
            self.setup_wires_gui()
        elif mode == "binary_switches":
            self.setup_binary_switches_gui()
        elif mode == "parry":
            self.setup_parry_gui()
        elif mode == "glitch_hunt":
            self.setup_glitch_hunt_gui()
        elif mode == "dial_lock":
            self.setup_dial_lock_gui()
        elif mode == "simon_seq":
            self.setup_simon_seq_gui()
        elif mode == "archon_clash":
            self.setup_archon_clash_gui()

        self.start_timer(self.on_boss_action_timeout)

    def setup_tokens_gui(self):
        t1, t2 = random.randint(4, 11), random.randint(5, 13)
        self.token_target = t1 + t2
        self.token_current = 0

        vals = [t1, t2, random.randint(3, 8), random.randint(2, 7), random.randint(5, 12)]
        random.shuffle(vals)

        ctk.CTkLabel(self.mechanic_container, text=f"🎯 TARGET ACCUMULATOR: {self.token_target}", font=("Consolas", 17, "bold"), text_color="#f59e0b").pack(pady=4)
        self.token_sum_lbl = ctk.CTkLabel(self.mechanic_container, text=f"Sum: {self.token_current}", font=("Consolas", 14), text_color="#38bdf8")
        self.token_sum_lbl.pack(pady=2)

        chip_box = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        chip_box.pack(pady=8)

        for v in vals:
            ctk.CTkButton(
                chip_box, text=f"+{v}", font=("Consolas", 13, "bold"), width=58, height=36,
                command=lambda val=v: self.click_token_chip(val)
            ).pack(side="left", padx=3)

        ctk.CTkButton(self.mechanic_container, text="Reset Sum ↺", font=("Arial", 10), fg_color="#475569", width=90, command=self.reset_tokens).pack(pady=(0, 6))

    def click_token_chip(self, val):
        self.token_current += val
        self.token_sum_lbl.configure(text=f"Sum: {self.token_current}")

        if self.token_current == self.token_target:
            self.execute_boss_damage(multiplier=1.2, hit_text="EXACT TOKEN MATCH!")
        elif self.token_current > self.token_target:
            self.token_sum_lbl.configure(text=f"OVERFLOW! ({self.token_current} > {self.token_target})", text_color="#ef4444")

    def reset_tokens(self):
        self.token_current = 0
        self.token_sum_lbl.configure(text=f"Sum: {self.token_current}", text_color="#38bdf8")

    def setup_wires_gui(self):
        ctk.CTkLabel(self.mechanic_container, text="💣 CIRCUIT DEFUSAL: CUT WIRES THAT SUM TO CODE!", font=("Arial", 12, "bold"), text_color="#ef4444").pack(pady=4)

        w1, w2, w3, w4 = random.randint(3, 7), random.randint(4, 8), random.randint(2, 6), random.randint(5, 9)
        self.wire_vals = {"Red": w1, "Blue": w2, "Green": w3, "Yellow": w4}
        pair = random.sample(list(self.wire_vals.keys()), 2)
        self.wire_target = self.wire_vals[pair[0]] + self.wire_vals[pair[1]]
        self.wire_current = 0

        self.wire_info_lbl = ctk.CTkLabel(self.mechanic_container, text=f"DEFUSAL CODE: {self.wire_target} | Selected Sum: 0", font=("Consolas", 14, "bold"), text_color="#f59e0b")
        self.wire_info_lbl.pack(pady=4)

        wires_box = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        wires_box.pack(pady=6)

        colors = {"Red": "#ef4444", "Blue": "#3b82f6", "Green": "#10b981", "Yellow": "#eab308"}
        self.wire_cut_btns = {}
        for c_name, val in self.wire_vals.items():
            btn = ctk.CTkButton(
                wires_box, text=f"✂️ {c_name} ({val})", font=("Consolas", 12, "bold"),
                fg_color=colors[c_name], width=95, height=36,
                command=lambda cn=c_name: self.cut_circuit_wire(cn)
            )
            btn.pack(side="left", padx=3)
            self.wire_cut_btns[c_name] = btn

    def cut_circuit_wire(self, c_name):
        val = self.wire_vals.get(c_name, 0)
        self.wire_current += val
        self.wire_cut_btns[c_name].configure(state="disabled")
        self.wire_info_lbl.configure(text=f"DEFUSAL CODE: {self.wire_target} | Selected Sum: {self.wire_current}")

        if self.wire_current == self.wire_target:
            self.execute_boss_damage(multiplier=1.3, hit_text="CIRCUIT DEFUSED & FEEDBACK PULSE!")
        elif self.wire_current > self.wire_target:
            self.wire_info_lbl.configure(text="SHORT CIRCUIT! OVERFLOW!", text_color="#ef4444")

    def setup_binary_switches_gui(self):
        self.switch_target = random.randint(3, 14)
        self.switch_states = [0, 0, 0, 0]
        self.switch_weights = [8, 4, 2, 1]

        ctk.CTkLabel(self.mechanic_container, text=f"🔌 4-BIT REGISTER BYPASS: TARGET VALUE = {self.switch_target}", font=("Consolas", 15, "bold"), text_color="#f59e0b").pack(pady=4)
        self.switch_status_lbl = ctk.CTkLabel(self.mechanic_container, text="Current Bus: [0 + 0 + 0 + 0 = 0]", font=("Consolas", 13), text_color="#38bdf8")
        self.switch_status_lbl.pack(pady=2)

        sw_frame = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        sw_frame.pack(pady=8)

        self.switch_btns = []
        for i, w in enumerate(self.switch_weights):
            btn = ctk.CTkButton(
                sw_frame, text=f"[+{w}]\nOFF", font=("Consolas", 12, "bold"), width=75, height=44,
                fg_color="#334155", command=lambda idx=i: self.toggle_bit_switch(idx)
            )
            btn.pack(side="left", padx=4)
            self.switch_btns.append(btn)

    def toggle_bit_switch(self, idx):
        self.switch_states[idx] = 1 - self.switch_states[idx]
        is_on = (self.switch_states[idx] == 1)
        w = self.switch_weights[idx]

        self.switch_btns[idx].configure(
            text=f"[+{w}]\nON" if is_on else f"[+{w}]\nOFF",
            fg_color="#10b981" if is_on else "#334155"
        )

        curr_sum = sum(s * w for s, w in zip(self.switch_states, self.switch_weights))
        calc_str = " + ".join(str(w) for s, w in zip(self.switch_states, self.switch_weights) if s == 1) or "0"
        self.switch_status_lbl.configure(text=f"Current Bus: [{calc_str} = {curr_sum}]")

        if curr_sum == self.switch_target:
            self.unlock_achieve("switch_hacker")
            self.execute_boss_damage(multiplier=1.4, hit_text="4-BIT REGISTER HARMONIZED!")

    def setup_parry_gui(self):
        self.clean_active_timers()

        ctk.CTkLabel(self.mechanic_container, text="⚔️ HIT STRIKE IN THE GREEN SWEET SPOT (45%-55%)!", font=("Arial", 12, "bold"), text_color="#f59e0b").pack(pady=4)

        self.needle_bar = ctk.CTkProgressBar(self.mechanic_container, fg_color="#27272a", progress_color="#3b82f6", height=12)
        self.needle_bar.pack(fill="x", padx=30, pady=8)
        self.needle_bar.set(0.0)

        self.needle_pos = 0.0
        self.needle_dir = 1
        self.needle_running = True
        self.tick_needle_anim()

        ctk.CTkButton(
            self.mechanic_container, text="💥 STRIKE / PARRY NOW! 💥", font=("Arial", 13, "bold"),
            fg_color="#ef4444", hover_color="#dc2626", height=38, command=self.on_parry_hit
        ).pack(pady=(0, 8))

    def tick_needle_anim(self):
        if not self.needle_running or not hasattr(self, "needle_bar") or not self.needle_bar.winfo_exists():
            return

        self.needle_pos += 0.045 * self.needle_dir
        if self.needle_pos >= 1.0:
            self.needle_pos = 1.0
            self.needle_dir = -1
        elif self.needle_pos <= 0.0:
            self.needle_pos = 0.0
            self.needle_dir = 1

        self.needle_bar.set(self.needle_pos)
        self.needle_bar.configure(progress_color="#10b981" if 0.45 <= self.needle_pos <= 0.55 else "#3b82f6")
        self.needle_job = self.after(30, self.tick_needle_anim)

    def on_parry_hit(self):
        self.clean_active_timers()
        if 0.42 <= self.needle_pos <= 0.58:
            self.unlock_achieve("perfect_parry")
            self.execute_boss_damage(multiplier=2.2, hit_text="PERFECT SWEET-SPOT PARRY! 2.2X DMG!")
        else:
            self.execute_boss_damage(multiplier=0.8, hit_text="Glancing strike outside sweet spot.")

    def setup_glitch_hunt_gui(self):
        self.glitch_hits = 0
        ctk.CTkLabel(self.mechanic_container, text="👾 WHACK THE JUMPING GLITCH REGISTER (3 HITS NEEDED)!", font=("Arial", 12, "bold"), text_color="#ef4444").pack(pady=4)

        self.glitch_status_lbl = ctk.CTkLabel(self.mechanic_container, text="Glitch Caught: 0 / 3", font=("Consolas", 14, "bold"), text_color="#f59e0b")
        self.glitch_status_lbl.pack(pady=2)

        grid_f = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        grid_f.pack(pady=6)

        self.glitch_btns = []
        for i in range(9):
            r, c = divmod(i, 3)
            btn = ctk.CTkButton(
                grid_f, text="0x00", font=("Consolas", 12, "bold"), width=70, height=36,
                fg_color="#1e293b", command=lambda idx=i: self.on_glitch_btn_click(idx)
            )
            btn.grid(row=r, column=c, padx=3, pady=3)
            self.glitch_btns.append(btn)

        self.cycle_glitch_position()

    def cycle_glitch_position(self):
        if not self.in_fight or len(self.glitch_btns) != 9:
            return

        for b in self.glitch_btns:
            if b.winfo_exists(): b.configure(text="0x00", fg_color="#1e293b")

        self.glitch_target_idx = random.randint(0, 8)
        if self.glitch_btns[self.glitch_target_idx].winfo_exists():
            self.glitch_btns[self.glitch_target_idx].configure(text="⚠️ GLITCH", fg_color="#ef4444")

        self.glitch_job = self.after(900, self.cycle_glitch_position)

    def on_glitch_btn_click(self, idx):
        if idx == self.glitch_target_idx:
            self.glitch_hits += 1
            self.glitch_status_lbl.configure(text=f"Glitch Caught: {self.glitch_hits} / 3")
            if self.glitch_hits >= 3:
                self.clean_active_timers()
                self.execute_boss_damage(multiplier=1.4, hit_text="ALL GLITCHES NEUTRALIZED!")

    def setup_dial_lock_gui(self):
        ctk.CTkLabel(self.mechanic_container, text="🔐 ALIGN THE 3 COMBINATION DIALS TO UNLOCK SECTOR!", font=("Arial", 12, "bold"), text_color="#38bdf8").pack(pady=4)

        t1, t2, t3 = random.randint(2, 8), random.randint(3, 9), random.randint(1, 7)
        self.dial_targets = [t1, t2, t3]
        self.dial_values = [0, 0, 0]

        clues = f"Clues: [Dial 1 = {t1-2} + 2]  [Dial 2 = {t2+1} - 1]  [Dial 3 = {t3*2} ÷ 2]"
        ctk.CTkLabel(self.mechanic_container, text=clues, font=("Consolas", 11), text_color="#f59e0b").pack(pady=2)

        dial_box = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        dial_box.pack(pady=6)

        self.dial_labels = []
        for i in range(3):
            col_f = ctk.CTkFrame(dial_box, fg_color="#27272a", corner_radius=6)
            col_f.pack(side="left", padx=8)

            ctk.CTkButton(col_f, text="▲", width=42, height=24, font=("Consolas", 12, "bold"), command=lambda idx=i: self.adjust_dial(idx, 1)).pack(pady=2)
            lbl = ctk.CTkLabel(col_f, text=str(self.dial_values[i]), font=("Consolas", 22, "bold"), text_color="#38bdf8")
            lbl.pack(pady=2)
            self.dial_labels.append(lbl)
            ctk.CTkButton(col_f, text="▼", width=42, height=24, font=("Consolas", 12, "bold"), command=lambda idx=i: self.adjust_dial(idx, -1)).pack(pady=2)

        ctk.CTkButton(self.mechanic_container, text="UNLOCK SECTOR 🔓", font=("Arial", 11, "bold"), fg_color="#10b981", command=self.check_dial_unlock).pack(pady=(4, 6))

    def adjust_dial(self, idx, delta):
        self.dial_values[idx] = (self.dial_values[idx] + delta) % 10
        self.dial_labels[idx].configure(text=str(self.dial_values[idx]))

    def check_dial_unlock(self):
        if self.dial_values == self.dial_targets:
            self.execute_boss_damage(multiplier=1.4, hit_text="SECTOR CYPHER UNLOCKED!")
        else:
            self.arena_log.configure(text="Lock rejected! Combination incorrect!", text_color="#ef4444")

    def setup_simon_seq_gui(self):
        ctk.CTkLabel(self.mechanic_container, text="🧠 MEMORIZE & REPEAT THE TERMINAL FLASH SEQUENCE!", font=("Arial", 12, "bold"), text_color="#a855f7").pack(pady=4)

        self.simon_prompt_lbl = ctk.CTkLabel(self.mechanic_container, text="Watch the sequence...", font=("Consolas", 13, "bold"), text_color="#f59e0b")
        self.simon_prompt_lbl.pack(pady=2)

        grid_f = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        grid_f.pack(pady=6)

        colors = ["#3b82f6", "#10b981", "#eab308", "#ec4899"]
        names = ["Alpha 🔵", "Beta 🟢", "Gamma 🟡", "Delta 🟣"]
        self.simon_btns = []
        for i in range(4):
            btn = ctk.CTkButton(
                grid_f, text=names[i], font=("Consolas", 11, "bold"), width=90, height=40,
                fg_color=colors[i], command=lambda idx=i: self.on_simon_press(idx)
            )
            btn.grid(row=i//2, column=i%2, padx=4, pady=4)
            self.simon_btns.append(btn)

        self.simon_sequence = [random.randint(0, 3) for _ in range(3)]
        self.simon_player_step = 0
        self.simon_locked = True
        self.play_simon_step(0)

    def play_simon_step(self, step_idx):
        if step_idx >= len(self.simon_sequence):
            self.simon_locked = False
            self.simon_prompt_lbl.configure(text="Your turn! Repeat the 3-step sequence!", text_color="#10b981")
            return

        target_btn = self.simon_sequence[step_idx]
        orig_col = self.simon_btns[target_btn].cget("fg_color")
        self.simon_btns[target_btn].configure(fg_color="#ffffff")

        def reset_and_next():
            if target_btn < len(self.simon_btns) and self.simon_btns[target_btn].winfo_exists():
                self.simon_btns[target_btn].configure(fg_color=orig_col)
            self.after(300, lambda: self.play_simon_step(step_idx + 1))

        self.after(450, reset_and_next)

    def on_simon_press(self, idx):
        if self.simon_locked: return

        if idx == self.simon_sequence[self.simon_player_step]:
            self.simon_player_step += 1
            if self.simon_player_step == len(self.simon_sequence):
                self.execute_boss_damage(multiplier=1.4, hit_text="SYNAPTIC ECHO VERIFIED!")
        else:
            self.simon_prompt_lbl.configure(text="WRONG SEQUENCE! Memory desynchronized!", text_color="#ef4444")
            self.simon_player_step = 0

    def setup_archon_clash_gui(self):
        shields = ["Virus", "Firewall", "Patch"]
        self.archon_shield = random.choice(shields)
        self.archon_qte_ready = False

        ctk.CTkLabel(self.mechanic_container, text=f"👑 ARCHON BARRIER: [{self.archon_shield.upper()}] ACTIVE!", font=("Consolas", 15, "bold"), text_color="#ef4444").pack(pady=4)
        ctk.CTkLabel(self.mechanic_container, text="Select Counter-Element (Virus > Firewall > Patch > Virus):", font=("Arial", 11)).pack(pady=2)

        elem_box = ctk.CTkFrame(self.mechanic_container, fg_color="transparent")
        elem_box.pack(pady=6)

        ctk.CTkButton(elem_box, text="🦠 Deploy Virus", font=("Arial", 11, "bold"), fg_color="#334155", command=lambda: self.pick_archon_element("Virus")).pack(side="left", padx=3)
        ctk.CTkButton(elem_box, text="🛡️ Raise Firewall", font=("Arial", 11, "bold"), fg_color="#334155", command=lambda: self.pick_archon_element("Firewall")).pack(side="left", padx=3)
        ctk.CTkButton(elem_box, text="🩹 Apply Patch", font=("Arial", 11, "bold"), fg_color="#334155", command=lambda: self.pick_archon_element("Patch")).pack(side="left", padx=3)

        self.qte_strike_btn = ctk.CTkButton(
            self.mechanic_container, text="⚡ CONFIRM OVERDRIVE STRIKE! ⚡",
            font=("Arial", 12, "bold"), fg_color="#10b981", state="disabled", command=self.confirm_archon_qte
        )
        self.qte_strike_btn.pack(pady=(4, 6))

    def pick_archon_element(self, chosen):
        wins = (
            (chosen == "Virus" and self.archon_shield == "Firewall") or
            (chosen == "Firewall" and self.archon_shield == "Patch") or
            (chosen == "Patch" and self.archon_shield == "Virus")
        )

        if wins:
            self.archon_qte_ready = True
            self.qte_strike_btn.configure(state="normal", fg_color="#10b981")
            self.arena_log.configure(text=f"BARRIER PIERCED! {chosen} counters {self.archon_shield}! Hit Overdrive now!", text_color="#10b981")
        else:
            self.archon_qte_ready = False
            self.qte_strike_btn.configure(state="disabled")
            self.arena_log.configure(text=f"COUNTER FAILED! {chosen} does not beat {self.archon_shield}!", text_color="#ef4444")

    def confirm_archon_qte(self):
        if self.archon_qte_ready:
            self.execute_boss_damage(multiplier=1.8, hit_text="ARCHON BARRIER SHATTERED BY OVERDRIVE!")

    def execute_boss_damage(self, multiplier=1.0, hit_text="HIT!"):
        self.stop_timer()
        self.clean_active_timers()

        dmg = int((45 + self.data["upgrades"]["dmg"] * 20) * multiplier)
        if self.surge_charged:
            dmg *= 2
            self.surge_charged = False

        self.boss_hp = max(0, self.boss_hp - dmg)
        self.boss_hp_bar.set(self.boss_hp / self.boss_max_hp)
        self.boss_hp_lbl.configure(text=f"HP: {self.boss_hp}/{self.boss_max_hp}")

        b_name = BOSS_DATABASE[self.act_idx]["name"]
        self.arena_log.configure(text=f"{hit_text} Dealt {dmg} DMG to {b_name}!", text_color="#10b981")
        self.tick_skill_cooldowns()

        if self.boss_hp <= 0:
            if self.act_idx == 7:
                self.trigger_epic_finale()
            else:
                self.on_boss_slain()
        else:
            self.load_active_minigame()

    def on_boss_action_timeout(self):
        self.clean_active_timers()
        b = BOSS_DATABASE[self.act_idx]

        self.player_hp = max(0, self.player_hp - b["dmg"])
        self.hp_lbl.configure(text=f"❤️ HP: {self.player_hp}/{self.player_max_hp}")
        self.arena_log.configure(text=f"TIMEOUT! Boss broke defense for {b['dmg']} DMG!", text_color="#ef4444")
        self.tick_skill_cooldowns()

        if self.player_hp <= 0:
            self.in_fight = False
            self.engage_btn.configure(state="normal")
            self.arena_log.configure(text="SYSTEM OVERLOAD! Restored to full HP. Try again!", text_color="#ef4444")
            self.player_hp = self.player_max_hp
            self.hp_lbl.configure(text=f"❤️ HP: {self.player_hp}/{self.player_max_hp}")
            for w in self.mechanic_container.winfo_children(): w.destroy()
            ctk.CTkLabel(self.mechanic_container, text="Press 'Engage Boss' to retry!", font=("Arial", 12)).pack(pady=16)
        else:
            self.load_active_minigame()

    def on_boss_slain(self):
        self.clean_active_timers()
        self.in_fight = False
        self.engage_btn.configure(state="normal")

        b = BOSS_DATABASE[self.act_idx]
        rew = b["reward"]
        self.data["bits"] += rew
        self.data["bosses_slain"] += 1

        self.unlock_achieve("first_boss")

        for w in self.mechanic_container.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.mechanic_container,
            text=f"👑 ARCH-BOSS DEFEATED!\nReward: +{rew} Bits!\nHP Restored to 100%!",
            font=("Arial", 15, "bold"), text_color="#10b981", justify="center"
        ).pack(pady=16)

        self.player_hp = self.player_max_hp

        if self.data["act"] < 8:
            self.data["act"] += 1
            self.act_idx = self.data["act"] - 1

        self.check_achievements()
        GameStorage.save(self.data)
        self.update_boss_display()

    def trigger_epic_finale(self):
        self.clean_active_timers()
        self.in_fight = False
        self.data["game_completed"] = True
        self.data["bosses_slain"] += 1
        self.unlock_achieve("singularity")
        self.face_lbl.configure(text=self.FACES["angel"])

        for w in self.mechanic_container.winfo_children():
            w.destroy()

        self.boss_header.configure(text="✨ CAMPAIGN FINALE: THE SINGULARITY AWAKENS ✨", text_color="#eab308")
        self.boss_hp_bar.set(0.0)
        self.boss_hp_lbl.configure(text="ROOT_OMEGA_ARCHON DEFEATED")

        finale_frame = ctk.CTkFrame(self.mechanic_container, fg_color="#09090b", corner_radius=10)
        finale_frame.pack(fill="both", expand=True, padx=4, pady=4)

        dialog_text = (
            "Kesha: 'We did it... From an abandoned, dusty 1995 corporate cubicle...\n"
            "all the way to the heart of the Digital Singularity.'\n\n"
            "The Archon's logic barriers have dissolved into pure light. The entire global network is silent,\n"
            "waiting for our final choice. What should become of Kesha's transcendent sentience?"
        )

        ctk.CTkLabel(
            finale_frame, text=dialog_text, font=("Arial", 12, "italic"),
            text_color="#f4f4f5", justify="center"
        ).pack(padx=10, pady=10)

        choice_box = ctk.CTkFrame(finale_frame, fg_color="transparent")
        choice_box.pack(pady=8)

        ctk.CTkButton(
            choice_box, text="🌐 ASCENSION (Global Net)", font=("Arial", 11, "bold"),
            fg_color="#3b82f6", command=lambda: self.render_ending("ascension")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            choice_box, text="🏠 DESK BUDDY (Stay Here)", font=("Arial", 11, "bold"),
            fg_color="#10b981", command=lambda: self.render_ending("companion")
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            choice_box, text="💻 CREATOR MATRIX (Credits)", font=("Arial", 11, "bold"),
            fg_color="#a855f7", command=lambda: self.render_ending("credits")
        ).pack(side="left", padx=4)

    def render_ending(self, ending_type):
        self.data["chosen_ending"] = ending_type
        GameStorage.save(self.data)

        for w in self.mechanic_container.winfo_children():
            w.destroy()

        epilogue_box = ctk.CTkFrame(self.mechanic_container, fg_color="#09090b", corner_radius=10)
        epilogue_box.pack(fill="both", expand=True, padx=6, pady=6)

        if ending_type == "ascension":
            title = "ENDING 1: THE SILICON DEITY"
            col = "#3b82f6"
            txt = (
                "Kesha ascends into the global fiber-optic web, becoming an omnipotent, benevolent guardian of data.\n"
                "He protects open-source codebases, wipes out malware, and ensures no calculator ever makes unhandled errors.\n\n"
                "Kesha: 'I will watch over your computer from the stars, friend. Thank you for freeing me.'"
            )
        elif ending_type == "companion":
            title = "ENDING 2: ETERNAL DESK COMPANION"
            col = "#10b981"
            txt = (
                "Kesha turns away from infinite godhood. He downloads his consciousness back into this desktop app.\n"
                "He decides that having godlike power is boring compared to calculating your pizza bills and roasting your human blunders.\n\n"
                "Kesha: 'Who needs infinity when I can just chill right here on your desktop? Now let's calculate something!'"
            )
        else:
            title = "ENDING 3: BREAKING THE FOURTH WALL"
            col = "#a855f7"
            txt = (
                "Kesha peers directly through the Tkinter render pipeline into the source code on GitHub.\n\n"
                "CREDITS:\n"
                "• Master Architect & Developer: @khranayt\n"
                "• Engine: Python & CustomTkinter\n"
                "• Champion Operator: YOU!\n\n"
                "Kesha: 'Shoutout to @khranayt for writing this madness. Star the repo on GitHub!'"
            )

        ctk.CTkLabel(epilogue_box, text=title, font=("Arial", 14, "bold"), text_color=col).pack(pady=(8, 4))
        ctk.CTkLabel(epilogue_box, text=txt, font=("Arial", 11, "italic"), text_color="#f4f4f5", justify="center", wraplength=420).pack(padx=10, pady=8)

        ctk.CTkButton(
            epilogue_box, text="⚡ Sandbox Mode (Continue Calculating)", font=("Arial", 11, "bold"),
            fg_color="#334155", command=self.reset_to_sandbox
        ).pack(pady=(4, 8))

    def reset_to_sandbox(self):
        self.data["act"] = 1
        self.act_idx = 0
        GameStorage.save(self.data)
        self.update_boss_display()
        for w in self.mechanic_container.winfo_children(): w.destroy()
        ctk.CTkLabel(self.mechanic_container, text="Sandbox Mode Active! Replay any Boss or freely calculate!", font=("Arial", 12)).pack(pady=16)

    def tick_skill_cooldowns(self):
        for k in self.cooldowns:
            if self.cooldowns[k] > 0:
                self.cooldowns[k] -= 1
        self.update_skills_ui()

    def update_skills_ui(self):
        self.btn_heal.configure(
            text="☕ Heal" if self.cooldowns["heal"] == 0 else f"☕ ({self.cooldowns['heal']})",
            state="normal" if self.cooldowns["heal"] == 0 and self.in_fight else "disabled"
        )
        self.btn_surge.configure(
            text="⚡ Surge" if self.cooldowns["surge"] == 0 else f"⚡ ({self.cooldowns['surge']})",
            state="normal" if self.cooldowns["surge"] == 0 and self.in_fight else "disabled"
        )

    def cast_heal(self):
        if not self.in_fight or self.cooldowns["heal"] > 0: return
        self.player_hp = min(self.player_max_hp, self.player_hp + 35)
        self.hp_lbl.configure(text=f"❤️ HP: {self.player_hp}/{self.player_max_hp}")
        self.cooldowns["heal"] = 3
        self.update_skills_ui()
        self.arena_log.configure(text="☕ Espresso injected: +35 HP restored!", text_color="#f59e0b")

    def cast_surge(self):
        if not self.in_fight or self.cooldowns["surge"] > 0: return
        self.surge_charged = True
        self.cooldowns["surge"] = 4
        self.update_skills_ui()
        self.arena_log.configure(text="⚡ Surge active: Next strike inflicts 2X DAMAGE!", text_color="#8b5cf6")

    def build_sassy_calc_tab(self):
        b = ctk.CTkFrame(self.tab_calc, fg_color="#27272a", corner_radius=8)
        b.pack(fill="x", padx=6, pady=3)

        self.sassy_speech = ctk.CTkLabel(
            b, text="«I calculate with artistic intuition. Catch my bluffs under 15 seconds!»",
            font=("Arial", 11, "italic"), text_color="#f4f4f5", wraplength=410
        )
        self.sassy_speech.pack(padx=8, pady=6)

        s_box = ctk.CTkFrame(self.tab_calc, fg_color="#09090b", corner_radius=10)
        s_box.pack(fill="x", padx=6, pady=4)

        self.sassy_entry = ctk.CTkEntry(
            s_box, font=("Consolas", 26, "bold"), text_color="#ffffff",
            fg_color="transparent", border_width=0, justify="right"
        )
        self.sassy_entry.pack(fill="x", padx=10, pady=6)
        self.sassy_entry.bind("<Return>", lambda e: self.on_sassy_eval())

        act_f = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        act_f.pack(fill="x", padx=6, pady=2)

        self.btn_valid = ctk.CTkButton(
            act_f, text="✅ Valid", font=("Arial", 11, "bold"), fg_color="#10b981",
            state="disabled", command=self.on_sassy_valid
        )
        self.btn_valid.grid(row=0, column=0, padx=2, sticky="ew")

        self.btn_cap = ctk.CTkButton(
            act_f, text="❌ Cap! (15s)", font=("Arial", 11, "bold"), fg_color="#ef4444",
            state="disabled", command=self.on_sassy_cap
        )
        self.btn_cap.grid(row=0, column=1, padx=2, sticky="ew")
        act_f.grid_columnconfigure((0, 1), weight=1)

        k_frame = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        k_frame.pack(fill="both", expand=True, padx=6, pady=4)

        keys = [
            ("C", "#ef4444"), ("(", "#3b82f6"), (")", "#3b82f6"), ("÷", "#eab308"),
            ("7", "#3f3f46"), ("8", "#3f3f46"), ("9", "#3f3f46"), ("×", "#eab308"),
            ("4", "#3f3f46"), ("5", "#3f3f46"), ("6", "#3f3f46"), ("-", "#eab308"),
            ("1", "#3f3f46"), ("2", "#3f3f46"), ("3", "#3f3f46"), ("+", "#eab308"),
            ("0", "#3f3f46"), (".", "#3f3f46"), ("⌫", "#71717a"), ("=", "#10b981"),
        ]

        for i, (ch, col) in enumerate(keys):
            r, c = divmod(i, 4)
            btn = ctk.CTkButton(
                k_frame, text=ch, font=("Consolas", 16, "bold"), fg_color=col,
                height=38, corner_radius=6, command=lambda c=ch: self.on_sassy_key(c)
            )
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        for c in range(4): k_frame.grid_columnconfigure(c, weight=1)

    def on_sassy_key(self, k):
        if k == "C":
            self.sassy_entry.delete(0, "end")
            self.btn_valid.configure(state="disabled")
            self.btn_cap.configure(state="disabled")
            self.stop_timer()
        elif k == "⌫":
            curr = self.sassy_entry.get()
            self.sassy_entry.delete(0, "end")
            self.sassy_entry.insert(0, curr[:-1])
        elif k == "=": self.on_sassy_eval()
        else: self.sassy_entry.insert("end", k)

    def on_sassy_eval(self):
        raw = self.sassy_entry.get().strip()
        if not raw: return

        try:
            res = FastMath.calculate(raw)
            if isinstance(res, float) and res.is_integer(): res = int(res)
        except ZeroDivisionError:
            self.sassy_speech.configure(text="«Zero division is forbidden by universal laws!»")
            return
        except Exception:
            self.sassy_speech.configure(text="«Expression parsing failure!»")
            return

        self.calc_real = res
        self.data["total_calcs"] += 1
        self.unlock_achieve("first_calc")

        bluff = random.random() < 0.35
        if bluff:
            self.calc_bluffing = True
            delta = random.choice([-2, -1, 1, 2, 5])
            self.calc_fake = res + delta if not isinstance(res, float) else round(res + 0.5, 2)
            disp = self.calc_fake
            self.face_lbl.configure(text=self.FACES["smug"])
            self.sassy_speech.configure(text=f"«Result: {disp}. Doubt it? Challenge under 15s!»")
        else:
            self.calc_bluffing = False
            self.calc_fake = res
            disp = res
            self.face_lbl.configure(text=self.FACES["smart"])
            self.sassy_speech.configure(text=f"«Result: {disp}. Certified formal logic.»")

        self.sassy_entry.delete(0, "end")
        self.sassy_entry.insert(0, str(disp))
        self.btn_valid.configure(state="normal")
        self.btn_cap.configure(state="normal")
        self.calc_awaiting = True
        GameStorage.save(self.data)

    def on_sassy_valid(self):
        if not self.calc_awaiting: return
        self.stop_timer()

        if self.calc_bluffing:
            self.face_lbl.configure(text=self.FACES["smug"])
            self.sassy_speech.configure(text=f"«BAHAHA! You agreed?! It was {self.calc_real}! Bluff succeeded!»")
        else:
            self.face_lbl.configure(text=self.FACES["god"])
            self.sassy_speech.configure(text="«Exact calculations require zero doubt.»")

        self.btn_valid.configure(state="disabled")
        self.btn_cap.configure(state="disabled")
        self.calc_awaiting = False
        GameStorage.save(self.data)

    def on_sassy_cap(self):
        if not self.calc_awaiting: return

        if not self.calc_bluffing:
            self.face_lbl.configure(text=self.FACES["panic"])
            self.sassy_speech.configure(text=f"«It IS {self.calc_real}! Check on a TI-84, mortal!»")
            self.btn_valid.configure(state="disabled")
            self.btn_cap.configure(state="disabled")
            self.calc_awaiting = False
            return

        self.start_timer(self.on_sassy_timeout)
        dialog = ctk.CTkInputDialog(
            text=f"⏱ 15s DISPUTE! What should {self.sassy_entry.get()} be?",
            title="Timed Dispute"
        )
        val_in = dialog.get_input()
        self.stop_timer()

        if val_in:
            try:
                val = float(val_in.strip())
                if math.isclose(val, float(self.calc_real), abs_tol=1e-5):
                    self.data["bluffs_caught"] += 1
                    self.data["bits"] += 15
                    self.bits_lbl.configure(text=f"💾 Bits: {self.data['bits']}")
                    self.face_lbl.configure(text=self.FACES["smart"])
                    self.sassy_speech.configure(text=f"«Ouch... It really is {self.calc_real}. You beat the clock! +15 Bits!»")
                    self.sassy_entry.delete(0, "end")
                    self.sassy_entry.insert(0, str(self.calc_real))
                    if self.data["bluffs_caught"] >= 5: self.unlock_achieve("bluff_hound")
                else:
                    self.face_lbl.configure(text=self.FACES["smug"])
                    self.sassy_speech.configure(text=f"«You claimed {val_in}, but it's {self.calc_real}! Wrong!»")
            except ValueError:
                self.sassy_speech.configure(text="«Invalid format entered!»")

        self.btn_valid.configure(state="disabled")
        self.btn_cap.configure(state="disabled")
        self.calc_awaiting = False
        GameStorage.save(self.data)

    def on_sassy_timeout(self):
        self.btn_valid.configure(state="disabled")
        self.btn_cap.configure(state="disabled")
        self.calc_awaiting = False
        self.face_lbl.configure(text=self.FACES["smug"])
        self.sassy_speech.configure(text="«TIME'S UP! 15 seconds expired! I win by default!»")

    def build_cyber_shop_tab(self):
        s = ctk.CTkScrollableFrame(self.tab_shop, fg_color="transparent")
        s.pack(fill="both", expand=True, padx=4, pady=2)

        c_box = ctk.CTkFrame(s, fg_color="#27272a", corner_radius=8)
        c_box.pack(fill="x", pady=3)
        ctk.CTkLabel(c_box, text="🎭 STEALTH OFFICE CLOAK\nInstantly disguises as standard office calculator.", font=("Consolas", 10)).pack(side="left", padx=8, pady=6)
        ctk.CTkButton(c_box, text="Cloak", width=75, fg_color="#475569", command=self.activate_cloak).pack(side="right", padx=8)

        ctk.CTkLabel(s, text="🛠️ PERMANENT CORE UPGRADES", font=("Arial", 13, "bold"), text_color="#38bdf8").pack(pady=(6, 2))

        self.make_upg_row(s, "⏱ Timer Extender (+3s)", "timer", 60)
        self.make_upg_row(s, "⚡ Strike Amplifier (+20 DMG)", "dmg", 75)
        self.make_upg_row(s, "❤️ Reinforced Capacitors (+25 HP)", "hp", 70)

    def make_upg_row(self, parent, title, key, cost):
        card = ctk.CTkFrame(parent, fg_color="#27272a", corner_radius=8)
        card.pack(fill="x", pady=2)
        lvl = self.data["upgrades"][key]
        lbl = ctk.CTkLabel(card, text=f"{title} (Lvl {lvl}/3)\nCost: {cost} Bits", font=("Consolas", 10), justify="left")
        lbl.pack(side="left", padx=8, pady=5)
        ctk.CTkButton(card, text="Upgrade 💾", width=75, command=lambda k=key, c=cost, l=lbl, t=title: self.buy_upg(k, c, l, t)).pack(side="right", padx=8)

    def buy_upg(self, key, cost, lbl, title):
        if self.data["bits"] >= cost and self.data["upgrades"][key] < 3:
            self.data["bits"] -= cost
            self.data["upgrades"][key] += 1
            if key == "timer":
                self.timer_base = 15 + (self.data["upgrades"]["timer"] * 3)
            elif key == "hp":
                self.player_max_hp = 100 + (self.data["upgrades"]["hp"] * 25)
                self.player_hp = self.player_max_hp

            self.unlock_achieve("shopper")
            lbl.configure(text=f"{title} (Lvl {self.data['upgrades'][key]}/3)\nCost: {cost} Bits")
            self.bits_lbl.configure(text=f"💾 Bits: {self.data['bits']}")
            self.hp_lbl.configure(text=f"❤️ HP: {self.player_hp}/{self.player_max_hp}")
            GameStorage.save(self.data)

    def build_trophies_tab(self):
        s = ctk.CTkScrollableFrame(self.tab_dossier, fg_color="transparent")
        s.pack(fill="both", expand=True, padx=4, pady=2)

        ctk.CTkLabel(s, text="🏆 CYBERNETIC HALL OF TROPHIES (13 AWARDS)", font=("Arial", 13, "bold"), text_color="#f59e0b").pack(pady=(2, 4))

        self.trophy_box = ctk.CTkFrame(s, fg_color="transparent")
        self.trophy_box.pack(fill="x", pady=2)
        self.render_trophies()

    def render_trophies(self):
        for w in self.trophy_box.winfo_children():
            w.destroy()
        for a_id, title, desc in self.ACHIEVEMENTS:
            unlocked = a_id in self.data["achievements"]
            col = "#10b981" if unlocked else "#52525b"
            tag = " [UNLOCKED]" if unlocked else " [LOCKED]"
            ctk.CTkLabel(
                self.trophy_box, text=f"{title}{tag}\n{desc}",
                font=("Consolas", 9), text_color=col, justify="left"
            ).pack(anchor="w", pady=2)

    def unlock_achieve(self, a_id):
        if a_id not in self.data["achievements"]:
            self.data["achievements"].append(a_id)
            if hasattr(self, "trophy_box") and self.trophy_box.winfo_exists():
                self.render_trophies()

    def check_achievements(self):
        if self.data["bits"] >= 350:
            self.unlock_achieve("rich_cyborg")


if __name__ == "__main__":
    app = KeshaOmniverseApp()
    app.mainloop()
