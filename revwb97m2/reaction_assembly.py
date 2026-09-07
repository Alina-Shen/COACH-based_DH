"""Strict species-to-reaction assembly for COACH fitting artifacts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


FEATURE_COUNT = 292


def assemble_reaction_arrays(
    reactions: Sequence[Mapping[str, Any]],
    species_vectors: Mapping[str, np.ndarray],
    species_fixed_energies: Mapping[str, float],
    species_grid_differences: Mapping[str, Mapping[str, np.ndarray]],
    grid_ids: Sequence[str],
) -> dict[str, Any]:
    """Apply frozen benchmark stoichiometry to validated species artifacts."""

    names: list[str] = []
    feature_rows: list[np.ndarray] = []
    fixed_rows: list[float] = []
    references: list[float] = []
    weights: list[float] = []
    grid_rows: dict[str, list[np.ndarray]] = {grid: [] for grid in grid_ids}
    seen: set[str] = set()
    for reaction in reactions:
        name = str(reaction["reaction"])
        if name in seen:
            raise ValueError(f"duplicate reaction: {name}")
        seen.add(name)
        stoichiometry = reaction["stoichiometry"]
        if not stoichiometry:
            raise ValueError(f"empty stoichiometry: {name}")
        feature = np.zeros(FEATURE_COUNT, dtype=np.float64)
        fixed = 0.0
        differences = {grid: np.zeros(FEATURE_COUNT, dtype=np.float64) for grid in grid_ids}
        for term in stoichiometry:
            coefficient = float(term["coefficient"])
            species = str(term["species"])
            if not np.isfinite(coefficient):
                raise FloatingPointError(f"non-finite coefficient in {name}")
            try:
                vector = np.asarray(species_vectors[species], dtype=np.float64)
                fixed_energy = float(species_fixed_energies[species])
                species_differences = species_grid_differences[species]
            except KeyError as exc:
                raise KeyError(f"missing species artifact for {species} in {name}") from exc
            if vector.shape != (FEATURE_COUNT,) or not np.isfinite(vector).all():
                raise ValueError(f"invalid 292-feature vector for {species}")
            if not np.isfinite(fixed_energy):
                raise FloatingPointError(f"non-finite fixed energy for {species}")
            feature += coefficient * vector
            fixed += coefficient * fixed_energy
            for grid in grid_ids:
                difference = np.asarray(species_differences[grid], dtype=np.float64)
                if difference.shape != (FEATURE_COUNT,) or not np.isfinite(difference).all():
                    raise ValueError(f"invalid {grid} grid difference for {species}")
                differences[grid] += coefficient * difference
        reference = float(reaction["reference_hartree"])
        weight = float(reaction["objective_weight"])
        if not np.isfinite(reference) or not np.isfinite(weight) or weight <= 0.0:
            raise ValueError(f"invalid reference or objective weight for {name}")
        names.append(name)
        feature_rows.append(feature)
        fixed_rows.append(fixed)
        references.append(reference)
        weights.append(weight)
        for grid in grid_ids:
            grid_rows[grid].append(differences[grid])
    if not names:
        raise ValueError("no reactions to assemble")
    fixed_array = np.asarray(fixed_rows, dtype=np.float64)
    reference_array = np.asarray(references, dtype=np.float64)
    return {
        "reaction_names": names,
        "feature_matrix": np.stack(feature_rows),
        "fixed_energy": fixed_array,
        "reference_energy": reference_array,
        "target": reference_array - fixed_array,
        "objective_weight": np.asarray(weights, dtype=np.float64),
        "grid_differences": {grid: np.stack(rows) for grid, rows in grid_rows.items()},
    }
