"""
AI Orchestrator agent that oversees all optimizer agents.
"""
from src.ai.db_logger import DatabaseLogger
from src.ai.optimizer_cpu import CPUOptimizerAgent
from src.ai.optimizer_memory import MemoryOptimizerAgent
from src.ai.optimizer_disk import DiskOptimizerAgent
from src.ai.optimizer_network import NetworkOptimizerAgent

class AIOrchestrator:
    def __init__(self, db_logger: DatabaseLogger):
        self.db = db_logger
        self.cpu_agent = CPUOptimizerAgent("cpu_optimizer", db_logger)
        self.memory_agent = MemoryOptimizerAgent("memory_optimizer", db_logger)
        self.disk_agent = DiskOptimizerAgent("disk_optimizer", db_logger)
        self.network_agent = NetworkOptimizerAgent("network_optimizer", db_logger)
        # Add more agents as needed

    def optimize_system(self, system_metrics):
        self.db.log_event("orchestrator", "optimize_system", str(system_metrics))
        actions = []
        cpu_action = self.cpu_agent.optimize(system_metrics)
        if cpu_action:
            actions.append(("cpu", cpu_action))
        mem_action = self.memory_agent.optimize(system_metrics)
        if mem_action:
            actions.append(("memory", mem_action))
        disk_action = self.disk_agent.optimize(system_metrics)
        if disk_action:
            actions.append(("disk", disk_action))
        net_action = self.network_agent.optimize(system_metrics)
        if net_action:
            actions.append(("network", net_action))
        # Add more agent calls as needed
        return actions

    def learn_from_success(self, problem: str, solution: str, outcome: str, context: str = "") -> None:
        self.db.log_solution(problem, solution, outcome, context)
