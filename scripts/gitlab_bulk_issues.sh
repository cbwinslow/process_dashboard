#!/bin/bash
# Bulk create GitLab issues for Process Dashboard project using GitLab CLI (glab)
# Usage: ./gitlab_bulk_issues.sh
# Requires: glab (https://gitlab.com/gitlab-org/cli)

REPO="cbwinslow/process_dashboard"

# Outstanding Bugs & Technical Debt
glab issue create --repo "$REPO" --title "Integration tests fail due to missing textual.testing" --description "Integration tests (test_integration.py) still fail due to missing textual.testing in the current textual version." --label bug

glab issue create --repo "$REPO" --title "Add UNKNOWN to ProcessState enum in process_controller.py" --description "ProcessState.UNKNOWN is missing in process_controller.py and should be added to resolve UI test errors." --label enhancement

glab issue create --repo "$REPO" --title "Fix syntax issues in src/config/correlation_engine.py and other flagged files" --description "Some modules (e.g., src/config/correlation_engine.py) have syntax or parsing issues and need review." --label bug

glab issue create --repo "$REPO" --title "Expand test coverage for UI, monitoring, and process modules" --description "Test coverage is still low for some modules; more tests are needed for UI, monitoring, and process control." --label enhancement

glab issue create --repo "$REPO" --title "Revisit SNMP support if a compatible pysnmp version is found" --description "SNMP functionality is currently disabled; revisit if/when a compatible pysnmp version is available." --label enhancement

# AI System Optimization Agents
glab issue create --repo "$REPO" --title "Evaluate free/open-source AI agent frameworks (Ollama, LangChain, CrewAI, etc.)" --description "Evaluate frameworks for local inference and agent orchestration." --label ai

glab issue create --repo "$REPO" --title "Define roles for each optimizer agent (CPU, memory, disk, network, etc.)" --description "Define roles and responsibilities for each optimizer agent." --label ai

glab issue create --repo "$REPO" --title "Implement stubs for each optimizer agent and orchestrator" --description "Implement stubs for each optimizer agent (with logging and dummy optimization) and orchestrator agent stub (routes tasks, aggregates results)." --label ai

glab issue create --repo "$REPO" --title "Integrate agent system with the main dashboard" --description "Integrate agent system with the main dashboard (as a service or plugin)." --label ai

glab issue create --repo "$REPO" --title "Connect agents to system metrics and controls" --description "Connect agents to system metrics and controls (via existing monitoring modules)." --label ai

glab issue create --repo "$REPO" --title "Implement basic optimization strategies" --description "Implement basic optimization strategies (e.g., suggest process kills, adjust priorities)." --label ai

glab issue create --repo "$REPO" --title "Add UI panel for AI optimization status, suggestions, and controls" --description "Add UI panel for AI optimization status, suggestions, and controls. Allow user to approve/deny AI suggestions." --label ai

glab issue create --repo "$REPO" --title "Add unit and integration tests for agent logic and orchestrator" --description "Add unit and integration tests for agent logic and orchestrator. Validate that optimizations improve system metrics in test scenarios." --label ai

glab issue create --repo "$REPO" --title "Document agent architecture, usage, and configuration in /docs/AI_OPTIMIZATION.md" --description "Document agent architecture, usage, and configuration in /docs/AI_OPTIMIZATION.md. Update README.md and /docs/ with AI integration details." --label documentation

# AI Optimizer Logging, Learning, and Database Integration
glab issue create --repo "$REPO" --title "Add a logging module for AI agents and orchestrator" --description "Add a logging module for AI agents and orchestrator (logs to file and DB)." --label ai

glab issue create --repo "$REPO" --title "Design and implement a SQLite schema for logs, events, solutions, attempts, responses" --description "Design and implement a SQLite schema for logs, events, solutions, attempts, responses." --label ai

glab issue create --repo "$REPO" --title "Implement a DatabaseLogger class for structured logging and retrieval" --description "Implement a DatabaseLogger class for structured logging and retrieval." --label ai

glab issue create --repo "$REPO" --title "Implement a learning module that suggests solutions based on past successes" --description "Implement a learning module that suggests solutions based on past successes." --label ai

glab issue create --repo "$REPO" --title "Add query functions/scripts for system analysis and troubleshooting" --description "Add query functions/scripts for system analysis and troubleshooting." --label ai

glab issue create --repo "$REPO" --title "Document the logging, learning, and query system in /docs/AI_OPTIMIZATION.md" --description "Document the logging, learning, and query system in /docs/AI_OPTIMIZATION.md." --label documentation

# CODEX_TASKS.md (High Priority)
glab issue create --repo "$REPO" --title "Refactor and modularize the dashboard UI for easier extension and testing" --description "Refactor and modularize the dashboard UI for easier extension and testing." --label enhancement

glab issue create --repo "$REPO" --title "Improve test coverage for all UI and monitoring modules" --description "Improve test coverage for all UI and monitoring modules (see src/ui/, src/monitoring/)." --label enhancement

glab issue create --repo "$REPO" --title "Implement robust error handling and user feedback for all configuration panels" --description "Implement robust error handling and user feedback for all configuration panels." --label enhancement

glab issue create --repo "$REPO" --title "Integrate AI orchestrator and optimizer agents with the main dashboard loop" --description "Integrate AI orchestrator and optimizer agents with the main dashboard loop." --label ai

glab issue create --repo "$REPO" --title "Add Netdata and Prometheus integration" --description "Add Netdata and Prometheus integration (webhook clients, config options, and UI display)." --label enhancement

glab issue create --repo "$REPO" --title "Make all AI/optimizer settings user-configurable via config files and UI" --description "Make all AI/optimizer settings user-configurable via config files and UI." --label enhancement

glab issue create --repo "$REPO" --title "Add a UI panel for AI optimization status, suggestions, and user controls" --description "Add a UI panel for AI optimization status, suggestions, and user controls." --label ai

glab issue create --repo "$REPO" --title "Document all new features and integrations in /docs/AI_OPTIMIZATION.md" --description "Document all new features and integrations in /docs/AI_OPTIMIZATION.md." --label documentation

echo "All issues created. Review them at https://gitlab.com/$REPO/-/issues"
