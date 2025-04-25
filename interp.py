#!/usr/bin/env python

# NOTE: midiutil is included as suggested in the project information
from midiutil import MIDIFile # version 1.2.1

import os # to play the midi
from dataclasses import dataclass
from typing import Any

# DOMAIN SPECIFIC TYPES
# -----------------------------------------------
type Pitch = str    # keys on the piano
type Duration = int # in seconds
type Note_t = tuple[Pitch, Duration]
type Tune_t = tuple[Note_t, ...]
emptyTune: Tune_t = ()

# C-Major scale
# https://computermusicresource.com/midikeys.html
CHROMATIC = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
REST = "R"

# this function is unused for now
def extendTune(pitch: Pitch, duration: Duration, tune: Tune_t) -> Tune_t:
    return tune + ((pitch, duration),)

def transposePitch(pitch: Pitch, half_steps: int):
    try:
        index = CHROMATIC.index(pitch)
        new_index = (index + half_steps) % 12
        return CHROMATIC[new_index]
    except:
        return REST
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
        return f"T'({",".join(f"({p}, {d})" for (p, d) in self.tune)},)"

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
                # DOMAIN SPECIFIC EXTENSION
                # shift each note by the specified number of half-steps
                case(Tune(l), r) if isInt(r):
                    new_notes = tuple((transposePitch(p, r), d) for (p, d) in l)
                    return Tune(new_notes)
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
                # DOMAIN SPECIFIC EXTENSION
                # change duration of each note by inverse of r if positive
                # else if negative scale by abs(r)
                case (Tune(l), r) if isInt(r):
                    if r == 0:
                        raise EvalError("divide by zero")
                    if r > 0:
                        new_notes = tuple((p, d // r) for (p, d) in l)
                    else:
                        new_notes = tuple((p, d * abs(r)) for (p, d) in l)
                    return Tune(new_notes)
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
        # Always false if types don't match

        case Eq(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                # DOMAIN SPECIFIC EXTENSION
                # pure equality
                case (Tune(l), Tune(r)):
                    if len(l) != len(r):
                        return False
                    for (l, r) in zip(l, r):
                        if l != r:
                            return False
                    return True
                case (l, r):
                    if type(l) != type(r):
                        return False
                    return l == r

        case Neq(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                # DOMAIN SPECIFIC EXTENSION
                # pure equality
                case (Tune(l), Tune(r)):
                    if len(l) != len(r):
                        return True
                    for (l, r) in zip(l, r):
                        if l != r:
                            return True
                    return False
                case (l, r):
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
            # join two tunes
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (Tune(l), Tune(r)):
                    return Tune(l + r)
                case _:
                    raise EvalError("non-joinable type")

def run(e: Expr):
    print(f"running {e}")
    try:
        match eval(e):
            case Tune(t):

                track    = 0
                channel  = 0
                time     = 0   # In beats
                tempo    = 250 # In BPM
                volume   = 100 # 0-127, as per the MIDI standard

                MyMIDI = MIDIFile(1)
                MyMIDI.addTempo(track, time, tempo)

                for (p, d) in t:
                    try:
                        pitch = CHROMATIC.index(p) + 60
                        MyMIDI.addNote(track, channel, pitch, time, d, volume)
                    except:
                        pass

                    time = time + d

                with open("tune.mid", "wb") as output_file:
                    MyMIDI.writeFile(output_file)

                print(f"result: {t}")
            case o:
                print(f"result: {o}")
    except EvalError as err:
        print(err)

if __name__ == "__main__":
    # Tune((("A", 1),)) has a lot of parens so be careful

    # Tests
    # -----

    # Lit
    print("lit")
    run(Lit(Tune((("A", 1),))))
    run(Lit(Tune((("A", 1), ("B", 2), ("C", 3)))))
    print()

    # Joins
    print("joins")
    run(Join(Lit(Tune((("A", 1),))), Lit(Tune((("B", 2),)))))
    run(Join(Lit(Tune((("A", 1),))), Lit(Tune((("B", 2), ("C", 3))))))
    print()

    # Multiply (change duration)
    print("multiply")
    run(Mul(Lit(Tune((("A", 5), ("B", 3),))), Lit(2)))
    run(Mul(Lit(Tune((("A", 5), ("B", 3),))), Lit(-2)))
    print()

    # Add (transpose pitch)
    print("add")
    run(Add(Lit(Tune((("A", 5), ("B", 3),))), Lit(2)))
    run(Add(Lit(Tune((("R", 5), ("D", 3),))), Lit(-2)))
    print()

    # Equality
    assert(eval(Eq(Lit(Tune((("R", 5),))), Lit(Tune((("D", 3),))))) == False)
    assert(eval(Eq(Lit(Tune((("R", 5), ("D", 3),))), Lit(2))) == False)
    assert(eval(Eq(Lit(Tune((("D", 3),))), Lit(Tune((("D", 3),))))) == True)
    assert(eval(Eq(Lit(Tune((("R", 5),))), Lit(Tune((("D", 3),("A", 4)))))) == False)
    assert(eval(Neq(Lit(Tune((("R", 5),))), Lit(Tune((("D", 3),))))) == True)
    assert(eval(Neq(Lit(Tune((("R", 5), ("D", 3),))), Lit(2))) == False)
    assert(eval(Neq(Lit(Tune((("D", 3),))), Lit(Tune((("D", 3),))))) == False)
    assert(eval(Neq(Lit(Tune((("R", 5),))), Lit(Tune((("D", 3),("A", 4)))))) == True)

    # Let
    run(Let('x', Lit(Tune((("A", 1),))),
                          Join(Name('x'), Lit(Tune((("B", 2),))))
            ))
    print()

    # Killer Queen (like the first two verses--I tried)
    run(Lit(Tune((
        ("A", 3), ("A", 3), ("D", 1), ("D", 2), ("C", 3), ("D", 1), ("A", 2),
        ("E", 2), ("D", 2), ("E", 1), ("F", 2), ("E", 1), ("D", 1), ("D", 2),
        ("D", 3), ("D", 3), ("C", 3), ("D", 2), ("A", 2), ("A", 2),
        ("E", 2), ("E", 2), ("E", 1), ("E", 3), ("F", 1), ("G", 1), ("A", 2),
        ("C", 2), ("A", 1), ("A", 2), ("G", 1), ("F", 1), ("G", 2),
        ("E", 3), ("F", 1), ("F", 3), ("F", 2), ("E", 1), ("D", 2), ("E", 1),
        ("D", 1), ("C#", 1), ("D", 1), ("C#", 2), ("C#", 2), 
        ("C", 1), ("C", 1), ("C", 1), ("C", 1),
        ("C#", 2), ("C#", 1), ("A", 1), ("A", 1), ("G", 1),
    ))))

    os.system('vlc tune.mid')

    """Description of Domain Specific Extension

    A tune is an immutable tuple of notes: ((pitch: str, duration: int),).
    Where pitch is a string representing a key on the chromatic scale and
    duration is the length of the note. There is an additional pitch "R"
    for rest.

    Two tunes may be joined with '|' and ordered left to right.
    A tune may be sped up by * {i in Z: i > 0} (integer)
    A tune may be slowed down by * {i in Z: i < 0} (integer)
    A tune may transpose it's tune along the scale with +/-
    """

    """How to use

    A tune is a tuple so be careful AND it is a Literal 
        => Lit(Tune(((pitch, duration),)))

    Join(Lit(Tune((("A", 1),)), Lit(Tune((("B", 2),)))))
        => Tune((("A", 1), ("B", 2),))

    Mul(Lit(Tune((("A", 2),)), Lit(2))
        => Tune((("A", 1),)) INVERSE ( duration * 1/2 )

    Mul(Lit(Tune((("A", 2),)), Lit(-2))
        => Tune((("A", 4),))

    Add(Lit(Tune((("A", 2),)), Lit(2))
        => Tune((("B", 2),))

    Add(Lit(Tune((("A", 2),)), Lit(-2))
        => Tune((("G", 2),))
    """
