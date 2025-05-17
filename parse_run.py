#!/usr/bin/env python3

from lark import Lark, Token, ParseTree, Transformer
from lark.exceptions import VisitError
from pathlib import Path

from interp import (
    Literal, Note, Expr,
    Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Eq,
    Neq, Lt, Gt, Leq, Geq, If, Let, Name, Note, Join, 
    Slice, Letfun, App,
    run
)


parser = Lark(Path('expr.lark').read_text(), parser='earley', ambiguity='explicit')
#for checking against ambiguity:
#parser = Lark(Path('expr.lark').read_text(), parser='lalr', strict='True')


class ParseError(Exception):
    pass


class AmbiguousParse(Exception):
    pass


class ToExpr(Transformer[Token, Expr]):
    """Defines a transformation from a parse tree into an AST"""

    def if_(self, args: tuple[Expr, Expr, Expr]) -> Expr:
        return If(*args)

    def or_(self, args: tuple[Expr, Expr]) -> Expr:
        return Or(*args)

    def and_(self, args: tuple[Expr, Expr]) -> Expr:
        return And(*args)

    def not_(self, args: tuple[Expr]) -> Expr:
        return Not(*args)

    def eq(self, args: tuple[Expr, Expr]) -> Expr:
        return Eq(*args)

    def neq(self, args: tuple[Expr, Expr]) -> Expr:
        return Neq(*args)

    def lt(self, args: tuple[Expr, Expr]) -> Expr:
        return Lt(*args)

    def gt(self, args: tuple[Expr, Expr]) -> Expr:
        return Gt(*args)

    def leq(self, args: tuple[Expr, Expr]) -> Expr:
        return Leq(*args)

    def geq(self, args: tuple[Expr, Expr]) -> Expr:
        return Geq(*args)

    # DOMAIN SPECIFIC EXTENSION
    def join(self, args: tuple[Expr, Expr]) -> Expr:
        return Join(*args)

    def add(self, args: tuple[Expr, Expr]) -> Expr:
        return Add(*args)

    def sub(self, args: tuple[Expr, Expr]) -> Expr:
        return Sub(*args)

    def mul(self, args: tuple[Expr, Expr]) -> Expr:
        return Mul(*args)

    def div(self, args: tuple[Expr, Expr]) -> Expr:
        return Div(*args)

    def neg(self, args: tuple[Expr]) -> Expr:
        return Neg(*args)

    # DOMAIN SPECIFIC EXTENSION
    def slice(self, args: tuple[Expr, Expr, Expr]) -> Expr:
        return Slice(*args)

    def true(self, _) -> Expr:
        # unused
        return Lit(True)

    def false(self, _) -> Expr:
        # unused
        return Lit(False)

    def int(self, args: tuple[Token]) -> Expr:
        return Lit(int(args[0].value))

    def name(self, args: tuple[Token]) -> Expr:
        value = args[0].value
        if value == "true":
            return Lit(True)
        elif value == "false":
            return Lit(False)
        else:
            return Name(value)

    # DOMAIN SPECIFIC EXTENSION
    def note(self, args: tuple[Token, Token]) -> Expr:
        return Note(args[0].value, int(args[1].value))

    def let(self, args: tuple[Token, Expr, Expr]) -> Expr:
        return Let(args[0].value, args[1], args[2])

    def letfun(self, args: tuple[Token, Token, Expr, Expr]) -> Expr:
        return Letfun(args[0].value, args[1].value, args[2], args[3])

    def app(self, args: tuple[Expr, Expr]) -> Expr:
        return App(*args)

    # ambiguity marker
    def _ambig(self, _) -> Expr:
        raise AmbiguousParse()


def parse(s:str) -> ParseTree:
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParseError(e)


def genAST(t:ParseTree) -> Expr:
    """Applies the transformer to convert a parse tree into an AST"""
    try:
        return ToExpr().transform(t)
    except VisitError as e:
        if isinstance(e.orig_exc, AmbiguousParse):
            raise AmbiguousParse()
        else:
            raise e


def parse_and_run(s: str):
    """Parses and runs an expression"""
    try:
        t = parse(s)
        print(t.pretty())

        ast = genAST(t)
        run(ast); print()

    except AmbiguousParse:
        print("ambiguous parse")

    except ParseError as e:
        print(f"parse error: {e}")


def just_parse(s: str) -> (Expr|None):
    """Parses and pretty-prints an expression"""
    try:
        t = parse(s)

        print("raw:", t)
        print("pretty:", t.pretty())

        ast = genAST(t)
        print("raw AST:", repr(ast))

        return ast

    except AmbiguousParse:
        print("ambiguous parse")
        return None

    except ParseError as e:
        print(f"parse error: {e}")
        return None


if __name__ == "__main__":
    import test_domain
    import unittest

    parse_and_run("30 + 12")
    parse_and_run("(A, 1) | (B, 2)")
    parse_and_run("30 / 10")
    parse_and_run("true")
    parse_and_run("((A, 5) | (B, 2))[1:2]")

    # functions
    parse_and_run("letfun getSlice (tune) = tune[1:2] in getSlice(((A, 1) | (B, 2) | (C, 3))) end") # [(B, 2)] Matches

    # functions and closures
    parse_and_run("let t1 = (A, 1) in letfun f(t2) = t1 | t2 in f((B, 2)) end end") # [(A, 1), (B, 2)] Matches

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(testCaseClass=test_domain.TestParseDomain)
    runner = unittest.TextTestRunner()
    runner.run(suite)
