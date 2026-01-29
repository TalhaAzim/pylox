# Pylox - A Python Implementation of the Lox Interpreter

A learning project to understand how interpreters work by implementing the Lox programming language from *Crafting Interpreters* by Robert Nystrom, ported 1:1 from Java to Python.

## About This Project

This is my personal journey through *Crafting Interpreters*, where I'm implementing the Lox language in Python. The project follows the book's structure exactly, starting with a direct Java-to-Python port to understand the core concepts, with plans to refactor into more idiomatic Python once the implementation is complete.

## Current Status

**Completed Chapters:**
- ✅ Chapter 4: Scanning
- ✅ Chapter 5: Representing Code
- ✅ Chapter 6: Parsing Expressions  
- ✅ Chapter 7: Evaluating Expressions
- ✅ Chapter 8: Statements and State
- ✅ Chapter 9: Control Flow
- ✅ Chapter 10: Functions
- ✅ Chapter 11: Resolving and Binding

**In Progress:**
- 🔄 Chapter 11.5: Resolution Errors (taking a break for IRL commitments)

The interpreter currently supports:
- Lexical scanning with all token types
- Recursive descent parsing
- AST generation and printing
- Expression evaluation
- Variable declarations and assignments
- Control flow (if/else, while)
- Function declarations and calls
- Local functions and closures
- Static analysis with resolver

## Project Structure

```
src/pylox/
├── __init__.py        # Main Pylox class and entry point
├── scanner.py         # Lexical analyzer (Chapter 4)
├── token.py           # Token and TokenType definitions
├── expr.py            # AST expression nodes (generated)
├── stmt.py            # AST statement nodes (generated)
├── parser.py          # Recursive descent parser (Chapter 6)
├── astprinter.py      # AST pretty printer (Chapter 5)
├── interpreter.py     # Expression evaluator (Chapter 7-8)
├── environment.py     # Variable scoping and environment
├── resolver.py        # Static analysis (Chapter 11)
├── loxcallable.py     # Base class for callable objects
├── loxfunction.py     # User-defined functions
├── returnexception.py # Control flow for function returns
├── runtimeerror.py    # Runtime error handling
├── tool.py            # AST code generation tool
└── test.lox          # Sample Lox program
```

## Usage

### Interactive REPL
```bash
cd src/pylox
python3 __init__.py
# or use the wrapper script:
./lox
```

### Run from file
```bash
cd src/pylox  
python3 __init__.py script.lox
# or:
./lox script.lox
```

### Sample Lox Program
```lox
// Example from test.lox
fun fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

print fibonacci(10); // Prints: 55
```

## Learning Journey

This project serves as a detailed learning log. Progress is tracked in:
- [`STATUS.md`](STATUS.md) - Day-by-day implementation notes
- [`TODO.md`](TODO.md) - Comprehensive refactoring roadmap

The project deliberately maintains a 1:1 Java port initially to ensure understanding of the core interpreter concepts before moving to Pythonic refinements.

## Future Refactoring Plans

Once the interpreter is functionally complete, the major refactor will include:

- **Phase 1**: Replace code generation with dynamic grammar-based AST construction
- **Phase 2**: Modernize type hints and module organization  
- **Phase 3**: Replace visitor pattern with `functools.singledispatch` or pattern matching
- **Phase 4**: Pythonic data structures and algorithms
- **Phase 5**: Proper exception handling and logging
- **Phase 6**: Performance optimizations and modern Python features

See [`TODO.md`](TODO.md) for the complete refactoring roadmap.

## Known Issues

The current codebase has some critical bugs that need fixing before the refactoring phase (see TODO.md Phase 0):
- Undefined variables in `interpreter.py`
- Method name mismatches
- Attribute reference errors
- Undefined variables in resolver

## Resources

- [*Crafting Interpreters* by Robert Nystrom](https://craftinginterpreters.com/) - The primary guide for this implementation
- [Lox Language Specification](https://craftinginterpreters.com/the-lox-language.html)

## Development Notes

- Developed with Python 3.x
- Follows the book's implementation exactly during the learning phase
- Uses the visitor pattern as presented in the book (to be refactored later)
- Includes comprehensive error handling as described in the text

---

*This project is primarily for educational purposes - to deeply understand how interpreters work by building one step by step.*