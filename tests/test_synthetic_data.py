from __future__ import annotations

import pytest

from scripts.generate_synthetic_data import generate_synthetic_dataset


def test_generator_is_reproducible_and_has_both_classes():
    first = generate_synthetic_dataset(rows=120, seed=7)
    second = generate_synthetic_dataset(rows=120, seed=7)
    assert first.equals(second)
    assert len(first) == 120
    assert set(first["Attrition"]) == {"Yes", "No"}
    assert first["Attrition"].value_counts().min() >= 7


def test_generator_rejects_small_samples():
    with pytest.raises(ValueError, match="at least 50"):
        generate_synthetic_dataset(rows=20)
