#!/usr/bin/env python3

import unittest
from unittest import TestCase

import interp
from interp import (
    Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Eq
   , Neq, Lt, Gt, Leq, Geq, If, Let, Name, Note, Join
   , Slice, Letfun, App, Tune, Show, Write, Run
   , Repeat, Reverse
)

from io import StringIO
import re

import contextlib
from contextlib import redirect_stdout, redirect_stderr
with redirect_stdout(None), redirect_stderr(None):
    from parse_run import just_parse

class TestEvalDomain(TestCase):
    def expect(self, expr, expected):
        try:
            got = interp.eval(expr)
        except BaseException as e:
            self.fail(f"eval({expr}) threw {type(e).__name__} (should be {expected})")
        self.assertEqual(got, expected, expr)

    def expect_error(self, expr):
        with self.assertRaises(BaseException, msg=expr):
            interp.eval(expr)

    # Evaluate Note
    def test_00(self):
        # Note
        # => Tune
        expr = Note("A", 1)
        self.expect(expr, Tune([Note("A", 1)]))

    # Join Notes
    def test_01(self):
        # Note | Note
        # => Tune
        expr = Join(Note("A", 1), Note("B", 2))
        self.expect(expr, Tune([Note("A", 1), Note("B", 2)]))

    # Join Notes
    def test_02(self):
        # Note | Note | Note
        # => Tune
        expr = Join(Note("A", 1), Join(Note("B", 2), Note("C", 3)))
        self.expect(expr, Tune([Note("A", 1), Note("B", 2), Note("C", 3)]))

    # Add (transpose pitch)
    def test_03(self):
        # Note + 2
        # => Tune
        expr = Add(Note("A", 1), Lit(2))
        self.expect(expr, Tune([Note("B", 1)]))

    # Subtract (transpose pitch)
    def test_04(self):
        # Note - 2
        # => Tune
        expr = Sub(Note("A", 1), Lit(2))
        self.expect(expr, Tune([Note("G", 1)]))

    # Multiply (change duration)
    def test_05(self):
        # Note * 2
        # => Tune
        expr = Mul(Note("A", 2), Lit(2))
        self.expect(expr, Tune([Note("A", 4)]))

    # Multiply (change duration) EXCEPT
    def test_06(self):
        # Note * -2
        # => Tune
        expr = Mul(Note("A", 2), Neg(Lit(2)))
        with self.assertRaises(Exception):
            interp.eval(expr)

    # Multiply (change duration)
    def test_07(self):
        # Tune * 2
        # => Tune
        expr = Mul(Join(Note("A", 2), Note("B", 4)), Lit(2))
        self.expect(expr, Tune([Note("A", 4), Note("B", 8)]))

    # Multiply (change duration) EXCEPT
    def test_08(self):
        # Tune * -2
        # => Tune
        expr = Mul(Join(Note("A", 2), Note("B", 4)), Neg(Lit(2)))
        with self.assertRaises(Exception):
            interp.eval(expr)

    # Note Equality
    def test_09(self):
        # Note == Note
        # => True
        expr = Eq(Note("A", 1), Note("A", 1))
        self.expect(expr, True)

    # Note Equality
    def test_10(self):
        # Note == Note
        # => False
        expr = Eq(Note("A", 1), Note("B", 2))
        self.expect(expr, False)

    # Note Inequality
    def test_11(self):
        # Note != Note
        # => False
        expr = Neq(Note("A", 1), Note("A", 1))
        self.expect(expr, False)

    # Note Inequality
    def test_12(self):
        # Note != Note
        # => True
        expr = Neq(Note("A", 1), Note("B", 2))
        self.expect(expr, True)

    # Tune Equality
    def test_13(self):
        # Tune == Tune
        # => True
        expr = Eq(Join(Note("A", 1), Note("B", 2)), Join(Note("A", 1), Note("B", 2)))
        self.expect(expr, True)

    # Tune Equality
    def test_14(self):
        # Tune == Tune
        # => False
        expr = Eq(Join(Note("A", 1), Note("B", 2)), Join(Note("C", 1), Note("D", 2)))
        self.expect(expr, False)

    # Tune Inequality
    def test_15(self):
        # Tune != Tune
        # => False
        expr = Neq(Join(Note("A", 1), Note("B", 2)), Join(Note("A", 1), Note("B", 2)))
        self.expect(expr, False)

    # Tune Inequality
    def test_16(self):
        # Tune != Tune
        # => True
        expr = Neq(Join(Note("A", 1), Note("B", 2)), Join(Note("C", 1), Note("D", 2)))
        self.expect(expr, True)

    # Tune Slice
    def test_17(self):
        # Tune[1:2]
        # => []
        expr = Slice(Note("A", 1), Lit(1), Lit(2))
        self.expect(expr, Tune([]))

    # Tune Slice
    def test_18(self):
        # Tune[1:2]
        # => Tune
        expr = Slice(Join(Note("A", 1), Note("B", 2)), Lit(1), Lit(2))
        self.expect(expr, Tune([Note("B", 2)]))

    def test_19(self):
        # Geq integers
        expr = Geq(Lit(42), Lit(0))
        self.expect(expr, True)
        expr = Geq(Lit(42), Lit(42))
        self.expect(expr, True)
        expr = Geq(Lit(0), Lit(42))
        self.expect(expr, False)

    def test_20(self):
        # Leq integers
        expr = Leq(Lit(42), Lit(0))
        self.expect(expr, False)
        expr = Leq(Lit(42), Lit(42))
        self.expect(expr, True)
        expr = Leq(Lit(0), Lit(42))
        self.expect(expr, True)

    def test_21(self):
        # Neq integers
        expr = Neq(Lit(42), Lit(0))
        self.expect(expr, True)
        expr = Neq(Lit(42), Lit(42))
        self.expect(expr, False)

    def test_22(self):
        # Repeat Tune
        expr = Repeat(Lit(1), Note("A", 1))
        self.expect(expr, Tune([Note("A", 1)]))
        expr = Repeat(Lit(3), Note("A", 1))
        self.expect(expr, Tune([Note("A", 1), Note("A", 1), Note("A", 1)]))
        expr = Repeat(Lit(2), Join(Note("A", 1), Note("B", 2)))
        self.expect(expr, Tune([Note("A", 1), Note("B", 2), Note("A", 1), Note("B", 2)]))

    def test_23(self):
        # Reverse Tune
        expr = Reverse(Note("A", 1))
        self.expect(expr, Tune([Note("A", 1)]))
        expr = Reverse(Join(Note("A", 1), Note("B", 2)))
        self.expect(expr, Tune([Note("B", 2), Note("A", 1)]))

    def test_23(self):
        # Divide Note
        expr = Div(Note("A", 1), Lit(10))
        self.expect(expr, Tune([Note("A", 1)]))
        expr = Div(Note("A", 10), Lit(2))
        self.expect(expr, Tune([Note("A", 5)]))

    def test_23(self):
        # Divide Tune
        expr = Div(Join(Note("A", 1), Note("B", 2)), Lit(10))
        self.expect(expr, Tune([Note("A", 1), Note("B", 1)]))
        expr = Div(Join(Note("A", 10), Note("B", 20)), Lit(2))
        self.expect(expr, Tune([Note("A", 5), Note("B", 10)]))


class TestParseDomain(TestCase):
    def parse(self, concrete:str, expected):
        got = just_parse(concrete)
        self.assertEqual(
            got,
            expected,
            f'parser error: "{concrete}" got: {got} expected: {expected}'
        )

    def test_00(self):
        self.parse(
            "(A, 1)",
            Note("A", 1)
        )

    def test_01(self):
        self.parse(
            "(A, 1) | (B, 2)",
            Join(Note("A", 1), Note("B", 2))
        )

    def test_02(self):
        self.parse(
            "(A, 1) | (B, 2) | (C, 3)",
            Join(Note("A", 1), Join(Note("B", 2), Note("C", 3)))
        )

    def test_03(self):
        self.parse(
            "(A, 1) + 2",
            Add(Note("A", 1), Lit(2))
        )

    def test_04(self):
        self.parse(
            "(A, 1) - 2",
            Sub(Note("A", 1), Lit(2))
        )

    def test_05(self):
        self.parse(
            "(A, 1) * 2",
            Mul(Note("A", 1), Lit(2))
        )

    def test_06(self):
        self.parse(
            "(A, 1) * -2",
            Mul(Note("A", 1), Neg(Lit(2)))
        )

    def test_07(self):
        self.parse(
            "(((A, 2) | (B, 4)) * 2)",
            Mul(Join(Note("A", 2), Note("B", 4)), Lit(2))
        )

    def test_08(self):
        self.parse(
            "(((A, 2) | (B, 4)) * -2)",
            Mul(Join(Note("A", 2), Note("B", 4)), Neg(Lit(2)))
        )

    def test_09(self):
        self.parse(
            "(A, 1) == (A, 1)",
            Eq(Note("A", 1), Note("A", 1))
        )

    def test_10(self):
        self.parse(
            "(A, 1) != (A, 1)",
            Neq(Note("A", 1), Note("A", 1))
        )

    def test_11(self):
        self.parse(
            "((A, 1) | (B, 2)) == ((A, 1) | (B, 2))",
            Eq(Join(Note("A", 1), Note("B", 2)), Join(Note("A", 1), Note("B", 2)))
        )

    def test_12(self):
        self.parse(
            "((A, 1) | (B, 2)) != ((A, 1) | (B, 2))",
            Neq(Join(Note("A", 1), Note("B", 2)), Join(Note("A", 1), Note("B", 2)))
        )

    def test_13(self):
        self.parse(
            "(A, 1)[1:2]",
            Slice(Note("A", 1), Lit(1), Lit(2))
        )

    def test_14(self):
        self.parse(
            "((A, 1) | (B, 2))[1:2]",
            Slice(Join(Note("A", 1), Note("B", 2)), Lit(1), Lit(2))
        )

    def test_15(self):
        self.parse(
            "letfun getSlice (tune) = tune[1:2] in getSlice(((A, 1) | (B, 2) | (C, 3))) end",
            Letfun("getSlice", "tune", Slice(Name("tune"), Lit(1), Lit(2)), App(Name("getSlice"), Join(Note("A", 1), Join(Note("B", 2), Note("C", 3)))))
        )

    def test_16(self):
        self.parse(
            "let t1 = (A, 1) in letfun f(t2) = t1 | t2 in f((B, 2)) end end",
            Let("t1", Note("A", 1), Letfun("f", "t2", Join(Name("t1"), Name("t2")), App(Name("f"), Note("B", 2))))
        )

    def test_17(self):
        self.parse(
            "let t1 = (A, 1) | (B, 2) in show t1 end",
            Let("t1", Join(Note("A", 1), Note("B", 2)), Show(Name("t1")))
        )

    def test_18(self):
        self.parse(
            "let t1 = (A, 1) | (B, 2) in write t1 : tune.mid end",
            Let("t1", Join(Note("A", 1), Note("B", 2)), Write(Name("t1"), "tune.mid"))
        )

    def test_19(self):
        self.parse(
            "run tune.mid",
            Run("tune.mid")
        )

    def test_20(self):
        self.parse(
            "if write (A, 1) | (B, 2) : tune.mid"
                " then run tune.mid"
                " else false",
            If(Write(Join(Note("A", 1), Note("B", 2)), "tune.mid"),
                Run("tune.mid"),
                Lit(False)
            )
        )

    def test_21(self):
        self.parse(
            "write ((A, 1) | (B, 2))[1:2] : tune.mid",
            Write(Slice(Join(Note("A", 1), Note("B", 2)), Lit(1), Lit(2)), "tune.mid")
        )

    def test_22(self):
        self.parse(
            "repeat 5 : (A, 1)",
            Repeat(Lit(5), Note("A", 1))
        )

    def test_23(self):
        self.parse(
            "let a = (A, 1) in repeat 5 : a end",
            Let("a", Note("A", 1), Repeat(Lit(5), Name("a")))
        )


if __name__ == "__main__":
    unittest.main()
