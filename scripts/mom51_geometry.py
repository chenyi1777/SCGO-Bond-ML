"""Periodic bond classification and path counting for MOM51."""
from collections import defaultdict
from itertools import combinations, product
from pathlib import Path

import numpy as np


METALS = ('Sr', 'Ga', 'Cr')


def read_poscar(path):
    lines = [line.strip() for line in Path(path).read_text(encoding='utf-8').splitlines()
             if line.strip()]
    scale = float(lines[1].split()[0])
    if scale <= 0:
        raise ValueError('This script requires a positive POSCAR scale factor.')
    lattice = np.array([[float(x) for x in line.split()[:3]] for line in lines[2:5]]) * scale
    elements = lines[5].split()
    counts = [int(x) for x in lines[6].split()]
    if len(elements) != len(counts):
        raise ValueError('POSCAR element/count mismatch.')
    coordinate_line = 7
    if lines[coordinate_line].lower().startswith('s'):
        coordinate_line += 1
    mode = lines[coordinate_line].lower()
    raw = np.array([[float(x) for x in lines[coordinate_line + 1 + i].split()[:3]]
                    for i in range(sum(counts))])
    if mode.startswith('d'):
        frac = raw
    elif mode.startswith(('c', 'k')):
        frac = (raw * scale) @ np.linalg.inv(lattice)
    else:
        raise ValueError(f'Unknown coordinate mode: {lines[coordinate_line]}')
    atoms = {}
    start = 0
    for element, count in zip(elements, counts):
        atoms[element] = frac[start:start + count]
        start += count
    return lines[0], lattice, atoms


def shortest_pair_vectors(atoms, lattice, metal):
    """One shortest periodic image for each cell-indexed metal/O pair."""
    shifts = np.array(list(product((-1, 0, 1), repeat=3)), dtype=float)
    rows = []
    for i, mf in enumerate(atoms[metal], 1):
        for j, of in enumerate(atoms['O'], 1):
            vectors = (mf - of + shifts) @ lattice
            distances = np.linalg.norm(vectors, axis=1)
            k = int(np.argmin(distances))
            rows.append(dict(metal=metal, metal_index=i, O_index=j,
                             distance_A=float(distances[k]), vector=vectors[k],
                             image=tuple(int(x) for x in shifts[k])))
    return rows


def suggest_cutoff(rows, max_search):
    values = np.sort([r['distance_A'] for r in rows
                      if 0.5 < r['distance_A'] < max_search])
    if len(values) < 2:
        raise ValueError('Too few distances to determine a bond cutoff.')
    gaps = np.diff(values)
    k = int(np.argmax(gaps))
    return float((values[k] + values[k + 1]) / 2), float(values[k]), float(values[k + 1])


def numerical_groups(values, tolerance):
    groups = []
    for value in sorted(values):
        if not groups or value - groups[-1][0] > tolerance:
            groups.append([value])
        else:
            groups[-1].append(value)
    boundaries = [(a[-1] + b[0]) / 2 for a, b in zip(groups, groups[1:])]
    return groups, boundaries


def classify_bonds(rows, metal, cutoff, tolerance):
    chosen = [r for r in rows if r['distance_A'] < cutoff]
    groups, boundaries = numerical_groups([r['distance_A'] for r in chosen], tolerance)
    classes = []
    for i, group in enumerate(groups, 1):
        classes.append(dict(metal=metal, bond_type=f'{metal}_O_{i:02d}',
                            count=len(group), representative_A=float(np.mean(group)),
                            observed_min_A=group[0], observed_max_A=group[-1],
                            lower_inclusive_A=0 if i == 1 else boundaries[i - 2],
                            upper_exclusive_A=cutoff if i == len(groups) else boundaries[i - 1]))
    for row in chosen:
        index = int(np.searchsorted(boundaries, row['distance_A'], side='right'))
        row['bond_type'] = classes[index]['bond_type']
    return chosen, classes


def ordered_bond_pair(a, b):
    ka = (METALS.index(a['metal']), int(a['bond_type'].rsplit('_', 1)[1]),
          a['metal_index'])
    kb = (METALS.index(b['metal']), int(b['bond_type'].rsplit('_', 1)[1]),
          b['metal_index'])
    return (a, b) if ka <= kb else (b, a)


def enumerate_paths(bonds):
    by_oxygen = defaultdict(list)
    for bond in bonds:
        by_oxygen[bond['O_index']].append(bond)
    paths = []
    for oxygen, neighbors in sorted(by_oxygen.items()):
        for a, b in combinations(neighbors, 2):
            if a['metal'] == b['metal'] and a['metal_index'] == b['metal_index']:
                continue
            a, b = ordered_bond_pair(a, b)
            cosine = float(np.dot(a['vector'], b['vector']) /
                           (a['distance_A'] * b['distance_A']))
            paths.append(dict(family=f"{a['metal']}-O-{b['metal']}",
                              left_type=a['bond_type'], right_type=b['bond_type'],
                              O_index=oxygen, left_metal=a['metal'],
                              left_index=a['metal_index'], right_metal=b['metal'],
                              right_index=b['metal_index'],
                              left_distance_A=a['distance_A'],
                              right_distance_A=b['distance_A'],
                              angle_deg=float(np.degrees(np.arccos(np.clip(cosine, -1, 1))))))
    return paths, by_oxygen


def split_repeated_length_types(paths, angle_tolerance):
    """Use angle only when identical element/length keys have distinct angles."""
    by_key = defaultdict(list)
    for row in paths:
        by_key[(row['family'], row['left_type'], row['right_type'])].append(row)
    for members in by_key.values():
        groups, boundaries = numerical_groups([r['angle_deg'] for r in members], angle_tolerance)
        for row in members:
            index = int(np.searchsorted(boundaries, row['angle_deg'], side='right'))
            row['angle_type'] = f'A{index + 1:02d}' if len(groups) > 1 else ''
            row['angle_group_mean_deg'] = float(np.mean(groups[index])) if len(groups) > 1 else None
            row['angle_lower_inclusive_deg'] = boundaries[index - 1] if index else 0.0
            row['angle_upper_exclusive_deg'] = boundaries[index] if index < len(boundaries) else 180.0
