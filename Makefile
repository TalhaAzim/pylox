PYLOX := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))/src/pylox

.PHONY: test

test:
	find tests -name '*.lox' -exec sh -c 'python3 src/pylox/__init__.py "$$1"' _ {} \;
