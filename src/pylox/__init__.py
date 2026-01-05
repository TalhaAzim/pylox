import sys
from token import Token

class Pylox:

    had_error = False

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
        # Importing scanner here to avoid circular import
        from scanner import Scanner
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        
        for token in tokens:
            print(token)

    @staticmethod
    def error(location: int | Token, message: str) -> None:
        if isinstance(location, int)
            Pylox.report(line, "", message)
        else:
            if location.tokentype == TokenType.EOF:
                self.report(location.line, "at end", message)
            else:
                self.report(location.line, f" at '{token.lexeme}'", message)

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[line {line}] Error {where}: {message}", file=sys.stderr)
        Pylox.had_error = True;

if __name__ == "__main__":
    Pylox.main(sys.argv[1:])
