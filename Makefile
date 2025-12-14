.PHONY: all install build start trunk-check

all: install start

install: # Install dependencies
	yarn install

start: # Start local development server
	yarn start

build: # Generate static content for GitHub Pages deployment
	yarn build

lint: # Run code quality checks
	trunk check
