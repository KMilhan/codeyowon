.PHONY: help install test lint format run-chat run-tui run-mcp clean

PYTHON = python
PIP = pip
UV = uv
UVR = uv run
PKG_NAME = codeyowon

help:
	@echo "Available Commands:"
	@echo "  help	  - Show help"
	@echo "  install   - Install development environment"
	@echo "  test	  - Run all tests"
	@echo "  lint	  - Run code static analysis"
	@echo "  format	- Run code auto-formatting"
	@echo "  run-chat  - Run CLI chat"
	@echo "  run-tui   - Run TUI interface" 
	@echo "  run-mcp   - Run MCP server"
	@echo "  clean	 - Clean generated files"

install:
	$(UV) pip install -e .
	if [ ! -f .env ]; then echo "OPENAI_API_KEY=your-api-key-here" > .env; fi

dev-install:
	$(UV) pip install -e '.[dev]'

test:
	$(UVR) pytest

lint:
	$(UVR) ruff check .
	$(UVR) pyright .

format:
	$(UVR) ruff format .

run-tui:
	$(UVR) $(PYTHON) -m yowon

run-mcp:
	$(UVR) $(PYTHON) -m yowon.server

build:
	$(UV) build

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/ .ruff_cache/
	$(PYTHON) -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.pyc')]"
	$(PYTHON) -c "import pathlib; [p.rmdir() for p in pathlib.Path('.').rglob('__pycache__') if p.is_dir()]"
