.PHONY: help run think check report cancel

# Default target - show help
help:
	@echo "Sleepless Agent Makefile Commands:"
	@echo ""
	@echo "  make run                                    - Start the sleepless-agent daemon"
	@echo "  make think TASK=\"description\"              - Submit a task"
	@echo "  make think TASK=\"description\" PROJECT=\"name\" - Submit a task with project"
	@echo "  make check                                  - Check system status"
	@echo "  make report [ID=\"identifier\"]              - View reports"
	@echo "  make cancel ID=\"identifier\"                - Cancel a task"
	@echo "  make help                                   - Show this help message"

# Run the sleepless-agent daemon
run:
	python -m sleepless_agent daemon

# Submit a task (use: make think TASK="your task description" or make think TASK="your task" PROJECT="project-name")
think:
	@if [ -z "$(TASK)" ]; then \
		echo "Usage: make think TASK=\"your task description\""; \
		echo "       make think TASK=\"your task\" PROJECT=\"project-name\""; \
		exit 1; \
	fi
	@if [ -n "$(PROJECT)" ]; then \
		python -m sleepless_agent think "$(TASK)" -p "$(PROJECT)"; \
	else \
		python -m sleepless_agent think "$(TASK)"; \
	fi

# Check system status
check:
	python -m sleepless_agent check

# View report (use: make report ID="identifier")
report:
	@if [ -z "$(ID)" ]; then \
		python -m sleepless_agent report; \
	else \
		python -m sleepless_agent report "$(ID)"; \
	fi

# Cancel a task (use: make cancel ID="identifier")
cancel:
	@if [ -z "$(ID)" ]; then \
		echo "Usage: make cancel ID=\"identifier\""; \
		exit 1; \
	fi
	python -m sleepless_agent cancel "$(ID)"
