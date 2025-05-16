#!/usr/bin/env python3

import unittest
from unittest import TestCase

import interp
from interp import (
    Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, Eq
   , Neq, Lt, Gt, Leq, Geq, If, Let, Name, Note, Join
   , Slice, Letfun, App, Tune
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
        self.expect(expr, Tune([Note("A", 1)]))

    # Multiply (change duration)
    def test_06(self):
        # Note * -2
        # => Tune
        expr = Mul(Note("A", 2), Neg(Lit(2)))
        self.expect(expr, Tune([Note("A", 4)]))

    # Multiply (change duration)
    def test_07(self):
        # Tune * 2
        # => Tune
        expr = Mul(Join(Note("A", 2), Note("B", 4)), Lit(2))
        self.expect(expr, Tune([Note("A", 1), Note("B", 2)]))

    # Multiply (change duration)
    def test_08(self):
        # Tune * -2
        # => Tune
        expr = Mul(Join(Note("A", 2), Note("B", 4)), Neg(Lit(2)))
        self.expect(expr, Tune([Note("A", 4), Note("B", 8)]))

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


if __name__ == "__main__":
    unittest.main()
