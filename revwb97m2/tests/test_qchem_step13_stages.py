from __future__ import annotations

import numpy as np

from revwb97m2.qchem_step13_stages import authority_fingerprint, canonical_sha256


def test_qchem_step13_identity_fingerprint_is_order_independent() -> None:
    identity = {"scope": "gscdb137", "species": "x", "source_record_sha256": "a" * 64}
    first = authority_fingerprint(identity, {"b": "2", "a": "1"})
    second = authority_fingerprint(dict(reversed(list(identity.items()))), {"a": "1", "b": "2"})
    assert first == second
    assert first == canonical_sha256({"identity": identity, "authorities": {"a": "1", "b": "2"}})


def test_r2_layout_is_exact_288_plus_four() -> None:
    semilocal = np.arange(288, dtype=np.float64)
    tail = np.asarray([-1.0, -2.0, -3.0, -4.0])
    vector = np.concatenate((semilocal, tail))
    assert vector.shape == (292,)
    assert np.array_equal(vector[:288], semilocal)
    assert np.array_equal(vector[288:], tail)
