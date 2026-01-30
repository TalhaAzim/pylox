#!/usr/bin/env python3
import sys
import os
from abc import ABC, abstractmethod
from grammar import GRAMMAR
from typing import TextIO


class GenerateAst():
    
    @staticmethod
    def main(args: list[str]) -> None:
        if len(args) != 1:
            print("Usage: generate_ast <output directory>", file = sys.stderr)
            sys.exit(64)
        output_dir: str = args[0]
        
        for basename, types in GRAMMAR:
            GenerateAst.define_ast(output_dir, basename, types)
    
    @staticmethod
    def define_ast(output_dir: str, basename: str, types: tuple) -> None:
        path = os.path.join(output_dir, f"{basename.lower()}.py")
        
        with open(path, "w") as f:
            src = '\n'.join([
              "from abc import ABC, abstractmethod",
              "from token import Token",
              "", 
              f"class {basename}(ABC):",
              "",
              "    @abstractmethod",
              "    def accept(self, visitor: 'Visitor') -> None:",
              "        raise NotImplementedError",
              ""])
            
            print(src, file=f)

            for atype in types:
                class_name = atype[0]
                fieldspec = atype[1:]
                GenerateAst.define_type(f, basename, class_name, fieldspec)

            GenerateAst.define_visitor(f, basename, types)
    
    @staticmethod
    def define_visitor(writer: TextIO, basename: str, types: tuple) -> None:
        print(f"class Visitor(ABC):", file=writer)

        for atype in types:
            type_name = atype[0]
            print("", file=writer)
            print(f"    @abstractmethod", file=writer)
            print(f"    def visit_{type_name.lower()}_{basename.lower()}(self, {basename.lower()}: '{type_name}') -> None:", file=writer)
            print("        raise NotImplementedError", file=writer)
        
        print("",file=writer)

    @staticmethod
    def define_type(writer: TextIO, basename: str, class_name: str, fieldspec: tuple) -> None:
        print(f"class {class_name}({basename}):", file=writer)
        print("", file=writer)
        
        # Build the constructor parameters
        param_strs = []
        for field_name, field_type in fieldspec:
            if field_type in ['Token', 'object']:
                param_strs.append(f"{field_name}: {field_type}")
            else:
                param_strs.append(f"{field_name}: '{field_type}'")
        
        print(f"    def __init__(self, {', '.join(param_strs)}) -> None:", file=writer)
        
        # Build the field assignments
        for field_name, field_type in fieldspec:
            if field_type in ['Token', 'object']:
                print(f"        self.{field_name}: {field_type} = {field_name}", file=writer)
            else:
                print(f"        self.{field_name}: '{field_type}' = {field_name}", file=writer)
        
        print("", file=writer)
        print("    def accept(self, visitor: 'Visitor') -> None:", file=writer)
        print(f"        return visitor.visit_{class_name.lower()}_{basename.lower()}(self)", file=writer)
        print("", file=writer)

if __name__ == '__main__':
    GenerateAst.main(["./"])