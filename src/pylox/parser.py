from token import TokenType, Token
import expr
import stmt
from __init__ import Pylox

class Parser:
    
    class ParseError(Exception):
        pass

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def expression(self) -> expr.Expr:
        return self.assignment()
    
    def declaration(self) -> stmt.Stmt:
        try:
            if (self.match(TokenType.VAR)):
                return self.var_declaration();
            return self.statement()
        except Parser.ParseError as error:
            self.synchronize()
            return None
    
    def statement(self) -> stmt.Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        return self.expression_statement()
    
    def print_statement(self) -> stmt.Stmt:
        value: expr.Expr = self.expression() # Isn't that what it's all about?
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)
    
    def var_declaration(self) -> stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: expr.Expr = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)
    
    def expression_statement(self) -> stmt.Stmt:
        expression: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expression)
    
    def assignment(self) -> expr.Expr:
        expression: expr.Expr = self.equality()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: expr.Expr = self.assignment()

            if isinstance(expression, expr.Variable):
                name: Token = expression.name
                return expr.Assign(name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expression
    
    def equality(self) -> expr.Expr:
        expression: expr.Expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator: Token = self.previous()
            right: expr.Expr = self.comparison()
            expression = expr.Binary(expression, operator, right)

        return expression
    
    def match(self, *tokentypes: TokenType) -> bool:

        for tokentype in tokentypes:
            if (self.check(tokentype)):
                self.advance()
                return True
        return False

    def check(self, tokentype: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().tokentype == tokentype

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current +=1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().tokentype == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def comparison(self) -> expr.Expr:
        expression: expr.Expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator: Token = self.previous()
            right: expr.Expr = self.term()
            expression = expr.Binary(expression, operator, right)

        return expression

    def term(self) -> expr.Expr:
        expression: expr.Expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: expr.Expr = self.factor()
            expression = expr.Binary(expression, operator, right)

        return expression

    def factor(self) -> expr.Expr:
        expression: expr.Expr = self.unary()
        
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: expr.Expr = self.unary()
            expression = expr.Binary(expression, operator, right)
        
        return expression
    
    def unary(self) -> expr.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: expr.Expr = self.unary()
            return expr.Unary(operator, right)
        return self.primary()

    def primary(self) -> expr.Expr:
        
        if self.match(TokenType.FALSE):
            return expr.Literal(False)
        
        if self.match(TokenType.TRUE):
            return expr.Literal(True)

        if self.match(TokenType.NIL):
            return expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return expr.Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expression: expr.Expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(expression)
        
        raise Parser.error(self.peek(), "Expect expression.")

    def consume(self, ttype: TokenType, message: str) -> Token:
        if self.check(ttype):
            return self.advance()
        
        raise Parser.error(self.peek(), message)
    
    @staticmethod
    def error(token: Token, message: str) -> "Parser.ParseError":
        Pylox.error(token, message)
        return Parser.ParseError()
    
    def synchronize(self) -> None:
        self.advance()

        while not self.is_at_end():

            if (self.previous().tokentype == TokenType.SEMICOLON):
                return None
            
            match self.peek().tokentype:
                case TokenType.CLASS:
                    pass
                case TokenType.FUN:
                    pass
                case TokenType.VAR:
                    pass
                case TokenType.FOR:
                    pass
                case TokenType.IF:
                    pass
                case TokenType.WHILE:
                    pass
                case TokenType.PRINT:
                    pass
                case TokenType.RETURN:
                    return None
                case _:
                    pass
                
            self.advance()
    
    def parse(self) -> list[stmt.Stmt]:
        statements: list[stmt.Stmt] = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements
