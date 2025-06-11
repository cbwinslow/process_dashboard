"""
DatabaseLogger for AI optimizer agents and orchestrator.
Logs events, solutions, attempts, responses, and raw logs to SQLite.
"""
import sqlite3
import threading
from datetime import datetime
from typing import Any, Dict, Optional

class DatabaseLogger:
    def __init__(self, db_path: str = "ai_optimizer_logs.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                agent TEXT,
                event_type TEXT,
                details TEXT
            )
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                agent TEXT,
                problem TEXT,
                action TEXT,
                result TEXT
            )
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                problem TEXT,
                solution TEXT,
                outcome TEXT,
                context TEXT
            )
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                agent TEXT,
                response TEXT,
                user_feedback TEXT
            )
            """)
            c.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                agent TEXT,
                log_level TEXT,
                message TEXT
            )
            """)
            conn.commit()

    def log_event(self, agent: str, event_type: str, details: str):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO events (timestamp, agent, event_type, details) VALUES (?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), agent, event_type, details)
            )
            conn.commit()

    def log_attempt(self, agent: str, problem: str, action: str, result: str):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO attempts (timestamp, agent, problem, action, result) VALUES (?, ?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), agent, problem, action, result)
            )
            conn.commit()

    def log_solution(self, problem: str, solution: str, outcome: str, context: str = ""):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO solutions (timestamp, problem, solution, outcome, context) VALUES (?, ?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), problem, solution, outcome, context)
            )
            conn.commit()

    def log_response(self, agent: str, response: str, user_feedback: str = ""):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO responses (timestamp, agent, response, user_feedback) VALUES (?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), agent, response, user_feedback)
            )
            conn.commit()

    def log(self, agent: str, log_level: str, message: str):
        with self._lock, sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO logs (timestamp, agent, log_level, message) VALUES (?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), agent, log_level, message)
            )
            conn.commit()

    # Example query: get recent events
    def get_recent_events(self, limit: int = 20):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
            return c.fetchall()

    # Example query: get successful solutions
    def get_successful_solutions(self, limit: int = 20):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM solutions WHERE outcome = 'success' ORDER BY timestamp DESC LIMIT ?", (limit,))
            return c.fetchall()

    # Add more queries as needed for analysis and troubleshooting
