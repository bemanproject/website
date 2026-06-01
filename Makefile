PYTHON ?= python3

.PHONY: all install build start serve lint

all: start

install: # Install dependencies
	$(PYTHON) -m pip install -r requirements.txt
	npm ci

start: install # Install dependencies and start local development server
	$(PYTHON) scripts/run-staged-website.py start

build: # Generate static content for GitHub Pages deployment
	$(PYTHON) scripts/run-staged-website.py build

serve: # Build and serve the staged static site
	$(PYTHON) scripts/run-staged-website.py serve

lint: # Run code quality checks
	trunk check
