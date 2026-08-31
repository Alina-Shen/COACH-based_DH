#!/usr/bin/env python3
"""Resolve frozen Q-Chem basis metadata into runnable PySCF definitions.

This module translates basis *metadata and text*, never orbitals.  It is kept
separate from the immutable Step-5 molecular-input snapshot so that the source
evidence remains byte-for-byte unchanged.
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from pyscf import df, gto
from pyscf.gto.basis import parse_gaussian


ORBITAL_ALIASES = {
    "AUG-CC-PCV5Z": "aug-cc-pcv5z",
    "AUG-CC-PV5Z": "aug-cc-pv5z",
    "AUG-CC-PVQZ": "aug-cc-pvqz",
    "AUG-CC-PWCVQZ": "aug-cc-pwcvqz",
    "AUG-PC-3": "aug-pc-3",
    "AUG-PC-4": "aug-pc-4",
    "DEF2-QZVPP": "def2-qzvpp",
    "DEF2-QZVPPD": "def2-qzvppd",
    "DEF2-TZVP": "def2-tzvp",
    "DEF2-TZVPD": "def2-tzvpd",
    "DEF2-TZVPPD": "def2-tzvppd",
}

AUXILIARY_ALIASES = {
    "RIMP2-DEF2-QZVPP": "rimp2-def2-QZVPP",
    "RIMP2-DEF2-QZVPPD": "rimp2-def2-QZVPPD",
}

# Explicit policy for sources that provide no RI basis.  These are not
# runtime guesses: Step 6 freezes one mapping for each observed source scope.
MISSING_AUXILIARY_BY_SCOPE = {
    "BigNC_external": "rimp2-def2-TZVPPD",
    "GDB9_W1_F12_external": "rimp2-def2-TZVP",
    "OPT_external": "rimp2-def2-QZVPPD",
}

QCHEM_AUXILIARY_ROOT = Path("/global/home/groups-sw/mhg/qcaux_public/qcaux_6p00/basis")
QCHEM_AUXILIARY_FILES = {
    name: QCHEM_AUXILIARY_ROOT / f"{name}.bas"
    for name in {
        "rimp2-def2-QZVPP",
        "rimp2-def2-QZVPPD",
        "rimp2-def2-TZVP",
        "rimp2-def2-TZVPPD",
    }
}

ORBITAL_ELEMENT_OVERRIDES = {
    ("AUG-CC-PCV5Z", "H"): "aug-cc-pv5z",
    ("AUG-CC-PCV5Z", "He"): "aug-cc-pv5z",
}

ANGULAR_LABELS = {"s": 0, "p": 1, "d": 2, "f": 3, "g": 4, "h": 5, "i": 6}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(payload.encode())


def normalized_label(label: str) -> str:
    return label.strip().upper()


def _meaningful_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith(("!", "#"))
    ]


def split_qchem_generated_sections(block: str) -> dict[str, list[str]]:
    """Split a Q-Chem $basis/$aux_basis/$ecp payload by ``****``."""
    sections: dict[str, list[str]] = {}
    for raw_section in block.split("****"):
        lines = _meaningful_lines(raw_section)
        if not lines:
            continue
        header = lines[0].split()
        if not re.fullmatch(r"[A-Za-z]{1,3}", header[0]):
            raise ValueError(f"invalid generated-section element header: {lines[0]}")
        element = header[0].capitalize()
        if element in sections:
            raise ValueError(f"duplicate generated section for {element}")
        sections[element] = lines[1:]
    if not sections:
        raise ValueError("generated block contains no element sections")
    return sections


@lru_cache(maxsize=None)
def parse_qchem_basis_block(block: str) -> dict[str, list[Any]]:
    """Translate Q-Chem/Gaussian generated basis text to PySCF objects."""
    parsed: dict[str, list[Any]] = {}
    for element, body in split_qchem_generated_sections(block).items():
        if not body:
            raise ValueError(f"empty generated basis section for {element}")
        if len(body) == 1 and re.fullmatch(r"[A-Za-z0-9+*()_.,-]+", body[0]):
            parsed[element] = gto.basis.load(body[0], element)
        else:
            parsed[element] = parse_gaussian.parse("\n".join(body))
    return parsed


@lru_cache(maxsize=None)
def parse_qchem_ecp_block(block: str) -> dict[str, list[Any]]:
    """Translate Q-Chem Gaussian ECP sections to PySCF ECP objects."""
    parsed: dict[str, list[Any]] = {}
    for element, body in split_qchem_generated_sections(block).items():
        if not body:
            raise ValueError(f"empty generated ECP section for {element}")
        header = body[0].split()
        if len(header) < 3 or not header[0].upper().endswith("-ECP"):
            raise ValueError(f"invalid ECP header for {element}: {body[0]}")
        nelec = int(header[-1])
        nwchem = [f"{element} nelec {nelec}"]
        index = 1
        channel_count = 0
        while index < len(body):
            potential = body[index].lower().split()
            if len(potential) != 2 or potential[1] != "potential":
                raise ValueError(f"invalid ECP channel for {element}: {body[index]}")
            channel_name = potential[0]
            channel = "ul" if "-" not in channel_name else channel_name.split("-", 1)[0]
            if channel != "ul" and channel not in ANGULAR_LABELS:
                raise ValueError(f"unsupported ECP channel for {element}: {channel_name}")
            index += 1
            term_count = int(body[index])
            index += 1
            nwchem.append(f"{element} {channel}")
            nwchem.extend(line.replace("D", "E").replace("d", "e") for line in body[index:index + term_count])
            index += term_count
            channel_count += 1
        # Q-Chem's header counts nonlocal projectors.  The file additionally
        # contains one local (``g potential``/``ul``) channel.
        if channel_count != int(header[-2]) + 1:
            raise ValueError(
                f"ECP channel-count mismatch for {element}: {channel_count} != {header[-2]}"
            )
        parsed[element] = gto.basis.parse_ecp("\n".join(nwchem), element)
    return parsed


def _select_elements(definitions: dict[str, Any], elements: list[str], kind: str) -> dict[str, Any]:
    selected = {element: definitions[element] for element in elements if element in definitions}
    missing = sorted(set(elements) - set(selected))
    if missing and kind != "ecp":
        raise ValueError(f"{kind} lacks elements: {', '.join(missing)}")
    return selected


@lru_cache(maxsize=None)
def load_qchem_auxiliary_library(name: str) -> dict[str, list[Any]]:
    if name not in QCHEM_AUXILIARY_FILES:
        raise ValueError(f"unknown Q-Chem auxiliary library: {name}")
    return parse_qchem_basis_block(QCHEM_AUXILIARY_FILES[name].read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _resolve_named_orbital_basis(label: str, elements: tuple[str, ...]) -> dict[str, list[Any]]:
    normalized = normalized_label(label)
    if normalized not in ORBITAL_ALIASES:
        raise ValueError(f"unmapped orbital-basis label: {label}")
    default = ORBITAL_ALIASES[normalized]
    return {
        element: gto.basis.load(ORBITAL_ELEMENT_OVERRIDES.get((normalized, element), default), element)
        for element in elements
    }


def resolve_named_orbital_basis(label: str, elements: list[str]) -> dict[str, list[Any]]:
    return _resolve_named_orbital_basis(label, tuple(elements))


def resolve_record(record: dict[str, Any]) -> dict[str, Any]:
    """Resolve one immutable Step-5 record to PySCF basis/ECP definitions."""
    elements = record["pyscf_molecule"]["elements"]
    orbital = record["orbital_basis"]
    auxiliary = record["auxiliary_basis"]
    ecp_record = record["ecp"]

    if orbital["embedded_block"]["present"]:
        orbital_basis = _select_elements(
            parse_qchem_basis_block(orbital["embedded_block"]["qchem_block"]),
            elements,
            "orbital basis",
        )
        orbital_resolution = "embedded_qchem_block"
        orbital_name = ""
    else:
        label = normalized_label(orbital["qchem_rem_label"])
        orbital_basis = resolve_named_orbital_basis(orbital["qchem_rem_label"], elements)
        orbital_name = ORBITAL_ALIASES[label]
        orbital_resolution = "named_alias"

    if auxiliary["embedded_block"]["present"]:
        auxiliary_basis = _select_elements(
            parse_qchem_basis_block(auxiliary["embedded_block"]["qchem_block"]),
            elements,
            "auxiliary basis",
        )
        auxiliary_resolution = "embedded_qchem_block"
        auxiliary_name = ""
    elif auxiliary["qchem_rem_label"]:
        label = normalized_label(auxiliary["qchem_rem_label"])
        if label not in AUXILIARY_ALIASES:
            raise ValueError(f"unmapped auxiliary-basis label: {auxiliary['qchem_rem_label']}")
        auxiliary_name = AUXILIARY_ALIASES[label]
        auxiliary_basis = _select_elements(
            load_qchem_auxiliary_library(auxiliary_name), elements, "auxiliary basis"
        )
        auxiliary_resolution = "hash_pinned_qchem_named_library"
    else:
        scope = record["identity"]["scope"]
        if scope not in MISSING_AUXILIARY_BY_SCOPE:
            raise ValueError(f"no explicit missing-auxiliary policy for scope: {scope}")
        auxiliary_name = MISSING_AUXILIARY_BY_SCOPE[scope]
        auxiliary_basis = _select_elements(
            load_qchem_auxiliary_library(auxiliary_name), elements, "auxiliary basis"
        )
        auxiliary_resolution = "explicit_scope_policy"

    if ecp_record["embedded_block"]["present"]:
        ecp = _select_elements(
            parse_qchem_ecp_block(ecp_record["embedded_block"]["qchem_block"]),
            elements,
            "ecp",
        )
        ecp_resolution = "embedded_qchem_block"
    elif ecp_record["qchem_rem_label"]:
        raise ValueError(f"unmapped named ECP label: {ecp_record['qchem_rem_label']}")
    else:
        # Q-Chem automatically pairs named def2 orbital bases with their
        # standard def2 ECPs.  PySCF requires the ECP to be assigned
        # explicitly, so reproduce that implicit Q-Chem behavior here.
        ecp = {}
        if orbital_name.startswith("def2-"):
            for element in elements:
                element_ecp = gto.basis.load_ecp(orbital_name, element)
                if element_ecp:
                    ecp[element] = element_ecp
        ecp_resolution = "implicit_named_def2_ecp" if ecp else "not_applicable"

    return {
        "orbital_basis": orbital_basis,
        "orbital_name": orbital_name,
        "orbital_resolution": orbital_resolution,
        "auxiliary_basis": auxiliary_basis,
        "auxiliary_name": auxiliary_name,
        "auxiliary_resolution": auxiliary_resolution,
        "ecp": ecp,
        "ecp_resolution": ecp_resolution,
    }


def build_molecules(record: dict[str, Any]) -> tuple[gto.Mole, gto.Mole, dict[str, Any]]:
    """Construct orbital and auxiliary PySCF molecules without any SCF work."""
    resolved = resolve_record(record)
    molecule = record["pyscf_molecule"]
    mol = gto.M(
        atom=molecule["atom"],
        unit=molecule["unit"],
        charge=molecule["charge"],
        spin=molecule["spin"],
        basis=resolved["orbital_basis"],
        ecp=resolved["ecp"],
        cart=False,
        verbose=0,
    )
    auxmol = df.addons.make_auxmol(mol, resolved["auxiliary_basis"])
    return mol, auxmol, resolved
