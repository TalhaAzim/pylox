#!/usr/bin/env python3
import sys, os
from abc import ABC, abstractmethod

class GenerateAst():
    
    @staticmethod
    def main(*args: list[str]) -> None:
        if len(args) != 1:
            print("Usage: generate_ast <output directory>", file = sys.stderr)
            sys.exit(64)
        output_dir: str = args[0]
        GenerateAst.define_ast(output_dir, "Expr", [
            "Assign   -> name: 'Token', value: 'Expr'",
            "Binary   -> left: 'Expr', operator: Token, right: 'Expr'",
            "Grouping -> expression: 'Expr'",
            "Literal  -> value: 'object'",
            "Logical  -> left: 'Expr', operator: 'Token', right: 'Expr'",
            "Unary    -> operator: 'Token', right: 'Expr'",
            "Variable -> name: 'Token'"
        ])
        GenerateAst.define_ast(output_dir, "Stmt", [
            "Block      -> statements: 'list[Stmt]'",
            "Expression -> expression: 'Expr'",
            "If         -> condition: 'Expr', thenBranch: 'Stmt', elseBranch: 'Stmt'",
            "Print      -> expression: 'Expr'",
            "Var        -> name: 'Token', initializer: 'Expr'",
            "While      -> condition: 'Expr', body: 'Stmt'"
        ])
    
    @staticmethod
    def define_ast(output_dir: str, basename: str, types: list[str]) -> None:
        path = os.path.join(output_dir, f"{basename.lower()}.py")
        
        with open(path, "w") as f:
            src = '\n'.join([
              "from abc import ABC, abstractmethod",
              "from token import Token",
              "", 
              f"class {basename.capitalize()}(ABC):",
              "",
              "    @abstractmethod",
              "    def accept(self, visitor: 'Visitor') -> None:",
              "        raise NotImplementedError",
              ""])
            
            print(src, file=f)

            for atype in types:
                class_name, fieldspec = (each.strip() for each in atype.split("->"))
                GenerateAst.define_type(f, basename, class_name, fieldspec)

            GenerateAst.define_visitor(f, basename, types)
    
    @staticmethod
    def define_visitor(writer: object, basename: str, types: list[str]) -> None:
        print(f"class Visitor(ABC):", file=writer)

        for atype in types:
            type_name = atype.split("->")[0].strip()
            print("", file=writer)
            print(f"    @abstractmethod", file=writer)
            print(f"    def visit_{type_name.lower()}_{basename.lower()}(self, {basename.lower()}: '{type_name}') -> None:", file=writer)
            print("        raise NotImplementedError", file=writer)
        
        print("",file=writer)

    @staticmethod
    def define_type(writer: object, basename: str, class_name: str, fieldspec: str) -> None:
        print(f"class {class_name}({basename}):", file=writer)
        print("", file=writer)
        print(f"    def __init__(self, {fieldspec}) -> None:", file=writer)
        
        for field in fieldspec.split(", "):
            print(f"        self.{field} = {field[:field.index(':')]}", file=writer)
        
        print("", file=writer)
        print("    def accept(self, visitor: 'Visitor') -> None:", file=writer)
        print(f"        return visitor.visit_{class_name.lower()}_{basename.lower()}(self)", file=writer)
        print("", file=writer)

if __name__ == '__main__':
    GenerateAst.main("./")
