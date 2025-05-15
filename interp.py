#!/usr/bin/env python

# NOTE: midiutil is included as suggested in the project information
from midiutil import MIDIFile  # version 1.2.1

import os  # to play the midi
from dataclasses import dataclass
from typing import Any

# ==============================================================================
# STANDARD TYPES
# ==============================================================================

type Literal = int | bool | Note
type Expr = (
    Lit | Add | Sub | Mul | Div | Neg | And | Or | Not | Eq
    | Neq | Lt | Gt | Leq | Geq | If | Let | Name | Note | Join
)

type Binding[V] = tuple[str, V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...]  # this tuple type has arbitrary length
emptyEnv: Env[Any] = ()  # the empty environment has no bindings

# ==============================================================================
# DOMAIN SPECIFIC TYPES
# ==============================================================================

# C-Major scale
# https://computermusicresource.com/midikeys.html
CHROMATIC = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
REST = "R"


def transposePitch(pitch: str, half_steps: int) -> str:
    try:
        index = CHROMATIC.index(pitch)
        new_index = (index + half_steps) % 12
        return CHROMATIC[new_index]
    except Exception:
        return REST


# DOMAIN SPECIFIC EXTENSION
@dataclass
class Note:
    """{Str, Int} Note"""
    pitch: str  # keys on the piano
    duration: int  # in seconds
    def __eq__(self, other) -> bool:
        if isinstance(other, Note):
            return self.pitch == other.pitch and self.duration == other.duration
        return False
    def __str__(self) -> str:
        return f"({self.pitch}, {self.duration})"


# DOMAIN SPECIFIC EXTENSION
@dataclass
class Tune:
    """{ ((Note), ...) } Tune"""
    notes: list[Note]
    def __str__(self) -> str:
        return f"[{','.join(f'({note.pitch}, {note.duration})' for note in self.notes)}]"


# DOMAIN SPECIFIC EXTENSION
@dataclass
class Join:
    """{Expr, Expr} Join"""
    left: Expr
    right: Expr
    def __str__(self) -> str:
        return f"({self.left} | {self.right})"


# DOMAIN SPECIFIC EXTENSION
@dataclass
class Slice:
    """{Tune, Int, Int} Slice"""
    tune: Expr
    start: Expr
    end: Expr
    def __str__(self) -> str:
        return f"{self.tune}[{self.start}:{self.end}]"


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
class Neg:
    """Negation"""
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
class Name:
    """Name"""
    name: str
    def __str__(self) -> str:
        return self.name


def isInt(*args):
    return all(type(x) is int for x in args)


def isBool(*args):
    return all(type(x) is bool for x in args)


class EvalError(Exception):
    """Invalid Expressions"""
    pass

class EnvError(Exception):
    """Invalid Environment"""
    pass


def lookupEnv[V](name: str, env: Env[V]) -> V:
    """Return the first value bound to name in the input environment env
    (or raise an exception if there is no such binding)"""
    try:
        return next(v for (n, v) in env if n == name)
    except StopIteration:
        raise EnvError("name is not in environment: " + name)


def extendEnv[V](name: str, value: V, env: Env[V]) -> Env[V]:
    """Return a new environment that extends the input environment
    env with a new binding from name to value"""
    return ((name, value),) + env


def eval(e: Expr) -> Literal:
    return evalInEnv(emptyEnv, e)


def evalInEnv(env: Env[Literal], e: Expr) -> Literal:
    match e:
        case Lit(lit):
            return lit

        # DOMAIN SPECIFIC EXTENSION
        case Note(pitch, duration):
            return Tune([Note(pitch, duration)])

        # Arithmetic Operators
        # --------------------

        case Add(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l + r
                # DOMAIN SPECIFIC EXTENSION
                # shift each note by the specified number of half-steps
                case (Tune(notes), shift) if isInt(shift):
                    new_notes = [
                        Note(transposePitch(note.pitch, shift), note.duration) 
                        for note in notes
                    ]
                    return Tune(new_notes)
                case _:
                    raise EvalError("addition of non-integers or unsupported types")

        case Sub(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l - r
                # DOMAIN SPECIFIC EXTENSION
                # shift each note by the specified number of half-steps
                case (Tune(notes), shift) if isInt(shift):
                    new_notes = [
                        Note(transposePitch(note.pitch, -shift), note.duration) 
                        for note in notes
                    ]
                    return Tune(new_notes)
                case _:
                    raise EvalError("subtraction of non-integers or unsupported types")

        case Mul(l, r):
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (l, r) if isInt(l, r):
                    return l * r
                # DOMAIN SPECIFIC EXTENSION
                # change duration of each note by inverse of val if positive
                # else if negative scale by abs(val)
                case (Tune(notes), val) if isInt(val):
                    if r == 0:
                        raise EvalError("divide by zero")
                    if r > 0:
                        new_notes = [
                            Note(note.pitch, note.duration // val)
                            for note in notes
                        ]
                    else:
                        new_notes = [
                            Note(note.pitch, note.duration * abs(val))
                            for note in notes
                        ]
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
                case (Tune(n1), Tune(n2)):
                    if len(n1) != len(n2):
                        return False
                    for n1, n2 in zip(n1, n2):
                        if n1 != n2:
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
                case (Tune(n1), Tune(n2)):
                    if len(n1) != len(n2):
                        return False
                    for n1, n2 in zip(n1, n2):
                        if n1 != n2:
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
            return lookupEnv(n, env)

        case Let(n, d, b):
            v = evalInEnv(env, d)
            newEnv = extendEnv(n, v, env)
            return evalInEnv(newEnv, b)

        # Join (represented by '|')
        # -------------------------

        case Join(l, r):
            # DOMAIN SPECIFIC EXTENSION
            # join two tunes
            match (evalInEnv(env, l), evalInEnv(env, r)):
                case (Tune(n1), Tune(n2)):
                    return Tune(n1 + n2)
                case _:
                    raise EvalError("non-joinable type")

        # Slice (represented by [:])
        # -------------------------

        case Slice(tune, start, end):
            # DOMAIN SPECIFIC EXTENSION
            # get a tune slice
            match (evalInEnv(env, tune), evalInEnv(env, start), evalInEnv(env, end)):
                case (Tune(notes), start, end) if isInt(start, end):
                    return Tune(notes[start:end])
                case (a, b, c):
                    raise EvalError("non-sliceable type")


def run(e: Expr):
    print(f"running {e}")
    try:
        match eval(e):
            case Tune(notes):
                track = 0
                channel = 0
                time = 0  # In beats
                tempo = 250  # In BPM
                volume = 100  # 0-127, as per the MIDI standard

                MyMIDI = MIDIFile(1)
                MyMIDI.addTempo(track, time, tempo)

                for note in notes:
                    try:
                        pitch = CHROMATIC.index(note.pitch) + 60
                        duration = note.duration
                        MyMIDI.addNote(track, channel, pitch, time, duration, volume)
                    except:
                        pass

                    time = time + note.duration

                with open("tune.mid", "wb") as output_file:
                    MyMIDI.writeFile(output_file)

                print(f"result: {Tune(notes)}")
            case o:
                print(f"result: {o}")
    except EvalError as err:
        print(err)


if __name__ == "__main__":
    run(Note("A", 1))
    run(
        Join(Note("A", 1), Note("B", 2))
    )
    run(
        Join(Note("A", 1), Join(Note("B", 2), Note("C", 3)))
    )
    run(
        Let(
            'x',
            Join(Note("A", 1), Note("B", 2)),
            Slice(Name('x'), Lit(1), Lit(2))
        )
    )
    run(
        Add(Join(Note("A", 1), Note("B", 2)), Lit(2))
    )
    run(
        Sub(Join(Note("A", 1), Note("B", 2)), Lit(2))
    )
    run(
        Mul(Join(Note("A", 10), Note("B", 10)), Lit(2))
    )
    run(
        Eq(
            Join(Note("A", 1), Join(Note("B", 2), Note("C", 3))),
            Join(Note("A", 1), Join(Note("B", 2), Note("C", 3)))
        )
    )
    run(
        Neq(
            Join(Note("A", 1), Join(Note("B", 2), Note("C", 3))),
            Join(Note("A", 1), Join(Note("B", 2), Note("C", 3)))
        )
    )

