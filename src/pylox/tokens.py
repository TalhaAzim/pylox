from dataclasses import dataclass
from enum import Enum

tokens_desc = """
// Single-character tokens.
LEFT_PAREN, RIGHT_PAREN, LEFT_BRACE, RIGHT_BRACE,
COMMA, DOT, MINUS, PLUS, SEMICOLON, SLASH, STAR,

// One or two character tokens.
BANG, BANG_EQUAL,
EQUAL, EQUAL_EQUAL,
GREATER, GREATER_EQUAL,
LESS, LESS_EQUAL,

// Literals.
IDENTIFIER, STRING, NUMBER,

// Keywords.
AND, CLASS, ELSE, FALSE, FUN, FOR, IF, NIL, OR,
PRINT, RETURN, SUPER, THIS, TRUE, VAR, WHILE,

EOF
"""

TOKENS = [ token.strip() for token in "".join(line for line in tokens_desc.split('\n') if not line.startswith("//")).split(",") ]

TokenType = Enum("TokenType", TOKENS)

@dataclass(frozen=True)
class Token:
    tokentype: TokenType
    lexeme: str
    literal: object
    line: int

    def __str__(self) -> str:
        return f"{self.tokentype} {self.lexeme} {self.literal}"
