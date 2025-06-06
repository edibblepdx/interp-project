#!/usr/bin/env python3

# testing parser for core of milestone 3

import unittest
import interp
from interp  import Expr, Lit, Add, Sub, Mul, Div, Neg, And, Or, Not, \
                  Let, Name, Eq, Lt, If, Letfun, App, \
                  Read, Show, Assign, Seq


from io import StringIO
import re

import contextlib
from contextlib import redirect_stdout, redirect_stderr
with redirect_stdout(None), redirect_stderr(None):
    from parse_run import just_parse

class TestParsing(unittest.TestCase):
    def parse(self, concrete:str, expected):
        got = just_parse(concrete)
        if expected == "anything":
            self.assertNotEqual(got, None)
        else:
            self.assertEqual(
                got,
                expected,
                f'parser error: "{concrete}" got: {got} expected: {expected}')

    def test_001(self):
        self.parse(
            "x; a; b",
            Seq(Name("x"), Seq(Name("a"), Name("b"))),
        )

    def test_001_1(self):
        self.parse(
            "(x; a); b",
            Seq(Seq(Name("x"), Name("a")), Name("b")),
        )

    def test_002(self):
        self.parse(
            "x; a := b",
            Seq(Name("x"), Assign("a", Name("b"))),
        )

    def test_003(self):
        self.parse(
            "x; show a",
            Seq(Name("x"), Show(Name("a"))),
        )

    def test_004(self):
        self.parse(
            "x; if a then b else c",
            Seq(Name("x"), If(Name("a"), Name("b"), Name("c"))),
        )

    def test_004(self):
        self.parse(
            "x; if a then b else c",
            Seq(Name("x"), If(Name("a"), Name("b"), Name("c"))),
        )

    def test_005(self):
        self.parse(
            "x; a || b",
            Seq(Name("x"), Or(Name("a"), Name("b"))),
        )

    def test_005_1(self):
        self.parse(
            "(x; a) || b",
            Or(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_006(self):
        self.parse(
            "x; a && b",
            Seq(Name("x"), And(Name("a"), Name("b"))),
        )

    def test_006_1(self):
        self.parse(
            "(x; a) && b",
            And(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_007(self):
        self.parse(
            "x; ! a",
            Seq(Name("x"), Not(Name("a"))),
        )

    def test_008(self):
        self.parse(
            "x; a == b",
            Seq(Name("x"), Eq(Name("a"), Name("b"))),
        )

    def test_008_1(self):
        self.parse(
            "(x; a) == b",
            Eq(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_009(self):
        self.parse(
            "x; a < b",
            Seq(Name("x"), Lt(Name("a"), Name("b"))),
        )

    def test_009_1(self):
        self.parse(
            "(x; a) < b",
            Lt(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_010(self):
        self.parse(
            "x; a + b",
            Seq(Name("x"), Add(Name("a"), Name("b"))),
        )

    def test_010_1(self):
        self.parse(
            "(x; a) + b",
            Add(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_011(self):
        self.parse(
            "x; a - b",
            Seq(Name("x"), Sub(Name("a"), Name("b"))),
        )

    def test_011_1(self):
        self.parse(
            "(x; a) - b",
            Sub(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_012(self):
        self.parse(
            "x; a * b",
            Seq(Name("x"), Mul(Name("a"), Name("b"))),
        )

    def test_012_1(self):
        self.parse(
            "(x; a) * b",
            Mul(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_013(self):
        self.parse(
            "x; a / b",
            Seq(Name("x"), Div(Name("a"), Name("b"))),
        )

    def test_013_1(self):
        self.parse(
            "(x; a) / b",
            Div(Seq(Name("x"), Name("a")), Name("b"))
        )

    def test_014(self):
        self.parse(
            "x; -a",
            Seq(Name("x"), Neg(Name("a"))),
        )

    def test_015(self):
        self.parse(
            "x; a",
            Seq(Name("x"), Name("a")),
        )

    def test_016(self):
        self.parse(
            "x; 0",
            Seq(Name("x"), Lit(0)),
        )

    def test_017(self):
        self.parse(
            "x; a(b)",
            Seq(Name("x"), App(Name("a"), Name("b"))),
        )

    def test_017_1(self):
        self.parse(
            "(x; a)(b)",
            App(Seq(Name("x"), Name("a")), Name("b")),
        )

    def test_018(self):
        self.parse(
            "x; let a = b in c end",
            Seq(Name("x"), Let("a", Name("b"), Name("c"))),
        )

    def test_019(self):
        self.parse(
            "x; letfun a(b) = c in d end",
            Seq(Name("x"), Letfun("a", "b", Name("c"), Name("d"))),
        )

    def test_020(self):
        self.parse(
            "x; (a)",
            Seq(Name("x"), Name("a")),
        )

    def test_021(self):
        self.parse(
            "show a; x",
            Seq(Show(Name("a")), Name("x")),
        )

    def test_021_1(self):
        self.parse(
            "show (a; x)",
            Show(Seq(Name("a"), Name("x"))),
        )

    def test_022(self):
        self.parse(
            "a := b; c",
            Seq(Assign("a", Name("b")), Name("c")),
        )

    def test_022_1(self):
        self.parse(
            "a := (b; c)",
            Assign("a", Seq(Name("b"), Name("c"))),
        )        

    def test_023(self):
        self.parse(
            "if a then b else c; d",
            Seq(If(Name("a"), Name("b"), Name("c")), Name("d")),
        )

    def test_023_1(self):
        self.parse(
            "if a then b else (c; d)",
            If(Name("a"), Name("b"), Seq(Name("c"), Name("d"))),
        )

    def test_024(self):
        self.parse(
            "a || b; x",
            Seq(Or(Name("a"), Name("b")), Name("x")),
        )

    def test_024_1(self):
        self.parse(
            "a || (b; x)",
            Or(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_025(self):
        self.parse(
            "a && b; x",
            Seq(And(Name("a"), Name("b")), Name("x")),
        )

    def test_025_1(self):
        self.parse(
            "a && (b; x)",
            And(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_026(self):
        self.parse(
            "! a; x",
            Seq(Not(Name("a")), Name("x")),
        )

    def test_026_1(self):
        self.parse(
            "! (a; x)",
            Not(Seq(Name("a"), Name("x"))),
        )

    def test_027(self):
        self.parse(
            "a == b; x",
            Seq(Eq(Name("a"), Name("b")), Name("x")),
        )

    def test_027_1(self):
        self.parse(
            "a == (b; x)",
            Eq(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_028(self):
        self.parse(
            "a < b; x",
            Seq(Lt(Name("a"), Name("b")), Name("x")),
        )

    def test_028_1(self):
        self.parse(
            "a < (b; x)",
            Lt(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_029(self):
        self.parse(
            "a + b; x",
            Seq(Add(Name("a"), Name("b")), Name("x")),
        )

    def test_029_1(self):
        self.parse(
            "a + (b; x)",
            Add(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_030(self):
        self.parse(
            "a - b; x",
            Seq(Sub(Name("a"), Name("b")), Name("x")),
        )

    def test_030_1(self):
        self.parse(
            "a - (b; x)",
            Sub(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_031(self):
        self.parse(
            "a * b; x",
            Seq(Mul(Name("a"), Name("b")), Name("x")),
        )

    def test_031_1(self):
        self.parse(
            "a * (b; x)",
            Mul(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_032(self):
        self.parse(
            "a / b; x",
            Seq(Div(Name("a"), Name("b")), Name("x")),
        )

    def test_032_1(self):
        self.parse(
            "a / (b; x)",
            Div(Name("a"), Seq(Name("b"), Name("x"))),
        )

    def test_033(self):
        self.parse(
            "- a; x",
            Seq(Neg(Name("a")), Name("x")),
        )

    def test_033_1(self):
        self.parse(
            "- (a; x)",
            Neg(Seq(Name("a"), Name("x"))),
        )

    def test_034(self):
        self.parse(
            "a; x",
            Seq(Name("a"), Name("x")),
        )

    def test_035(self):
        self.parse(
            "0; x",
            Seq(Lit(0), Name("x")),
        )

    def test_036(self):
        self.parse(
            "a(b); x",
            Seq(App(Name("a"), Name("b")), Name("x")),
        )

    def test_037(self):
        self.parse(
            "let a = b in c end; x",
            Seq(Let("a", Name("b"), Name("c")), Name("x")),
        )

    def test_038(self):
        self.parse(
            "letfun a(b) = c in d end; x",
            Seq(Letfun("a", "b", Name("c"), Name("d")), Name("x")),
        )

    def test_039(self):
        self.parse(
            "(a); x",
            Seq(Name("a"), Name("x")),
        )

    def test_040(self):
        self.parse(
            "if a; b then c else d",
            If(Seq(Name("a"), Name("b")), Name("c"), Name("d")),
        )

    def test_041(self):
        self.parse(
            "if a then b; c else d",
            If(Name("a"), Seq(Name("b"), Name("c")), Name("d")),
        )

    def test_042(self):
        self.parse(
            "let a = b; c in d end",
            Let("a", Seq(Name("b"), Name("c")), Name("d")),
        )

    def test_043(self):
        self.parse(
            "let a = b in c; d end",
            Let("a", Name("b"), Seq(Name("c"), Name("d"))),
        )

    def test_044(self):
        self.parse(
            "letfun a(b) = c; d in e end",
            Letfun("a", "b", Seq(Name("c"), Name("d")), Name("e")),
        )

    def test_045(self):
        self.parse(
            "letfun a(b) = c in d; e end",
            Letfun("a", "b", Name("c"), Seq(Name("d"), Name("e"))),
        )

    def test_046(self):
        self.parse(
            "a(b; c)",
            App(Name("a"), Seq(Name("b"), Name("c"))),
        )

    def test_047(self):
        self.parse(
            "(a; b)",
            Seq(Name("a"), Name("b")),
        )

    def test_048(self):
        self.parse(
            "x := a := b",
            Assign("x", Assign("a", Name("b"))),
        )

    def test_049(self):
        self.parse(
            "x := show a",
            Assign("x", Show(Name("a"))),
        )

    def test_050(self):
        self.parse(
            "x := a || b",
            Assign("x", Or(Name("a"), Name("b"))),
        )

    def test_050_1(self):
        self.parse(
            "(x := a) || b",
            Or(Assign("x", Name("a")), Name("b")),
        )

    def test_051(self):
        self.parse(
            "x := a && b",
            Assign("x", And(Name("a"), Name("b"))),
        )

    def test_051_1(self):
        self.parse(
            "(x := a) && b",
            And(Assign("x", Name("a")), Name("b")),
        )

    def test_052(self):
        self.parse(
            "x := ! a",
            Assign("x", Not(Name("a"))),
        )

    def test_053(self):
        self.parse(
            "x := a == b",
            Assign("x", Eq(Name("a"), Name("b"))),
        )

    def test_053_1(self):
        self.parse(
            "(x := a) == b",
            Eq(Assign("x", Name("a")), Name("b")),
        )

    def test_054(self):
        self.parse(
            "x := a < b",
            Assign("x", Lt(Name("a"), Name("b"))),
        )

    def test_054_1(self):
        self.parse(
            "(x := a) < b",
            Lt(Assign("x", Name("a")), Name("b")),
        )

    def test_055(self):
        self.parse(
            "x := a + b",
            Assign("x", Add(Name("a"), Name("b"))),
        )

    def test_055_1(self):
        self.parse(
            "(x := a) + b",
            Add(Assign("x", Name("a")), Name("b")),
        )

    def test_056(self):
        self.parse(
            "x := a - b",
            Assign("x", Sub(Name("a"), Name("b"))),
        )

    def test_056_1(self):
        self.parse(
            "(x := a) - b",
            Sub(Assign("x", Name("a")), Name("b")),
        )

    def test_057(self):
        self.parse(
            "x := a * b",
            Assign("x", Mul(Name("a"), Name("b"))),
        )

    def test_057_1(self):
        self.parse(
            "(x := a) * b",
            Mul(Assign("x", Name("a")), Name("b")),
        )

    def test_058(self):
        self.parse(
            "x := a / b",
            Assign("x", Div(Name("a"), Name("b"))),
        )

    def test_058_1(self):
        self.parse(
            "(x := a) / b",
            Div(Assign("x", Name("a")), Name("b")),
        )

    def test_059(self):
        self.parse(
            "x := - a",
            Assign("x", Neg(Name("a"))),
        )

    def test_060(self):
        self.parse(
            "x := a",
            Assign("x", Name("a")),
        )

    def test_061(self):
        self.parse(
            "x := 0",
            Assign("x", Lit(0)),
        )

    def test_062(self):
        self.parse(
            "x := a(b)",
            Assign("x", App(Name("a"), Name("b"))),
        )

    def test_063(self):
        self.parse(
            "x := let a = b in c end",
            Assign("x", Let("a", Name("b"), Name("c"))),
        )

    def test_064(self):
        self.parse(
            "x := letfun a(b) = c in d end",
            Assign("x", Letfun("a", "b", Name("c"), Name("d"))),
        )

    def test_065(self):
        self.parse(
            "x := (a)",
            Assign("x", Name("a")),
        )

    def test_066(self):
        self.parse(
            "if a := b then c else d",
            If(Assign("a", Name("b")), Name("c"), Name("d")),
        )

    def test_999(self):
        self.parse(
            "if a then b := c else d",
            If(Name("a"), Assign("b", Name("c")), Name("d")),
        )

    def test_067(self):
        self.parse(
            "if a then b else c := d",
            If(Name("a"), Name("b"), Assign("c", Name("d"))),
        )

    def test_068(self):
        self.parse(
            "let a = b := c in d end",
            Let("a", Assign("b", Name("c")), Name("d")),
        )

    def test_069(self):
        self.parse(
            "let a = b in c := d end",
            Let("a", Name("b"), Assign("c", Name("d"))),
        )

    def test_070(self):
        self.parse(
            "letfun a(b) = c := d in e end",
            Letfun("a", "b", Assign("c", Name("d")), Name("e")),
        )

    def test_071(self):
        self.parse(
            "letfun a(b) = c in d := e end",
            Letfun("a", "b", Name("c"), Assign("d", Name("e"))),
        )

    def test_072(self):
        self.parse(
            "a(b := c)",
            App(Name("a"), Assign("b", Name("c"))),
        )

    def test_073(self):
        self.parse(
            "(a := b)",
            Assign("a", Name("b")),
        )

    def test_074(self):
        self.parse(
            "show a := b",
            Show(Assign("a", Name("b"))),
        )

    def test_075(self):
        self.parse(
            "show show a",
            Show(Show(Name("a"))),
        )

    def test_076(self):
        self.parse(
            "show if a then b else c",
            Show(If(Name("a"), Name("b"), Name("c"))),
        )

    def test_077(self):
        self.parse(
            "show a || b",
            Show(Or(Name("a"), Name("b"))),
        )

    def test_077_1(self):
        self.parse(
            "(show a) || b",
            Or(Show(Name("a")), Name("b")),
        )

    def test_078(self):
        self.parse(
            "show a && b",
            Show(And(Name("a"), Name("b"))),
        )

    def test_078_1(self):
        self.parse(
            "(show a) && b",
            And(Show(Name("a")), Name("b")),
        )

    def test_079(self):
        self.parse(
            "show ! a",
            Show(Not(Name("a"))),
        )

    def test_080(self):
        self.parse(
            "show a == b",
            Show(Eq(Name("a"), Name("b"))),
        )

    def test_080_1(self):
        self.parse(
            "(show a) == b",
            Eq(Show(Name("a")), Name("b")),
        )

    def test_081(self):
        self.parse(
            "show a < b",
            Show(Lt(Name("a"), Name("b"))),
        )

    def test_81_1(self):
        self.parse(
            "(show a) < b",
            Lt(Show(Name("a")), Name("b")),
        )

    def test_082(self):
        self.parse(
            "show a + b",
            Show(Add(Name("a"), Name("b"))),
        )

    def test_082_1(self):
        self.parse(
            "(show a) + b",
            Add(Show(Name("a")), Name("b")),
        )

    def test_083(self):
        self.parse(
            "show a - b",
            Show(Sub(Name("a"), Name("b"))),
        )

    def test_083_1(self):
        self.parse(
            "(show a) - b",
            Sub(Show(Name("a")), Name("b")),
        )

    def test_084(self):
        self.parse(
            "show a * b",
            Show(Mul(Name("a"), Name("b"))),
        )

    def test_084_1(self):
        self.parse(
            "(show a) * b",
            Mul(Show(Name("a")), Name("b")),
        )

    def test_085(self):
        self.parse(
            "show a / b",
            Show(Div(Name("a"), Name("b"))),
        )

    def test_85_1(self):
        self.parse(
            "(show a) / b",
            Div(Show(Name("a")), Name("b")),
        )

    def test_086(self):
        self.parse(
            "show - a",
            Show(Neg(Name("a"))),
        )

    def test_087(self):
        self.parse(
            "show a",
            Show(Name("a")),
        )

    def test_088(self):
        self.parse(
            "show 0",
            Show(Lit(0)),
        )

    def test_089(self):
        self.parse(
            "show a(b)",
            Show(App(Name("a"), Name("b"))),
        )

    def test_089_1(self):
        self.parse(
            "(show a)(b)",
            App(Show(Name("a")), Name("b")),
        )

    def test_090(self):
        self.parse(
            "show let a = b in c end",
            Show(Let("a", Name("b"), Name("c"))),
        )

    def test_091(self):
        self.parse(
            "show letfun a(b) = c in d end",
            Show(Letfun("a", "b", Name("c"), Name("d"))),
        )

    def test_092(self):
        self.parse(
            "show (a)",
            Show(Name("a")),
        )

    def test_093(self):
        self.parse(
            "if show x then a else b",
            If(Show(Name("x")), Name("a"), Name("b")),
        )

    def test_094(self):
        self.parse(
            "if a then show x else b",
            If(Name("a"), Show(Name("x")), Name("b")),
        )

    def test_095(self):
        self.parse(
            "if a then b else show x",
            If(Name("a"), Name("b"), Show(Name("x"))),
        )

    def test_096(self):
        self.parse(
            "let a = show x in b end",
            Let("a", Show(Name("x")), Name("b")),
        )

    def test_097(self):
        self.parse(
            "let a = b in show x end",
            Let("a", Name("b"), Show(Name("x"))),
        )

    def test_098(self):
        self.parse(
            "letfun a(b) = show x in c end",
            Letfun("a", "b", Show(Name("x")), Name("c")),
        )

    def test_099(self):
        self.parse(
            "letfun a(b) = c in show x end",
            Letfun("a", "b", Name("c"), Show(Name("x"))),
        )

    def test_100(self):
        self.parse(
            "a(show x)",
            App(Name("a"), Show(Name("x"))),
        )

    def test_101(self):
        self.parse(
            "(show x)",
            Show(Name("x"))
        )

    def test_102(self):
        self.parse(
            "read",
            Read(),
        )

    def test_103(self):
        self.parse(
            "read; a",
            Seq(Read(), Name("a")),
        )

    def test_104(self):
        self.parse(
            "a; read",
            Seq(Name("a"), Read()),
        )

    def test_105(self):
        self.parse(
            "if read then b else c",
            If(Read(), Name("b"), Name("c"))
        )

    def test_106(self):
        self.parse(
            "if a then read else c",
            If(Name("a"), Read(), Name("c"))
        )

    def test_107(self):
        self.parse(
            "if a then b else read",
            If(Name("a"), Name("b"), Read())
        )

    def test_108(self):
        self.parse(
            "a := read",
            Assign("a", Read()),
        )

    def test_109(self):
        self.parse(
            "show read",
            Show(Read()),
        )

    def test_110(self):
        self.parse(
            "a || read",
            Or(Name("a"), Read()),
        )

    def test_111(self):
        self.parse(
            "read || b",
            Or(Read(), Name("b")),
        )

    def test_112(self):
        self.parse(
            "a && read",
            And(Name("a"), Read()),
        )

    def test_113(self):
        self.parse(
            "read && b",
            And(Read(), Name("b")),
        )

    def test_114(self):
        self.parse(
            "! read",
            Not(Read()),
        )

    def test_115(self):
        self.parse(
            "a == read",
            Eq(Name("a"), Read()),
        )

    def test_116(self):
        self.parse(
            "read == b",
            Eq(Read(), Name("b")),
        )

    def test_117(self):
        self.parse(
            "a + read",
            Add(Name("a"), Read()),
        )

    def test_118(self):
        self.parse(
            "read + b",
            Add(Read(), Name("b")),
        )

    def test_119(self):
        self.parse(
            "a - read",
            Sub(Name("a"), Read()),
        )

    def test_120(self):
        self.parse(
            "read - b",
            Sub(Read(), Name("b")),
        )

    def test_121(self):
        self.parse(
            "a * read",
            Mul(Name("a"), Read()),
        )

    def test_122(self):
        self.parse(
            "read * b",
            Mul(Read(), Name("b")),
        )

    def test_123(self):
        self.parse(
            "a / read",
            Div(Name("a"), Read()),
        )

    def test_124(self):
        self.parse(
            "read / b",
            Div(Read(), Name("b")),
        )

    def test_125(self):
        self.parse(
            "- read",
            Neg(Read()),
        )

    def test_126(self):
        self.parse(
            "read(b)",
            App(Read(), Name("b")),
        )

    def test_127(self):
        self.parse(
            "a(read)",
            App(Name("a"), Read()),
        )

    def test_128(self):
        self.parse(
            "let a = read in c end",
            Let("a", Read(), Name("c")),
        )

    def test_129(self):
        self.parse(
            "let a = b in read end",
            Let("a", Name("b"), Read()),
        )

    def test_130(self):
        self.parse(
            "letfun a(b) = read in d end",
            Letfun("a", "b", Read(), Name("d")),
        )

    def test_131(self):
        self.parse(
            "letfun a(b) = c in read end",
            Letfun("a", "b", Name("c"), Read()),
        )

    def test_132(self):
        self.parse(
            "(read)",
            Read(),
        )

# NOTE In order to pass the tests, your interpreter should ONLY print to stdout
# when evaluating a Read or Show (i.e., it should never print anything when
# evaluating any other kind of expression).  Show needs to print for obvious
# reasons; Read will probably print a prompt when calling input().
#
# If you want to print debug messages, you can print to stderr instead of
# stdout.  To do this, put the following near the top of your file:
#
# from sys import stderr
#
# Then, when you want to print a debug message:
#
# print("some message", file=stderr)
#
# (Just make sure not to accidentally do this when evaluating Show.)
#
# If you want to make it even easier on yourself, you could do something like
# this:
#
# def debug(*args, **kwargs):
#     print(*args, **kwargs, file=stderr)
#
# and then just call debug() whenever you want to print debug output.


class redirect_stdin(contextlib._RedirectStream):
    # https://stackoverflow.com/questions/5062895/how-to-use-a-string-as-stdin/69228101#69228101
    #
    # Why isn't this in the stdlib?
    _stream = "stdin"


# XXX This is purely to make tests easier to read.
prompt = None


class TestEval(unittest.TestCase):
    def eval_with(self, expr, inputs):
        with redirect_stdin(StringIO("\n".join(inputs) + "\n")):
            return interp.eval(expr)

    def eval_equal(self, expr, expected_result, inputs=[], expected_outputs=None):
        out = StringIO()
        with redirect_stdout(out):
            result = self.eval_with(expr, inputs)
        self.assertIs(type(result), type(expected_result))
        self.assertEqual(result, expected_result)
        self.check_outputs(inputs, expected_outputs, out)

    def eval_except(self, lhs, inputs=[], expected_outputs=None):
        out = StringIO()
        with redirect_stdout(out):
            with self.assertRaises(BaseException):
                self.eval_with(lhs, inputs)
        self.check_outputs(inputs, expected_outputs, out)

    def check_outputs(self, inputs, expected_outputs, out):
        if expected_outputs is None:
            expected_outputs = len(inputs) * [prompt]
        # Checking the output is tricky, because input() prompts also get
        # printed to stdout, and we haven't mandated any particular prompt
        # string.  To get around this, we build a regular expression in
        # which every input prompt is matched by an arbitrary sequence of
        # non-newline characters.  This isn't a 100% solution, but I think
        # it's the best solution that's realistically possible without a
        # mandated prompt string.
        #
        # NOTE If you (yes, YOU, the person running the tests) want to
        # tighten things up, replace [^\n]* below with your input prompt.
        # That should make the tests 100% accurate and precise.
        r = re.compile(
            "^" +
            "".join(
                "[^\n]*" if o is prompt else f"{re.escape(o)}\n"
                for o in expected_outputs
            ) +
            "$"
        )
        out.seek(0)
        self.assertRegex(out.read(), r)

    def test_00(self):
        # !true
        #
        # => false
        self.eval_equal(
            Not(Lit(True)),
            False
        )

    def test_01(self):
        # !false
        #
        # => true
        self.eval_equal(
            Not(Lit(False)),
            True
        )

    def test_02(self):
        # !0
        #
        # => error
        self.eval_except(
            Not(Lit(0)),
        )

    def test_03(self):
        # !1
        #
        # => error
        self.eval_except(
            Not(Lit(1)),
        )

    def test_04(self):
        # !-1
        #
        # => error
        self.eval_except(
            Not(Lit(-1)),
        )

    def test_05(self):
        # !2
        #
        # => error
        self.eval_except(
            Not(Lit(2)),
        )

    def test_06(self):
        # (let x = 0 in letfun f(y) = x in f end end)(2)
        #
        # => 0
        self.eval_equal(
            App(Let("x", Lit(0), Letfun("f", "y", Name("x"), Name("f"))), Lit(2)),
            0,
        )

    def test_07(self):
        # letfun f(x) = x in let x in 0 in f(1) end end
        #
        # => 1
        self.eval_equal(
            Letfun("f", "x", Name("x"),
                   Let("x", Lit(0),
                       App(Name("f"), Lit(1)))),
            1,
        )

    def test_08(self):
        # (let x = 1 in letfun f(y) = x + y in f end end)(let x = 2 in 3 end)
        #
        # => 4
        self.eval_equal(
            App(Let("x", Lit(1),
                    Letfun("f", "y", Add(Name("x"), Name("y")),
                           Name("f"))),
                Let("x", Lit(2),
                    Lit(3))),
            4,
        )

    def test_09(self):
        # letfun f(x) = y in let y = 0 in f(y) end end
        #
        # => error
        self.eval_except(
            Letfun("f", "x", Name("y"),
                   Let("y", Lit(0),
                       App(Name("f"), Name("y")))),
        )

    def test_10(self):
        # letfun fac(x) = if x == 0 then 1 else x * fac(x - 1) in fac(3) end
        #
        # => 6
        self.eval_equal(
            Letfun("fac", "x", If(Eq(Name("x"), Lit(0)),
                                  Lit(1),
                                  Mul(Name("x"), App(Name("fac"), Sub(Name("x"), Lit(1))))),
                   App(Name("fac"), Lit(3))),
            6,
        )

    def test_11(self):
        # letfun y(f) =
        #   letfun g(x) =
        #     letfun h(v) = x(x)(v)
        #     in f(h) end
        #   in g(g) end
        # in letfun fac(r) =
        #      letfun g(x) = if x == 0 then 1 else x * r(x - 1)
        #      in g end
        #    in y(fac)(3) end
        # end
        #
        # => 6
        self.eval_equal(
            Letfun("y", "f",
                   Letfun("g", "x",
                          Letfun("h", "v",
                                 App(App(Name("x"), Name("x")), Name("v")),
                                 App(Name("f"), Name("h"))),
                          App(Name("g"), Name("g"))),
                   Letfun("fac", "r",
                          Letfun("g", "x",
                                 If(Eq(Name("x"), Lit(0)),
                                    Lit(1),
                                    Mul(Name("x"), App(Name("r"), Sub(Name("x"), Lit(1))))),
                                 Name("g")),
                          App(App(Name("y"), Name("fac")), Lit(3)))),
            6,
        )

    def test_12(self):
        # let x = 1 in letfun f(y) = x := y in f(2); x end end
        # => 2
        self.eval_equal(
            Let("x", Lit(1),
                Letfun("f", "y", Assign("x", Name("y")),
                       Seq(App(Name("f"), Lit(2)),
                           Name("x")))),
            2,
        )

    def test_13(self):
        # let x = 0 in letfun f(y) = x := x + y in f(1); f(2); f(3); f(4); x end end
        #
        # => 10
        self.eval_equal(
            Let("x", Lit(0),
                Letfun("f", "y", Assign("x", Add(Name("x"), Name("y"))),
                       Seq(App(Name("f"), Lit(1)),
                           Seq(App(Name("f"), Lit(2)),
                               Seq(App(Name("f"), Lit(3)),
                                   Seq(App(Name("f"), Lit(4)),
                                       Name("x"))))))),
            10,
        )

    def test_14(self):
        # x := 0
        #
        # => error
        self.eval_except(
            Assign("x", Lit(0))
        )

    def test_15(self):
        # letfun f(y) = let x := 0 in x := y end in f(1); x end
        #
        # => error
        self.eval_except(
            Letfun("f", "y",
                   Let("x", Lit(0), Assign("x", Name("y"))),
                   Seq(App(Name("f"), Lit(1)),
                       Name("x")))
        )

    def test_16(self):
        # let x = 0 in let y = x := 1 in y end end
        #
        # => 1
        self.eval_equal(
            Let("x", Lit(0),
                Let("y", Assign("x", Lit(1)),
                    Name("y"))),
            1
        )

    def test_17(self):
        # letfun f(x) = let y = 0 in x end
        # in f(1); y end
        #
        # => error
        self.eval_except(
            Letfun("f", "x",
                   Let("y", Lit(0), Name("x")),
                   Seq(App(Name("f"), Lit(1)),
                       Name("y")))
        )

    def test_18(self):
        # let x = 0 in x := 1 end
        #
        # => 1
        self.eval_equal(
            Let("x", Lit(0),
                Assign("x", Lit(1))),
            1
        )

    def test_19(self):
        # let x = 0 in x := true end
        #
        # => true
        self.eval_equal(
            Let("x", Lit(0),
                Assign("x", Lit(True))),
            True
        )

    def test_20(self):
        # let x = 2 in (x := if x == 2 then 3 else 4) + (x := 10) end
        #
        # => 13
        self.eval_equal(
            Let('x', Lit(2),
                Add(Assign('x', If(Eq(Name('x'), Lit(2)), Lit(3), Lit(4))),
                    Assign('x', Lit(10)))),
            13
        )

    def test_21(self):
        # read
        #
        # => 39
        #
        # inputs: 39
        self.eval_equal(Read(), 39, inputs=["39"])

    def test_22(self):
        # read
        #
        # => -67
        #
        # inputs: -67
        self.eval_equal(Read(), -67, inputs=["-67"])

    def test_23(self):
        # show -58
        #
        # => -58
        #
        # outputs: -58
        self.eval_equal(
            Show(Lit(-58)),
            -58,
            expected_outputs=["-58"],
        )

    def test_24(self):
        # show 86
        #
        # => 86
        #
        # inputs: 86
        #
        # outputs: 86
        self.eval_equal(
            Show(Lit(86)),
            86,
            expected_outputs=["86"],
        )

    def test_25(self):
        # show read
        #
        # => -22
        #
        # inputs: -22
        #
        # outputs: -22
        self.eval_equal(
            Show(Read()),
            -22,
            inputs=["-22"],
            expected_outputs=[prompt, "-22"],
        )

    def test_26(self):
        # show read
        #
        # => 14
        #
        # inputs: 14
        #
        # outputs: 14
        self.eval_equal(
            Show(Read()),
            14,
            inputs=["14"],
            expected_outputs=[prompt, "14"],
        )

    def test_27(self):
        # show true
        #
        # => true
        #
        # outputs: True
        self.eval_equal(
            Show(Lit(True)),
            True,
            expected_outputs=["True"],
        )

    def test_28(self):
        # show false
        #
        # => false
        #
        # outputs: False
        self.eval_equal(
            Show(Lit(False)),
            False,
            expected_outputs=["False"],
        )

    def test_29(self):
        # let x = 0 in (x := read; show x) + (x := read; show x) end
        #
        # => 3
        #
        # inputs: 1, 2
        #
        # outputs: 1, 2
        self.eval_equal(
            Let("x", Lit(0),
                Add(Seq(Assign("x", Read()), Show(Name("x"))),
                    Seq(Assign("x", Read()), Show(Name("x"))))),
            3,
            inputs=["1", "2"],
            expected_outputs=[prompt, "1", prompt, "2"],
        )

    def test_30(self):
        # letfun f(x) = x := x + x; show x in let x = 1 in f(x); x end end
        #
        # => 1
        #
        # outputs: 2
        self.eval_equal(
            Letfun("f", "x",
                   Seq(Assign("x", Add(Name("x"), Name("x"))),
                       Show(Name("x"))),
                   Let("x", Lit(1),
                       Seq(App(Name("f"), Name("x")), Name("x")))),
            1,
            expected_outputs=["2"],
        )

    def test_31(self):
        # let f = let x = 2 in letfun f(y) = x := x * y in f end end
        # in let x = 3 in show(f(4)); x end end
        #
        # => 3
        #
        # outputs: 8
        self.eval_equal(
            Let("f", Let("x", Lit(2),
                         Letfun("f", "y",
                                Assign("x", Mul(Name("x"), Name("y"))),
                                Name("f"))),
                Let("x", Lit(3),
                    Seq(Show(App(Name("f"), Lit(4))), Name("x")))),
            3,
            expected_outputs=["8"],
        )

    def test_32(self):
        # let fac =
        #   let acc = 1
        #   in letfun go(x) = if x == 0 then acc else (acc := acc * x; go(x - 1))
        #      in letfun fac(x) =
        #        let r = go(x) in acc := 1; r end
        #        in fac
        #        end
        #      end
        #   end
        # in show(fac(3)); show(fac(4))
        # end
        #
        # => 24
        #
        # outputs: 6, 24
        self.eval_equal(
            Let("fac", Let("acc", Lit(1),
                           Letfun("go", "x",
                                  If(Eq(Name("x"), Lit(0)),
                                     Name("acc"),
                                     Seq(Assign("acc", Mul(Name("acc"), Name("x"))),
                                         App(Name("go"), Sub(Name("x"), Lit(1))))),
                                  Letfun("fac", "x",
                                         Let("r", App(Name("go"), Name("x")),
                                             Seq(Assign("acc", Lit(1)), Name("r"))),
                                         Name("fac")))),
                Seq(Show(App(Name("fac"), Lit(3))),
                    Show(App(Name("fac"), Lit(4))))),
            24,
            expected_outputs=["6", "24"],
        )
        
    def test_33(self):
        # letfun fac(n) =
        #   let acc = 1 in
        #     letfun loop(n) =
        #       if n == 0 then acc else (
        #         acc := acc * n;
        #         loop(n - 1)
        #       )
        #     in
        #       loop(n)
        #     end
        #   end
        # in
        #   fac(3)
        # end
        #
        # => 120
        self.eval_equal(
            Letfun("fac", "n",
                   Let("acc", Lit(1),
                       Letfun("loop", "n",
                              If(Eq(Name("n"), Lit(0)),
                                 Name("acc"),
                                 Seq(Assign("acc", Mul(Name("acc"), Name("n"))),
                                     App(Name("loop"), Sub(Name("n"), Lit(1))))),
                              App(Name("loop"), Name("n")))),
                   App(Name("fac"), Lit(5))),
            120,
        )

    def test_34(self):
        # letfun b(n) =
        #   if n < 2 then
        #     show n
        #   else (
        #     b(n / 2);
        #     show (n - (n / 2) * 2)
        #   )
        # in
        #   b(42)
        # end
        #
        # => 0
        #
        # outputs: 1, 0, 1, 0, 1, 0
        self.eval_equal(
            Letfun("b", "n",
                   If(Lt(Name("n"), Lit(2)),
                      Show(Name("n")),
                      Seq(App(Name("b"), Div(Name("n"), Lit(2))),
                          Show(Sub(Name("n"), Mul(Div(Name("n"), Lit(2)), Lit(2)))))),
                   App(Name("b"), Lit(42))),
            0,
            expected_outputs=["1", "0", "1", "0", "1", "0"],
        )

    def test_35(self):
        # letfun f(x) = x in f := 1 end
        #
        # => error
        self.eval_except(
            Letfun("f", "x", Name("x"),
                   Assign("f", Lit(1)))
        )

    def test_36(self):
        # letfun f(x) = x / 0 in 10 end
        #
        # => 10
        self.eval_equal(
            Letfun("f", "x", Div(Name("x"), Lit(0)),
                   Lit(10)),
            10,
        )

    def test_37(self):
        # let f = letfun f(x) = x in f end
        # in f := 1
        # end
        #
        # => error
        self.eval_except(
            Let("f", Letfun("f", "x", Name("x"), Name("f")),
                Assign("f", Lit(1))),
        )

    def test_38(self):
        # let u = 1 in
        #   u := letfun f(x) = x in f end;
        #   u(3)
        # end
        #
        # => 3
        self.eval_equal(
            Let("u", Lit(1),
                Seq(Assign("u", Letfun("f", "x", Name("x"), Name("f"))),
                    App(Name("u"), Lit(3)))),
            3,
        )

    def test_39(self):
        # letfun nil(_) = 0 / 0 in
        # letfun pair(a) =
        #   letfun inner(b) =
        #     letfun dispatch(flag) = if flag then a else b
        #     in dispatch
        #   end
        #   in inner
        # end in
        # letfun head(xs) = xs(true) in
        # letfun tail(xs) = xs(false) in
        # letfun nth(n) =
        #   letfun inner(xs) =
        #     if n == 0 then
        #       head(xs)
        #     else (
        #       n := n - 1;
        #       inner(tail(xs))
        #     )
        #   in inner
        # end in
        # let xs = pair(5)(pair(4)(pair(3)(pair(2)(pair(1)(pair(0)(nil)))))) in
        # (show(nth(0)(xs));
        #  show(nth(1)(xs));
        #  show(nth(2)(xs)));
        # (show(nth(3)(xs));
        #  show(nth(4)(xs));
        #  show(nth(5)(xs)))
        # end end end end end end
        #
        # => 0
        #
        # ouputs: 5, 4, 3, 2, 1, 0
        self.eval_equal(
            Letfun("nil", "_", Div(Lit(0), Lit(0)),
                   Letfun("pair", "a",
                          Letfun("inner", "b",
                                 Letfun("dispatch", "flag",
                                        If(Name("flag"), Name("a"), Name("b")),
                                        Name("dispatch")),
                                 Name("inner")),
                          Letfun("head", "xs",
                                 App(Name("xs"), Lit(True)),
                                 Letfun("tail", "xs",
                                        App(Name("xs"), Lit(False)),
                                        Letfun("nth", "n",
                                               Letfun("inner", "xs",
                                                      If(Eq(Name("n"), Lit(0)),
                                                         App(Name("head"),
                                                             Name("xs")),
                                                         Seq(Assign("n", Sub(Name("n"), Lit(1))),
                                                             App(Name("inner"),
                                                                 App(Name("tail"),
                                                                     Name("xs"))))),
                                                      Name("inner")),
                                               Let("xs", App(App(Name("pair"), Lit(5)),
                                                             App(App(Name("pair"), Lit(4)),
                                                                 App(App(Name("pair"), Lit(3)),
                                                                     App(App(Name("pair"), Lit(2)),
                                                                         App(App(Name("pair"), Lit(1)),
                                                                             App(App(Name("pair"), Lit(0)),
                                                                                 Name("nil"))))))),
                                                   Seq(Seq(Show(App(App(Name("nth"), Lit(0)), Name("xs"))),
                                                           Seq(Show(App(App(Name("nth"), Lit(1)), Name("xs"))),
                                                               Show(App(App(Name("nth"), Lit(2)), Name("xs"))))),
                                                       Seq(Show(App(App(Name("nth"), Lit(3)), Name("xs"))),
                                                           Seq(Show(App(App(Name("nth"), Lit(4)), Name("xs"))),
                                                               Show(App(App(Name("nth"), Lit(5)), Name("xs")))))))))))),
            0,
            expected_outputs=["5", "4", "3", "2", "1", "0"],
        )

    def test_40(self):
        # show (show 0) + 1
        self.eval_equal(
            Show(Add(Show(Lit(0)), Lit(1))),
            1,
            expected_outputs=["0", "1"],
        )

    def test_41(self):
        # (read == 0) || (0 / 0)
        #
        # => true
        #
        # inputs: 0
        self.eval_equal(
            Or(Eq(Read(), Lit(0)),
               Div(Lit(0), Lit(0))),
            True,
            inputs=["0"],
        )

    def test_42(self):
        # true || read
        #
        # => true
        self.eval_equal(
            Or(Lit(True), Read()),
            True,
        )

    def test_43(self):
        # show false || (0 / 0)
        #
        # => error
        #
        # outputs: False
        self.eval_except(
            Or(Show(Lit(False)), Div(Lit(0), Lit(0))),
            expected_outputs=["False"],
        )

    def test_44(self):
        # read / show 0
        #
        # => error
        #
        # inputs: 1
        self.eval_except(
            Div(Read(), Show(Lit(0))),
            inputs=["1"],
        )

    def test_45(self):
        # read || read
        #
        # => error
        #
        # inputs: 1
        self.eval_except(
            Or(Read(), Read()),
            inputs=["1"],
        )

    # If this test fails, you may have implemented multi-argument functions.
    # These tests expect single-argument functions.  You can fix this by
    # converting parameters/arguments to lists as necessary when evaluating
    # `Letfun` and `App`.
    def test_46(self):
        # letfun func(arg) = arg in func(0) end
        #
        # => 0
        self.eval_equal(
            Letfun("func", "arg", Name("arg"), App(Name("func"), Lit(0))),
            0,
        )

    def test_47(self):
        # let x = 1 in x + x end
        #
        # => 2
        self.eval_equal(
            Let("x", Lit(1), Add(Name("x"), Name("x"))),
            2,
        )

    def test_48(self):
        # 1 || false
        #
        # => error
        self.eval_except(
            Or(Lit(1), Lit(False)),
        )

    def test_49(self):
        # read
        #
        # => error
        #
        # inputs: x
        self.eval_except(
            Read(),
            inputs=["x"],
        )

    def test_50(self):
        # let counter =
        #   let x = 0 in
        #     letfun counter(y) = x := x + y in counter end
        #   end
        # in counter(1); counter(1); counter(1) end
        #
        # => 3
        self.eval_equal(
            Let("counter",
                Let("x", Lit(0),
                    Letfun("counter", "y",
                           Assign("x", Add(Name("x"), Name("y"))),
                           Name("counter"))),
                Seq(App(Name("counter"), Lit(1)),
                    Seq(App(Name("counter"), Lit(1)),
                        App(Name("counter"), Lit(1))))),
            3
        )

if __name__ == "__main__":
    unittest.main()
