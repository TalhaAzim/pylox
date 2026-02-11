import sys
import runtimeerror
import stmt
from tokens import Token, TokenType
import scanner 
import parser 
import resolver 
import interpreter 


class Pylox:

    def __init__(self, Scanner, Parser, Resolver, Interpreter) -> None:
        self.scanner = Scanner(self)
        self.parser = Parser(self)
        self.resolver = Resolver(self)
        self.interpreter = Interpreter(self)
        self.had_error = False
        self.had_runtime_error = False
    
    def main(self, args: list[str]) -> None:

        if len(args) > 1:
            print("Usage: pylox [script]")
            sys.exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

    def run_file(self, path: str) -> None:
        with open(path, "r") as f:
            self.run(f.read())
        
        if self.had_error:
            sys.exit(65)
        
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self) -> None:
        while True:
            try:
                self.run(input("pylox> "))
                self.had_error = False
            except KeyboardInterrupt:
                break

    def run(self, source: str) -> None:

        self.scanner(source)
        tokens: list[Token] = self.scanner.scan_tokens()

        self.parser(tokens)
        statements: list[stmt.Stmt] = self.parser.parse()

        if self.had_error:
            return
        
        self.interpreter()
        self.resolver(self.interpreter)
        self.resolver.resolve(statements)
       
        if self.had_error:
            return
        
        self.interpreter.interpret(statements)

    def error(self, location: int | Token, message: str) -> None:
        if isinstance(location, int):
            self.report(location, "", message)
        else:
            if location.tokentype == TokenType.EOF:
                self.report(location.line, " at end", message)
            else:
                self.report(location.line, f" at '{location.lexeme}'", message)
    
    def runtime_error(self, error: runtimeerror.RuntimeError) -> None:
        print(f"{error.message}\n[line {error.token.line}]")
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
        self.had_error = True;

if __name__ == "__main__":
    Pylox(scanner.Scanner, parser.Parser, resolver.Resolver, interpreter.Interpreter).main(sys.argv[1:])
