# Pylox Refactor Plan: From Java Port to Idiomatic Python

This document outlines a comprehensive refactoring plan to transform the current 1:1 Java port of the Lox interpreter into idiomatic, maintainable Python code with a focus on **modular components** and **instance-based architecture** that can be swapped out for learning and experimentation purposes, including the ability to run multiple interpreter instances.

## Phase 0: Critical Bug Fixes (Immediate Priority)

The current codebase has several critical bugs that prevent proper execution:

1. **interpreter.py:94** - undefined `distance` variable in `visit_assign_expr`
2. **interpreter.py:133** - method name mismatch (`visit_variable_expr` vs `lookup_variable_expr`)  
3. **environment.py:31** - incorrect attribute reference (`closing` vs `enclosing`)
4. **resolver.py:58** - undefined `function` variable in `resolve_function`

## Phase 0.5: Instance-Based Architecture Refactoring

**Convert from Java-like static/class-based to Pythonic instance-based design:**

### Current State Analysis
- **Pylox class**: All methods are `@staticmethod`, variables are class-level (singleton pattern)
- **Scanner**: `keywords` dictionary is a class variable shared across instances
- **Token**: `TOKENS` list is module-level, global state
- **Tool**: All methods are static, acts like a utility namespace
- **Parser**: Mixed - mostly instance-based but has nested static `ParseError` class

### Target State: Proper Instance-Based Design

#### Pylox Class Refactoring
- Remove all `@staticmethod` decorators
- Convert class variables to instance variables (`had_error`, `had_runtime_error`, `interpreter`)
- Create proper `__init__` method that initializes interpreter instance
- Convert `main()` to instance method, add classmethod for CLI entry point
- Enable creating multiple `Pylox` instances with independent state

```python
class Pylox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter()
    
    def run_file(self, path: str) -> None:
        # Instance-based implementation
    
    def run_prompt(self) -> None:
        # Instance-based implementation
    
    @classmethod
    def main(cls, args: list[str]) -> None:
        # Entry point for CLI usage
```

#### Scanner Instance-Based Design
- Move `keywords` dictionary from class variable to instance variable
- Ensure each Scanner instance has its own copy of keywords
- Remove static dependencies on global Pylox class for error reporting
- Inject error handler via constructor or method parameters

#### Token Module Refactoring
- Move `TOKENS` list from module-level to class-level or method-level
- Consider lazy initialization for better memory management
- Remove global state that could affect multiple instances

#### Tool Class Refactoring
- Convert all static methods to instance methods
- Create `GenerateAst` instances instead of calling static methods
- Make AST generation configurable per instance
- Support multiple grammar formats per instance

#### Parser Improvements
- Extract `ParseError` from nested class to module-level
- Remove static dependencies on global Pylox class
- Make error reporting injectable for better testability

### Multi-Instance Support Benefits
- **Parallel Testing**: Run multiple test suites simultaneously
- **A/B Testing**: Compare different parser implementations side-by-side
- **Isolation**: Each interpreter instance has independent state
- **Learning**: Experiment without affecting other instances
- **Concurrency**: Foundation for future multi-threading support

### Dependency Injection Pattern
- Replace direct imports and global access with injection
- Create `InterpreterContext` class to coordinate components
- Enable component swapping without modifying core classes
- Support different error handling strategies per instance

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

## Phase 1.5: Component Interface Design & Modularity

**Design swappable component architecture:**

### Define Abstract Interfaces
- Create abstract base classes for Scanner, Parser, Resolver, Interpreter
- Use `abc.ABC` and `@abstractmethod` for clear contracts
- Define standard input/output interfaces for each component
- Implement dependency injection pattern for component assembly

### Component Registry System
- Create `ComponentRegistry` class for dynamic component registration
- Support multiple implementations of same interface
- Enable runtime component swapping via configuration
- Add component discovery and validation mechanisms
- Implement instance factories for creating fresh component sets
- Support component isolation for multi-instance interpreters

### Plugin Architecture Examples
- **Parsers**: Recursive descent, Pratt parser, packrat parser
- **AST Processing**: Visitor pattern, pattern matching, data-driven
- **Interpreters**: Tree-walking, bytecode, JIT compilation
- **Error Handling**: Panic mode, error recovery, continuation

### Learning-Focused Features
- Component comparison framework for benchmarking different approaches
- A/B testing interface for trying different algorithms
- Educational mode with detailed component operation logging
- Example implementations showing different trade-offs
- Multi-instance testing suite for comparing configurations
- Instance isolation validation tools

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
- Implement component factory pattern for runtime assembly
- Add configuration system for component selection
- Design instance lifecycle management for multi-interpreter support
- Create context objects for component coordination

## Phase 3: Pythonic Data Structures

### Replace Visitor Pattern with Modern Approaches
- **Option A**: Use `functools.singledispatch` for visitor pattern
- **Option B**: Use Python 3.10+ pattern matching for AST processing
- **Option C**: Hybrid approach with method dispatch based on node type
- Eliminate verbose `accept()` methods
- Make AST nodes immutable with `@dataclass(frozen=True)`
- Design AST interface to support multiple processing backends
- Add adapter pattern for legacy visitor implementations

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
- [ ] Components can be swapped out without code changes
- [ ] Multiple parser and interpreter implementations available
- [ ] Multiple interpreter instances can run independently
- [ ] No global state or singleton patterns remain

---

## Notes & Considerations

### Dynamic Grammar System Benefits
- **Single Source of Truth**: Grammar defines the AST structure
- **No Code Generation**: Eliminates build step and generated files
- **Flexibility**: Easy to extend grammar without regenerating code
- **Maintainability**: Changes only need to be made in one place
- **Learning Opportunities**: Easy to experiment with different AST processing approaches
- **Multi-Instance Support**: Foundation for running multiple interpreters simultaneously

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

---

## Future Research: Extreme Component Decoupling

### Protocol-Based Component Architecture

**Research Goal**: Take component modularity to the extreme by making each interpreter component a separate utility that exchanges data through standardized protocols and formats.

### Proposed Architecture
- **Component Isolation**: Each component (Scanner, Parser, Resolver, Interpreter) runs as independent process/service
- **Protocol Design**: Define standardized communication protocols between components
- **Data Format**: Consider s-expressions as intermediate representation (language-agnostic)
- **Transport Layer**: Support multiple communication methods (stdin/stdout, sockets, message queues)

### S-Expression Protocol Research
```python
# Example: Parser → Resolver communication
"(define-function 'add '(x y) '(+ x y))"
→ "(resolve-ast '((function add (x y) (+ x y)))"

# Example: Resolver → Interpreter communication  
"(resolved-function 'add (x y) (+ x y))"
→ "(execute '((function add (x y) (+ x y)) 5 3)"
```

### Research Questions
1. **Performance Impact**: What are the overhead costs of serialization/deserialization?
2. **Protocol Design**: How to design protocols that are both simple and extensible?
3. **Error Handling**: How to propagate detailed errors across component boundaries?
4. **Debugging**: How to trace execution across multiple independent processes?
5. **Language Interoperability**: Can components be written in different languages?

### Potential Benefits
- **Maximum Flexibility**: Components can be written in any language
- **Independent Development**: Teams can work on components in isolation
- **Runtime Swapping**: Components can be hot-swapped without restarting
- **Distributed Execution**: Components can run on different machines
- **Educational Value**: Clear separation of concerns with explicit data flow

### Implementation Challenges
- **Performance Overhead**: IPC costs vs. in-process execution
- **Type Safety**: Maintaining type safety across protocol boundaries
- **Tooling**: Need for protocol debugging and testing tools
- **Complexity**: Increased system complexity and deployment requirements
- **Instance Management**: Coordinating multiple independent interpreter instances

### Investigation Plan
1. **Prototype**: Build simple prototype with two components using s-expressions
2. **Benchmark**: Compare performance against in-process execution
3. **Protocol Evolution**: Refine protocol based on practical usage
4. **Tool Development**: Create debugging and testing utilities
5. **Documentation**: Document best practices for protocol-based components

This research explores the theoretical limits of component decoupling while maintaining practical usability. Even if not adopted for production, the insights will inform the modular design of the main interpreter.