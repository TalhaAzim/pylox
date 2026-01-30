"""
AST Grammar definitions for the Lox interpreter in structured s-expression format.
Each grammar entry contains the base class name and a tuple of concrete types,
where each type has a name followed by field-name/type pairs.

You either die a hero, or live long enough to see yourself write lisp. - Harvey Dent (I think)
"""

GRAMMAR = (
    ("Expr", (
        ("Assign", ("name", "Token"), ("value", "Expr")),
        ("Binary", ("left", "Expr"), ("operator", "Token"), ("right", "Expr")),
        ("Call", ("callee", "Expr"), ("paren", "Token"), ("arguments", "list[Expr]")),
        ("Grouping", ("expression", "Expr")),
        ("Literal", ("value", "object")),
        ("Logical", ("left", "Expr"), ("operator", "Token"), ("right", "Expr")),
        ("Unary", ("operator", "Token"), ("right", "Expr")),
        ("Variable", ("name", "Token"))
    )),
    ("Stmt", (
        ("Block", ("statements", "list[Stmt]")),
        ("Expression", ("expression", "Expr")),
        ("Function", ("name", "Token"), ("params", "list[Token]"), ("body", "list[Stmt]")),
        ("If", ("condition", "Expr"), ("then_branch", "Stmt"), ("else_branch", "Stmt")),
        ("Print", ("expression", "Expr")),
        ("Return", ("keyword", "Token"), ("value", "Expr")),
        ("Var", ("name", "Token"), ("initializer", "Expr")),
        ("While", ("condition", "Expr"), ("body", "Stmt"))
    ))
)