import sqlite3
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_FILE = os.path.join(BASE_DIR, 'maze_scores.db')
DEFAULT_CSV_FILE = os.path.join(BASE_DIR, 'scores.csv')
USERS_DB_FILE = os.path.join(BASE_DIR, 'users.db')

class ScoreDB:
    def __init__(self, db_file=None, csv_file=None):
        self.db_file = db_file or DEFAULT_DB_FILE
        self.csv_file = csv_file or DEFAULT_CSV_FILE
        self.init_db()
        self.sync_csv_to_db()

    def init_db(self):
        """Initialize the SQLite database table for scores."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        score INTEGER NOT NULL,
                        grid_size INTEGER,
                        mode TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")

    def sync_csv_to_db(self):
        """Import existing records from scores.csv if the database table is empty."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM scores")
                count = cursor.fetchone()[0]

                if count == 0 and os.path.exists(self.csv_file):
                    with open(self.csv_file, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader, None)
                        rows_to_insert = []
                        for row in reader:
                            if len(row) >= 4:
                                try:
                                    uname = str(row[0]).strip()
                                    sc = int(row[1])
                                    gsize = int(row[2])
                                    mode = str(row[3])
                                    if uname:
                                        rows_to_insert.append((uname, sc, gsize, mode))
                                except (ValueError, IndexError):
                                    continue
                        if rows_to_insert:
                            cursor.executemany(
                                "INSERT INTO scores (username, score, grid_size, mode) VALUES (?, ?, ?, ?)",
                                rows_to_insert
                            )
                            conn.commit()
        except Exception as e:
            print(f"Error syncing CSV to database: {e}")

    def save_score(self, username, score, grid_size, mode):
        """Save a new score into SQLite database, sync with users.db high_score and scores.csv."""
        try:
            score = int(score)
        except (ValueError, TypeError):
            score = 0

        # 1. Save to maze_scores.db
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO scores (username, score, grid_size, mode) VALUES (?, ?, ?, ?)",
                    (username, score, grid_size, str(mode))
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error saving score to database: {e}")

        # 2. Update high_score in users.db if applicable (lower time is better in maze)
        try:
            if os.path.exists(USERS_DB_FILE):
                with sqlite3.connect(USERS_DB_FILE) as user_conn:
                    user_cursor = user_conn.cursor()
                    user_cursor.execute("SELECT high_score FROM users WHERE username = ?", (username,))
                    row = user_cursor.fetchone()
                    if row is not None:
                        curr_best = row[0]
                        if curr_best is None or score < curr_best:
                            user_cursor.execute(
                                "UPDATE users SET high_score = ? WHERE username = ?",
                                (score, username)
                            )
                            user_conn.commit()
        except Exception as e:
            print(f"Error updating high_score in users.db: {e}")

        # 3. Synchronize with scores.csv
        try:
            file_exists = os.path.exists(self.csv_file)
            with open(self.csv_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists or os.path.getsize(self.csv_file) == 0:
                    writer.writerow(['Username', 'Score', 'Grid Size', 'Mode'])
                writer.writerow([username, score, grid_size, mode])
        except Exception as e:
            print(f"Error appending to CSV: {e}")

    def get_high_scores(self, limit=10):
        """Retrieve top scores from database (ordered by fastest completion time)."""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT username, score, grid_size, mode FROM scores ORDER BY score ASC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                if rows:
                    return [[row[0], row[1], row[2], row[3]] for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching high scores from database: {e}")

        # Fallback to CSV if DB query failed
        try:
            if os.path.exists(self.csv_file):
                with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    scores = list(reader)[1:]
                    scores.sort(key=lambda x: int(x[1]))
                    return scores[:limit]
        except Exception:
            pass

        return []

def display_formatted_scores(scores):
    """Format and print high scores in a clean tabular view."""
    if not scores:
        print("No scores available.")
        return
    print(f"\n{'Rank':<6}{'Username':<16}{'Time (s)':<12}{'Grid Size':<12}{'Mode':<10}")
    print("-" * 56)
    for i, s in enumerate(scores):
        uname = str(s[0])
        score_val = f"{s[1]}s"
        grid_val = str(s[2]) if len(s) > 2 else "-"
        mode_val = str(s[3]) if len(s) > 3 else "-"
        print(f"{i+1:<6}{uname:<16}{score_val:<12}{grid_val:<12}{mode_val:<10}")

_default_db = ScoreDB()

def save_score(username, score, grid_size, mode):
    _default_db.save_score(username, score, grid_size, mode)

def get_high_scores(limit=10):
    return _default_db.get_high_scores(limit)