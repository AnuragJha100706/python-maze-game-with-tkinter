import os
import sqlite3
import hashlib
from tkinter import (
    Button,
    Canvas,
    Entry,
    Frame,
    Label,
    LEFT,
    Radiobutton,
    StringVar,
    Tk,
    Toplevel,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_USERS_DB = os.path.join(BASE_DIR, "users.db")

class LoginSystem:
    def __init__(self, db_file=None):
        self.db_file = db_file or DEFAULT_USERS_DB
        self.current_user = None
        self.root = None
        self.reg_window = None
        self.login_feedback = None
        self.reg_feedback = None
        self.init_db()

    def init_db(self):
        """Ensure users table exists in SQLite database."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        age INTEGER,
                        gender TEXT,
                        high_score INTEGER DEFAULT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing users database: {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def register_user_db(self, username, password, age, gender):
        """Database registration logic, returns (bool, message)."""
        username = username.strip()
        password = password.strip()

        if not username or not password or age is None or not gender:
            return False, "Please fill in all fields."

        try:
            age = int(age)
            if age < 1:
                return False, "Please enter a valid age."
        except (ValueError, TypeError):
            return False, "Age must be a valid number."

        hashed_password = self.hash_password(password)

        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password, age, gender) VALUES (?, ?, ?, ?)",
                    (username, hashed_password, age, str(gender))
                )
                conn.commit()
            return True, "Registration successful!"
        except sqlite3.IntegrityError:
            return False, "Username already exists. Try another."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

    def verify_user_db(self, username, password):
        """Database login authentication logic, returns (bool, message)."""
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return False, "Please enter username and password."

        hashed_password = self.hash_password(password)

        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT password FROM users WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row and row[0] == hashed_password:
                    return True, f"Welcome, {username}!"
                else:
                    return False, "Invalid username or password."
        except sqlite3.Error as e:
            return False, f"Database error: {e}"

    def _get_entry_val(self, entry, placeholder):
        val = entry.get().strip()
        return "" if val == placeholder else val

    def show_feedback(self, label, text, is_error=True):
        if label:
            color = "#e74c3c" if is_error else "#2ecc71"
            label.config(text=text, fg=color)

    def register_user(self):
        username = self._get_entry_val(self.entry_username_reg, "Username")
        password = self._get_entry_val(self.entry_password_reg, "Password")
        age = self._get_entry_val(self.entry_age, "Age")
        gender = self.gender_var.get()

        success, msg = self.register_user_db(username, password, age, gender)
        if success:
            self.show_feedback(self.reg_feedback, "Account created! You can now log in.", is_error=False)
            if self.reg_window:
                self.reg_window.after(700, lambda: self._on_register_success(username))
        else:
            self.show_feedback(self.reg_feedback, msg, is_error=True)

    def _on_register_success(self, username):
        if self.reg_window:
            self.reg_window.destroy()
            self.reg_window = None
        if self.entry_username:
            self.entry_username.delete(0, 'end')
            self.entry_username.insert(0, username)
            self.entry_username.config(fg="white")
        if self.login_feedback:
            self.show_feedback(self.login_feedback, "Account created! Please enter your password.", is_error=False)

    def login_user(self):
        username = self._get_entry_val(self.entry_username, "Username")
        password = self._get_entry_val(self.entry_password, "Password")

        success, msg = self.verify_user_db(username, password)
        if success:
            self.current_user = username
            self.show_feedback(self.login_feedback, f"Welcome, {username}! Launching game...", is_error=False)
            if self.root:
                self.root.after(450, self._on_login_success)
            return True
        else:
            self.show_feedback(self.login_feedback, msg, is_error=True)
            return False

    def _on_login_success(self):
        if self.reg_window:
            try:
                self.reg_window.destroy()
            except Exception:
                pass
        if self.root:
            self.root.destroy()

    def center_window(self, win, width, height):
        win.update_idletasks()
        screen_width = win.winfo_screenwidth()
        screen_height = win.winfo_screenheight()
        x = max(0, (screen_width // 2) - (width // 2))
        y = max(0, (screen_height // 2) - (height // 2) - 30)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def create_rounded_entry(self, placeholder, window, show="", is_password=False):
        canvas = Canvas(window, width=320, height=44, bg="#242a3a", highlightthickness=0)
        canvas.pack(pady=6)

        def round_rectangle(x1, y1, x2, y2, radius=12, **kwargs):
            points = [
                x1 + radius, y1,
                x2 - radius, y1,
                x2, y1,
                x2, y1 + radius,
                x2, y2 - radius,
                x2, y2,
                x2 - radius, y2,
                x1 + radius, y2,
                x1, y2,
                x1, y2 - radius,
                x1, y1 + radius,
                x1, y1
            ]
            return canvas.create_polygon(points, smooth=True, **kwargs)

        round_rectangle(3, 3, 317, 41, radius=8, fill="#1a1e2a", outline="#363e52", width=1)

        entry_width = 250 if is_password else 285
        entry = Entry(canvas, bg="#1a1e2a", fg="#94a3b8", font=self.label_font,
                      bd=0, highlightthickness=0, insertbackground="white")
        entry.insert(0, placeholder)

        is_visible = [False]

        def on_focus_in(_event):
            if entry.get() == placeholder:
                entry.delete(0, 'end')
                entry.config(fg="white")
                if show and not is_visible[0]:
                    entry.config(show=show)

        def on_focus_out(_event):
            if not entry.get().strip():
                if show:
                    entry.config(show="")
                entry.delete(0, 'end')
                entry.insert(0, placeholder)
                entry.config(fg="#888c9c")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.place(x=15, y=11, width=entry_width, height=22)

        if is_password:
            def toggle_eye():
                is_visible[0] = not is_visible[0]
                if entry.get() != placeholder:
                    entry.config(show="" if is_visible[0] else "*")
                eye_btn.config(text="👁" if not is_visible[0] else "🔒")

            eye_btn = Button(canvas, text="👁", font=("Arial", 9), bg="#1a1e2a", fg="#94a3b8",
                             activebackground="#1a1e2a", activeforeground="#f59e0b",
                             bd=0, cursor="hand2", command=toggle_eye)
            eye_btn.place(x=280, y=10, width=30, height=24)

        return entry

    def open_registration(self):
        if self.reg_window and Toplevel.winfo_exists(self.reg_window):
            self.reg_window.lift()
            return

        self.reg_window = Toplevel(self.root)
        self.reg_window.title("Register New User")
        self.reg_window.geometry("420x530")
        self.reg_window.configure(bg="#1a1e2a")
        self.reg_window.resizable(False, False)
        self.center_window(self.reg_window, 420, 530)
        self.reg_window.bind("<Return>", lambda _e: self.register_user())

        # Card container
        reg_card = Frame(self.reg_window, bg="#242a3a", highlightbackground="#363e52", highlightthickness=1)
        reg_card.pack(padx=25, pady=20, fill="both", expand=True)

        Label(reg_card, text="Create Account", font=("Segoe UI", 17, "bold"),
              bg="#242a3a", fg="#f59e0b").pack(pady=(18, 4))
        Label(reg_card, text="Join the maze challenge", font=("Segoe UI", 10),
              bg="#242a3a", fg="#94a3b8").pack(pady=(0, 10))

        self.entry_username_reg = self.create_rounded_entry("Username", reg_card)
        self.entry_password_reg = self.create_rounded_entry("Password", reg_card, show="*", is_password=True)
        self.entry_age = self.create_rounded_entry("Age", reg_card)

        gender_frame = Frame(reg_card, bg="#242a3a")
        gender_frame.pack(pady=6)
        Label(gender_frame, text="Gender: ", font=self.label_font, bg="#242a3a", fg="#f0f2f8").pack(side=LEFT, padx=5)

        self.gender_var = StringVar(value="Male")
        Radiobutton(gender_frame, text="Male", variable=self.gender_var, value="Male",
                    bg="#242a3a", fg="#f0f2f8", selectcolor="#1a1e2a", activebackground="#242a3a",
                    activeforeground="white").pack(side=LEFT, padx=8)
        Radiobutton(gender_frame, text="Female", variable=self.gender_var, value="Female",
                    bg="#242a3a", fg="#f0f2f8", selectcolor="#1a1e2a", activebackground="#242a3a",
                    activeforeground="white").pack(side=LEFT, padx=8)

        # Inline Feedback label
        self.reg_feedback = Label(reg_card, text="", font=("Segoe UI", 9, "bold"),
                                  bg="#242a3a", fg="#e74c3c", wraplength=310)
        self.reg_feedback.pack(pady=4)

        Button(reg_card, text="Create Account", font=("Segoe UI", 11, "bold"), bg="#f59e0b",
               fg="#1a1e2a", activebackground="#d97706", activeforeground="#1a1e2a",
               cursor="hand2", bd=0, width=20, height=1,
               command=self.register_user).pack(pady=(6, 8))

        Button(reg_card, text="Back to Login", font=("Segoe UI", 9, "underline"), bg="#242a3a",
               fg="#94a3b8", activebackground="#242a3a", activeforeground="#f59e0b",
               bd=0, cursor="hand2", command=self.reg_window.destroy).pack()

    def login(self):
        """Launches login window, waits for completion, and returns the username (or None)."""
        self.start()
        return self.current_user

    def start(self):
        self.root = Tk()
        self.root.title("Maze Game - Login")
        self.root.geometry("420x460")
        self.root.configure(bg="#1a1e2a")
        self.root.resizable(False, False)
        self.center_window(self.root, 420, 460)
        self.root.bind("<Return>", lambda _e: self.login_user())

        self.label_font = ("Segoe UI", 10)

        # Card container
        card = Frame(self.root, bg="#242a3a", highlightbackground="#363e52", highlightthickness=1)
        card.pack(padx=25, pady=20, fill="both", expand=True)

        Label(card, text="Yet Another Maze", font=("Segoe UI", 19, "bold"),
              bg="#242a3a", fg="#f59e0b").pack(pady=(22, 4))
        Label(card, text="Sign in to your account", font=("Segoe UI", 10),
              bg="#242a3a", fg="#94a3b8").pack(pady=(0, 16))

        self.entry_username = self.create_rounded_entry("Username", card)
        self.entry_password = self.create_rounded_entry("Password", card, show="*", is_password=True)

        # Inline feedback label
        self.login_feedback = Label(card, text="", font=("Segoe UI", 9, "bold"),
                                   bg="#242a3a", fg="#e74c3c", wraplength=310)
        self.login_feedback.pack(pady=4)

        Button(card, text="Sign In", font=("Segoe UI", 11, "bold"), bg="#f59e0b", fg="#1a1e2a",
               activebackground="#d97706", activeforeground="#1a1e2a",
               cursor="hand2", bd=0, width=20, height=1,
               command=self.login_user).pack(pady=(8, 12))

        Button(card, text="Don't have an account? Register", font=("Segoe UI", 9, "underline"),
               bg="#242a3a", fg="#60a5fa", activebackground="#242a3a", activeforeground="#93c5fd",
               bd=0, cursor="hand2", command=self.open_registration).pack(pady=4)

        self.root.mainloop()

if __name__ == "__main__":
    login_system = LoginSystem()
    user = login_system.login()
    print("Logged in as:", user)