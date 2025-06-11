"""
Query interface for AI optimizer logs and learning database.
"""
from src.ai.db_logger import DatabaseLogger

def print_recent_events(db_logger, limit=10):
    events = db_logger.get_recent_events(limit)
    for e in events:
        print(e)

def print_successful_solutions(db_logger, limit=10):
    solutions = db_logger.get_successful_solutions(limit)
    for s in solutions:
        print(s)

# Add more queries as needed for analysis and troubleshooting
