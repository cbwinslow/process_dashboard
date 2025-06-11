"""
Mock classes for UI tests.
"""
from src.processes.process_controller import ProcessController
from src.processes.snmp_monitor import SNMPMonitor

class DummyProcessController(ProcessController):
    def __init__(self):
        pass

class DummySNMPMonitor(SNMPMonitor):
    def __init__(self):
        pass
