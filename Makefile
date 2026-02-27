PYLOX := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))/src/pylox

# clox
CLOX_SRC := $(wildcard src/clox/*.c)
CLOX_OBJ := $(CLOX_SRC:.c=.o)
CLOX_BIN := build/clox
CFLAGS := -std=c99 -Wall -Wextra -Isrc/clox

.PHONY: test clox clean compile_commands

clox: $(CLOX_BIN)

$(CLOX_BIN): $(CLOX_OBJ)
	@mkdir -p build
	$(CC) $(CFLAGS) -o $@ $^

src/clox/%.o: src/clox/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# Generate compile_commands.json for clangd
compile_commands:
	@echo '[' > compile_commands.json
	@first=true; for f in $(CLOX_SRC); do \
		if [ "$$first" = true ]; then first=false; else echo ',' >> compile_commands.json; fi; \
		echo '  {"directory":"$(CURDIR)","command":"clang $(CFLAGS) -c '"$$f"'","file":"$(CURDIR)/'"$$f"'"}' >> compile_commands.json; \
	done
	@echo ']' >> compile_commands.json
	@echo "compile_commands.json updated"

clean:
	rm -f src/clox/*.o $(CLOX_BIN)

test:
	find tests -name '*.lox' -exec sh -c 'python3 src/pylox/__init__.py "$$1"' _ {} \;
