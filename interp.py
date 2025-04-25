#!/usr/bin/env python

# NOTE: midiutil is included as suggested in the project information
from midiutil import MIDIFile # version 1.2.1

from dataclasses import dataclass
from typing import Any

# DOMAIN SPECIFIC TYPES
# -----------------------------------------------
type Pitch = str    # keys on the piano
type Duration = int # in seconds
type Note_t = tuple[Pitch, Duration]
type Tune_t = tuple[Note_t, ...]
emptyTune: Tune_t = ()

# map notes to midi numbers on octave 3
# https://computermusicresource.com/midikeys.html
DEGREES = {
    "C": 60,
    "D": 62,
    "E": 64,
    "F": 65,
    "G": 67,
    "A": 69,
    "B": 71,
    "R": None, # Rest
}

def extendTune(pitch: Pitch, duration: Duration, tune: Tune_t) -> Tune_t:
    return tune + ((pitch, duration),)
# -----------------------------------------------

type Literal = int | bool | Tune
type Expr = Lit | Add | Sub | Mul | Div | Neg | And | Or | Not | Eq | Neq | \
            Lt | Gt | Leq | Geq | If | Let | Name | Join

type Binding[V] = tuple[str,V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...] # this tuple type has arbitrary length
emptyEnv : Env[Any] = ()  # the empty environment has no bindings

# DOMAIN SPECIFIC EXTENSION
@dataclass
class Tune:
    """{Str, Int} Note"""
    tune: Tune_t
    def __str__(self) -> str:
        return ",".join(f"({p}, {d})" for (p, d) in self.tune)

# DOMAIN SPECIFIC EXTENSION
@dataclass
class Join:
    """{Str, Int} Note"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} | {self.right})"

@dataclass
class Lit:
    """{Int, Bool} Literal"""
    value: Literal
    def __str__(self) -> str:
        return f"{self.value}"

@dataclass
class Add:
    """Addition"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} + {self.right})"

@dataclass
class Sub:
    """Subtraction"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} - {self.right})"

@dataclass
class Mul:
    """Multiplication"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} * {self.right})"

@dataclass
class Div:
    """Integer Division"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} // {self.right})"

@dataclass
class Neg():
    subexpr: Expr
    def __str__(self) -> str:
        return f"(- {self.subexpr})"

@dataclass
class And:
    """Logical And"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} and {self.right})"

@dataclass
class Or:
    """Logical Or"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} or {self.right})"

@dataclass
class Not:
    """Logical Not"""
    subexpr: Expr
    def __str__(self) -> str:
        return f"(not {self.subexpr})"

@dataclass
class Eq:
    """Equality"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} == {self.right})"

@dataclass
class Neq:
    """Equality"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} != {self.right})"

@dataclass
class Lt:
    """Strictly less than"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} < {self.right})"

@dataclass
class Gt:
    """Strictly greater than"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} > {self.right})"

@dataclass
class Leq:
    """Less than or equal"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} <= {self.right})"

@dataclass
class Geq:
    """Greater than or equal"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} >= {self.right})"

@dataclass
class If:
    """If {} then {} else {}"""
    cond: Expr
    thenexpr: Expr
    elseexpr: Expr
    def __str__(self) -> str:
        return f"(if {self.cond} then {self.thenexpr} else {self.elseexpr})"

@dataclass
class Let:
    """Let {} = {} in {}"""
    name: str
    defexpr: Expr
    bodyexpr: Expr
    def __str__(self) -> str:
        return f"(let {self.name} = {self.defexpr} in {self.bodyexpr})"

@dataclass
class Name():
    """Name"""
    name:str
    def __str__(self) -> str:
        return self.name

def isInt(*args):
    return all(type(x) is int for x in args)

def isBool(*args):
    return all(type(x) is bool for x in args)

def isTune(*args):
    return all

def lookupEnv[V](name: str, env: Env[V]) -> V :
    '''Return the first value bound to name in the input environment env
       (or raise an exception if there is no such binding)'''
    try:
        return next(v for (n,v) in env if n == name)
    except StopIteration:
        raise EnvError('name is not in environment: ' + name)

class EvalError(Exception):
    """Invalid Expressions"""
    pass

def extendEnv[V](name: str, value: V, env:Env[V]) -> Env[V]:
    """Return a new environment that extends the input environment
    env with a new binding from name to value"""
    return ((name, value),) + env

def eval(e: Expr) -> Literal :
    return evalInEnv(emptyEnv, e)

def evalInEnv(env: Env[Literal], e:Expr) -> bool:
    match e:
        case Lit(lit):
            return lit

        # Arithmetic Operators
        # --------------------

        case Add(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l + r
                case _:
                    raise EvalError("addition of non-integers")

        case Sub(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l - r
                case _:
                    raise EvalError("subtraction of non-integers")

        case Mul(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l * r
                case _:
                    raise EvalError("multiplication of non-integers")

        case Div(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    if r == 0:
                        raise EvalError("division by zero")
                    return l // r
                case _:
                    raise EvalError("division of non-integers")

        case Neg(subexpr):
            match evalInEnv(env, subexpr):
                case subexpr if isInt(subexpr):
                    return -subexpr
                case _:
                    raise EvalError("negation of non-integer")

        # Logical Operators
        # -----------------
        # And / Or should short circuit on the left operand
        # EVEN IF the right operand is non-boolean based on test file

        case And(l, r):
            match evalInEnv(env, l):
                case l if isBool(l):
                    if not l:
                        return l
                    match evalInEnv(env, r):
                        case r if isBool(r):
                            return r
                        case _:
                            raise EvalError("R logical operation on non-boolean")
                case _:
                    raise EvalError("L logical operation on non-boolean")

        case Or(l, r):
            match evalInEnv(env, l):
                case l if isBool(l):
                    if l:
                        return l
                    match evalInEnv(env, r):
                        case r if isBool(r):
                            return r
                        case _:
                            raise EvalError("R logical operation on non-boolean")
                case _:
                    raise EvalError("L logical operation on non-boolean")

        case Not(subexpr):
            match evalInEnv(env, subexpr):
                case subexpr if isBool(subexpr):
                    return not subexpr
                case _:
                    raise EvalError("logical operation on non-boolean")

        # Equality Operators
        # ------------------

        case Eq(l, r):
            (l, r) = (evalInEnv(env, l), evalInEnv(env, r))
            if type(l) != type(r):
                return False
            return l == r

        case Neq(l, r):
            (l, r) = (evalInEnv(env, l), evalInEnv(env, r))
            if type(l) != type(r):
                return False
            return l != r

        # Relational Operators
        # --------------------

        case Lt(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l < r
                case _:
                    raise EvalError("relational operation on non-integer")

        case Gt(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l > r
                case _:
                    raise EvalError("relational operation on non-integer")

        case Leq(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l <= r
                case _:
                    raise EvalError("relational operation on non-integer")

        case Geq(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l >= r
                case _:
                    raise EvalError("relational operation on non-integer")

        # Conditional Statements
        # ----------------------

        case If(cond, thenexpr, elseexpr):
            match evalInEnv(env, cond):
                case cond if isBool(cond):
                    if cond:
                        return evalInEnv(env, thenexpr)
                    else:
                        return evalInEnv(env, elseexpr)
                case _:
                    raise EvalError("if condition must be a boolean")

        # Let Bindings
        # ------------

        case Name(n):
             return lookupEnv(n,env)

        case Let(n,d,b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b)

        # Join (represented by '|')
        # -------------------------

        case Join(l, r):
            # DOMAIN SPECIFIC EXTENSION
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (Tune(l), Tune(r)):
                    return l + r
                case _:
                    raise EvalError("non-joinable type")

def run(e: Expr):
    print(f"running {e}")
    try:
        print(f"result: {eval(e)}")
    except EvalError as err:
        print(err)

if __name__ == "__main__":
    # Lit(Tune((("A", 1)))) has a lot of parens so be careful
    run(Lit(Tune((("A", 1),))))
    run(Join(Lit(Tune((("A", 1),))), Lit(Tune((("B", 2),)))))
