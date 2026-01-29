# Pylox Refactor Plan: From Java Port to Idiomatic Python

This document outlines a comprehensive refactoring plan to transform the current 1:1 Java port of the Lox interpreter into idiomatic, maintainable Python code.

## Phase 0: Critical Bug Fixes (Immediate Priority)

The current codebase has several critical bugs that prevent proper execution:

1. **interpreter.py:94** - undefined `distance` variable in `visit_assign_expr`
2. **interpreter.py:133** - method name mismatch (`visit_variable_expr` vs `lookup_variable_expr`)  
3. **environment.py:31** - incorrect attribute reference (`closing` vs `enclosing`)
4. **resolver.py:58** - undefined `function` variable in `resolve_function`

## Phase 1: Dynamic Grammar-Based AST Generation

**Replace tool.py with dynamic class construction:**

### Current State
- `tool.py` statically generates `expr.py` and `stmt.py` files
- Hardcoded grammar definitions in the tool
- Requires regeneration when grammar changes

### Target State
- Create `grammar.lox` or `grammar.yaml` with grammar definitions
- Use `type()` to dynamically construct AST classes at runtime
- Eliminate code generation step entirely
- Build visitor interfaces dynamically

#### Implementation Steps:
1. **Create Grammar Format** (`grammar.lox`):
   ```
   Expr:
     Assign    -> name: Token, value: Expr
     Binary    -> left: Expr, operator: Token, right: Expr
     Call      -> callee: Expr, paren: Token, arguments: list[Expr]
     Grouping  -> expression: Expr
     Literal   -> value: object
     Logical   -> left: Expr, operator: Token, right: Expr
     Unary     -> operator: Token, right: Expr
     Variable  -> name: Token

   Stmt:
     Block      -> statements: list[Stmt]
     Expression -> expression: Expr
     Function   -> name: Token, params: list[Token], body: list[Stmt]
     If         -> condition: Expr, then_branch: Stmt, else_branch: Stmt
     Print      -> expression: Expr
     Return     -> keyword: Token, value: Expr
     Var        -> name: Token, initializer: Expr
     While      -> condition: Expr, body: Stmt
   ```

2. **Create Dynamic AST Builder** (`ast_builder.py`):
   - Parse grammar file at import time
   - Use `type()` to create AST node classes dynamically
   - Generate visitor interfaces automatically
   - Add `@dataclass` decorations automatically
   - Replace static `expr.py` and `stmt.py` files

3. **Update Import System**:
   - Replace direct imports with dynamic class access
   - Create `ast_nodes` module that loads from grammar
   - Maintain backward compatibility with existing code

## Phase 2: Core Infrastructure Improvements

### Modernize Type Hints
- Replace string type hints with proper imports (`list[Expr]` → `list['Expr']`)
- Add comprehensive return type annotations for visitor methods
- Use `typing` module for generic types like `Union`, `Optional`, `TypeVar`
- Add proper forward references where needed

### Improve Module Organization
- Fix circular imports by restructuring dependencies
- Move `Pylox` class to separate `main.py` module
- Create `types.py` for common type definitions
- Establish clear dependency hierarchy

## Phase 3: Pythonic Data Structures

### Replace Visitor Pattern with Modern Approaches
- **Option A**: Use `functools.singledispatch` for visitor pattern
- **Option B**: Use Python 3.10+ pattern matching for AST processing
- **Option C**: Hybrid approach with method dispatch based on node type
- Eliminate verbose `accept()` methods
- Make AST nodes immutable with `@dataclass(frozen=True)`

### Enhance Token System
- Convert `Token` class to `@dataclass`
- Replace enum parsing with more Pythonic approach
- Add `__str__`, `__repr__`, and `__eq__` methods
- Consider using `namedtuple` or `typing.NamedTuple` for performance

### Modernize Environment
- Use `collections.ChainMap` for nested scopes
- Replace manual dictionary chaining
- Add context managers for scope management (`with self.new_scope():`)
- Implement proper variable shadowing semantics

## Phase 4: Algorithm Improvements

### Scanner Refactoring
- Use regex patterns for tokenization where appropriate
- Replace character-by-character matching with more efficient methods
- Use generators instead of building token lists
- Add proper Unicode support

### Parser Improvements
- Use `@dataclass` for parse results
- Implement proper error recovery with exceptions
- Replace method chaining with more readable structure
- Add better error messages with context

### Interpreter Enhancements
- Use `@dataclass` for runtime objects
- Replace type checking with `isinstance()` and pattern matching
- Use Python's truthiness instead of custom `is_truthy()`
- Optimize common operations (lookup, assignment, etc.)

## Phase 5: Error Handling & Logging

### Modern Exception Handling
- Create proper exception hierarchy (`LoxError`, `ParseError`, `RuntimeError`)
- Use context managers for error recovery
- Add structured error reporting with source context
- Implement proper exception chaining

### Add Proper Logging
- Replace `print()` with `logging` module
- Add debug/trace capabilities
- Use context managers for operation tracking
- Configure different log levels for different use cases

## Phase 6: Performance & Pythonic Features

### Use Python Built-ins Effectively
- Replace loops with comprehensions where appropriate
- Use `itertools` for token processing
- Leverage `functools` and `operator` modules
- Consider `__slots__` for memory optimization

### Add Modern Python Features
- Use pattern matching (Python 3.10+) for AST processing
- Implement `__iter__` and `__len__` where appropriate
- Use `pathlib` for file operations
- Consider `dataclasses` for all value objects

### Performance Monitoring
- Add execution timing and profiling
- Memory usage tracking
- AST visualization options
- Benchmark suite for performance regression testing

## Phase 7: Testing & Documentation

### Add Comprehensive Test Suite
- Unit tests for each component
- Integration tests with Lox examples from the book
- Property-based testing for edge cases
- Performance benchmarks

### Improve Documentation
- Add docstrings with proper format (Google/NumPy style)
- Create API documentation with Sphinx
- Add usage examples and tutorials
- Document the dynamic grammar system

## Phase 8: CLI & UX Improvements

### Modern CLI
- Use `argparse` for command-line interface
- Add REPL improvements (history, completion, colors)
- Support for configuration files
- Better error messages and help text

### Development Tools
- Add AST pretty-printing
- Grammar validation tools
- Development mode with verbose output
- Integration with IDEs and editors

---

## Implementation Strategy

### Immediate Actions (Week 1)
1. Fix critical bugs in Phase 0
2. Set up development environment with proper testing
3. Create backup of working state before major changes

### First Major Refactor (Week 2-3)
4. Implement Phase 1: Dynamic grammar system
5. Ensure all existing tests pass with new AST generation

### Systematic Improvements (Week 4-8)
6. Work through Phases 2-4 methodically
7. Test each phase thoroughly before proceeding
8. Maintain backward compatibility where possible

### Polish and Performance (Week 9-12)
9. Implement Phases 5-8
10. Add comprehensive testing and documentation
11. Performance optimization and benchmarking

---

## Success Criteria

- [ ] All existing Lox programs run unchanged
- [ ] Code is significantly more readable and maintainable
- [ ] Performance is improved or at least maintained
- [ ] Full test coverage with CI/CD
- [ ] Dynamic grammar system works seamlessly
- [ ] Documentation is comprehensive and up-to-date

---

## Notes & Considerations

### Dynamic Grammar System Benefits
- **Single Source of Truth**: Grammar defines the AST structure
- **No Code Generation**: Eliminates build step and generated files
- **Flexibility**: Easy to extend grammar without regenerating code
- **Maintainability**: Changes only need to be made in one place

### Potential Challenges
- Performance impact of dynamic class creation (likely minimal)
- IDE support for dynamically generated classes
- Debugging dynamically constructed objects
- Backward compatibility during transition

### Alternative Approaches Considered
- **Keep static generation**: Simpler but less flexible
- **Use metaclasses**: More complex than needed
- **Code generation on import**: Hybrid approach with complexities

The chosen approach balances flexibility, maintainability, and performance while eliminating the need for a separate build step.