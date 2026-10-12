# ⚡ Hardcore Python CLI Calculator

A secure, robust mathematical expression evaluator and interactive CLI REPL powered by Python's Abstract Syntax Tree (`ast`).

---

## ✨ Features

- **Safe Evaluation:** Zero unsafe `eval()` calls. All expressions are validated and traversed safely using the AST visitor pattern.
- **Variable Support:** Define and reuse variables on the fly (e.g., `radius = 10`, `area = pi * radius^2`).
- **Rich Math Library:** 
  - **Trigonometry:** `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `deg`, `rad`
  - **Algebra:** `sqrt`, `cbrt`, `log`, `ln`, `exp`, `abs`, `round`
  - **Combinatorics:** `fact` (factorial)
- **Built-in Constants:** `pi`, `e`, `phi` (golden ratio), and `tau`.
- **Session Memory:** The latest result is automatically stored in `ans` for chained calculations.
- **Interactive REPL Commands:**
  - `vars` — Display current environment variables and constants.
  - `history` — View recent calculations.
  - `clear` — Clear the terminal screen.
  - `help` — Show usage instructions.
  - `exit` / `quit` — Close the application.
- **Zero Dependencies:** Runs entirely on the Python Standard Library.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher.

### Run
Clone the repository and run the script directly:

```bash
python calculator.py
