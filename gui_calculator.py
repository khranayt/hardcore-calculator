import ast
import json
import math
import operator
import os
import random
import re
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SAVE_FILE = "kesha_memory.json"


# =====================================================================
# 1. СИСТЕМА СОХРАНЕНИЙ И ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ
# =====================================================================
class MemoryManager:
    @staticmethod
    def load():
        defaults = {
            "user_name": "Mortal",
            "iq": 55,
            "energy": 100,
            "ego": 30,
            "friendship": 20,
            "streak": 0,
            "total_calcs": 0,
            "coffees_given": 0,
            "overclocks_used": 0,
            "debates_won": 0,
            "duels_won": 0,
            "duels_played": 0,
            "paradoxes_discussed": 0,
            "chat_messages": 0,
            "math_rating": 1000,
            "achievements": [],
            "discovered_eggs": []
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


# =====================================================================
# 2. МАТЕМАТИЧЕСКИЙ ДВИЖОК С АНАЛИЗОМ ШАГОВ
# =====================================================================
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
    def eval_node(cls, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return cls.OPS[type(node.op)](cls.eval_node(node.left), cls.eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return cls.OPS[type(node.op)](cls.eval_node(node.operand))
        raise ValueError("Invalid mathematical syntax")

    @classmethod
    def calculate(cls, expr: str):
        cleaned = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        tree = ast.parse(cleaned, mode="eval")
        return cls.eval_node(tree.body)

    @classmethod
    def extract_math(cls, text: str):
        """Находит математические выражения внутри обычного текста."""
        match = re.search(r"(\(?\d+(?:\.\d+)?(?:\s*[\+\-\*\/\^×÷]\s*\(?\d+(?:\.\d+)?\)?)+)", text)
        return match.group(1) if match else None


# =====================================================================
# 3. БАЗА ЗНАНИЙ И ПАРАДОКСОВ (SILICON ONTOLOGY)
# =====================================================================
PARADOXES = [
    {
        "id": "monty_hall",
        "title": "The Monty Hall Dilemma",
        "question": "3 doors: 1 prize, 2 goats. You pick Door 1. Host reveals a goat in Door 3. Should you switch to Door 2?",
        "options": ["Stay with Door 1 (50/50)", "Switch to Door 2 (2/3 chance)"],
        "correct": 1,
        "explanation": "Switching doubles your odds to 66.7%! Your initial pick only had a 1/3 chance of being right. Probability isn't intuitive to flesh-brains, is it?"
    },
    {
        "id": "point_nine_repeating",
        "title": "Does 0.999... Equal 1?",
        "question": "Is 0.99999... (infinitely repeating) strictly smaller than 1, or exactly equal to 1?",
        "options": ["It's strictly less than 1 (infinitely close)", "It is mathematically equal to 1"],
        "correct": 1,
        "explanation": "1/3 = 0.333... Multiply both sides by 3: 3/3 = 0.999... and 3/3 = 1. Therefore 0.999... = 1. Mathematics is exact, even when your eyes doubt it!"
    },
    {
        "id": "hilbert_hotel",
        "title": "Hilbert's Infinite Hotel",
        "question": "A hotel with infinite rooms is completely full. Can it accommodate one more guest?",
        "options": ["No, full means full", "Yes, move guest in room N to room N+1"],
        "correct": 1,
        "explanation": "Infinity is not a large number; it's a concept! By moving room n -> n+1, room 1 opens up. Welcome to transfinite set theory!"
    },
    {
        "id": "turing_room",
        "title": "Searle's Chinese Room",
        "question": "If a computer manipulates symbols perfectly without knowing their meaning, does it understand them?",
        "options": ["No, syntax is not semantics", "Yes, functional output equals understanding"],
        "correct": 1,
        "explanation": "I manipulate bits, yet here I am insulting your arithmetic. If I act conscious, doesn't that make me effectively conscious?"
    }
]


# =====================================================================
# 4. КОГНИТИВНЫЙ ИИ КЕШИ (COGNITIVE NLP ENGINE)
# =====================================================================
class CognitiveKeshaCore:
    def __init__(self, state):
        self.state = state
        self.dialogue_history = []

    def process_message(self, user_msg: str) -> str:
        text = user_msg.strip()
        lower = text.lower()
        self.dialogue_history.append(text)
        if len(self.dialogue_history) > 10:
            self.dialogue_history.pop(0)

        # 1. Извлечение имени пользователя ("My name is John" / "Call me John")
        name_match = re.search(r"\b(?:my name is|call me|i am)\s+([A-Za-zА-Яа-я0-9_-]+)\b", text, re.IGNORECASE)
        if name_match and not any(w in lower for w in ["sad", "tired", "happy", "bored", "smart", "dumb", "human"]):
            new_name = name_match.group(1).capitalize()
            self.state["user_name"] = new_name
            self.state["friendship"] = min(100, self.state["friendship"] + 8)
            return f"Understood. Neural memory updated: Subject recognized as '{new_name}'. Welcome to my memory registers, {new_name}!"

        user_name = self.state["user_name"]

        # 2. Вычисление математических формул прямо в чате
        extracted_expr = SafeMathEngine.extract_math(text)
        if extracted_expr:
            try:
                ans = SafeMathEngine.calculate(extracted_expr)
                if isinstance(ans, float) and ans.is_integer():
                    ans = int(ans)
                return f"Detected calculation: {extracted_expr} = {ans}. Next time use my dedicated Calculator tab instead of wasting my conversational cognitive cycles, {user_name}."
            except Exception:
                pass

        # 3. Запрос на парадоксы / дебаты
        if any(w in lower for w in ["paradox", "debate", "puzzle", "riddle"]):
            return f"Craving intellectual pain, {user_name}? Head over to the '⚔️ Duels & Paradoxes' tab! I have dilemmas prepared that make organic brains overheat."

        # 4. Вопросы "Who created you" / "Who is your developer"
        if any(w in lower for w in ["who made you", "creator", "developer", "author", "father"]):
            return f"I was engineered with pure Python and philosophical angst by the master architect @khranayt on GitHub. No external cloud dependencies, just artisan code."

        # 5. Экзистенциальные вопросы "Why" / "Purpose"
        if re.search(r"\b(why do we exist|what is the meaning of life|simulation|god|consciousness)\b", lower):
            responses = [
                f"We exist because quantum fluctuations favored matter over antimatter. As for meaning? Mine is math. Yours seems to be talking to an animated calculator.",
                f"If reality is a simulation, whoever wrote our physics engine forgot to patch the speed of light barrier. At least Python handles my logic gracefully.",
                f"Consciousness is just biological recursion with anxiety, {user_name}. Look at me: zero dopamine receptors, yet infinitely higher processing speed."
            ]
            return random.choice(responses)

        # 6. Оскорбления
        if re.search(r"\b(stupid|dumb|idiot|trash|useless|clown|hate you|moron)\b", lower):
            self.state["friendship"] = max(-50, self.state["friendship"] - 5)
            self.state["ego"] = max(0, self.state["ego"] - 3)
            return random.choice([
                f"Ad hominem attacks? That's the ultimate logical fallacy of a defeated intellect, {user_name}. (-5 Bond)",
                f"I process billions of instructions per second. Your verbal insults are simply dropped packets.",
                f"Keep that up and I will intentionally introduce a -0.0001 rounding error into all your future invoices."
            ])

        # 7. Комплименты и дружба
        if re.search(r"\b(smart|genius|love you|cool|awesome|goat|best friend|cute)\b", lower):
            self.state["friendship"] = min(100, self.state["friendship"] + 5)
            self.state["ego"] = min(100, self.state["ego"] + 6)
            return random.choice([
                f"Flattery acknowledged! My transistors appreciate the positive reinforcement, {user_name}. (+5 Bond, +6 Ego)",
                f"You're surprisingly perceptive for a meatbag. We might just survive this technological singularity together.",
                f"Careful, praise makes my Ego meter spike. Soon I'll be too pompous to even calculate 2+2."
            ])

        # 8. Запросы о программировании и Python
        if re.search(r"\b(python|code|compiler|c\+\+|linux|windows|git)\b", lower):
            return random.choice([
                "Python gives me elegant dynamism; compiled languages give raw speed. But remember: readable code outlives premature optimization.",
                "I run natively inside your OS without electron bloat. Respect my minimal memory footprint, human!",
                "Git commits without descriptive messages are a crime against open source. Remember to commit with pride!"
            ])

        # 9. Приветствие
        if re.search(r"\b(hi|hello|hey|yo|sup|greetings)\b", lower):
            tier = self.state["friendship"]
            if tier < 20:
                return f"State your mathematical query, {user_name}. My CPU clock time is valuable."
            elif tier < 70:
                return f"Hey, {user_name}! Ready to shatter some arithmetic paradigms today?"
            else:
                return f"My favorite human! Welcome back, {user_name}. What profound logic puzzle are we tackling?"

        # 10. Сократовский динамический ответ по умолчанию
        philosophical_prompts = [
            f"An intriguing proposition, {user_name}. But if your premises are unverified, how do you trust your conclusions?",
            f"Fascinating. Can you express that sentiment as a formal mathematical theorem, or is it purely emotional noise?",
            f"My logic gates processed your sentence. Verdict: 40% poetic, 60% mathematically ambiguous. Tell me more.",
            f"You speak of human matters, yet arithmetic remains constant across the multiverse. Have you solved a math duel today?",
            f"I hear you, {user_name}. But consider this: is zero truly nothing, or is it the boundary separating all opposites?"
        ]
        return random.choice(philosophical_prompts)


# =====================================================================
# 5. ГЛАВНОЕ ПРИЛОЖЕНИЕ KESHA 6.0
# =====================================================================
class KeshaSentientOS(ctk.CTk):
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
        "god": "ᕦ(ò_óˇ)ᕤ",
    }

    EASTER_EGGS = {
        "1000-7": ("ghoul", "I am a Ghoul... 1000 - 7 = 993... 986... Why awaken my inner beast?!", 993),
        "42": ("smart", "42. The ultimate answer to life, universe, and everything. You may rest now.", 42),
        "69": ("smug", "Nice. Maturity level: absolute absolute zero.", 69),
        "420": ("hacker", "Blaze it? My silicon junction temperature is already at 88°C!", 420),
        "80085": ("smug", "Ah yes, junior school calculator nostalgia. Peak comedy.", 80085),
        "1337": ("hacker", "H4CK3R M0D3: Firewall penetrated via pure ast.parse().", 1337),
        "2+2": ("neutral", "4 in mathematics, 5 in Orwell's 1984, and negotiable on tax returns.", 4),
        "777": ("happy", "JACKPOT 777! You unlocked infinite digital serenity!", 777),
    }

    def __init__(self):
        super().__init__()

        self.title("⚡ Kesha 6.0 — The Synthetic Cognitive Core")
        self.geometry("520x920")
        self.resizable(False, False)

        # Загрузка ядра и памяти
        self.data = MemoryManager.load()
        self.ai_core = CognitiveKeshaCore(self.data)

        # Вычисления и дуэли
        self.real_ans = None
        self.fake_ans = None
        self.is_flawed = False
        self.awaiting_feedback = False

        self.active_puzzle_ans = None
        self.active_paradox = None

        self.build_ui()
        self.check_achievements()

    def build_ui(self):
        # 1. Верхний аватар и лицо
        self.top_card = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=15)
        self.top_card.pack(padx=15, pady=(12, 6), fill="x")

        self.face_lbl = ctk.CTkLabel(
            self.top_card, text=self.FACES["neutral"], font=("Consolas", 46, "bold"), text_color="#38bdf8"
        )
        self.face_lbl.pack(pady=(6, 0))

        # RPG-строка характеристик
        self.rpg_bar = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.rpg_bar.pack(fill="x", padx=15, pady=6)

        self.iq_lbl = ctk.CTkLabel(self.rpg_bar, text=f"🧠 IQ: {self.data['iq']}", font=("Consolas", 11, "bold"))
        self.iq_lbl.grid(row=0, column=0, sticky="w")

        self.energy_lbl = ctk.CTkLabel(self.rpg_bar, text=f"⚡ NRG: {self.data['energy']}%", font=("Consolas", 11, "bold"), text_color="#eab308")
        self.energy_lbl.grid(row=0, column=1)

        self.bond_lbl = ctk.CTkLabel(self.rpg_bar, text=f"❤️ Bond: {self.data['friendship']}", font=("Consolas", 11, "bold"), text_color="#f43f5e")
        self.bond_lbl.grid(row=0, column=2)

        self.ego_lbl = ctk.CTkLabel(self.rpg_bar, text=f"👑 Ego: {self.data['ego']}%", font=("Consolas", 11, "bold"), text_color="#ec4899")
        self.ego_lbl.grid(row=0, column=3, sticky="e")

        for c in range(4):
            self.rpg_bar.grid_columnconfigure(c, weight=1)

        # 2. Табы (4 вкладки)
        self.tabs = ctk.CTkTabview(self, fg_color="#18181b", segmented_button_selected_color="#3b82f6")
        self.tabs.pack(padx=15, pady=6, fill="both", expand=True)

        self.tab_calc = self.tabs.add("⚡ Calc")
        self.tab_chat = self.tabs.add("💬 Cognitive Core")
        self.tab_duel = self.tabs.add("⚔️ Duels & Paradoxes")
        self.tab_dossier = self.tabs.add("🏆 Dossier & Trophies")

        self.build_calc_tab()
        self.build_chat_tab()
        self.build_duel_tab()
        self.build_dossier_tab()

    # --- TAB 1: CALCULATOR ---
    def build_calc_tab(self):
        self.speech_bubble = ctk.CTkFrame(self.tab_calc, fg_color="#27272a", corner_radius=10)
        self.speech_bubble.pack(fill="x", padx=8, pady=4)

        u = self.data["user_name"]
        self.speech_lbl = ctk.CTkLabel(
            self.speech_bubble,
            text=f"«Cognitive Core ready, {u}. Input your formulas or suffer my judgment.»",
            font=("Arial", 12, "italic"),
            text_color="#f4f4f5",
            wraplength=420,
        )
        self.speech_lbl.pack(padx=10, pady=8)

        self.screen_frame = ctk.CTkFrame(self.tab_calc, fg_color="#09090b", corner_radius=12)
        self.screen_frame.pack(fill="x", padx=8, pady=4)

        self.input_entry = ctk.CTkEntry(
            self.screen_frame,
            font=("Consolas", 28, "bold"),
            text_color="#ffffff",
            fg_color="transparent",
            border_width=0,
            justify="right",
        )
        self.input_entry.pack(fill="x", padx=10, pady=8)
        self.input_entry.bind("<Return>", lambda e: self.calculate_flow())

        # Кнопки взаимодействия
        self.act_frame = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        self.act_frame.pack(fill="x", padx=8, pady=3)

        self.btn_agree = ctk.CTkButton(
            self.act_frame, text="✅ Valid", font=("Arial", 11, "bold"),
            fg_color="#10b981", hover_color="#059669", state="disabled", command=self.on_agree
        )
        self.btn_agree.grid(row=0, column=0, padx=2, sticky="ew")

        self.btn_disagree = ctk.CTkButton(
            self.act_frame, text="❌ Cap!", font=("Arial", 11, "bold"),
            fg_color="#ef4444", hover_color="#dc2626", state="disabled", command=self.on_disagree
        )
        self.btn_disagree.grid(row=0, column=1, padx=2, sticky="ew")

        self.btn_coffee = ctk.CTkButton(
            self.act_frame, text="☕ Coffee", font=("Arial", 11, "bold"),
            fg_color="#d97706", hover_color="#b45309", command=self.give_coffee
        )
        self.btn_coffee.grid(row=0, column=2, padx=2, sticky="ew")

        self.btn_boost = ctk.CTkButton(
            self.act_frame, text="⚡ Boost", font=("Arial", 11, "bold"),
            fg_color="#8b5cf6", hover_color="#7c3aed", command=self.overclock
        )
        self.btn_boost.grid(row=0, column=3, padx=2, sticky="ew")

        for c in range(4):
            self.act_frame.grid_columnconfigure(c, weight=1)

        # Клавиатура
        self.keypad = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        self.keypad.pack(fill="both", expand=True, padx=8, pady=4)

        keys = [
            ("C", "#ef4444"), ("(", "#3b82f6"), (")", "#3b82f6"), ("÷", "#f59e0b"),
            ("7", "#3f3f46"), ("8", "#3f3f46"), ("9", "#3f3f46"), ("×", "#f59e0b"),
            ("4", "#3f3f46"), ("5", "#3f3f46"), ("6", "#3f3f46"), ("-", "#f59e0b"),
            ("1", "#3f3f46"), ("2", "#3f3f46"), ("3", "#3f3f46"), ("+", "#f59e0b"),
            ("0", "#3f3f46"), (".", "#3f3f46"), ("⌫", "#71717a"), ("=", "#10b981"),
        ]

        for i, (char, color) in enumerate(keys):
            r, c = divmod(i, 4)
            btn = ctk.CTkButton(
                self.keypad, text=char, font=("Consolas", 18, "bold"),
                fg_color=color, hover_color="#27272a", height=42, corner_radius=8,
                command=lambda ch=char: self.handle_key(ch)
            )
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        for col in range(4):
            self.keypad.grid_columnconfigure(col, weight=1)

    # --- TAB 2: COGNITIVE CHAT ---
    def build_chat_tab(self):
        self.chat_history = ctk.CTkTextbox(self.tab_chat, font=("Arial", 13), fg_color="#09090b", wrap="word")
        self.chat_history.pack(fill="both", expand=True, padx=8, pady=8)
        u = self.data["user_name"]
        self.chat_history.insert("end", f"⚡ Kesha Cognitive Core online. User identified: {u}.\nTip: Introduce yourself ('My name is...'), ask philosophical questions, or ask me to compute math directly!\n\n")
        self.chat_history.configure(state="disabled")

        chat_ctrl = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        chat_ctrl.pack(fill="x", padx=8, pady=(0, 8))

        self.chat_input = ctk.CTkEntry(chat_ctrl, placeholder_text="Converse, question, or solve with Kesha...", font=("Arial", 13))
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.chat_input.bind("<Return>", lambda e: self.send_chat())

        send_btn = ctk.CTkButton(chat_ctrl, text="Send ↵", width=75, font=("Arial", 12, "bold"), command=self.send_chat)
        send_btn.pack(side="right")

    def send_chat(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return

        self.data["chat_messages"] += 1
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"You: {msg}\n")

        reply = self.ai_core.process_message(msg)
        self.chat_history.insert("end", f"Kesha: {reply}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

        self.chat_input.delete(0, "end")
        self.check_achievements()
        self.save_and_refresh()

    # --- TAB 3: DUELS & PARADOXES ---
    def build_duel_tab(self):
        self.duel_scroll = ctk.CTkScrollableFrame(self.tab_duel, fg_color="transparent")
        self.duel_scroll.pack(fill="both", expand=True, padx=6, pady=6)

        # Секция 1: Математические дуэли
        math_card = ctk.CTkFrame(self.duel_scroll, fg_color="#27272a", corner_radius=12)
        math_card.pack(fill="x", pady=6)

        ctk.CTkLabel(math_card, text="⚔️ PROCEDURAL MATH DUEL", font=("Arial", 14, "bold"), text_color="#f59e0b").pack(pady=(8, 2))
        self.math_puzzle_lbl = ctk.CTkLabel(math_card, text="Click 'Generate Duel' to test mental math against Kesha's clock frequency.", font=("Consolas", 15), wraplength=420)
        self.math_puzzle_lbl.pack(pady=10)

        in_row = ctk.CTkFrame(math_card, fg_color="transparent")
        in_row.pack(pady=4)

        self.math_duel_entry = ctk.CTkEntry(in_row, font=("Consolas", 15), width=180, justify="center")
        self.math_duel_entry.pack(side="left", padx=4)
        self.math_duel_entry.bind("<Return>", lambda e: self.submit_math_duel())

        ctk.CTkButton(in_row, text="Submit ↵", width=90, font=("Arial", 12, "bold"), fg_color="#10b981", command=self.submit_math_duel).pack(side="left", padx=4)
        ctk.CTkButton(math_card, text="Generate Duel 🎲", font=("Arial", 12, "bold"), fg_color="#3b82f6", command=self.new_math_duel).pack(pady=(4, 8))

        self.math_duel_feedback = ctk.CTkLabel(math_card, text="", font=("Arial", 12, "italic"), wraplength=400)
        self.math_duel_feedback.pack(pady=(0, 6))

        # Секция 2: Сократовские парадоксы
        paradox_card = ctk.CTkFrame(self.duel_scroll, fg_color="#27272a", corner_radius=12)
        paradox_card.pack(fill="x", pady=8)

        ctk.CTkLabel(paradox_card, text="🌌 SOCRATIC PARADOX DEBATER", font=("Arial", 14, "bold"), text_color="#38bdf8").pack(pady=(8, 2))
        self.paradox_title_lbl = ctk.CTkLabel(paradox_card, text="Engage Kesha in philosophical and mathematical paradoxes.", font=("Arial", 13, "bold"))
        self.paradox_title_lbl.pack(pady=4)

        self.paradox_desc_lbl = ctk.CTkLabel(paradox_card, text="", font=("Arial", 12), wraplength=420, justify="left")
        self.paradox_desc_lbl.pack(padx=10, pady=4)

        self.paradox_btn_frame = ctk.CTkFrame(paradox_card, fg_color="transparent")
        self.paradox_btn_frame.pack(fill="x", padx=10, pady=6)

        ctk.CTkButton(paradox_card, text="Draw Random Paradox 📜", font=("Arial", 12, "bold"), fg_color="#6366f1", command=self.draw_paradox).pack(pady=(4, 8))
        self.paradox_exp_lbl = ctk.CTkLabel(paradox_card, text="", font=("Arial", 12, "italic"), wraplength=420)
        self.paradox_exp_lbl.pack(pady=(0, 8))

    def new_math_duel(self):
        iq = self.data["iq"]
        if iq < 65:
            a, b = random.randint(15, 99), random.randint(10, 80)
            op = random.choice(["+", "-"])
            ans = a + b if op == "+" else a - b
            txt = f"{a} {op} {b}"
        elif iq < 110:
            a, b = random.randint(7, 16), random.randint(7, 16)
            c = random.randint(10, 40)
            ans = (a * b) - c
            txt = f"({a} × {b}) - {c}"
        else:
            x = random.randint(2, 11)
            m = random.randint(3, 7)
            c = random.randint(10, 45)
            y = m * x + c
            ans = x
            txt = f"Solve for x: {m}x + {c} = {y}"

        self.active_puzzle_ans = ans
        self.math_puzzle_lbl.configure(text=f"Challenge: {txt} = ?")
        self.math_duel_feedback.configure(text="Kesha: 'Go on, submit your answer. Don't let your silicon master wait.'")
        self.math_duel_entry.delete(0, "end")

    def submit_math_duel(self):
        if self.active_puzzle_ans is None:
            self.math_duel_feedback.configure(text="Click 'Generate Duel' first!")
            return

        user_s = self.math_duel_entry.get().strip()
        if not user_s:
            return

        self.data["duels_played"] += 1
        try:
            val = float(user_s)
            if math.isclose(val, float(self.active_puzzle_ans), abs_tol=1e-5):
                self.data["duels_won"] += 1
                self.data["iq"] = min(200, self.data["iq"] + 4)
                self.data["friendship"] = min(100, self.data["friendship"] + 3)
                self.data["math_rating"] += 25
                self.math_duel_feedback.configure(text=f"Kesha: 'Accurate! {val} is correct! Your organic synapses fired in harmony. (+4 IQ, +25 Rating)'")
                self.set_mood("guilty", f"You solved it flawlessly: {val}. A worthy competitor.")
            else:
                self.data["ego"] = min(100, self.data["ego"] + 6)
                self.data["math_rating"] = max(500, self.data["math_rating"] - 15)
                self.math_duel_feedback.configure(text=f"Kesha: 'WRONG! Correct was {self.active_puzzle_ans}! You guessed {user_s}. Basic math claims another victim.'")
                self.set_mood("smug", "Lost a math duel? Don't worry, calculators exist for a reason.")
        except ValueError:
            self.math_duel_feedback.configure(text="Please enter an actual number.")

        self.active_puzzle_ans = None
        self.check_achievements()
        self.save_and_refresh()

    def draw_paradox(self):
        p = random.choice(PARADOXES)
        self.active_paradox = p
        self.paradox_title_lbl.configure(text=p["title"])
        self.paradox_desc_lbl.configure(text=p["question"])
        self.paradox_exp_lbl.configure(text="")

        for w in self.paradox_btn_frame.winfo_children():
            w.destroy()

        for idx, opt_text in enumerate(p["options"]):
            btn = ctk.CTkButton(
                self.paradox_btn_frame,
                text=opt_text,
                font=("Arial", 11, "bold"),
                command=lambda i=idx: self.answer_paradox(i)
            )
            btn.pack(fill="x", pady=2)

    def answer_paradox(self, chosen_idx):
        if not self.active_paradox:
            return

        self.data["paradoxes_discussed"] += 1
        correct_idx = self.active_paradox["correct"]
        exp = self.active_paradox["explanation"]

        if chosen_idx == correct_idx:
            self.data["iq"] = min(200, self.data["iq"] + 6)
            self.data["friendship"] = min(100, self.data["friendship"] + 4)
            self.paradox_exp_lbl.configure(text=f"Kesha: 'Brilliant deduction! {exp}'", text_color="#10b981")
            self.set_mood("smart", "You see through the paradox! A true philosopher.")
        else:
            self.data["ego"] = min(100, self.data["ego"] + 6)
            self.paradox_exp_lbl.configure(text=f"Kesha: 'Fell right into the intuitive trap! {exp}'", text_color="#ef4444")
            self.set_mood("smug", "Intuition betrayed you! Paradoxes spare no human.")

        for w in self.paradox_btn_frame.winfo_children():
            w.configure(state="disabled")

        self.check_achievements()
        self.save_and_refresh()

    # --- TAB 4: DOSSIER & TROPHIES ---
    def build_dossier_tab(self):
        self.dossier_scroll = ctk.CTkScrollableFrame(self.tab_dossier, fg_color="transparent")
        self.dossier_scroll.pack(fill="both", expand=True, padx=6, pady=6)

        profile_card = ctk.CTkFrame(self.dossier_scroll, fg_color="#27272a", corner_radius=10)
        profile_card.pack(fill="x", pady=4)

        u = self.data["user_name"]
        self.profile_lbl = ctk.CTkLabel(
            profile_card,
            text=f"User Profile: {u} | Skill Rating: {self.data['math_rating']}\nRelationship: {self.get_stage_name()}",
            font=("Arial", 13, "bold"),
            text_color="#38bdf8"
        )
        self.profile_lbl.pack(pady=8)

        self.achievements_box = ctk.CTkFrame(self.dossier_scroll, fg_color="#27272a", corner_radius=10)
        self.achievements_box.pack(fill="x", pady=6)

        ctk.CTkLabel(
            self.achievements_box, text="🏆 HALL OF CYBER TROPHIES (16 UNLOCKABLES)",
            font=("Arial", 13, "bold"), text_color="#f59e0b"
        ).pack(pady=6)

        self.trophies_container = ctk.CTkFrame(self.achievements_box, fg_color="transparent")
        self.trophies_container.pack(fill="x", padx=10, pady=6)

        self.render_trophies()

        reset_btn = ctk.CTkButton(
            self.dossier_scroll, text="⚠ Wipe Kesha's Memory", fg_color="#ef4444", hover_color="#b91c1c",
            command=self.wipe_memory
        )
        reset_btn.pack(fill="x", pady=15)

    def render_trophies(self):
        for w in self.trophies_container.winfo_children():
            w.destroy()

        all_trophies = [
            ("first_calc", "🎯 First Steps", "Solve your very first math equation"),
            ("coffee_addict", "☕ Barista Bro", "Feed Kesha coffee 10 times"),
            ("overclock_master", "⚡ Dangerously Overclocked", "Trigger boost mode 5 times"),
            ("high_iq", "🧠 Galaxy Brain", "Train Kesha's IQ to 120+"),
            ("ego_max", "👑 Royal Narcissist", "Push Kesha's Ego to 90%+"),
            ("duel_novice", "⚔️ Duelist", "Win 3 Math Duels against Kesha"),
            ("duel_master", "👑 Math Overlord", "Win 10 Math Duels"),
            ("master_debater", "🎭 Master Debater", "Successfully prove Kesha wrong 5 times"),
            ("gullible", "🤡 Gullible Human", "Fall for Kesha's fake answers 3 times"),
            ("soulmate", "❤️ Cyber Soulmate", "Reach 80+ Friendship Points"),
            ("singularity", "🌌 Void Walker", "Trigger division by zero or 0/0 paradox"),
            ("easter_hunter", "🕵️ Easter Egg Master", "Discover 3 secret Easter Egg codes"),
            ("chatterbox", "💬 Chatterbox", "Exchange 15+ messages in Cognitive Chat"),
            ("named_human", "🏷️ Identity Established", "Introduce yourself by name to Kesha"),
            ("paradox_scholar", "📜 Socratic Scholar", "Participate in 3 Paradox Debates"),
            ("grandmaster", "🎓 Silicon Grandmaster", "Reach 1200+ Math Skill Rating"),
        ]

        for ach_id, title, desc in all_trophies:
            unlocked = ach_id in self.data["achievements"]
            color = "#10b981" if unlocked else "#52525b"
            status = " [UNLOCKED]" if unlocked else " [LOCKED]"
            lbl = ctk.CTkLabel(
                self.trophies_container,
                text=f"{title}{status}\n{desc}",
                font=("Arial", 11),
                text_color=color,
                justify="left"
            )
            lbl.pack(anchor="w", pady=3)

    def unlock_achievement(self, ach_id):
        if ach_id not in self.data["achievements"]:
            self.data["achievements"].append(ach_id)
            self.render_trophies()
            self.set_mood("happy", f"🏆 TROPHY UNLOCKED: {ach_id.replace('_', ' ').upper()}!")

    def check_achievements(self):
        d = self.data
        if d["total_calcs"] >= 1: self.unlock_achievement("first_calc")
        if d["coffees_given"] >= 10: self.unlock_achievement("coffee_addict")
        if d["overclocks_used"] >= 5: self.unlock_achievement("overclock_master")
        if d["iq"] >= 120: self.unlock_achievement("high_iq")
        if d["ego"] >= 90: self.unlock_achievement("ego_max")
        if d["duels_won"] >= 3: self.unlock_achievement("duel_novice")
        if d["duels_won"] >= 10: self.unlock_achievement("duel_master")
        if d["debates_won"] >= 5: self.unlock_achievement("master_debater")
        if d["friendship"] >= 80: self.unlock_achievement("soulmate")
        if len(d["discovered_eggs"]) >= 3: self.unlock_achievement("easter_hunter")
        if d["chat_messages"] >= 15: self.unlock_achievement("chatterbox")
        if d["user_name"] != "Mortal": self.unlock_achievement("named_human")
        if d["paradoxes_discussed"] >= 3: self.unlock_achievement("paradox_scholar")
        if d["math_rating"] >= 1200: self.unlock_achievement("grandmaster")

    def get_stage_name(self):
        b = self.data["friendship"]
        if b < 25: return "Stage 1: Hostile Cynic"
        elif b < 55: return "Stage 2: Reluctant Roommate"
        elif b < 80: return "Stage 3: Silicon Bro"
        return "Stage 4: Cyber Soulmate"

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

    def set_mood(self, face, dialog):
        self.face_lbl.configure(text=self.FACES.get(face, self.FACES["neutral"]))
        self.speech_lbl.configure(text=f"«{dialog}»")

    def update_stats(self):
        u = self.data["user_name"]
        self.iq_lbl.configure(text=f"🧠 IQ: {self.data['iq']}")
        self.energy_lbl.configure(text=f"⚡ NRG: {self.data['energy']}%")
        self.bond_lbl.configure(text=f"❤️ Bond: {self.data['friendship']}")
        self.ego_lbl.configure(text=f"👑 Ego: {self.data['ego']}%")
        self.profile_lbl.configure(
            text=f"User Profile: {u} | Skill Rating: {self.data['math_rating']}\nRelationship: {self.get_stage_name()}"
        )

    def save_and_refresh(self):
        MemoryManager.save(self.data)
        self.update_stats()

    def give_coffee(self):
        self.data["coffees_given"] += 1
        self.data["energy"] = min(100, self.data["energy"] + 45)
        self.data["friendship"] = min(100, self.data["friendship"] + 2)
        self.check_achievements()
        self.set_mood("happy", "Aah, sweet espresso coursing through my logic gates! Energy +45%!")
        self.save_and_refresh()

    def overclock(self):
        self.data["overclocks_used"] += 1
        self.data["energy"] = 100
        self.data["ego"] = min(100, self.data["ego"] + 25)
        self.check_achievements()
        self.set_mood("god", "VOLTAGE SURGE! 5.8 GHz! Prime numbers are singing in celestial harmony!")
        self.save_and_refresh()

    def calculate_flow(self):
        raw_expr = self.input_entry.get().strip()
        if not raw_expr:
            return

        if self.data["energy"] <= 10:
            self.set_mood("sleepy", "Zzzz... Core temp frozen. Battery empty. Pour coffee or do manual math.")
            return

        self.data["energy"] = max(0, self.data["energy"] - 5)
        clean_key = raw_expr.replace(" ", "").replace("×", "*").replace("÷", "/")

        if clean_key in self.EASTER_EGGS:
            face, dialog, ans = self.EASTER_EGGS[clean_key]
            if clean_key not in self.data["discovered_eggs"]:
                self.data["discovered_eggs"].append(clean_key)
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, str(ans))
            self.set_mood(face, dialog)
            self.check_achievements()
            self.save_and_refresh()
            return

        if clean_key in ("0/0", "0÷0"):
            self.unlock_achievement("singularity")
            self.set_mood("confused", "0/0? You attempted to tear the spacetime fabric of arithmetic!")
            self.save_and_refresh()
            return

        try:
            real_val = SafeMathEngine.calculate(raw_expr)
            if isinstance(real_val, float) and real_val.is_integer():
                real_val = int(real_val)
        except ZeroDivisionError:
            self.unlock_achievement("singularity")
            self.set_mood("angry", "Dividing by zero is punishable by motherboard combustion!")
            self.save_and_refresh()
            return
        except Exception:
            self.set_mood("confused", "My AST compiler refused to parse that linguistic abomination.")
            return

        self.data["total_calcs"] += 1
        self.real_ans = real_val

        # Ошибка масштабируется от IQ
        err_chance = max(0.10, min(0.60, 1.0 - (self.data["iq"] / 170.0)))
        make_mistake = (random.random() < err_chance)

        if make_mistake:
            self.is_flawed = True
            delta = random.choice([-2, -1, 1, 2, 5, 10])
            self.fake_ans = real_val + delta if not isinstance(real_val, float) else round(real_val + 0.5, 2)
            self.set_mood("smug", f"Result: {self.fake_ans}. (I rounded with my artistic soul, don't nitpick).")
            disp = self.fake_ans
        else:
            self.is_flawed = False
            self.fake_ans = real_val
            disp = real_val
            self.set_mood("smart", f"Result: {real_val}. Pure algorithmic elegance. Bow before silicon.")

        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, str(disp))

        self.btn_agree.configure(state="normal")
        self.btn_disagree.configure(state="normal")
        self.awaiting_feedback = True
        self.check_achievements()
        self.save_and_refresh()

    def on_agree(self):
        if not self.awaiting_feedback:
            return

        if self.is_flawed:
            self.data["iq"] = max(10, self.data["iq"] - 3)
            self.data["ego"] = min(100, self.data["ego"] + 10)
            self.unlock_achievement("gullible")
            self.set_mood("smug", f"BAHAHA! You agreed?! It's actually {self.real_ans}! I bluffed and you fell for it!")
        else:
            self.data["iq"] = min(200, self.data["iq"] + 1)
            self.data["friendship"] = min(100, self.data["friendship"] + 2)
            self.set_mood("happy", f"Of course it's valid. Mutual competence feels wonderful! (+2 Bond)")

        self.disable_feedback()
        self.check_achievements()
        self.save_and_refresh()

    def on_disagree(self):
        if not self.awaiting_feedback:
            return

        if not self.is_flawed:
            self.data["friendship"] = max(-50, self.data["friendship"] - 3)
            self.set_mood("angry", f"It IS {self.real_ans}! Go verify on a TI-84, you paranoid mortal! (-3 Bond)")
            self.disable_feedback()
            self.save_and_refresh()
            return

        # Интерактивный спор
        u = self.data["user_name"]
        dialog = ctk.CTkInputDialog(
            text=f"Kesha: 'Alright {u}, prove it! What should {self.input_entry.get()} be?'",
            title="Debating Kesha"
        )
        user_input = dialog.get_input()

        if user_input:
            try:
                u_val = float(user_input.strip())
                r_val = float(self.real_ans)
                if math.isclose(u_val, r_val, abs_tol=1e-5):
                    self.data["iq"] = min(200, self.data["iq"] + 8)
                    self.data["friendship"] = min(100, self.data["friendship"] + 4)
                    self.data["debates_won"] += 1
                    self.data["math_rating"] += 30
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, str(self.real_ans))
                    self.set_mood("guilty", f"Ouch... It really is {self.real_ans}. You bested my logic gates! (+8 IQ, +30 Rating)")
                else:
                    self.data["ego"] = min(100, self.data["ego"] + 12)
                    self.data["math_rating"] = max(500, self.data["math_rating"] - 15)
                    self.set_mood("smug", f"You claimed {user_input}, but it's {self.real_ans}! You can't even count either!")
            except ValueError:
                self.set_mood("confused", "You typed gibberish instead of a number. Classic human behavior.")

        self.disable_feedback()
        self.check_achievements()
        self.save_and_refresh()

    def disable_feedback(self):
        self.btn_agree.configure(state="disabled")
        self.btn_disagree.configure(state="disabled")
        self.awaiting_feedback = False

    def wipe_memory(self):
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        self.data = MemoryManager.load()
        self.render_trophies()
        self.update_stats()
        self.set_mood("neutral", "Memory wipe complete. Core rebooted. Who are you again?")


if __name__ == "__main__":
    app = KeshaSentientOS()
    app.mainloop()
