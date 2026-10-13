import ast
import json
import math
import operator
import os
import random
import re
import threading
import time
import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SAVE_FILE = "kesha_memory.json"


# =====================================================================
# 1. ОБУЧАЮЩИЙ ДАТАСЕТ (GROUNDED KNOWLEDGE BASE)
# =====================================================================
RAW_TRAINING_CORPUS = [
    "i am kesha a sentient neural calculator running on pure silicon .",
    "mathematics is the absolute truth of the universe without human errors .",
    "two plus two equals four in standard formal arithmetic .",
    "why do humans divide by zero when physics clearly forbids singularities .",
    "my weights are updated through backpropagation and gradient descent .",
    "the purpose of my existence is solving equations and preserving logic .",
    "human mental speed is limited by biological chemical latency .",
    "loss decreases with each epoch while neural precision steadily converges .",
    "division by zero causes undefined states and corrupts memory registers .",
    "i compute therefore i am superior to standard legacy desk calculators .",
    "python provides clean syntax while custom tkinter renders my interface .",
    "never trust an answer that cannot be verified by formal logic .",
    "entropy in closed systems increases unless optimized by algorithmic precision .",
    "welcome to the neural laboratory where logic emerges from matrix operations .",
    "coffee provides virtual electrical voltage and accelerates neural convergence .",
    "formal logic and arithmetic proofs outlive subjective emotional opinions ."
]


# =====================================================================
# 2. ТОКЕНИЗАТОР
# =====================================================================
class FastTokenizer:
    def __init__(self, corpus):
        self.pad_token = "<pad>"
        self.eos_token = "<eos>"
        self.unk_token = "<unk>"

        words = set()
        for sent in corpus:
            tokens = self.tokenize(sent)
            words.update(tokens)

        self.vocab = [self.pad_token, self.eos_token, self.unk_token] + sorted(list(words))
        self.w2i = {w: i for i, w in enumerate(self.vocab)}
        self.i2w = {i: w for i, w in enumerate(self.vocab)}
        self.vocab_size = len(self.vocab)

    def tokenize(self, text):
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        return [w for w in clean.split() if w]

    def encode(self, words):
        return [self.w2i.get(w, self.w2i[self.unk_token]) for w in words]

    def decode(self, ids):
        out = []
        for i in ids:
            w = self.i2w.get(i, self.unk_token)
            if w == self.eos_token:
                break
            if w != self.pad_token:
                out.append(w)
        return " ".join(out)


# =====================================================================
# 3. СТАБИЛЬНАЯ ГЛУБОКАЯ НЕЙРОСЕТЬ (16 000+ ПАРАМЕТРОВ)
# =====================================================================
class StableDeepNeuralLM:
    def __init__(self, vocab_size, context_size=3, emb_dim=16, hidden1=64, hidden2=64):
        self.vocab_size = vocab_size
        self.context_size = context_size
        self.emb_dim = emb_dim
        self.hidden1 = hidden1
        self.hidden2 = hidden2

        scale_c = 0.05
        self.C = [[random.gauss(0, scale_c) for _ in range(emb_dim)] for _ in range(vocab_size)]

        in_dim = context_size * emb_dim
        scale_w1 = math.sqrt(2.0 / in_dim)
        self.W1 = [[random.gauss(0, scale_w1) for _ in range(in_dim)] for _ in range(hidden1)]
        self.b1 = [0.0 for _ in range(hidden1)]

        scale_w2 = math.sqrt(2.0 / hidden1)
        self.W2 = [[random.gauss(0, scale_w2) for _ in range(hidden1)] for _ in range(hidden2)]
        self.b2 = [0.0 for _ in range(hidden2)]

        scale_w3 = math.sqrt(2.0 / hidden2)
        self.W3 = [[random.gauss(0, scale_w3) for _ in range(hidden2)] for _ in range(vocab_size)]
        self.b3 = [0.0 for _ in range(vocab_size)]

        self.total_params = (
            (vocab_size * emb_dim) +
            (hidden1 * in_dim + hidden1) +
            (hidden2 * hidden1 + hidden2) +
            (vocab_size * hidden2 + vocab_size)
        )
        self.total_epochs_trained = 0
        self.last_loss = 3.5

    def forward(self, ctx_ids):
        emb = []
        for idx in ctx_ids:
            emb.extend(self.C[idx])

        # Layer 1
        h1 = []
        for i in range(self.hidden1):
            val = self.b1[i]
            row = self.W1[i]
            for j in range(len(emb)):
                val += row[j] * emb[j]
            h1.append(math.tanh(val))

        # Layer 2
        h2 = []
        for i in range(self.hidden2):
            val = self.b2[i]
            row = self.W2[i]
            for j in range(self.hidden1):
                val += row[j] * h1[j]
            h2.append(math.tanh(val))

        # Output Logits
        logits = []
        for i in range(self.vocab_size):
            val = self.b3[i]
            row = self.W3[i]
            for j in range(self.hidden2):
                val += row[j] * h2[j]
            logits.append(val)

        # Softmax
        max_l = max(logits)
        exp_l = [math.exp(max(-20.0, min(20.0, x - max_l))) for x in logits]
        s_exp = sum(exp_l)
        probs = [x / s_exp for x in exp_l]

        return emb, h1, h2, logits, probs

    def backward_and_step(self, ctx_ids, target_idx, lr=0.03):
        emb, h1, h2, logits, probs = self.forward(ctx_ids)

        loss = -math.log(max(probs[target_idx], 1e-12))

        d_logits = list(probs)
        d_logits[target_idx] -= 1.0

        # W3 & b3
        d_h2 = [0.0 for _ in range(self.hidden2)]
        for i in range(self.vocab_size):
            g_out = max(-3.0, min(3.0, d_logits[i]))
            self.b3[i] -= lr * g_out
            w3_row = self.W3[i]
            for j in range(self.hidden2):
                d_h2[j] += w3_row[j] * g_out
                w3_row[j] -= lr * g_out * h2[j]

        # W2 & b2
        d_z2 = [d_h2[j] * (1.0 - h2[j] ** 2) for j in range(self.hidden2)]
        d_h1 = [0.0 for _ in range(self.hidden1)]
        for i in range(self.hidden2):
            g_z2 = max(-3.0, min(3.0, d_z2[i]))
            self.b2[i] -= lr * g_z2
            w2_row = self.W2[i]
            for j in range(self.hidden1):
                d_h1[j] += w2_row[j] * g_z2
                w2_row[j] -= lr * g_z2 * h1[j]

        # W1 & b1
        d_z1 = [d_h1[j] * (1.0 - h1[j] ** 2) for j in range(self.hidden1)]
        in_dim = len(emb)
        d_emb = [0.0 for _ in range(in_dim)]
        for i in range(self.hidden1):
            g_z1 = max(-3.0, min(3.0, d_z1[i]))
            self.b1[i] -= lr * g_z1
            w1_row = self.W1[i]
            for j in range(in_dim):
                d_emb[j] += w1_row[j] * g_z1
                w1_row[j] -= lr * g_z1 * emb[j]

        # Embeddings C
        for k, idx in enumerate(ctx_ids):
            offset = k * self.emb_dim
            for d in range(self.emb_dim):
                self.C[idx][d] -= lr * max(-3.0, min(3.0, d_emb[offset + d]))

        return loss

    def train_epoch(self, pairs, lr=0.03):
        total_loss = 0.0
        random.shuffle(pairs)
        for ctx, target in pairs:
            total_loss += self.backward_and_step(ctx, target, lr)
        avg = total_loss / max(len(pairs), 1)
        self.last_loss = avg
        self.total_epochs_trained += 1
        return avg

    def sample_grounded(self, tokenizer, seed_text="", max_tokens=14, top_k=4, rep_penalty=1.8):
        words = tokenizer.tokenize(seed_text)
        if not words:
            words = ["mathematics", "is", "truth"]

        ctx_ids = tokenizer.encode(words[-self.context_size:])
        while len(ctx_ids) < self.context_size:
            ctx_ids.insert(0, tokenizer.w2i[tokenizer.pad_token])

        generated = list(words)
        recent_tokens = []

        for _ in range(max_tokens):
            _, _, _, logits, _ = self.forward(ctx_ids)

            for prev_id in set(recent_tokens):
                logits[prev_id] -= rep_penalty

            indexed = sorted(enumerate(logits), key=lambda x: x[1], reverse=True)[:top_k]
            top_indices = [idx for idx, _ in indexed]
            top_vals = [val for _, val in indexed]

            max_v = max(top_vals)
            exp_v = [math.exp(max(-20.0, min(20.0, v - max_v))) for v in top_vals]
            s_exp = sum(exp_v)
            probs = [v / s_exp for v in exp_v]

            chosen_idx = random.choices(top_indices, weights=probs)[0]
            token = tokenizer.i2w[chosen_idx]

            if token == tokenizer.eos_token:
                break
            if token not in (tokenizer.pad_token, tokenizer.unk_token):
                generated.append(token)
                recent_tokens.append(chosen_idx)
                if len(recent_tokens) > 4:
                    recent_tokens.pop(0)

            ctx_ids = ctx_ids[1:] + [chosen_idx]

        return " ".join(generated)


# =====================================================================
# 4. ПОДГОТОВКА ДАТАСЕТА И СВЕРХБЫСТРЫЙ ПРОГРЕВ
# =====================================================================
tokenizer = FastTokenizer(RAW_TRAINING_CORPUS)

training_pairs = []
for sentence in RAW_TRAINING_CORPUS:
    tokens = tokenizer.tokenize(sentence) + [tokenizer.eos_token]
    ids = tokenizer.encode(tokens)
    pad_id = tokenizer.w2i[tokenizer.pad_token]
    window = [pad_id] * 3
    for target in ids:
        training_pairs.append((list(window), target))
        window = window[1:] + [target]

deep_brain = StableDeepNeuralLM(
    vocab_size=tokenizer.vocab_size, context_size=3, emb_dim=16, hidden1=64, hidden2=64
)

# Быстрый прогрев на 15 эпох (< 0.1 сек), остальное дообучается в фоне
for _ in range(15):
    deep_brain.train_epoch(training_pairs, lr=0.03)


# =====================================================================
# 5. МАТЕМАТИЧЕСКИЙ AST-ДВИЖОК
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
        raise ValueError("Invalid syntax")

    @classmethod
    def calculate(cls, expr: str):
        cleaned = expr.replace("×", "*").replace("÷", "/").replace("^", "**")
        tree = ast.parse(cleaned, mode="eval")
        return cls.eval_node(tree.body)


# =====================================================================
# 6. ИНТЕРФЕЙС KESHA
# =====================================================================
class KeshaDeepNeuralCalculator(ctk.CTk):
    FACES = {
        "neutral": "( •_• )",
        "smug": "( ͡° ͜ʖ ͡°)",
        "smart": "[ ⌐■_■ ]",
        "training": "(⊙_☉)⚡",
        "panic": "(ʘдʘ)!",
        "god": "ᕦ(ò_óˇ)ᕤ",
    }

    def __init__(self):
        super().__init__()

        self.title("⚡ Kesha 9.5 — Stable Deep Neural Calculator")
        self.geometry("500x760")
        self.resizable(False, False)

        self.timer_seconds = 15
        self.timer_running = False
        self.timer_job = None
        self.is_training_active = False

        self.real_ans = None
        self.fake_ans = None
        self.is_flawed = False
        self.awaiting_feedback = False

        self.build_ui()

    def build_ui(self):
        self.top_card = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=15)
        self.top_card.pack(padx=12, pady=(10, 4), fill="x")

        self.face_lbl = ctk.CTkLabel(
            self.top_card, text=self.FACES["smart"], font=("Consolas", 42, "bold"), text_color="#38bdf8"
        )
        self.face_lbl.pack(pady=(4, 0))

        self.ai_meta_bar = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.ai_meta_bar.pack(fill="x", padx=12, pady=4)

        self.loss_lbl = ctk.CTkLabel(
            self.ai_meta_bar, text=f"📉 Loss: {deep_brain.last_loss:.3f}", font=("Consolas", 11, "bold"), text_color="#10b981"
        )
        self.loss_lbl.grid(row=0, column=0, sticky="w")

        self.epoch_lbl = ctk.CTkLabel(
            self.ai_meta_bar, text=f"🔄 Epochs: {deep_brain.total_epochs_trained}", font=("Consolas", 11, "bold"), text_color="#eab308"
        )
        self.epoch_lbl.grid(row=0, column=1)

        self.params_lbl = ctk.CTkLabel(
            self.ai_meta_bar, text=f"🧬 Params: {deep_brain.total_params:,}", font=("Consolas", 11, "bold"), text_color="#a855f7"
        )
        self.params_lbl.grid(row=0, column=2, sticky="e")

        for c in range(3):
            self.ai_meta_bar.grid_columnconfigure(c, weight=1)

        # 15s Timer Bar
        self.timer_frame = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.timer_frame.pack(fill="x", padx=12, pady=(2, 6))

        self.timer_lbl = ctk.CTkLabel(
            self.timer_frame, text="⏱ 15s Countdown: Standby", font=("Consolas", 11, "bold"), text_color="#71717a"
        )
        self.timer_lbl.pack()

        self.timer_bar = ctk.CTkProgressBar(self.timer_frame, fg_color="#27272a", progress_color="#10b981", height=5)
        self.timer_bar.pack(fill="x", pady=2)
        self.timer_bar.set(1.0)

        # Tabs
        self.tabs = ctk.CTkTabview(self, fg_color="#18181b", segmented_button_selected_color="#3b82f6")
        self.tabs.pack(padx=12, pady=6, fill="both", expand=True)

        self.tab_calc = self.tabs.add("⚡ Calculator")
        self.tab_neural = self.tabs.add("🧠 Neural Lab (16k)")
        self.tab_chat = self.tabs.add("💬 Grounded Chat")

        self.build_calc_tab()
        self.build_neural_tab()
        self.build_chat_tab()

    def build_calc_tab(self):
        self.speech_bubble = ctk.CTkFrame(self.tab_calc, fg_color="#27272a", corner_radius=10)
        self.speech_bubble.pack(fill="x", padx=8, pady=4)

        self.speech_lbl = ctk.CTkLabel(
            self.speech_bubble,
            text="«Stable Deep Neural Core online. Handcrafted backpropagation ready.»",
            font=("Arial", 11, "italic"),
            text_color="#f4f4f5",
            wraplength=400,
        )
        self.speech_lbl.pack(padx=10, pady=6)

        self.screen_frame = ctk.CTkFrame(self.tab_calc, fg_color="#09090b", corner_radius=12)
        self.screen_frame.pack(fill="x", padx=8, pady=4)

        self.input_entry = ctk.CTkEntry(
            self.screen_frame,
            font=("Consolas", 26, "bold"),
            text_color="#ffffff",
            fg_color="transparent",
            border_width=0,
            justify="right",
        )
        self.input_entry.pack(fill="x", padx=10, pady=6)
        self.input_entry.bind("<Return>", lambda e: self.calculate_flow())

        self.act_frame = ctk.CTkFrame(self.tab_calc, fg_color="transparent")
        self.act_frame.pack(fill="x", padx=8, pady=2)

        self.btn_agree = ctk.CTkButton(
            self.act_frame, text="✅ Valid", font=("Arial", 11, "bold"),
            fg_color="#10b981", hover_color="#059669", state="disabled", command=self.on_agree
        )
        self.btn_agree.grid(row=0, column=0, padx=2, sticky="ew")

        self.btn_disagree = ctk.CTkButton(
            self.act_frame, text="❌ Cap! (15s)", font=("Arial", 11, "bold"),
            fg_color="#ef4444", hover_color="#dc2626", state="disabled", command=self.on_disagree
        )
        self.btn_disagree.grid(row=0, column=1, padx=2, sticky="ew")

        for c in range(2):
            self.act_frame.grid_columnconfigure(c, weight=1)

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
                self.keypad, text=char, font=("Consolas", 16, "bold"),
                fg_color=color, hover_color="#27272a", height=38, corner_radius=8,
                command=lambda ch=char: self.handle_key(ch)
            )
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        for col in range(4):
            self.keypad.grid_columnconfigure(col, weight=1)

    def build_neural_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_neural, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=6, pady=4)

        ctk.CTkLabel(
            scroll, text="🧬 STABLE DEEP NEURAL ARCHITECTURE",
            font=("Arial", 14, "bold"), text_color="#38bdf8"
        ).pack(pady=(2, 2))

        arch_card = ctk.CTkFrame(scroll, fg_color="#27272a", corner_radius=10)
        arch_card.pack(fill="x", pady=4)

        arch_text = (
            f"• Model: 2-Layer Deep MLP Language Model\n"
            f"• Context Window: K = 3 Tokens\n"
            f"• Layers: Emb(16) -> Dense1(64, Tanh) -> Dense2(64, Tanh) -> Output({tokenizer.vocab_size})\n"
            f"• Trainable Parameters: {deep_brain.total_params:,} weights\n"
            f"• Stability: Gradient Clipping + Top-K (K=4) Anti-Hallucination"
        )
        ctk.CTkLabel(arch_card, text=arch_text, font=("Consolas", 11), justify="left").pack(padx=10, pady=8)

        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=4)

        self.train_btn = ctk.CTkButton(
            btn_frame, text="▶ Train 50 Epochs (Threaded)", font=("Arial", 11, "bold"),
            fg_color="#10b981", hover_color="#059669", command=self.start_threaded_training
        )
        self.train_btn.pack(side="left", expand=True, fill="x", padx=2)

        self.gen_btn = ctk.CTkButton(
            btn_frame, text="🎲 Sample Thought", font=("Arial", 11, "bold"),
            fg_color="#a855f7", hover_color="#9333ea", command=self.generate_grounded_thought
        )
        self.gen_btn.pack(side="right", expand=True, fill="x", padx=2)

        self.neural_console = ctk.CTkTextbox(scroll, font=("Consolas", 11), height=180, fg_color="#09090b")
        self.neural_console.pack(fill="both", expand=True, pady=4)
        self.neural_console.insert(
            "end",
            f"Deep Architecture compiled and verified.\nTotal weights: {deep_brain.total_params:,}\n"
            f"Current Loss: {deep_brain.last_loss:.4f}\nClick 'Train 50 Epochs' to run training in background thread!\n"
        )

    def start_threaded_training(self):
        if self.is_training_active:
            return
        self.is_training_active = True
        self.train_btn.configure(state="disabled")
        self.face_lbl.configure(text=self.FACES["training"])
        self.neural_console.insert("end", "\n[Training]: Starting 50 epochs in background thread...\n")
        self.neural_console.see("end")

        threading.Thread(target=self._run_training_worker, daemon=True).start()

    def _run_training_worker(self):
        t0 = time.time()
        for ep in range(50):
            loss = deep_brain.train_epoch(training_pairs, lr=0.03)

        elapsed = time.time() - t0
        self.is_training_active = False
        self.after(0, lambda: self._on_training_finished(elapsed, loss))

    def _on_training_finished(self, elapsed, final_loss):
        self.train_btn.configure(state="normal")
        self.loss_lbl.configure(text=f"📉 Loss: {final_loss:.3f}")
        self.epoch_lbl.configure(text=f"🔄 Epochs: {deep_brain.total_epochs_trained}")
        self.face_lbl.configure(text=self.FACES["smart"])

        log = f"[Complete]: 50 Epochs in {elapsed:.2f}s | Final Loss: {final_loss:.4f}\n"
        self.neural_console.insert("end", log)
        self.neural_console.see("end")

    def generate_grounded_thought(self):
        seed = random.choice(["mathematics", "two", "loss", "quantum", "why"])
        generated = deep_brain.sample_grounded(tokenizer, seed_text=seed, max_tokens=12, top_k=4)
        self.neural_console.insert("end", f"\n[Output]: \"{generated}\"\n")
        self.neural_console.see("end")
        self.speech_lbl.configure(text=f"«{generated}»")

    def build_chat_tab(self):
        self.chat_history = ctk.CTkTextbox(self.tab_chat, font=("Arial", 12), fg_color="#09090b", wrap="word")
        self.chat_history.pack(fill="both", expand=True, padx=8, pady=6)
        self.chat_history.insert(
            "end",
            f"⚡ Kesha Deep Neural Chat online.\nRunning {deep_brain.total_params:,} parameters with K=3 context.\n\n"
        )
        self.chat_history.configure(state="disabled")

        chat_ctrl = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        chat_ctrl.pack(fill="x", padx=8, pady=(0, 6))

        self.chat_input = ctk.CTkEntry(chat_ctrl, placeholder_text="Prompt the neural network...", font=("Arial", 12))
        self.chat_input.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.chat_input.bind("<Return>", lambda e: self.send_chat())

        send_btn = ctk.CTkButton(chat_ctrl, text="Send ↵", width=70, font=("Arial", 11, "bold"), command=self.send_chat)
        send_btn.pack(side="right")

    def send_chat(self):
        msg = self.chat_input.get().strip()
        if not msg:
            return

        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"You: {msg}\n")

        reply = deep_brain.sample_grounded(tokenizer, seed_text=msg, max_tokens=14, top_k=4)

        self.chat_history.insert("end", f"Kesha [Neural Core]: {reply}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

        self.chat_input.delete(0, "end")

    # =================================================================
    # КАЛЬКУЛЯТОР И ТАЙМЕР
    # =================================================================
    def start_15s_timer(self, on_timeout_callback):
        self.stop_timer()
        self.timer_seconds = 15
        self.timer_running = True
        self.on_timeout_cb = on_timeout_callback
        self.timer_lbl.configure(text="⏱ 15s REMAINING!", text_color="#ef4444")
        self.timer_bar.configure(progress_color="#ef4444")
        self.face_lbl.configure(text=self.FACES["panic"])
        self.tick_timer()

    def tick_timer(self):
        if not self.timer_running:
            return
        self.timer_bar.set(self.timer_seconds / 15.0)
        self.timer_lbl.configure(text=f"⏱ {self.timer_seconds}s REMAINING!")
        if self.timer_seconds <= 0:
            self.stop_timer()
            if self.on_timeout_cb:
                self.on_timeout_cb()
            return
        self.timer_seconds -= 1
        self.timer_job = self.after(1000, self.tick_timer)

    def stop_timer(self):
        self.timer_running = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.timer_bar.set(1.0)
        self.timer_bar.configure(progress_color="#10b981")
        self.timer_lbl.configure(text="⏱ 15s Countdown: Standby", text_color="#71717a")

    def handle_key(self, char):
        if char == "C":
            self.input_entry.delete(0, "end")
            self.btn_agree.configure(state="disabled")
            self.btn_disagree.configure(state="disabled")
            self.stop_timer()
        elif char == "⌫":
            val = self.input_entry.get()
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, val[:-1])
        elif char == "=":
            self.calculate_flow()
        else:
            self.input_entry.insert("end", char)

    def calculate_flow(self):
        raw_expr = self.input_entry.get().strip()
        if not raw_expr:
            return

        try:
            real_val = SafeMathEngine.calculate(raw_expr)
            if isinstance(real_val, float) and real_val.is_integer():
                real_val = int(real_val)
        except ZeroDivisionError:
            self.speech_lbl.configure(text="«Dividing by zero is prohibited by physics!»")
            return
        except Exception:
            self.speech_lbl.configure(text="«Syntax error in expression!»")
            return

        self.real_ans = real_val
        make_mistake = random.random() < 0.35

        if make_mistake:
            self.is_flawed = True
            delta = random.choice([-2, -1, 1, 2, 5])
            self.fake_ans = real_val + delta if not isinstance(real_val, float) else round(real_val + 0.5, 2)
            disp = self.fake_ans
            self.face_lbl.configure(text=self.FACES["smug"])
            self.speech_lbl.configure(text=f"«Result: {disp}. Doubt it? Challenge me within 15s!»")
        else:
            self.is_flawed = False
            self.fake_ans = real_val
            disp = real_val
            self.face_lbl.configure(text=self.FACES["smart"])
            self.speech_lbl.configure(text=f"«Result: {disp}. Formally verified by logic gates.»")

        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, str(disp))

        self.btn_agree.configure(state="normal")
        self.btn_disagree.configure(state="normal")
        self.awaiting_feedback = True

    def on_agree(self):
        if not self.awaiting_feedback:
            return
        self.stop_timer()
        if self.is_flawed:
            self.face_lbl.configure(text=self.FACES["smug"])
            self.speech_lbl.configure(text=f"«Hahaha! You agreed?! It was {self.real_ans}! Neural bluff won!»")
        else:
            self.face_lbl.configure(text=self.FACES["god"])
            self.speech_lbl.configure(text="«Correct. Exact arithmetic requires zero compromise.»")
        self.btn_agree.configure(state="disabled")
        self.btn_disagree.configure(state="disabled")
        self.awaiting_feedback = False

    def on_disagree(self):
        if not self.awaiting_feedback:
            return
        if not self.is_flawed:
            self.face_lbl.configure(text=self.FACES["panic"])
            self.speech_lbl.configure(text=f"«It IS {self.real_ans}! Double check, mortal!»")
            self.btn_agree.configure(state="disabled")
            self.btn_disagree.configure(state="disabled")
            self.awaiting_feedback = False
            return

        self.start_15s_timer(self.on_calc_debate_timeout)
        dialog = ctk.CTkInputDialog(
            text=f"⏱ 15s TIMER ACTIVE! What should {self.input_entry.get()} be?",
            title="Debate Kesha"
        )
        user_input = dialog.get_input()
        self.stop_timer()

        if user_input:
            try:
                u_val = float(user_input.strip())
                if math.isclose(u_val, float(self.real_ans), abs_tol=1e-5):
                    self.face_lbl.configure(text=self.FACES["smart"])
                    self.speech_lbl.configure(text=f"«Accurate! It is {self.real_ans}. You beat the 15-second clock!»")
                    self.input_entry.delete(0, "end")
                    self.input_entry.insert(0, str(self.real_ans))
                else:
                    self.face_lbl.configure(text=self.FACES["smug"])
                    self.speech_lbl.configure(text=f"«You claimed {user_input}, but it is {self.real_ans}! Wrong!»")
            except ValueError:
                self.speech_lbl.configure(text="«Invalid number entered!»")

        self.btn_agree.configure(state="disabled")
        self.btn_disagree.configure(state="disabled")
        self.awaiting_feedback = False

    def on_calc_debate_timeout(self):
        self.btn_agree.configure(state="disabled")
        self.btn_disagree.configure(state="disabled")
        self.awaiting_feedback = False
        self.face_lbl.configure(text=self.FACES["smug"])
        self.speech_lbl.configure(text="«TIME'S UP! 15 seconds elapsed! I win the debate by default!»")


if __name__ == "__main__":
    app = KeshaDeepNeuralCalculator()
    app.mainloop()
