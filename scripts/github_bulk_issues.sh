#!/bin/bash
# Bulk create GitHub issues for Process Dashboard project using GitHub CLI (gh)
# Usage: ./github_bulk_issues.sh
# Requires: gh (https://cli.github.com/)

REPO="cbwinslow/process_dashboard"

# Outstanding Bugs & Technical Debt
gh issue create --repo "$REPO" --title "Integration tests fail due to missing textual.testing" --body "Integration tests (test_integration.py) still fail due to missing textual.testing in the current textual version." --label bug

gh issue create --repo "$REPO" --title "Add UNKNOWN to ProcessState enum in process_controller.py" --body "ProcessState.UNKNOWN is missing in process_controller.py and should be added to resolve UI test errors." --label enhancement

gh issue create --repo "$REPO" --title "Fix syntax issues in src/config/correlation_engine.py and other flagged files" --body "Some modules (e.g., src/config/correlation_engine.py) have syntax or parsing issues and need review." --label bug

gh issue create --repo "$REPO" --title "Expand test coverage for UI, monitoring, and process modules" --body "Test coverage is still low for some modules; more tests are needed for UI, monitoring, and process control." --label enhancement

gh issue create --repo "$REPO" --title "Revisit SNMP support if a compatible pysnmp version is found" --body "SNMP functionality is currently disabled; revisit if/when a compatible pysnmp version is available." --label enhancement

# AI System Optimization Agents
gh issue create --repo "$REPO" --title "Evaluate free/open-source AI agent frameworks (Ollama, LangChain, CrewAI, etc.)" --body "Evaluate frameworks for local inference and agent orchestration." --label ai

gh issue create --repo "$REPO" --title "Define roles for each optimizer agent (CPU, memory, disk, network, etc.)" --body "Define roles and responsibilities for each optimizer agent." --label ai

gh issue create --repo "$REPO" --title "Implement stubs for each optimizer agent and orchestrator" --body "Implement stubs for each optimizer agent (with logging and dummy optimization) and orchestrator agent stub (routes tasks, aggregates results)." --label ai

gh issue create --repo "$REPO" --title "Integrate agent system with the main dashboard" --body "Integrate agent system with the main dashboard (as a service or plugin)." --label ai

gh issue create --repo "$REPO" --title "Connect agents to system metrics and controls" --body "Connect agents to system metrics and controls (via existing monitoring modules)." --label ai

gh issue create --repo "$REPO" --title "Implement basic optimization strategies" --body "Implement basic optimization strategies (e.g., suggest process kills, adjust priorities)." --label ai

gh issue create --repo "$REPO" --title "Add UI panel for AI optimization status, suggestions, and controls" --body "Add UI panel for AI optimization status, suggestions, and controls. Allow user to approve/deny AI suggestions." --label ai

gh issue create --repo "$REPO" --title "Add unit and integration tests for agent logic and orchestrator" --body "Add unit and integration tests for agent logic and orchestrator. Validate that optimizations improve system metrics in test scenarios." --label ai

gh issue create --repo "$REPO" --title "Document agent architecture, usage, and configuration in /docs/AI_OPTIMIZATION.md" --body "Document agent architecture, usage, and configuration in /docs/AI_OPTIMIZATION.md. Update README.md and /docs/ with AI integration details." --label documentation

# AI Optimizer Logging, Learning, and Database Integration
gh issue create --repo "$REPO" --title "Add a logging module for AI agents and orchestrator" --body "Add a logging module for AI agents and orchestrator (logs to file and DB)." --label ai

gh issue create --repo "$REPO" --title "Design and implement a SQLite schema for logs, events, solutions, attempts, responses" --body "Design and implement a SQLite schema for logs, events, solutions, attempts, responses." --label ai

gh issue create --repo "$REPO" --title "Implement a DatabaseLogger class for structured logging and retrieval" --body "Implement a DatabaseLogger class for structured logging and retrieval." --label ai

gh issue create --repo "$REPO" --title "Implement a learning module that suggests solutions based on past successes" --body "Implement a learning module that suggests solutions based on past successes." --label ai

gh issue create --repo "$REPO" --title "Add query functions/scripts for system analysis and troubleshooting" --body "Add query functions/scripts for system analysis and troubleshooting." --label ai

gh issue create --repo "$REPO" --title "Document the logging, learning, and query system in /docs/AI_OPTIMIZATION.md" --body "Document the logging, learning, and query system in /docs/AI_OPTIMIZATION.md." --label documentation

# CODEX_TASKS.md (High Priority)
gh issue create --repo "$REPO" --title "Refactor and modularize the dashboard UI for easier extension and testing" --body "Refactor and modularize the dashboard UI for easier extension and testing." --label enhancement

gh issue create --repo "$REPO" --title "Improve test coverage for all UI and monitoring modules" --body "Improve test coverage for all UI and monitoring modules (see src/ui/, src/monitoring/)." --label enhancement

gh issue create --repo "$REPO" --title "Implement robust error handling and user feedback for all configuration panels" --body "Implement robust error handling and user feedback for all configuration panels." --label enhancement

gh issue create --repo "$REPO" --title "Integrate AI orchestrator and optimizer agents with the main dashboard loop" --body "Integrate AI orchestrator and optimizer agents with the main dashboard loop." --label ai

gh issue create --repo "$REPO" --title "Add Netdata and Prometheus integration" --body "Add Netdata and Prometheus integration (webhook clients, config options, and UI display)." --label enhancement

gh issue create --repo "$REPO" --title "Make all AI/optimizer settings user-configurable via config files and UI" --body "Make all AI/optimizer settings user-configurable via config files and UI." --label enhancement

gh issue create --repo "$REPO" --title "Add a UI panel for AI optimization status, suggestions, and user controls" --body "Add a UI panel for AI optimization status, suggestions, and user controls." --label ai

gh issue create --repo "$REPO" --title "Document all new features and integrations in /docs/AI_OPTIMIZATION.md" --body "Document all new features and integrations in /docs/AI_OPTIMIZATION.md." --label documentation

echo "All issues created. Review them at https://github.com/$REPO/issues"
