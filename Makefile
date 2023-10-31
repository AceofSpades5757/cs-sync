# Project
PROJECT_NAME = cs-sync

# Environment
VENV_DIR = .venv
ifeq ($(OS),Windows_NT)
	PYTHON = py
	VENV_BIN = ${VENV_DIR}/Scripts
else
	PYTHON = python3
	VENV_BIN = ${VENV_DIR}/bin
endif

VENV_PYTHON = ${VENV_BIN}/python
VENV_PIP = ${VENV_BIN}/pip

# Makefile Settings
.DEFAULT_GOAL = help
.PHONY: build publish test venv clean coverage

help:
	@echo Manage $(PROJECT_NAME). Usage:
	@echo
	@echo make test - Test $(PROJECT_NAME).
	@echo make venv - Create virtual environment.
	@echo make clean - Remove caches, temp files, build files, etc.
	@echo make build - Build wheels.
	@echo make publish - Publish to PyPi.
	@echo make coverage - Check code coverage.

venv:
	-${PYTHON} -m pip install --upgrade pip
	${PYTHON} -m pip install --upgrade virtualenv
	${PYTHON} -m virtualenv .venv
	-${VENV_PIP} install --upgrade pip
	${VENV_PIP} install -r requirements.txt
	${VENV_PIP} install -r requirements-dev.txt

test:
	@echo "Testing $(PROJECT_NAME)."
	$(VENV_BIN)/tox

coverage:
	@echo "Checking Code Coverage."
	${VENV_BIN}/pytest --cov="cs_sync" tests

clean:
	@echo "Removing temporary files, caches, and build files."
	# Build Directories
	rm -rf build/
	rm -rf dist/
	# Temporary Files
	rm -rf __pycache__/
	rm -rf **/__pycache__/
	rm -rf *.egg-info/
	rm -rf **/*.egg-info/
	rm -rf .mypy_cache/
	# Logs
	rm -rf logs/
	rm -rf **/logs/
	rm -rf *.log
	rm -rf **/*.log

build:
	@echo "Building $(PROJECT_NAME)."
	# Build
	${VENV_PYTHON} setup.py sdist bdist_wheel

publish: build
	@echo "Deploying $(PROJECT_NAME) to PyPi."
	${VENV_PIP} install --upgrade twine
	${VENV_PYTHON} -m twine upload dist/*
