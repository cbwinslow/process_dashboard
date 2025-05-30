"""
Process Management Panel UI Component.

This module provides the main UI components for managing processes, including:
- Resource control panel (CPU, memory limits)
- Process priority and grouping controls
- SNMP monitoring display
- Process control buttons
- Color-coded process state display
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QComboBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QLineEdit, QCheckBox, QTabWidget
)
from PyQt6.QtGui import QColor, QBrush, QFont

from ..processes.process_controller import (
    ProcessController,
    ProcessPriority,
    ProcessState,
    ProcessGroup
)
from ..processes.snmp_monitor import SNMPMonitor

logger = logging.getLogger(__name__)

# Color scheme for process states
STATE_COLORS = {
    ProcessState.RUNNING: QColor("#4CAF50"),      # Green
    ProcessState.SLEEPING: QColor("#2196F3"),     # Blue
    ProcessState.STOPPED: QColor("#FFC107"),      # Yellow
    ProcessState.ZOMBIE: QColor("#F44336"),       # Red
    ProcessState.DEAD: QColor("#9E9E9E"),         # Gray
    ProcessState.UNKNOWN: QColor("#607D8B")       # Blue Gray
}

@dataclass
class ProcessDisplayInfo:
    """Process information for display."""
    pid: int
    name: str
    state: ProcessState
    cpu_percent: float
    memory_percent: float
    priority: ProcessPriority
    group: Optional[str]
    start_time: datetime

class ProcessManagementPanel(QWidget):
    """
    Main panel for process management UI.
    
    Provides controls for:
    - Resource limits
    - Process priorities
    - Process grouping
    - SNMP monitoring
    - Process control actions
    """
    
    # Signals for process control
    process_selected = pyqtSignal(int)  # PID
    process_state_changed = pyqtSignal(int, ProcessState)  # PID, new state
    
    def __init__(
        self,
        process_controller: ProcessController,
        snmp_monitor: SNMPMonitor,
        parent: Optional[QWidget] = None
    ):
        """Initialize the process management panel."""
        super().__init__(parent)
        
        self.process_controller = process_controller
        self.snmp_monitor = snmp_monitor
        self.selected_pid: Optional[int] = None
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
        
        self._init_ui()
    
    def _init_ui(self) -> None:
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different panels
        tabs = QTabWidget()
        tabs.addTab(self._create_process_list_panel(), "Processes")
        tabs.addTab(self._create_resource_control_panel(), "Resources")
        tabs.addTab(self._create_snmp_panel(), "SNMP Monitor")
        
        layout.addWidget(tabs)
    
    def _create_process_list_panel(self) -> QWidget:
        """Create the process list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(8)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Name", "State", "CPU %", "Memory %",
            "Priority", "Group", "Start Time"
        ])
        self.process_table.itemSelectionChanged.connect(self._on_process_selected)
        layout.addWidget(self.process_table)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.kill_button = QPushButton("Kill")
        self.kill_button.clicked.connect(self._on_kill_process)
        self.kill_button.setEnabled(False)
        button_layout.addWidget(self.kill_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self._on_stop_process)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        self.resume_button = QPushButton("Resume")
        self.resume_button.clicked.connect(self._on_resume_process)
        self.resume_button.setEnabled(False)
        button_layout.addWidget(self.resume_button)
        
        layout.addLayout(button_layout)
        
        return panel
    
    def _create_resource_control_panel(self) -> QWidget:
        """Create the resource control panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # CPU Limit Group
        cpu_group = QGroupBox("CPU Control")
        cpu_layout = QHBoxLayout(cpu_group)
        
        cpu_layout.addWidget(QLabel("CPU Limit (%):"))
        self.cpu_limit_spin = QSpinBox()
        self.cpu_limit_spin.setRange(0, 100)
        self.cpu_limit_spin.valueChanged.connect(self._on_cpu_limit_changed)
        cpu_layout.addWidget(self.cpu_limit_spin)
        
        layout.addWidget(cpu_group)
        
        # Memory Limit Group
        memory_group = QGroupBox("Memory Control")
        memory_layout = QHBoxLayout(memory_group)
        
        memory_layout.addWidget(QLabel("Memory Limit (MB):"))
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(0, 99999)
        self.memory_limit_spin.valueChanged.connect(self._on_memory_limit_changed)
        memory_layout.addWidget(self.memory_limit_spin)
        
        layout.addWidget(memory_group)
        
        # Priority Group
        priority_group = QGroupBox("Process Priority")
        priority_layout = QHBoxLayout(priority_group)
        
        priority_layout.addWidget(QLabel("Priority:"))
        self.priority_combo = QComboBox()
        for priority in ProcessPriority:
            self.priority_combo.addItem(priority.name)
        self.priority_combo.currentIndexChanged.connect(self._on_priority_changed)
        priority_layout.addWidget(self.priority_combo)
        
        layout.addWidget(priority_group)
        
        # Process Group
        group_group = QGroupBox("Process Group")
        group_layout = QHBoxLayout(group_group)
        
        group_layout.addWidget(QLabel("Group:"))
        self.group_combo = QComboBox()
        self.group_combo.setEditable(True)
        self.group_combo.currentTextChanged.connect(self._on_group_changed)
        group_layout.addWidget(self.group_combo)
        
        layout.addWidget(group_group)
        
        return panel
    
    def _create_snmp_panel(self) -> QWidget:
        """Create the SNMP monitoring panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # System metrics group
        metrics_group = QGroupBox("System Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU Usage:"))
        self.cpu_progress = QProgressBar()
        cpu_layout.addWidget(self.cpu_progress)
        metrics_layout.addLayout(cpu_layout)
        
        # Memory Usage
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Usage:"))
        self.memory_progress = QProgressBar()
        memory_layout.addWidget(self.memory_progress)
        metrics_layout.addLayout(memory_layout)
        
        # Network Usage
        network_layout = QHBoxLayout()
        network_layout.addWidget(QLabel("Network I/O:"))
        self.network_label = QLabel()
        network_layout.addWidget(self.network_label)
        metrics_layout.addLayout(network_layout)
        
        layout.addWidget(metrics_group)
        
        # SNMP Status group
        status_group = QGroupBox("SNMP Status")
        status_layout = QVBoxLayout(status_group)
        
        self.snmp_status_label = QLabel()
        status_layout.addWidget(self.snmp_status_label)
        
        layout.addWidget(status_group)
        
        return panel
    
    def update_display(self) -> None:
        """Update all display elements with current data."""
        try:
            # Update process table
            processes = self.process_controller.get_all_processes()
            self.process_table.setRowCount(len(processes))
            
            for row, process in enumerate(processes):
                self._update_process_row(row, process)
            
            # Update SNMP metrics
            if self.snmp_monitor.is_connected():
                metrics = self.snmp_monitor.get_system_metrics()
                self.cpu_progress.setValue(int(metrics.cpu_percent))
                self.memory_progress.setValue(int(metrics.memory_percent))
                self.network_label.setText(
                    f"In: {metrics.bytes_in}/s, Out: {metrics.bytes_out}/s"
                )
                self.snmp_status_label.setText("Connected")
                self.snmp_status_label.setStyleSheet("color: green")
            else:
                self.snmp_status_label.setText("Disconnected")
                self.snmp_status_label.setStyleSheet("color: red")
        
        except Exception as e:
            logger.error("Failed to update display: %s", str(e))
    
    def _update_process_row(self, row: int, process: ProcessDisplayInfo) -> None:
        """Update a single row in the process table."""
        def set_item(col: int, value: str) -> None:
            item = QTableWidgetItem(value)
            item.setForeground(QBrush(STATE_COLORS[process.state]))
            self.process_table.setItem(row, col, item)
        
        set_item(0, str(process.pid))
        set_item(1, process.name)
        set_item(2, process.state.name)
        set_item(3, f"{process.cpu_percent:.1f}")
        set_item(4, f"{process.memory_percent:.1f}")
        set_item(5, process.priority.name)
        set_item(6, process.group or "")
        set_item(7, process.start_time.strftime("%Y-%m-%d %H:%M:%S"))
    
    def _on_process_selected(self) -> None:
        """Handle process selection in the table."""
        items = self.process_table.selectedItems()
        if items:
            self.selected_pid = int(items[0].text())
            self.process_selected.emit(self.selected_pid)
            
            # Enable control buttons
            self.kill_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.resume_button.setEnabled(True)
            
            # Update resource controls
            process = self.process_controller.get_process(self.selected_pid)
            if process:
                self.cpu_limit_spin.setValue(process.cpu_limit or 0)
                self.memory_limit_spin.setValue(process.memory_limit or 0)
                self.priority_combo.setCurrentText(process.priority.name)
                self.group_combo.setCurrentText(process.group or "")
    
    def _on_kill_process(self) -> None:
        """Handle kill button click."""
        if self.selected_pid:
            try:
                self.process_controller.kill_process(self.selected_pid)
                self.process_state_changed.emit(self.selected_pid, ProcessState.DEAD)
            except Exception as e:
                logger.error("Failed to kill process %d: %s", self.selected_pid, str(e))
    
    def _on_stop_process(self) -> None:
        """Handle stop button click."""
        if self.selected_pid:
            try:
                self.process_controller.stop_process(self.selected_pid)
                self.process_state_changed.emit(self.selected_pid, ProcessState.STOPPED)
            except Exception as e:
                logger.error("Failed to stop process %d: %s", self.selected_pid, str(e))
    
    def _on_resume_process(self) -> None:
        """Handle resume button click."""
        if self.selected_pid:
            try:
                self.process_controller.resume_process(self.selected_pid)
                self.process_state_changed.emit(self.selected_pid, ProcessState.RUNNING)
            except Exception as e:
                logger.error("Failed to resume process %d: %s", self.selected_pid, str(e))
    
    def _on_cpu_limit_changed(self, value: int) -> None:
        """Handle CPU limit change."""
        if self.selected_pid:
            try:
                self.process_controller.set_cpu_limit(self.selected_pid, value)
            except Exception as e:
                logger.error("Failed to set CPU limit for process %d: %s",
                           self.selected_pid, str(e))
    
    def _on_memory_limit_changed(self, value: int) -> None:
        """Handle memory limit change."""
        if self.selected_pid:
            try:
                self.process_controller.set_memory_limit(self.selected_pid, value)
            except Exception as e:
                logger.error("Failed to set memory limit for process %d: %s",
                           self.selected_pid, str(e))
    
    def _on_priority_changed(self, index: int) -> None:
        """Handle priority change."""
        if self.selected_pid:
            try:
                priority = ProcessPriority[self.priority_combo.currentText()]
                self.process_controller.set_priority(self.selected_pid, priority)
            except Exception as e:
                logger.error("Failed to set priority for process %d: %s",
                           self.selected_pid, str(e))
    
    def _on_group_changed(self, group: str) -> None:
        """Handle group change."""
        if self.selected_pid:
            try:
                if group:
                    self.process_controller.add_to_group(self.selected_pid, group)
                else:
                    self.process_controller.remove_from_group(self.selected_pid)
            except Exception as e:
                logger.error("Failed to update group for process %d: %s",
                           self.selected_pid, str(e))

