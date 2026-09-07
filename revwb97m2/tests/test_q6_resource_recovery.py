from pathlib import Path

import pytest

from revwb97m2.scripts.recover_q6_resource_pilot import qchem_reported_wall_seconds
from revwb97m2.scripts.prepare_q3_qchem_gateway import derive_input


def test_qchem_reported_wall_seconds_requires_one_positive_record(tmp_path: Path):
    output = tmp_path / "qchem.out"
    output.write_text("Total job time:  1140.81s(wall), 8761.73s(cpu)\n", encoding="utf-8")
    assert qchem_reported_wall_seconds(output) == pytest.approx(1140.81)

    output.write_text("no terminal timing\n", encoding="utf-8")
    with pytest.raises(ValueError, match="expected one"):
        qchem_reported_wall_seconds(output)

    output.write_text(
        "Total job time:  1.0s(wall), 1.0s(cpu)\n"
        "Total job time:  2.0s(wall), 2.0s(cpu)\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="got 2"):
        qchem_reported_wall_seconds(output)


def test_fixed_orbital_retry_skips_post_fock_diagonalization():
    source = (
        "$molecule\n0 1\nH 0 0 0\n$end\n\n"
        "$rem\nSCF_GUESS READ\nUNRESTRICTED TRUE\nMETHOD wB97M-V\n$end\n"
    )
    historical = derive_input(source, "000075000302")
    retry = derive_input(
        source, "000075000302", skip_post_fock_diagonalization=True
    )
    assert "MP2_RESTART_NO_SCF" not in historical
    assert retry.count("MP2_RESTART_NO_SCF TRUE") == 1
