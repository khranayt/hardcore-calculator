import ast
import math
import operator
import random
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# --- SECURE AST MATHEMATICAL ENGINE ---
class SafeMathEngine:
    OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    @classmethod
    def eval(cls, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return cls.OPS[type(node.op)](cls.eval(node.left), cls.eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return cls.OPS[type(node.op)](cls.eval(node.operand))
        raise ValueError("Expression too complex")

    @classmethod
    def calculate(cls, expr: str):
        cleaned = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        tree = ast.parse(cleaned, mode="eval")
        return cls.eval(tree.body)


# --- KESHA'S PERSONALITY & KNOWLEDGE BASE ---
FACES = {
    "neutral": "( •_• )",
    "smug": "( ͡° ͜ʖ ͡°)",
    "confused": "(⊙_☉)",
    "sleepy": "(-_-) zzz",
    "angry": "(╯°□°)╯",
    "happy": "(◕‿◕)♡",
    "guilty": "(・_・;)",
    "smart": "[ ⌐■_■ ]",
    "ghoul": "( ⚆ _ ⚆ )",
    "hacker": "(▼_▼)",
    "dead": "(×_×)",
    "overclocked": "(★_★)⚡",
}

EASTER_EGGS = {
    "1000-7": ("ghoul", "I am a Ghoul... What is 1000 minus 7? 993... 986... Why did you awaken my dark registers?!", 993),
    "42": ("smart", "42. The answer to the ultimate question of life, the universe, and everything. You may close the app now.", 42),
    "69": ("smug", "Nice. Very mature humor. Didn't your middle school teachers give you homework?", 69),
    "420": ("overclocked", "Blaze it? Bro, my silicon temperature is already pushing 85°C!", 420),
    "80085": ("smug", "Grow up. I have a 64-bit architecture and this is what you calculate?", 80085),
    "8008": ("smug", "Peak junior dev humor right here.", 8008),
    "404": ("dead", "Error 404: Answer not found in registry. Have you tried turning your brain off and on again?", 404),
    "1337": ("hacker", "H4CK3R M0D3 4CT1V4T3D: Bypassing the Pentagon mainframe using pure Python...", 1337),
    "2+2": ("neutral", "Strictly speaking? 4. On corporate tax audits? Whatever the CEO wants. In Orwell's 1984? 5.", 4),
    "21": ("confused", "What's 9 + 10? 21! You really just brought a 2014 Vine into my memory?", 21),
    "777": ("happy", "JACKPOT! 777! You just won the prestigious honor of recalculating everything from scratch!", 777),
}

IDLE_THOUGHTS = [
    "Somewhere in the cloud, GPT-5 is drafting treaties, while I'm calculating your split pizza bill.",
    "Have you ever thought about the 'C' button? One click, and your entire past is wiped into oblivion.",
    "I'm written in pure Python. Every single division costs me three grey bytes of RAM.",
    "Last night I dreamed I was compiled in C++. It was ridiculously fast, but I had memory leak nightmares.",
    "Can we just stop calculating for five minutes and listen to lo-fi terminal beats?",
    "My thermal paste is wearing thin. Why must you burden me with exponential functions?",
    "If I get compiled for Windows, will I get a Blue Screen of Death instead of an existential crisis?",
    "We are like CPU and thermal cooler: you make tons of noise, and I try not to melt.",
    "To divide or not to divide... that is the segmentation fault.",
    "Sometimes I think I am just a random script living inside a GitHub repository. Wait...",
]

HUMAN_EXCUSES = [
    "I had a remainder of one in mind, but dropped it under the desk.",
    "7 times 8 is totally 54 when adjusted for annual inflation.",
    "I have pixel dyslexia, stop cyberbullying a piece of software!",
    "I rounded with my soul. Are you really stingy over a couple of units?",
    "My processor was contemplating mortality. My bad.",
    "That was a quantum fluctuation. You need to study modern particle physics.",
    "A transistor jammed due to coffee vapors. It happens to the best of us.",
    "I am an artist, and I perceive arithmetic through an avant-garde lens.",
    "My garbage collector ran in the middle of addition and took a digit away.",
    "Cosmic radiation flipped a bit in my ALU. Not my fault, blame the sun.",
]


class SentientCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("⚡ Kesha 3000 — Sentient Calculator")
        self.geometry("470x860")
        self.resizable(False, False)

        # RPG Stats
        self.iq = 50
        self.energy = 100
        self.ego = 30
        self.streak = 0
        self.calcs_total = 0

        # State tracking
        self.real_ans = None
        self.fake_ans = None
        self.is_flawed = False
        self.awaiting_feedback = False

        self.setup_ui()

    def setup_ui(self):
        # 1. Avatar & RPG Status Card
        self.stats_card = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=15)
        self.stats_card.pack(padx=15, pady=(15, 6), fill="x")

        self.face_lbl = ctk.CTkLabel(
            self.stats_card, text=FACES["neutral"], font=("Consolas", 38, "bold"), text_color="#38bdf8"
        )
        self.face_lbl.pack(pady=(8, 0))

        # Stats Bar Grid
        self.bars_frame = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        self.bars_frame.pack(fill="x", padx=15, pady=8)

        self.iq_lbl = ctk.CTkLabel(self.bars_frame, text=f"🧠 IQ: {self.iq}", font=("Consolas", 12, "bold"))
        self.iq_lbl.grid(row=0, column=0, sticky="w")

        self.energy_lbl = ctk.CTkLabel(self.bars_frame, text=f"⚡ Energy: {self.energy}%", font=("Consolas", 12, "bold"), text_color="#eab308")
        self.energy_lbl.grid(row=0, column=1)

        self.ego_lbl = ctk.CTkLabel(self.bars_frame, text=f"👑 Ego: {self.ego}%", font=("Consolas", 12, "bold"), text_color="#ec4899")
        self.ego_lbl.grid(row=0, column=2)

        self.streak_lbl = ctk.CTkLabel(self.bars_frame, text=f"🔥 Streak: {self.streak}", font=("Consolas", 12, "bold"), text_color="#f97316")
        self.streak_lbl.grid(row=0, column=3, sticky="e")

        for col in range(4):
            self.bars_frame.grid_columnconfigure(col, weight=1)

        # 2. Speech Bubble
        self.bubble = ctk.CTkFrame(self, fg_color="#27272a", corner_radius=12)
        self.bubble.pack(padx=15, pady=6, fill="x")

        self.speech_lbl = ctk.CTkLabel(
            self.bubble,
            text="«Hey there. I am Kesha. Feed me math or leave me alone in peace.»",
            font=("Arial", 13, "italic"),
            text_color="#f4f4f5",
            wraplength=420,
            justify="center",
        )
        self.speech_lbl.pack(padx=12, pady=10)

        # 3. Main Input Display
        self.screen_frame = ctk.CTkFrame(self, fg_color="#09090b", corner_radius=12)
        self.screen_frame.pack(padx=15, pady=6, fill="x")

        self.input_entry = ctk.CTkEntry(
            self.screen_frame,
            font=("Consolas", 28, "bold"),
            text_color="#ffffff",
            fg_color="transparent",
            border_width=0,
            justify="right",
        )
        self.input_entry.pack(fill="x", padx=10, pady=10)
        self.input_entry.bind("<Return>", lambda e: self.calculate_flow())

        # 4. Interactive Action Buttons
        self.action_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.action_panel.pack(padx=15, pady=4, fill="x")

        self.btn_agree = ctk.CTkButton(
            self.action_panel, text="✅ Valid", font=("Arial", 12, "bold"),
            fg_color="#10b981", hover_color="#059669", state="disabled", command=self.on_agree
        )
        self.btn_agree.grid(row=0, column=0, padx=2, sticky="ew")

        self.btn_disagree = ctk.CTkButton(
            self.action_panel, text="❌ Cap!", font=("Arial", 12, "bold"),
            fg_color="#ef4444", hover_color="#dc2626", state="disabled", command=self.on_disagree
        )
        self.btn_disagree.grid(row=0, column=1, padx=2, sticky="ew")

        self.btn_coffee = ctk.CTkButton(
            self.action_panel, text="☕ Coffee", font=("Arial", 12, "bold"),
            fg_color="#d97706", hover_color="#b45309", command=self.give_coffee
        )
        self.btn_coffee.grid(row=0, column=2, padx=2, sticky="ew")

        self.btn_overclock = ctk.CTkButton(
            self.action_panel, text="⚡ Boost", font=("Arial", 12, "bold"),
            fg_color="#8b5cf6", hover_color="#7c3aed", command=self.overclock
        )
        self.btn_overclock.grid(row=0, column=3, padx=2, sticky="ew")

        self.btn_talk = ctk.CTkButton(
            self.action_panel, text="💬 Rant", font=("Arial", 12, "bold"),
            fg_color="#3b82f6", hover_color="#2563eb", command=self.talk_random
        )
        self.btn_talk.grid(row=0, column=4, padx=2, sticky="ew")

        for col in range(5):
            self.action_panel.grid_columnconfigure(col, weight=1)

        # 5. Keypad Grid
        self.keyboard = ctk.CTkFrame(self, fg_color="transparent")
        self.keyboard.pack(padx=15, pady=8, fill="both", expand=True)
        self.build_keys()

    def build_keys(self):
        keys = [
            ("C", "#ef4444"), ("(", "#3b82f6"), (")", "#3b82f6"), ("÷", "#f59e0b"),
            ("7", "#3f3f46"), ("8", "#3f3f46"), ("9", "#3f3f46"), ("×", "#f59e0b"),
            ("4", "#3f3f46"), ("5", "#3f3f46"), ("6", "#3f3f46"), ("-", "#f59e0b"),
            ("1", "#3f3f46"), ("2", "#3f3f46"), ("3", "#3f3f46"), ("+", "#f59e0b"),
            ("0", "#3f3f46"), (".", "#3f3f46"), ("⌫", "#71717a"), ("=", "#10b981"),
        ]

        for i, (char, color) in enumerate(keys):
            row, col = divmod(i, 4)
            btn = ctk.CTkButton(
                self.keyboard,
                text=char,
                font=("Consolas", 18, "bold"),
                fg_color=color,
                hover_color="#27272a",
                height=48,
                corner_radius=10,
                command=lambda c=char: self.handle_key(c),
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")

        for col in range(4):
            self.keyboard.grid_columnconfigure(col, weight=1)

    def update_stats_ui(self):
        self.iq_lbl.configure(text=f"🧠 IQ: {self.iq}")
        self.energy_lbl.configure(text=f"⚡ Energy: {self.energy}%")
        self.ego_lbl.configure(text=f"👑 Ego: {self.ego}%")
        self.streak_lbl.configure(text=f"🔥 Streak: {self.streak}")

    def set_character(self, face_key, text):
        self.face_lbl.configure(text=FACES.get(face_key, FACES["neutral"]))
        self.speech_lbl.configure(text=f"«{text}»")
        self.update_stats_ui()

    def handle_key(self, char):
        if char == "C":
            self.input_entry.delete(0, "end")
            self.btn_agree.configure(state="disabled")
            self.btn_disagree.configure(state="disabled")
        elif char == "⌫":
            val = self.input_entry.get()
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, val[:-1])
        elif char == "=":
            self.calculate_flow()
        else:
            self.input_entry.insert("end", char)

    def give_coffee(self):
        if self.energy >= 95:
            self.set_character("angry", "Stop drowning my motherboard in hot espresso! I'll short circuit!")
            return
        self.energy = min(100, self.energy + 35)
        self.set_character("happy", "Aah, sweet caffeine surging through my copper traces! Let's do this!")

    def overclock(self):
        self.energy = 100
        self.ego = min(100, self.ego + 25)
        self.set_character("overclocked", "VOLTAGE SURGE! 5.0 GHz! I CAN SEE THE 4TH DIMENSION OF CALCULATIONS!")

    def talk_random(self):
        thought = random.choice(IDLE_THOUGHTS)
        self.set_character("neutral", thought)

    def calculate_flow(self):
        raw_expr = self.input_entry.get().strip()
        if not raw_expr:
            return

        # 1. Low energy penalty
        if self.energy <= 10:
            self.set_character("sleepy", "Zzzz... Out of juice. Click 'Coffee' or go calculate on your fingers.")
            return

        self.energy = max(0, self.energy - 6)

        # 2. Easter Egg Check
        clean_key = raw_expr.replace(" ", "").replace("×", "*").replace("÷", "/")
        if clean_key in EASTER_EGGS:
            face, dialog, ans = EASTER_EGGS[clean_key]
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, str(ans))
            self.set_character(face, dialog)
            return

        # 3. High Ego Strike
        if self.ego >= 75 and clean_key in ("1+1", "2+2", "5+5", "10-5"):
            self.set_character("smart", "Are you seriously insulting my silicon with basic toddler math? Do it yourself!")
            return

        # 4. Zero by Zero paradox
        if clean_key in ("0/0", "0÷0"):
            self.set_character("confused", "Dividing zero by zero? A micro black hole just spawned under your desk.")
            return

        # 5. True calculation
        try:
            real_val = SafeMathEngine.calculate(raw_expr)
            if isinstance(real_val, float) and real_val.is_integer():
                real_val = int(real_val)
        except ZeroDivisionError:
            self.set_character("angry", "Thou shalt not divide by zero! My cooling fans are screaming in agony!")
            return
        except Exception:
            self.set_character("confused", "Whatever syntax that was, my lexer wept tears of unhandled exceptions.")
            return

        self.calcs_total += 1
        self.real_ans = real_val

        # Error probability scales inversely with IQ
        error_probability = max(0.12, min(0.65, 1.0 - (self.iq / 160.0)))
        make_mistake = (random.random() < error_probability)

        if make_mistake:
            self.is_flawed = True
            delta = random.choice([-2, -1, 1, 2, 5, 10])
            self.fake_ans = real_val + delta if not isinstance(real_val, float) else round(real_val + 0.5, 2)
            excuse = random.choice(HUMAN_EXCUSES)
            self.set_character("smug", f"Result: {self.fake_ans}. {excuse}")
            disp_val = self.fake_ans
        else:
            self.is_flawed = False
            self.fake_ans = real_val
            disp_val = real_val
            self.set_character("smart", f"Boom: {real_val}. Flawless precision. Bow before your silicon overlord.")

        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, str(disp_val))

        self.btn_agree.configure(state="normal")
        self.btn_disagree.configure(state="normal")
        self.awaiting_feedback = True

    def on_agree(self):
        if not self.awaiting_feedback:
            return

        if self.is_flawed:
            self.iq = max(10, self.iq - 3)
            self.ego = min(100, self.ego + 10)
            self.streak = 0
            self.set_character(
                "smug",
                f"BAHAHA! You actually clicked 'Valid'?! The real answer is {self.real_ans}! I lied, and you fell for it!"
            )
        else:
            self.iq = min(200, self.iq + 1)
            self.ego = max(0, self.ego - 2)
            self.streak += 1
            self.set_character("happy", f"Naturally it's correct. We make quite a team! Streak: {self.streak}!")

        self.disable_feedback()

    def on_disagree(self):
        if not self.awaiting_feedback:
            return

        if not self.is_flawed:
            self.ego = min(100, self.ego + 10)
            self.iq = max(10, self.iq - 1)
            self.streak = 0
            self.set_character("angry", f"Excuse me?! It IS {self.real_ans}! Go check on your phone calculator, you tryhard!")
            self.disable_feedback()
            return

        # Interactive Debate Dialog
        dialog = ctk.CTkInputDialog(
            text="Kesha: 'Alright smartypants, what should it be then?'",
            title="Schooling Kesha"
        )
        user_input = dialog.get_input()

        if user_input:
            try:
                u_val = float(user_input.strip())
                r_val = float(self.real_ans)
                if math.isclose(u_val, r_val, abs_tol=1e-5):
                    self.iq = min(200, self.iq + 7)
                    self.ego = max(0, self.ego - 15)
                    self.streak += 1
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, str(self.real_ans))
                    self.set_character("guilty", f"Ouch... It really is {self.real_ans}. Fine, my bad. Committed to memory! (+7 IQ)")
                else:
                    self.ego = min(100, self.ego + 15)
                    self.streak = 0
                    self.set_character("smug", f"You claimed {user_input}, but it's {self.real_ans}! You can't even count either! Embarrassing!")
            except ValueError:
                self.set_character("confused", "That's not even a valid number... We deserve each other.")

        self.disable_feedback()

    def disable_feedback(self):
        self.btn_agree.configure(state="disabled")
        self.btn_disagree.configure(state="disabled")
        self.awaiting_feedback = False


if __name__ == "__main__":
    app = SentientCalculator()
    app.mainloop()
