"""
Process History Tracking Module
Tracks and manages historical process data for analysis and visualization.
"""

import time
from typing import List, Dict, Any

class ProcessHistory:
    def __init__(self, max_length: int = 3600):
        self.max_length = max_length
        self.history: List[Dict[str, Any]] = []

    def add_snapshot(self, snapshot: Dict[str, Any]):
        timestamped = {'timestamp': time.time(), **snapshot}
        self.history.append(timestamped)
        if len(self.history) > self.max_length:
            self.history.pop(0)

    def get_history(self, key: str = None) -> List[Dict[str, Any]]:
        if key:
            return [{"timestamp": h["timestamp"], key: h.get(key)} for h in self.history if key in h]
        return self.history

    def clear(self):
        self.history.clear()
