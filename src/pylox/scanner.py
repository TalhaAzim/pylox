from token import Token, TokenType

class Scanner:

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
    
    def scan_tokens() -> None:
        while not is_at_end:
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
    
    def scan_token() -> None:
        c = self.advance()
        match c:
            case '(': add_token(TokenType.LEFT_PAREN)
            case ')': add_token(TokenType.RIGHT_PAREN)
            case '{': add_token(TokenType.LEFT_BRACE)
            case '}': add_token(TokenType.RIGHT_BRACE)
            case ',': add_token(TokenType.LEFT_PAREN)
            case '.': add_token(TokenType.RIGHT_PAREN)
            case '-': add_token(TokenType.LEFT_BRACE)
            case '+': add_token(TokenType.RIGHT_BRACE)
            case ';': add_token(TokenType.LEFT_BRACE)
            case '*': add_token(TokenType.RIGHT_BRACE)
            case '!': add_token(TokenType.BANG_EQUAL if match('=')  else TokenType.BANG)
            case '=': add_token(TokenType.EQUAL_EQUAL if match('=')  else TokenType.EQUAL)
            case '<': add_token(TokenType.LESS_EQUAL if match('=')  else TokenType.LESS)
            case '>': add_token(TokenType.GREATER_EQUAL if match('=')  else TokenType.GREATER)
            case '/':
                if match('/'):
                    while True:
                        if (peek() != '\n' and not self.is_at_end()):
                            self.advance()
                        else:
                            addToken(TokenType.SLASH)
            case ' ' | '\r' | 't':
                pass
            case '\n':
                self.line += 1
            case _: Pylox.error(self.line, "Unexpected character.")
    
    def match(expected: str) -> bool:
        if (self.is_at_end()): return False
        if (self.source(self.current) != expected): return false
        self.current += 1
        return True
    
    def peek() -> None:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def is_at_end() -> bool:
        return current >= len(self.source)
    
    def advance() -> None:
        self.current += 1
        return self.source[self.current]
    
    def add_token(ttype: TokenType, literal: object = None) -> None:
        text: str = self.source[self.start, self.current]
        self.tokens.append(Token(ttype, text, literal, self.line))
