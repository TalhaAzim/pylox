import sys
import runtimeerror
import stmt
from token import Token, TokenType

class Pylox:

    had_error = False
    had_runtime_error = False
    interpreter = None

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def main(args: list[str]) -> None:
        if len(args) > 1:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 1:
            Pylox.run_file(args[0])
        else:
            Pylox.run_prompt()

    @staticmethod
    def run_file(path: str) -> None:
        with open(path, "r") as f:
            Pylox.run(f.read())
        
        if Pylox.had_error:
            sys.exit(65)
        
        if Pylox.had_runtime_error:
            sys.exit(70)

    @staticmethod
    def run_prompt() -> None:
        while True:
            try:
                Pylox.run(input("pylox> "))
                Pylox.had_error = False
            except KeyboardInterrupt:
                break

    @staticmethod
    def run(source: str) -> None:
        # Importing scanner, parser, and interpreter here to avoid circular import
        from scanner import Scanner
        from parser import Parser

        scanner: Scanner = Scanner(source)
        tokens: list[Token] = scanner.scan_tokens()

        if Pylox.interpreter is None:
            from interpreter import Interpreter
            Pylox.interpreter = Interpreter()

        parser: Parser = Parser(tokens)
        statements: list[stmt.Stmt] = parser.parse()

        if Pylox.had_error:
            return
        
        from resolver import Resolver
        resolver: Resolver = Resolver(interpreter)
        resolver.resolve(statement)
        
        Pylox.interpreter.interpret(statements)

    @staticmethod
    def error(location: int | Token, message: str) -> None:
        if isinstance(location, int):
            Pylox.report(location, "", message)
        else:
            if location.tokentype == TokenType.EOF:
                Pylox.report(location.line, " at end", message)
            else:
                Pylox.report(location.line, f" at '{location.lexeme}'", message)
    
    @staticmethod
    def runtime_error(error: runtimeerror.RuntimeError) -> None:
        print(f"{error.message}\n[line {error.token.line}]")
        Pylox.had_runtime_error = True

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
        Pylox.had_error = True;

if __name__ == "__main__":
    Pylox.main(sys.argv[1:])
