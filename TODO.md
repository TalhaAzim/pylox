# Pylox Refactor TODO

Idiomatic-Python refactor of the reference jlox port. Scope: this branch only.

## Instance-based architecture
- [ ] Extract `Pylox` class out of `__init__.py` into its own module
- [ ] Remove remaining static state (`GenerateAst`/`tool.py` is still all-static)
- [ ] Resolve remaining circular imports (mostly typing-related forward references)

## Type hints
- [ ] Replace string type hints with real imports where circular imports allow

## Pythonic data structures
- [ ] Convert `Token` to `@dataclass`
- [ ] Convert `Environment` to use `collections.ChainMap` for scope chaining
- [ ] Replace the visitor `accept()` pattern with `functools.singledispatch` or `match` statements

## Error handling & logging
- [ ] Proper exception hierarchy (`LoxError`, `ParseError`, `LoxRuntimeError`)
- [ ] Replace `print()` diagnostics with the `logging` module

## CLI/UX
- [ ] `argparse`-based CLI instead of manual `sys.argv` handling
- [ ] REPL history support
