from token import Token, TokenType

class Scanner:

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
    
    def scan_tokens(self) -> None:
        while not is_at_end:
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
    
    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case '(': self.add_token(TokenType.LEFT_PAREN)
            case ')': self.add_token(TokenType.RIGHT_PAREN)
            case '{': self.add_token(TokenType.LEFT_BRACE)
            case '}': self.add_token(TokenType.RIGHT_BRACE)
            case ',': self.add_token(TokenType.LEFT_PAREN)
            case '.': self.add_token(TokenType.RIGHT_PAREN)
            case '-': self.add_token(TokenType.LEFT_BRACE)
            case '+': self.add_token(TokenType.RIGHT_BRACE)
            case ';': self.add_token(TokenType.LEFT_BRACE)
            case '*': self.add_token(TokenType.RIGHT_BRACE)
            case '!': self.add_token(TokenType.BANG_EQUAL if match('=')  else TokenType.BANG)
            case '=': self.add_token(TokenType.EQUAL_EQUAL if match('=')  else TokenType.EQUAL)
            case '<': self.add_token(TokenType.LESS_EQUAL if match('=')  else TokenType.LESS)
            case '>': self.add_token(TokenType.GREATER_EQUAL if match('=')  else TokenType.GREATER)
            case '/':
                if match('/'):
                    while True:
                        if (peek() != '\n' and not self.is_at_end()):
                            self.advance()
                        else:
                            self.add_token(TokenType.SLASH)
            case ' ' | '\r' | 't':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _: 
                if c.isdigit():
                    self.number()
                else:
                    Pylox.error(self.line, "Unexpected character.")
    
    def match(self, expected: str) -> bool:
        if (self.is_at_end()): return False
        if (self.source(self.current) != expected): return false
        self.current += 1
        return True
    
    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self) -> str:
        if (self.current + 1 >= len(self.source)):
            return '\0';
        return self.source[self.current + 1]
    
    def is_at_end(self) -> bool:
        return current >= len(self.source)
    
    def advance(self) -> None:
        self.current += 1
        return self.source[self.current]
    
    def add_token(self, ttype: TokenType, literal: object = None) -> None:
        text: str = self.source[self.start, self.current]
        self.tokens.append(Token(ttype, text, literal, self.line))
    
    def string(self) -> None:
        while (self.peek() != '"' and not self.is_at_end()):
            if (self.peek() == '\n'):
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            Pylox.error(self.line, "Unterminated string.")
            return
        
        self.advance()

        value = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)
    
    def number(self) -> None:
        
        while True:
            if self.peek().isdigit():
                self.advance()
            else:
                break
        
        if self.peek() == '.' and self.peek_next().is_digit():
            advance()

        while True:
            if self.peek().isdigit():
                self.advance()
            else:
                break

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUM, value)
            
