import ast
import math
import operator
import sys
from typing import Any, Dict, List

# Цвета для красивого терминала (ANSI)
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"


class HardcoreCalculator:
    # Поддерживаемые математические операторы
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Встроенные функции
    FUNCTIONS = {
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "sqrt": math.sqrt,
        "cbrt": math.cbrt if hasattr(math, "cbrt") else lambda x: x ** (1 / 3),
        "log": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "abs": abs,
        "round": round,
        "fact": math.factorial,
        "deg": math.degrees,
        "rad": math.radians,
    }

    def __init__(self):
        # Базовые константы
        self.variables: Dict[str, Any] = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "phi": (1 + 5**0.5) / 2,
            "ans": 0,
        }
        self.history: List[str] = []

    def _eval_node(self, node: ast.AST) -> Any:
        """Рекурсивный безопасный обход синтаксического дерева (AST)."""
        # Числа (литералы)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, complex)):
                return node.value
            raise ValueError(f"Недопустимый тип значения: {node.value}")

        # Имена переменных
        elif isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            raise NameError(f"Переменная '{node.id}' не найдена")

        # Бинарные операции: 2 + 2, 5 * 3 и т.д.
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in self.OPERATORS:
                raise TypeError(f"Оператор {op_type.__name__} не поддерживается")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            return self.OPERATORS[op_type](left, right)

        # Унарные операции: -5, +3
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in self.OPERATORS:
                raise TypeError(f"Унарный оператор {op_type.__name__} не поддерживается")
            operand = self._eval_node(node.operand)
            return self.OPERATORS[op_type](operand)

        # Вызовы функций: sin(pi / 2)
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise TypeError("Вызов сложных функций не поддерживается")
            func_name = node.func.id
            if func_name not in self.FUNCTIONS:
                raise NameError(f"Функция '{func_name}' неизвестна")
            args = [self._eval_node(arg) for arg in node.args]
            return self.FUNCTIONS[func_name](*args)

        else:
            raise TypeError(f"Недопустимая синтаксическая конструкция: {type(node).__name__}")

    def execute(self, expression: str):
        """Парсинг и исполнение введённой строки."""
        expr = expression.strip()
        if not expr:
            return None

        # Замена степени символом ^ на питоновский **
        expr = expr.replace("^", "**")

        # Пробуем разобрать выражение через AST
        tree = ast.parse(expr, mode="exec")

        if not tree.body:
            return None

        stmt = tree.body[0]

        # Присваивание переменной: x = 10 + 5
        if isinstance(stmt, ast.Assign):
            if len(stmt.targets) != 1 or not isinstance(stmt.targets[0], ast.Name):
                raise ValueError("Присваивать можно только одной переменной (например: x = 5)")
            var_name = stmt.targets[0].id
            val = self._eval_node(stmt.value)
            self.variables[var_name] = val
            self.variables["ans"] = val
            self.history.append(f"{var_name} = {val}")
            return f"{var_name} = {val}"

        # Простое выражение: 10 + 5
        elif isinstance(stmt, ast.Expr):
            val = self._eval_node(stmt.value)
            self.variables["ans"] = val
            self.history.append(f"{expression} = {val}")
            return val

        else:
            raise ValueError("Неподдерживаемая инструкция")


def print_banner():
    print(f"""{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════╗
║             ★ HARDCORE PYTHON CALCULATOR ★               ║
║                                                          ║
║  • Функции: sin, cos, tan, sqrt, fact, ln, log, abs      ║
║  • Константы: pi, e, phi, ans                            ║
║  • Память: x = 5, y = x^2 + 10                           ║
║  • Команды: vars | history | help | clear | exit         ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")


def repl():
    calc = HardcoreCalculator()
    print_banner()

    while True:
        try:
            line = input(f"{MAGENTA}calc > {RESET}").strip()
            if not line:
                continue

            # Команды REPL
            cmd = line.lower()
            if cmd in ("exit", "quit", "q"):
                print(f"{YELLOW}Выход. Удачных вычислений!{RESET}")
                sys.exit(0)

            elif cmd == "clear":
                print("\033[H\033[J", end="")
                print_banner()
                continue

            elif cmd == "vars":
                print(f"\n{BOLD}Текущие переменные и константы:{RESET}")
                for k, v in calc.variables.items():
                    print(f"  {CYAN}{k}{RESET} = {GREEN}{v}{RESET}")
                print()
                continue

            elif cmd == "history":
                print(f"\n{BOLD}История вычислений:{RESET}")
                if not calc.history:
                    print("  История пуста.")
                for idx, item in enumerate(calc.history[-10:], 1):
                    print(f"  {idx}. {item}")
                print()
                continue

            elif cmd == "help":
                print_banner()
                continue

            # Вычисление
            result = calc.execute(line)
            if result is not None:
                # Округляем плавающую запятую для чистоты вывода, если возможно
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                print(f"{GREEN}{BOLD}=> {result}{RESET}")

        except (ZeroDivisionError, OverflowError) as e:
            print(f"{RED}[Математическая ошибка]: {e}{RESET}")
        except (SyntaxError, ValueError, TypeError, NameError) as e:
            print(f"{RED}[Ошибка]: {e}{RESET}")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{YELLOW}Сессия прервана.{RESET}")
            sys.exit(0)


if __name__ == "__main__":
    repl()