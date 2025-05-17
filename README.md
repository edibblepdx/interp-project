# interp-project

# Changes to Milestone 1

- `Tune` is no longer a literal type; it is now a value type. `Note` now exists
  as the literal type.

- There is a new slice operator which can be used as `Tune[begin:end]`

# Requirements

```
Package     Version
----------- -------
interegular 0.3.3
lark        1.2.2
MIDIUtil    1.2.1
```

# What are Notes and Tunes?

A <em>Literal</em> `Note` is a tuple of `(pitch, duration)`.

A <em>Value</em> `Tune` is a list of `Notes`.

Evaluating a `Note` returns a `Tune` that contains a single note. Multiple `Tunes`
and `Notes` can be joined using `|` to create longer `Tunes`. A `Tune` can be
sliced using `[start:end]` to get a subsequence of the `Tune`.

```python
myTune = (A, 1) | (B, 2) | (C, 3)
myTune[1:2] -> [(B, 2)]
```

Tunes can be written to midi format by setting `writeMidi=True` in a call to `run`.

```python
run(expr, writeMidi=True)
```

`Tune` exists only as a value type. Only a `Note` exists as a literal. But
evaluating a `Note` returns a `Tune`.

# How to use Notes and Tunes

A `Note` literal has the form `(pitch, duration)`, where pitch is a note on the
chromatic scale or a rest at middle C. Transposing a pitch will wrap.

> CHROMATIC = (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
> REST = R

Creating a `Note` will evaluate to a `Tune` which has the form `[Note, ...]`.
Multiple notes or tunes can be concatenated with `|`, compared for equality
with `==` or `!=`, pitch shifted with `+` or `-` on the right, and sped up or
slowed down with `*` on the right. Positive integers will speed up the tune and
negative integers will slow down the tune. Tunes and Notes can be sliced with
`[start:end]` to get smaller tunes.

# Operator Summary

- Tunes can be multiplied on the right by an integer to speed up or slow down the
  Tune. Positive integers will speed up the Tune and negative integers will slow
  down the Tune.

- Tunes can be added to on the right by an integer to transpose their pitch
  by an integer number of half-steps.

- Tunes can be compared for strict equality.

- Tunes and Notes can be joined to create longer Tunes.

- Tunes and Notes (since Notes evaluate to Tunes) can be sliced to get a subset
  of a Tune.

# Operator Precedence

> In order of Highest to Lowest

```
literals name parenthesized-expr func-application let-in-end letfun-in-end
[:] (slice)
- (unary)
* /
+ -
| (join)
== < > <= >=
!
&&
||
if-then-else
```

`|` is right-associative. `==`, `<`, `>`, `<=`, `>=` are non-associative.
And all remaining binary operators are left-associative

# Test File

- `interp.py` and `parse_run.py` each import and run their respective TestCase
  from `test_domain.py`.
