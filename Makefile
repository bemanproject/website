.PHONY: install build start

# Default target: make => install + start
make: install start

install:
	yarn install

build:
	yarn build

start:
	yarn start
