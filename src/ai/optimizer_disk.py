"""
AI agent for disk optimization.
"""
from src.ai.agent_base import AIAgentBase

class DiskOptimizerAgent(AIAgentBase):
    def optimize(self, system_metrics):
        self.log_event("disk_optimize_attempt", f"Metrics: {system_metrics}")
        # Dummy logic: if disk usage > 90%, suggest cleanup
        if system_metrics.get("disk_percent", 0) > 90:
            action = "Suggest cleaning up disk space"
            self.log_attempt("high_disk_usage", action, "suggested")
            return action
        return None
