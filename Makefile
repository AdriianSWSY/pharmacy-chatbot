.PHONY: activate deactivate run

# Activate virtual environment (show instructions)
activate:
	@echo "Run this command in your shell to activate the virtual environment:"
	@echo ""
	@echo "  source .venv/bin/activate"
	@echo ""

# Deactivate virtual environment (show instructions)
deactivate:
	@echo "Run this command in your shell to deactivate the virtual environment:"
	@echo ""
	@echo "  deactivate"
	@echo ""

# Run FastAPI server with uv
run:
	uv run python main.py