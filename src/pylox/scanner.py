from token import Token, TokenType
from __init__ import Pylox

class Scanner:

    keywords = {
        "and": TokenType.AND,
        "class": TokenType.CLASS,
        "else": TokenType.ELSE,
        "false": TokenType.FALSE,
        "for": TokenType.FOR,
        "fun": TokenType.FUN,
        "if": TokenType.IF,
        "nil": TokenType.NIL,
        "or": TokenType.OR,
        "print": TokenType.PRINT,
        "return": TokenType.RETURN,
        "super": TokenType.SUPER,
        "this": TokenType.THIS,
        "true": TokenType.TRUE,
        "var": TokenType.VAR,
        "while": TokenType.WHILE
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start: int = 0
        self.current: int = 0
        self.line: int = 1
    
    def scan_tokens(self) -> None:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scan_token(self) -> None:
        c = self.advance()
        match c:
            case '(': self.add_token(TokenType.LEFT_PAREN)
            case ')': self.add_token(TokenType.RIGHT_PAREN)
            case '{': self.add_token(TokenType.LEFT_BRACE)
            case '}': self.add_token(TokenType.RIGHT_BRACE)
            case ',': self.add_token(TokenType.COMMA)
            case '.': self.add_token(TokenType.DOT)
            case '-': self.add_token(TokenType.MINUS)
            case '+': self.add_token(TokenType.PLUS)
            case ';': self.add_token(TokenType.SEMICOLON)
            case '*': self.add_token(TokenType.STAR)
            case '!': self.add_token(TokenType.BANG_EQUAL if self.match('=')  else TokenType.BANG)
            case '=': self.add_token(TokenType.EQUAL_EQUAL if self.match('=')  else TokenType.EQUAL)
            case '<': self.add_token(TokenType.LESS_EQUAL if self.match('=')  else TokenType.LESS)
            case '>': self.add_token(TokenType.GREATER_EQUAL if self.match('=')  else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    while (self.peek() != '\n' and not self.is_at_end()):
                            self.advance()
                else:
                    self.add_token(TokenType.SLASH)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string()
            case _: 
                if c.isdigit():
                    self.number()
                elif (c.isalpha() or c == '_'):
                    self.identifier()
                else:
                    Pylox.error(self.line, "Unexpected character.")

    def identifier(self) -> None:
        while True:
            c = self.peek()
            if (c.isalnum() or
                c == '_'):
                self.advance()
            else:
                break
            
        text = self.source[self.start:self.current]
        ttype = Scanner.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(ttype)
            
        
    def match(self, expected: str) -> bool:
        if (self.is_at_end()): return False
        if (self.source[self.current] != expected): return False
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
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c
    
    def add_token(self, ttype: TokenType, literal: object = None) -> None:
        text: str = self.source[self.start:self.current]
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
        
        while self.peek().isdigit():
            self.advance()
        
        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()

        while self.peek().isdigit():
            self.advance()

        value = float(self.source[self.start:self.current])
        self.add_token(TokenType.NUMBER, value)
            
