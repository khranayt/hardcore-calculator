import ast
import math
import operator
import customtkinter as ctk

# Настройка общей темы
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class HardcoreEngine:
    """Безопасный математический движок на базе AST."""
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "sqrt": math.sqrt,
        "ln": math.log,
        "log": math.log10,
        "fact": math.factorial,
        "abs": abs,
    }

    def __init__(self):
        self.variables = {
            "pi": math.pi,
            "e": math.e,
            "ans": 0,
        }

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            raise NameError(f"Неизвестно: {node.id}")
        elif isinstance(node, ast.BinOp):
            return self.OPERATORS[type(node.op)](self._eval(node.left), self._eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self.OPERATORS[type(node.op)](self._eval(node.operand))
        elif isinstance(node, ast.Call):
            func = self.FUNCTIONS[node.func.id]
            args = [self._eval(arg) for arg in node.args]
            return func(*args)
        raise ValueError("Синтаксис неверен")

    def evaluate(self, expr: str):
        cleaned = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
        tree = ast.parse(cleaned, mode="eval")
        res = self._eval(tree.body)
        self.variables["ans"] = res
        return res


class ModernCalculator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.engine = HardcoreEngine()

        self.title("⚡ Hardcore Calculator")
        self.geometry("380x600")
        self.resizable(False, False)

        # Контейнер дисплея
        self.display_frame = ctk.CTkFrame(self, fg_color="#18181b", corner_radius=15)
        self.display_frame.pack(padx=20, pady=(20, 10), fill="both")

        # История предыдущего выражения
        self.history_label = ctk.CTkLabel(
            self.display_frame, text="", text_color="#71717a", font=("Consolas", 14), anchor="e"
        )
        self.history_label.pack(fill="x", padx=15, pady=(10, 0))

        # Главное поле ввода
        self.entry = ctk.CTkEntry(
            self.display_frame,
            font=("Consolas", 28, "bold"),
            text_color="#f4f4f5",
            fg_color="transparent",
            border_width=0,
            justify="right",
        )
        self.entry.pack(fill="x", padx=10, pady=(0, 10))
        self.entry.focus_set()

        # Биндим нажатие Enter на клавиатуре
        self.bind("<Return>", lambda event: self.calculate())

        # Сетка кнопок
        self.create_buttons()

    def create_buttons(self):
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # Раскладка кнопок
        layout = [
            [("sin", "fn"), ("cos", "fn"), ("tan", "fn"), ("sqrt", "fn"), ("^", "op")],
            [("ln", "fn"),  ("fact", "fn"),("pi", "fn"),  ("e", "fn"),    ("ans", "fn")],
            [("C", "danger"), ("(", "op"), (")", "op"),   ("⌫", "danger"),("÷", "op")],
            [("7", "num"),  ("8", "num"),  ("9", "num"),  ("×", "op")],
            [("4", "num"),  ("5", "num"),  ("6", "num"),  ("-", "op")],
            [("1", "num"),  ("2", "num"),  ("3", "num"),  ("+", "op")],
            [("0", "num"),  (".", "num"),  ("=", "equal")]
        ]

        # Цветовая палитра элементов
        colors = {
            "num":    {"fg": "#27272a", "hover": "#3f3f46", "text": "#ffffff"},
            "op":     {"fg": "#3b82f6", "hover": "#2563eb", "text": "#ffffff"},
            "fn":     {"fg": "#1e293b", "hover": "#334155", "text": "#38bdf8"},
            "danger": {"fg": "#ef4444", "hover": "#dc2626", "text": "#ffffff"},
            "equal":  {"fg": "#10b981", "hover": "#059669", "text": "#ffffff"}
        }

        for r_idx, row in enumerate(layout):
            for c_idx, (text, b_type) in enumerate(row):
                cfg = colors[b_type]
                colspan = 1

                # Удлиняем кнопку "=" в последнем ряду
                if text == "=":
                    colspan = 2

                btn = ctk.CTkButton(
                    btn_frame,
                    text=text,
                    font=("Consolas", 16, "bold"),
                    fg_color=cfg["fg"],
                    hover_color=cfg["hover"],
                    text_color=cfg["text"],
                    corner_radius=10,
                    width=60,
                    height=45,
                    command=lambda t=text: self.on_click(t),
                )
                btn.grid(row=r_idx, column=c_idx, columnspan=colspan, padx=3, pady=3, sticky="nsew")

        # Пропорции колонок
        for i in range(5):
            btn_frame.grid_columnconfigure(i, weight=1)

    def on_click(self, char):
        if char == "C":
            self.entry.delete(0, "end")
            self.history_label.configure(text="")
        elif char == "⌫":
            curr = self.entry.get()
            self.entry.delete(0, "end")
            self.entry.insert(0, curr[:-1])
        elif char == "=":
            self.calculate()
        elif char in ("sin", "cos", "tan", "sqrt", "ln", "fact"):
            self.entry.insert("end", f"{char}(")
        else:
            self.entry.insert("end", char)

    def calculate(self):
        expr = self.entry.get().strip()
        if not expr:
            return

        try:
            res = self.engine.evaluate(expr)
            # Округляем дроби до 8 знаков, если это не целое число
            if isinstance(res, float):
                if res.is_integer():
                    res = int(res)
                else:
                    res = round(res, 8)

            self.history_label.configure(text=f"{expr} =")
            self.entry.delete(0, "end")
            self.entry.insert(0, str(res))
        except ZeroDivisionError:
            self.history_label.configure(text="Деление на ноль!")
        except Exception:
            self.history_label.configure(text="Синтаксическая ошибка!")


if __name__ == "__main__":
    app = ModernCalculator()
    app.mainloop()
