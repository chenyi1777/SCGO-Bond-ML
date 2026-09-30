# Hands-on tutorial

[中文](../zh/tutorial.md) · [Home](../../README.md)

## 1. Inspect the inputs before running code

Open [the original new bulk](../../data/bulk_input_original.vasp). Its scale factor is 1.0; the formal elements are `Sr Ga O`, the counts are `2 24 38`, and the coordinate mode is `Cartesian`. The next 64 lines contain coordinates; the 24 Ga lines also carry site labels.

The first line is a descriptive title, not the formal species definition. Its Ba/Fe wording was explicitly resolved in favor of Sr/Ga/O. Do not silently infer elements from the filename.

Then open [configuration_sites.csv](../../data/configuration_sites.csv). Each row represents one prescribed occupation, with fields `nCr_cell`, `group`, and `Cr_sites`. The `group` string identifies a calculation; it does not determine coordinates.

## 2. Set up a small Python environment

Use Python 3.12 to match the tested environment. Only NumPy is required.

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell, without needing to activate the environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_workflow.py --output .reproduction
.\.venv\Scripts\python.exe scripts/verify_results.py --results .reproduction
```

On Linux/macOS or an already active environment:

```bash
python scripts/run_workflow.py --output .reproduction
python scripts/verify_results.py --results .reproduction
```

Run these commands from the repository root. Paths containing spaces should be quoted. The scripts derive their default input paths from their own location, so no author-specific absolute path is needed to reproduce the results.

## 3. Understand what runs

`run_workflow.py` calls `count_doped.py`, then `export_english.py`.

The counting program:

1. Reads the new bulk and maps its Ga labels.
2. Recomputes shortest metal–O distances and new cutoffs.
3. Builds shared Sr–O/Ga–O/Cr–O categories.
4. Applies each occupation and writes a POSCAR.
5. Verifies geometry and reconstructs bonds independently.
6. Enumerates paths, creates shared path classes, and writes tables.

The exporter changes filenames and table headers, preserving row order and numeric strings. The English and Chinese structures are byte-identical. `verify_results.py` checks that both language versions contain the same numerical data.

To replace the published results after inspecting a trial, omit `--output .reproduction`. Existing files at the chosen output location are updated; unrelated output directories are not deleted.

## 4. Read a worked example

Use `2Cr/group10_2a_layer16__2b_layer12`:

- New-bulk Ga indices 10 and 14 are replaced by Cr.
- The generated composition is Sr₂Ga₂₂Cr₂O₃₈.
- Its [POSCAR](../../results/en/2Cr/group10_2a_layer16__2b_layer12/POSCAR_bulk_doped) contains the new bulk's positions, regrouped by species.
- [Bond classes](../../results/en/2Cr/group10_2a_layer16__2b_layer12/bond_types_and_counts.csv) list the 24 shared classes, including classes absent from this particular configuration.
- [Observed path classes](../../results/en/2Cr/group10_2a_layer16__2b_layer12/observed_MOM_types_and_counts.csv) omit zero-count categories.

For a short numerical check, save the following as a Python snippet and run it from the repository root:

```python
import csv
from pathlib import Path

case = Path('results/en/2Cr/group10_2a_layer16__2b_layer12')
def rows(name):
    with (case / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

bonds = rows('bond_types_and_counts.csv')
paths = rows('observed_MOM_types_and_counts.csv')
print(sum(int(r['count']) for r in bonds))  # 152 bonds
print(sum(int(r['count']) for r in paths))  # 228 paths
for r in paths[:3]:
    print(r['path_family'], r['left_representative_distance_A'],
          r['right_representative_distance_A'], r['count'])
```

Use `.reproduction/en/...` in the snippet if you want to inspect your trial output instead of the packaged tables.

## 5. Distinguish representative and individual lengths

`bond_types_and_counts.csv` contains a representative mean length and interval for each shared class. `bonds.csv` contains the actual length of each individual counted pair.

Similarly, `observed_MOM_types_and_counts.csv` contains representative left/right lengths and a mean angle, whereas `MOM_paths.csv` contains each path's actual lengths and angle. All distances use Å and all angles use degrees.

Do not treat a classification boundary as an observed bond length. Do not round distances before assigning categories. Spreadsheet software may display fewer decimals than the CSV stores.

## 6. Check the result rather than trusting a single total

The completed verification report should show 75 configurations, 11,400 bonds, 17,100 paths, and English/Chinese parity. Review both type counts and occurrence counts. A type can disappear while the total number of bonds stays constant.

If reproduction fails, first check the bulk hash, formal elements, coordinate mode, unique site labels, and occupation prefix normalization. An unexpected class count may indicate a changed tolerance or reference geometry rather than a missing atom.

## 7. Learn from the example and adapt carefully

The parser handles positive POSCAR scale factors, Direct or Cartesian coordinates, and a Selective Dynamics marker. The supplied cell uses a positive scalar factor. This is not a complete implementation of every POSCAR variant; negative volume scaling is rejected.

The reference-cell workflow deliberately asserts 24 labeled Ga sites, 75 configurations, and this dataset's verified bond/path totals. To adapt it to another system, review those assumptions explicitly. If you change the cutoff or image convention, describe the change and regenerate all classes; do not compare new IDs against old IDs as though they were unchanged.

Keep the reference geometry, occupation list, script version, tolerances, and input hash together. That is what makes a bond-counting result reproducible.
