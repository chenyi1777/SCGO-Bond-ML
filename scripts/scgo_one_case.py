"""Geometry helpers retained from the accepted bond-counting workflow.

Use run_workflow.py for the fixed-reference, shared-category analysis.
This module computes geometry only; archived calculation audits are separate.
"""

import argparse
import csv
import json
from collections import defaultdict
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path

import numpy as np


METALS = ('Sr', 'Ga', 'Cr')
MAX_SEARCH = {'Sr': 5.0, 'Ga': 4.0, 'Cr': 4.0}


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


def save_csv(path, rows, columns, labels):
    with Path(path).open('w', newline='', encoding='utf-8-sig') as handle:
        writer = csv.DictWriter(handle, fieldnames=[labels.get(c, c) for c in columns])
        writer.writeheader()
        for row in rows:
            writer.writerow({labels.get(c, c): row.get(c, '') for c in columns})


def analyze(poscar, output, length_tol=1e-5, angle_tol=0.01):
    if length_tol <= 0 or angle_tol <= 0:
        raise ValueError('Both tolerances must be positive.')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    title, lattice, atoms = read_poscar(poscar)
    missing = [e for e in (*METALS, 'O') if e not in atoms]
    if missing:
        raise ValueError(f'Missing elements: {missing}')
    cutoffs = {}
    selected = []
    classes = []
    for metal in METALS:
        raw = shortest_pair_vectors(atoms, lattice, metal)
        cutoff, low, high = suggest_cutoff(raw, MAX_SEARCH[metal])
        bonds, found = classify_bonds(raw, metal, cutoff, length_tol)
        cutoffs[metal] = dict(cutoff_A=cutoff, gap_lower_A=low, gap_upper_A=high,
                              bond_count=len(bonds), length_type_count=len(found))
        selected.extend(bonds)
        classes.extend(found)
    paths, by_oxygen = enumerate_paths(selected)
    split_repeated_length_types(paths, angle_tol)

    lengths = {row['bond_type']: row for row in classes}
    observed = defaultdict(list)
    for row in paths:
        observed[(row['family'], row['left_type'], row['right_type'], row['angle_type'])].append(row)
    combinations_rows = []
    metal_types = {m: [r['bond_type'] for r in classes if r['metal'] == m] for m in METALS}
    for im, left_metal in enumerate(METALS):
        for right_metal in METALS[im:]:
            if left_metal == right_metal:
                pairs = combinations_with_replacement(metal_types[left_metal], 2)
            else:
                pairs = product(metal_types[left_metal], metal_types[right_metal])
            for left, right in pairs:
                family = f'{left_metal}-O-{right_metal}'
                matching = [(key, members) for key, members in observed.items()
                            if key[:3] == (family, left, right)]
                if not matching:
                    matching = [((family, left, right, ''), [])]
                for key, members in matching:
                    combinations_rows.append(dict(family=family, left_type=left,
                                                  left_representative_A=lengths[left]['representative_A'],
                                                  right_type=right,
                                                  right_representative_A=lengths[right]['representative_A'],
                                                  angle_type=key[3],
                                                  angle_mean_deg=(float(np.mean([x['angle_deg'] for x in members]))
                                                                  if key[3] and members else None),
                                                  angle_min_deg=(min(x['angle_deg'] for x in members)
                                                                 if key[3] and members else None),
                                                  angle_max_deg=(max(x['angle_deg'] for x in members)
                                                                 if key[3] and members else None),
                                                  count=len(members)))
    expected = sum(len(v) * (len(v) - 1) // 2 for v in by_oxygen.values())
    assert len(paths) == expected
    assert sum(x['count'] for x in combinations_rows) == len(paths)
    assert len({(p['O_index'], p['left_metal'], p['left_index'],
                 p['right_metal'], p['right_index']) for p in paths}) == len(paths)

    common = {'family': '组合类型', 'left_type': '左侧键类别', 'right_type': '右侧键类别',
              'left_representative_A': '左侧代表键长（Å）',
              'right_representative_A': '右侧代表键长（Å）',
              'angle_type': '键角类别', 'angle_mean_deg': '代表键角（度）',
              'angle_min_deg': '实际最小键角（度）', 'angle_max_deg': '实际最大键角（度）',
              'count': '数量'}
    combination_cols = list(common)
    save_csv(output / 'all_combinations.csv', combinations_rows, combination_cols, common)
    save_csv(output / 'existing_combinations.csv',
             [r for r in combinations_rows if r['count']], combination_cols, common)
    save_csv(output / 'bond_length_types.csv', classes,
             ['metal', 'bond_type', 'representative_A', 'observed_min_A',
              'observed_max_A', 'lower_inclusive_A', 'upper_exclusive_A', 'count'],
             {'metal': '金属元素', 'bond_type': '键类别', 'representative_A': '代表键长（Å）',
              'observed_min_A': '实际最短键长（Å）', 'observed_max_A': '实际最长键长（Å）',
              'lower_inclusive_A': '分类下限（含，Å）',
              'upper_exclusive_A': '分类上限（不含，Å）', 'count': '数量'})
    bond_cols = ['metal', 'metal_index', 'O_index', 'distance_A', 'bond_type',
                 'image_x', 'image_y', 'image_z']
    bond_rows = [dict((k, v) for k, v in row.items() if k != 'vector') for row in selected]
    for row in bond_rows:
        row['image_x'], row['image_y'], row['image_z'] = row.pop('image')
    save_csv(output / 'selected_bonds.csv', bond_rows, bond_cols,
             {'metal': '金属元素', 'metal_index': '金属原子编号', 'O_index': 'O原子编号',
              'distance_A': '实际键长（Å）', 'bond_type': '键类别',
              'image_x': '周期镜像x', 'image_y': '周期镜像y', 'image_z': '周期镜像z'})
    path_cols = ['family', 'O_index', 'left_metal', 'left_index', 'left_type',
                 'left_distance_A', 'right_metal', 'right_index', 'right_type',
                 'right_distance_A', 'angle_deg', 'angle_type']
    save_csv(output / 'paths.csv', paths, path_cols,
             {'family': '组合类型', 'O_index': 'O原子编号', 'left_metal': '左侧金属元素',
              'left_index': '左侧金属原子编号', 'left_type': '左侧键类别',
              'left_distance_A': '左侧实际键长（Å）', 'right_metal': '右侧金属元素',
              'right_index': '右侧金属原子编号', 'right_type': '右侧键类别',
              'right_distance_A': '右侧实际键长（Å）', 'angle_deg': '实际键角（度）',
              'angle_type': '键角类别'})
    summary = dict(title=title, composition={e: len(v) for e, v in atoms.items()},
                   POSCAR=str(Path(poscar).resolve()), cutoffs=cutoffs,
                   length_tolerance_A=length_tol, angle_tolerance_deg=angle_tol,
                   bond_count=len(selected), path_count=len(paths),
                   baseline_possible_types=len({(r['family'], r['left_type'], r['right_type'])
                                                for r in combinations_rows}),
                   existing_types=sum(bool(r['count']) for r in combinations_rows),
                   family_counts={f: sum(r['count'] for r in combinations_rows if r['family'] == f)
                                  for f in sorted({r['family'] for r in combinations_rows})})
    (output / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                                          encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('poscar')
    parser.add_argument('--output', required=True)
    parser.add_argument('--length-tol', type=float, default=1e-5)
    parser.add_argument('--angle-tol', type=float, default=0.01)
    arguments = parser.parse_args()
    print(json.dumps(analyze(arguments.poscar, arguments.output,
                             arguments.length_tol, arguments.angle_tol),
                     ensure_ascii=False, indent=2))
