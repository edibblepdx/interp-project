#!/usr/bin/env python3

from lark import Lark, Token, ParseTree, Transformer
from lark.exceptions import VisitError
from pathlib import Path

from interp import (
    Literal, Note, Expr,
    Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Eq,
    Neq, Lt, Gt, Leq, Geq, If, Let, Name, Note, Join, 
    Slice, Letfun, App
)

parser = Lark(Path('expr.lark').read_text(), ambiguity='explicit')
#for checking against ambiguity:
#parser = Lark(Path('imp.lark').read_text(), parser='lalr', strict='True')

class ParseError(Exception):
    pass

class AmbiguousParse(Exception):
    pass

class ToProgram(Transformer[Token,Program]):
    """Defines a transformation from a parse tree into an AST"""
    def if(self, args: tuple[Expr, Expr, Expr]):
        pass
    def or(self, args: tuple[Expr, Expr]):
        pass
    def and(self, args: tuple[Expr, Expr]):
        pass
    def not(self, args: tuple[Expr]):
        pass
    def eq(self, args: tuple[Expr, Expr]):
        pass
    def neq(self, args: tuple[Expr, Expr]):
        pass
    def lt(self, args: tuple[Expr, Expr]):
        pass
    def gt(self, args: tuple[Expr, Expr]):
        pass
    def leq(self, args: tuple[Expr, Expr]):
        pass
    def geq(self, args: tuple[Expr, Expr]):
        pass
    # DOMAIN SPECIFIC EXTENSION
    def join(self, args: tuple[Expr, Expr]):
        pass
    def add(self, args: tuple[Expr, Expr]):
        pass
    def sub(self, args: tuple[Expr, Expr]):
        pass
    def mul(self, args: tuple[Expr, Expr]):
        pass
    def div(self, args: tuple[Expr, Expr]):
        pass
    def neg(self, args: tuple[Expr]):
        pass
    # DOMAIN SPECIFIC EXTENSION
    def slice(self, args: tuple[Expr, Expr, Expr]):
        pass
    def true(self):
        pass
    def false(self):
        pass
    def int(self, args: tuple[Token]):
        pass
    def name(self, args: tuple[Token]):
        pass
    # DOMAIN SPECIFIC EXTENSION
    def note(self, args: tuple[Token, Token]):
        pass
    def let(self, args: tuple[Token, Expr, Expr]):
        pass
    def letfun(self, args: tuple[Token, Token, Expr, Expr]):
        pass
    def app(self, args: tuple[Expr, Expr]):
        pass
    # ambiguity marker
    def _ambig(self,_) -> Expr:
        raise AmbiguousParse()

def parse(s:str) -> ParseTree:
    try:
        return parser.parse(s)
    except Exception as e:
        raise ParseError(e)

def genAST(t:ParseTree) -> Program:
    """Applies the transformer to convert a parse tree into an AST"""
    try:
        return ToProgram().transform(t)
    except VisitError as e:
        if isinstance(e.orig_exc, AmbiguousParse):
            raise AmbiguousParse()
        else:
            raise e

def parse_and_run(s: str):
    try:
        run(genAST(parse(s)))
    except AmbiguousParse:
        print("ambiguous parse")
    except ParseError as e:
        print(f"parse error: {e}")
