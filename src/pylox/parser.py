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
            if self.match(TokenType.FUN):
                return self.function("function")
            if self.match(TokenType.VAR):
                return self.var_declaration();
            return self.statement()
        except Parser.ParseError as error:
            self.synchronize()
            return None
    
    def statement(self) -> stmt.Stmt:
        if self.match(TokenType.FOR):
            return self.for_statement()
        
        if self.match(TokenType.IF):
            return self.if_statement()

        if self.match(TokenType.PRINT):
            return self.print_statement()
        
        if self.match(TokenType.RETURN):
            return self.return_statement()
        
        if self.match(TokenType.WHILE):
            return self.while_statement()

        if self.match(TokenType.LEFT_BRACE):
            return stmt.Block(self.block())

        return self.expression_statement()
    
    def for_statement(self) -> stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer: stmt.Stmt = None # redundant for python but including in the 1:1 port
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        
        condition: expr.Expr = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment: expr.Expr = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body: stmt.Stmt = self.statement()

        if increment:
            body = stmt.Block([body, stmt.Expression(increment)])
        
        if condition is None:
            condition = expr.Literal(True)
        
        body = stmt.While(condition, body)

        if initializer:
            body = stmt.Block([initializer, body])

        return body
    
    def if_statement(self) -> stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition: expr.Expr = self.expression() # The true human condition.
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        then_branch: stmt.Stmt = self.statement()
        else_branch: stmt.Stmt = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return stmt.If(condition, then_branch, else_branch)
    
    def print_statement(self) -> stmt.Stmt:
        value: expr.Expr = self.expression() # Isn't that what it's all about?
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)
    
    def return_statement(self) -> stmt.Stmt:
        keyword: Token = self.previous()
        value: expr.Expr = None

        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return stmt.Return(keyword, value)
    
    def var_declaration(self) -> stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer: expr.Expr = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def while_statement(self) -> stmt.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.)")
        condition: expr.Expr = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body: stmt.Stmt = self.statement()

        return stmt.While(condition, body)
    
    def expression_statement(self) -> stmt.Stmt:
        expression: expr.Expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expression)
    
    def function(self, kind: str) -> stmt.Stmt:
        name: Token = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters: list[Token] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    Parser.error(self.peek(), "Can't  have more than 255 parameters")
                
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))

                if not self.match(TokenType.COMMA):
                    break
            
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")

        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body: list[stmt.Stmt] = self.block()
        return stmt.Function(name, parameters, body)
    
    def block(self) -> list[stmt.Stmt]:
        statements: list[stmt.Stmt] = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def assignment(self) -> expr.Expr:
        expression: expr.Expr = self.or_()
        if self.match(TokenType.EQUAL):
            equals: Token = self.previous()
            value: expr.Expr = self.assignment()

            if isinstance(expression, expr.Variable):
                name: Token = expression.name
                return expr.Assign(name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expression
    
    def or_(self) -> expr.Expr:
        expression: expr.Expr = self.and_()

        while self.match(TokenType.OR):
            operator: Token = self.previous()
            right: expr.Expr = self.and_()
            expression = expr.Logical(expression, operator, right)
        
        return expression
    
    def and_(self) -> expr.Expr:
        expression: expr.Expr = self.equality()

        while self.match(TokenType.AND):
            operator: Token = self.previous()
            right: expr.Expr = self.equality()
            expression = expr.Logical(expression, operator, right)
        
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
        return self.call()
    
    def finish_call(self, callee: expr.Expr) -> expr.Expr:
        arguments: list[expr.Expr] = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    Parser.error(self.peek(), "Can't have more than 255 arguments.")
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        
        paren: Token = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return expr.Call(callee, paren, arguments)
    
    def call(self) -> expr.Expr:
        expression: expr.Expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(expression)
            else:
                break
        
        return expression

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
