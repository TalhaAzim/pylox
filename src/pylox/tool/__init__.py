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
            "Binary   -> left: Expr, operator: Token, right: Expr",
            "Grouping -> expression: Expr",
            "Literal  -> value: object",
            "Unary    -> operator: Token, right: Expr"
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
              "    pass",
              "",
              ""])
            
            print(src, file=f)
            
            for atype in types:
                class_name, fields = (each.strip() for each in atype.split("->"))
                
                GenerateAst.define_type(f, basename, class_name, fields)
    
    @staticmethod
    def define_type(writer: object, basename: str, class_name: str, fieldspec: str) -> None:
        print(f"class {class_name}({basename}):", file=writer)
        print("", file=writer)
        print(f"    def __init__(self, {fieldspec}) -> None:", file=writer)
        
        for field in fieldspec.split(", "):
            print(f"        this.{field} = {field[:field.index(':')]}", file=writer)
        
        print("", file=writer)

if __name__ == '__main__':
    GenerateAst.main("./")
