from __future__ import annotations

import argparse
import sys

from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener

from code_generator import CodeGeneratorVisitor
from interpreter import Interpreter
from PJPLexer import PJPLexer
from PJPParser import PJPParser
from type_checker import TypeCheckerVisitor


class SyntaxErrorListener(ErrorListener):
    def __init__(self) -> None:
        super().__init__()
        self.errors: list[str] = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):  # type: ignore[override]
        self.errors.append(f"Syntax error at {line}:{column}: {msg}")


def parse_program(source_file: str):
    listener = SyntaxErrorListener()
    lexer = PJPLexer(FileStream(source_file, encoding="utf-8"))
    lexer.removeErrorListeners()
    lexer.addErrorListener(listener)

    token_stream = CommonTokenStream(lexer)
    parser = PJPParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(listener)

    tree = parser.program()
    return tree, listener.errors


def compile_program(source_file: str, output_file: str) -> bool:
    tree, syntax_errors = parse_program(source_file)
    if syntax_errors:
        for error in syntax_errors:
            print(error, file=sys.stderr)
        return False

    checker = TypeCheckerVisitor()
    checker.visit(tree)
    if checker.errors:
        for error in checker.errors:
            print(error, file=sys.stderr)
        return False

    generator = CodeGeneratorVisitor(checker.symbol_table, checker.node_types)
    generator.visit(tree)

    with open(output_file, "w", encoding="utf-8") as handle:
        for instruction in generator.instructions:
            handle.write(instruction + "\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple PJP compiler and interpreter")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile", help="Compile source code into stack instructions")
    compile_parser.add_argument("source")
    compile_parser.add_argument("-o", "--output", default="output.txt")

    run_parser = subparsers.add_parser("run", help="Run generated stack instructions")
    run_parser.add_argument("program")
    run_parser.add_argument("--input")

    execute_parser = subparsers.add_parser("execute", help="Compile source code and run it")
    execute_parser.add_argument("source")
    execute_parser.add_argument("-o", "--output", default="output.txt")
    execute_parser.add_argument("--input")

    args = parser.parse_args()

    if args.command == "compile":
        return 0 if compile_program(args.source, args.output) else 1

    if args.command == "run":
        Interpreter(args.program, args.input).run()
        return 0

    if args.command == "execute":
        if not compile_program(args.source, args.output):
            return 1
        Interpreter(args.output, args.input).run()
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
