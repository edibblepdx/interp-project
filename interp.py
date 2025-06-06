#!/usr/bin/env python

# ==============================================================================
# There are some misc tests at the bottom of this file, but it also runs a test
# suite defined in eval_domain.py. The README has more information.
# ==============================================================================

# NOTE: midiutil is included as suggested in the project information
from midiutil import MIDIFile  # version 1.2.1

import os  # to play the midi
import tempfile  # also to play the midi
from dataclasses import dataclass
from typing import Any

# ==============================================================================
# TYPES
# ==============================================================================

type Literal = int | bool | Note
type Expr = (
    Lit | Add | Sub | Mul | Div | Neg | And | Or | Not | Eq
    | Neq | Lt | Gt | Leq | Geq | If | Let | Name | Note | Join
    | Slice | Letfun | App | Assign | Seq | Show | Write
)

type Loc[V] = list[V] # always a singleton list
type Binding[V] = tuple[str, V]  # this tuple type is always a pair
type Env[V] = tuple[Binding[V], ...]  # this tuple type has arbitrary length
emptyEnv: Env[Any] = ()  # the empty environment has no bindings


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


@dataclass
class Letfun():
    """Function Definition"""
    name: str
    param: str
    bodyexpr: Expr
    inexpr: Expr
    def __str__(self) -> str:
        return f"letfun {self.name} ({self.param}) = {self.bodyexpr} in {self.inexpr} end"


@dataclass
class App():
    """Function Application"""
    fun: Expr
    arg: Expr
    def __str__(self) -> str:
        return f"({self.fun} ({self.arg}))"


type Value = Literal | Closure | Tune
@dataclass
class Closure:
    """Closure"""
    param: str
    body: Expr
    env: Env[Value]
    def __str__(self) -> str:
        return f"({self.param}, {self.body})"


@dataclass
class Assign:
    """Variable Assignment"""
    name: str
    value: Expr
    def __str__(self) -> str:
        return f"({self.name} := {self.value})"


@dataclass
class Seq:
    """Sequence Expression"""
    expr1: Expr
    expr2: Expr
    def __str__(self) -> str:
        return f"({self.expr1}; {self.expr2})"


@dataclass
class Show:
    """Show Expression Value"""
    expr: Expr
    def __str__(self) -> str:
        return f"(show {self.expr})"


@dataclass
class Read:
    """Read Integer"""
    def __str__(self) -> str:
        return f"read"


@dataclass
class Write:
    """Write Midi"""
    tune: Expr
    name: str
    def __str__(self) -> str:
        return f"(write {self.tune} {self.name})"


@dataclass
class Run:
    """Run Midi"""
    name: str
    def __str__(self) -> str:
        return f"(run {self.name})"


@dataclass
class Repeat:
    """Repeat Tune"""
    count: Expr
    tune: Expr
    def __str__(self) -> str:
        return f"(repeat {self.count} {self.tune})"


@dataclass
class Reverse:
    """Reverse Tune"""
    tune: Expr
    def __str__(self) -> str:
        return f"(reverse {self.tune})"


class EvalError(Exception):
    """Invalid Expressions"""
    pass


class EnvError(Exception):
    """Invalid Environment"""
    pass


class RuntimeError(Exception):
    """Input/Output"""
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


def newLoc[V](value: V) -> Loc[V]:
    return [value]


def getLoc[V](loc: Loc[V]) -> V:
    return loc[0]


def setLoc[V](loc: Loc[V], value: V) -> None:
    loc[0] = value


def eval(e: Expr) -> (Literal|Tune):
    return evalInEnv(emptyEnv, e)


def evalInEnv(env: Env[Literal], e: Expr) -> (Literal|Tune):
    def isInt(*args) -> bool:
        return all(type(x) is int for x in args)

    def isBool(*args) -> bool:
        return all(type(x) is bool for x in args)

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
                case (Tune(notes), v) if isInt(v):
                    if v <= 0:
                        raise EvalError("duration modifier must be positive")
                    new_notes = [
                        Note(note.pitch, note.duration * v)
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
                # DOMAIN SPECIFIC EXTENSION
                case (Tune(notes), v) if isInt(v):
                    if v <= 0:
                        raise EvalError("duration modifier must be positive")
                    else:
                        new_notes = [
                            Note(
                                note.pitch,
                                d if (d := note.duration // v) != 0 else 1
                            )
                            for note in notes
                        ]
                    return Tune(new_notes)
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
                            raise EvalError("Right logical operation on non-boolean")
                case _:
                    raise EvalError("Left logical operation on non-boolean")

        case Or(l, r):
            match evalInEnv(env, l):
                case l if isBool(l):
                    if l:
                        return l
                    match evalInEnv(env, r):
                        case r if isBool(r):
                            return r
                        case _:
                            raise EvalError("Right logical operation on non-boolean")
                case _:
                    raise EvalError("Left logical operation on non-boolean")

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
                    if type(l) is not type(r):
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
                    if type(l) is not type(r):
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
            loc = lookupEnv(n, env)
            return getLoc(loc)

        case Let(n, d, b):
            v = evalInEnv(env, d)
            loc = newLoc(v)
            newEnv = extendEnv(n, loc, env)
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
                case _:
                    raise EvalError("non-sliceable type")

        # Functions
        # ---------

        case Letfun(n, p, b, i):
            c = Closure(p, b, env)
            loc = newLoc(c)
            newEnv = extendEnv(n, loc, env)
            c.env = newEnv
            return evalInEnv(newEnv, i)

        case App(f, a):
            fun = evalInEnv(env, f)
            match fun:
                case Closure(p, b, cenv):
                    arg = evalInEnv(env, a)
                    loc = newLoc(arg)
                    newEnv = extendEnv(p, loc, cenv)
                    return evalInEnv(newEnv, b)
                case _:
                    raise EvalError("application of non-function")

        # Variable Assignment
        # -------------------

        case Assign(n, v):
            loc = lookupEnv(n, env)
            if isinstance(getLoc(loc), Closure):
                raise EvalError("attempted assignment to name bound function")
            val = evalInEnv(env, v)
            setLoc(loc, val)
            return val

        # Sequence Expression
        # -------------------

        case Seq(e1, e2):
            evalInEnv(env, e1)
            return evalInEnv(env, e2)

        # Show Expression Value
        # ---------------------

        case Show(e):
            v = evalInEnv(env, e)
            match v:
                case Tune(notes):
                    print(notes)
                    try:
                        with tempfile.NamedTemporaryFile(suffix=".mid") as file:
                            writeMidi(notes, file.name)
                            runMidi(file.name)
                    except Exception as e:
                        print(f"failed to play tune: {e}")
                case _:
                    print(v)
            return v

        # Read Integer
        # ------------

        case Read():
            try:
                v = int(input("enter Integer: "))
                return v
            except Exception:
                raise RuntimeError("Expected Integer")

        # Midi Operations
        # ---------------

        case Write(e, name):
            match(evalInEnv(env, e)):
                case Tune(notes):
                    try:
                        writeMidi(notes, name)
                        return True
                    except Exception as e:
                        raise RuntimeError(f"Failed to write Midi: {e}")
                case _:
                    raise RuntimeError("Expected Tune")

        case Run(name):
            try:
                runMidi(name)
                return True
            except Exception as e:
                raise RuntimeError(f"Failed to run Midi: {e}")

        # Repeat and Reverse
        # ------------------

        case Repeat(count, tune):
            match (evalInEnv(env, count), evalInEnv(env, tune)):
                case (count, Tune(notes)) if isInt(count):
                    return Tune(notes * count)
                case (_, _):
                    raise EvalError("expected integer and tune")

        case Reverse(tune):
            match evalInEnv(env, tune):
                case Tune(notes):
                    return Tune(notes[::-1])
                case _:
                    raise EvalError("expected tune")

        # Invalid Expression
        # ------------------

        case _:
            raise EvalError(f"unknown expression type: {e}")

    return # type: ignore

def writeMidi(notes: list[Note], name: str):
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
        except Exception:
            pass

        time = time + note.duration

    with open(name, "wb") as output_file:
        MyMIDI.writeFile(output_file)


def runMidi(name: str):
    if os.name != 'posix':
        raise RuntimeError("non-POSIX system")

    if os.system("which vlc > /dev/null 2>&1") != 0:
        raise RuntimeError("VLC player not found")

    if os.system(f"[ -f {name} ] > /dev/null 2>&1") != 0:
        raise RuntimeError(f"no midi file {name}")

    if os.system(f"vlc {name} > /dev/null 2>&1"):
        raise RuntimeError(f"VLC error")


def run(e: Expr, pretty = True, write: bool = False):
    if pretty:
        print(f"running {e}")
    try:
        match eval(e):
            case Tune(notes):
                print(f"result: {Tune(notes)}")

                if write:
                    writeMidi(notes, "tune.mid")

            case o:
                print(f"result: {o}")
    except EvalError as err:
        print(err)


if __name__ == "__main__":
    import unittest
    import test_domain

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
    run(
        Join(Note("A", 1), Join(Note("B", 2), Join(Note("C", 3), Note("D", 4)))),
        write=True
    )

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(testCaseClass=test_domain.TestEvalDomain)
    runner = unittest.TextTestRunner()
    runner.run(suite)

