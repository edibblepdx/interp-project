# interp-project

# What are Notes and Tunes?

A <em>Literal</em> `Note` is a tuple of `(pitch, duration)`.

A <em>Value</em> `Tune` is a list of `Notes`.

Evaluating a `Note` returns a `Tune` that contains a single note. Multiple `Tunes`
and `Notes` can be joined using `|` to create longer `Tunes`. A `Tune` can be
sliced using `[start:end]` to get a subsequence of the `Tune`.

```
myTune = (A, 1) | (B, 2) | (C, 3)
myTune[1:2] -> [(B, 2)]
```

`Tune` exists only as a value type. Only a `Note` exists as a literal. But
evaluating a `Note` returns a `Tune`.

# Changes to Milestone 1

- `Tune` is no longer a literal type; it is now a value type. `Note` now exists
  as the literal type.

- There is a new slice operator which can be used as `Tune[begin:end]`

# Test File

- `interp.py` and `parse_run.py` each import and run their respective TestCase
  from `test_domain.py`.
