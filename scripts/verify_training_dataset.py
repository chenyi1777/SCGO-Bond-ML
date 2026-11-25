"""Verify the published 88-configuration training dataset and recompute MOM51."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from scgo_one_case import (
    classify_bonds,
    enumerate_paths,
    read_poscar,
    shortest_pair_vectors,
    split_repeated_length_types,
    suggest_cutoff,
)


DATA = Path(__file__).resolve().parents[1] / "appendices" / "appendix-f"
EXPECTED_COUNTS = {2: 15, 4: 18, 6: 18, 8: 21, 10: 16}
EXPECTED_SOURCES = {"earlier_base": 54, "earlier_rebuilt": 28, "additional": 6}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def parent_bonds(path):
    _, lattice, atoms = read_poscar(path)
    assert {element: len(indices) for element, indices in atoms.items()} == {
        "Sr": 2, "Ga": 24, "O": 38,
    }
    bonds = []
    for element, search_limit in (("Sr", 5.0), ("Ga", 4.0)):
        pairs = shortest_pair_vectors(atoms, lattice, element)
        cutoff, _, _ = suggest_cutoff(pairs, search_limit)
        selected, _ = classify_bonds(pairs, element, cutoff, tolerance=1e-5)
        bonds.extend(selected)
    return bonds


def recompute_mom51(bonds, occupied_indices):
    occupied = set(occupied_indices)
    relabeled = [
        {**bond, "metal": "Cr", "bond_type": bond["bond_type"].replace("Ga_", "Cr_")}
        if bond["metal"] == "Ga" and bond["metal_index"] - 1 in occupied else bond
        for bond in bonds
    ]
    paths, _ = enumerate_paths(relabeled)
    split_repeated_length_types(paths, angle_tolerance=0.01)
    return Counter("__".join(path[key] for key in ("family", "left_type", "right_type", "angle_type"))
                   for path in paths)


def check_manifest():
    checked = set()
    for line in (DATA / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        target = DATA / relative
        assert target.resolve().is_relative_to(DATA) and relative not in checked, relative
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest, relative
        checked.add(relative)
    return checked


def verify():
    checked = check_manifest()
    configs = read_csv(DATA / "configurations.csv")
    sources = read_csv(DATA / "configuration_provenance.csv")
    counts_csv = read_csv(DATA / "mom51_counts.csv")
    features = read_csv(DATA / "mom51_feature_catalog.csv")
    sites = {int(row["reference_Ga_index_0based"]): row for row in read_csv(DATA / "site_mapping.csv")}
    assert sites.keys() == set(range(24))

    with np.load(DATA / "filtered88.npz", allow_pickle=False) as archive:
        counts, targets, ns = (archive[key] for key in ("x", "y", "ns"))
        identifiers, occupations, names = (archive[key] for key in ("ids", "groups", "names"))
    assert counts.shape == (88, 51)
    assert len(set(identifiers)) == len(set(occupations)) == 88
    assert Counter(ns) == EXPECTED_COUNTS
    assert len(configs) == len(sources) == len(counts_csv) == 88
    assert [feature["MOM_type"] for feature in features] == list(names)
    assert Counter(row["source_cohort"] for row in sources) == EXPECTED_SOURCES
    assert Counter(row["selected_spin_branch"] for row in configs) == {"AFM": 57, "FM": 31}

    bonds = parent_bonds(DATA / "reference_Sr2Ga24O38.vasp")
    for i, (row, provenance, csv_counts) in enumerate(zip(configs, sources, counts_csv)):
        identifier, occupation, n = identifiers[i], occupations[i], int(ns[i])
        for table_row in (row, provenance, csv_counts):
            assert table_row["configuration_id"] == identifier, identifier
            assert int(table_row["row_1based"]) == i + 1, identifier
        assert row["occupation_key"] == provenance["occupation_key"] == occupation, identifier
        assert int(row["n_Cr"]) == int(provenance["n_Cr"]) == n, identifier

        occupied = json.loads(row["occupied_reference_indices_0based_json"])
        assert occupied == sorted(set(occupied)) and len(occupied) == n, identifier
        assert occupation == f"{n}:" + ",".join(map(str, occupied)), identifier
        assert json.loads(row["occupied_reference_labels_json"]) == [
            sites[index]["label"] for index in occupied
        ], identifier
        family_counts = Counter(sites[index]["family"] for index in occupied)
        for family in ("12k", "4f2", "2a", "2b", "4f1"):
            assert int(row[f"n_Cr_{family}"]) == family_counts[family], identifier

        for branch in ("FM", "AFM"):
            moments = json.loads(row[f"{branch}_Cr_moments_muB_json"])
            assert len(moments) == n and all(2.9 <= abs(value) <= 3.1 for value in moments), identifier
        energies = {branch: float(row[f"E_{branch}_sigma0_eV_per_cell"]) for branch in ("FM", "AFM")}
        assert row["selected_spin_branch"] == min(energies, key=energies.get), identifier
        assert np.isclose(float(row["selected_E_sigma0_eV_per_cell"]), targets[i], atol=1e-8, rtol=0), identifier
        assert np.isclose(min(energies.values()), targets[i], atol=1e-8, rtol=0), identifier
        assert {row["initial_structure"], row["relaxed_structure"]} <= checked, identifier

        recomputed = recompute_mom51(bonds, occupied)
        assert set(recomputed).issubset(names) and recomputed.total() == 228, identifier
        assert list(counts[i]) == [recomputed[name] for name in names], identifier
        assert list(counts[i]) == [int(csv_counts[name]) for name in names], identifier

    print(f"Verified {len(checked)} file checksums, 88 paired-spin training rows, and 88 × 51 recomputed MOM51 counts.")


if __name__ == "__main__":
    verify()
