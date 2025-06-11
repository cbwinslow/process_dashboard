"""
AI agent for network optimization.
"""
from src.ai.agent_base import AIAgentBase

class NetworkOptimizerAgent(AIAgentBase):
    def optimize(self, system_metrics):
        self.log_event("network_optimize_attempt", f"Metrics: {system_metrics}")
        # Dummy logic: if network usage > 90%, suggest limiting bandwidth
        if system_metrics.get("network_percent", 0) > 90:
            action = "Suggest limiting bandwidth or investigating network hogs"
            self.log_attempt("high_network_usage", action, "suggested")
            return action
        return None
