"""
Base class for AI optimizer agents and orchestrator.
Provides logging and event hooks.
"""
from src.ai.db_logger import DatabaseLogger

class AIAgentBase:
    def __init__(self, name: str, db_logger: DatabaseLogger):
        self.name = name
        self.db = db_logger

    def log_event(self, event_type: str, details: str):
        self.db.log_event(self.name, event_type, details)

    def log_attempt(self, problem: str, action: str, result: str):
        self.db.log_attempt(self.name, problem, action, result)

    def log_solution(self, problem: str, solution: str, outcome: str, context: str = ""):
        self.db.log_solution(problem, solution, outcome, context)

    def log_response(self, response: str, user_feedback: str = ""):
        self.db.log_response(self.name, response, user_feedback)

    def log(self, log_level: str, message: str):
        self.db.log(self.name, log_level, message)
