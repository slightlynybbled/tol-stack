import pytest

import tol_stack


def test_creation():
    part = tol_stack.Part(
        name='part',
        nominal_length=0.0,
        tolerance=0.05
    )
    assert part


def test_invalid_distribution():
    with pytest.raises(ValueError):
        tol_stack.Part(
            name='part', nominal_length=0.0, tolerance=0.05, distribution='invalid dist'
        )
