# Data reference and HPC provenance

[中文](../zh/data_and_provenance.md) · [Home](../../README.md)

## 1. Authoritative structure and source identity

Original supplied location:

```text
C:/Users/yuany/Downloads/BaFeO (1).vasp
```

Bundled unchanged as `data/bulk_input_original.vasp`. SHA-256:

```text
73bfd6939e1f1996e2938504004307aeb6ef55716ae53223f229fd8cc8c0305a
```

Formal composition: Sr₂Ga₂₄O₃₈. The title still says `Ba2 Fe24 O38`; preservation of the original bytes is deliberate. The new bulk lattice and all 64 coordinates are included in the file. The 24 Ga labels and their new indices are exported to `results/en/bulk_site_map.csv`.

The undoped supporting calculation is summarized in `data/undoped_reference_summary.json`: 2 Sr–O classes/18 bonds and 11 Ga–O classes/134 bonds; 4 Sr–O–Ga classes/54 paths and 12 Ga–O–Ga classes/174 paths. This is a baseline record, not a substitute for the 75 doped results.

## 2. Original calculation directories

The inherited record uses only `Compare_Energy` calculations under:

```text
/ix/gwang/yiy219/SrCrGaO/{N}/Compare_Energy/{group}/{spin}/
```

where `N` is 2, 4, 6, 8, or 10 and `spin` is FM or AFM. The group names differ across concentrations. The braces above are placeholders; see the manifests for exact strings.

One recorded selected directory is:

```text
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM
```

The corresponding conventional file paths are:

```text
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM/OUTCAR
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM/INCAR
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM/POSCAR
```

**Evidence boundary:** the directory is recorded in the inherited CSV; the three file paths are formed by appending conventional filenames. This packaging task did not connect to the supercomputer or verify current file existence. The hostname, SSH alias, login account, and credentials were not supplied. A username-looking component of a directory is not sufficient to establish login details.

Raw HPC OUTCAR, INCAR, and POSCAR files are **not** bundled. The generated local `POSCAR_bulk_doped` files use the new fixed bulk and must not be described as copies of the original HPC structures.

## 3. Which provenance tables are included?

| File | Contents |
|---|---|
| `provenance/hpc_selected_paths_en.csv` | 75 selected configurations, site labels, recorded directories, derived file paths, and corresponding new-bulk structures |
| `provenance/hpc_selected_paths_zh.csv` | Chinese counterpart |
| `provenance/all_156_hpc_directories.csv` | All recorded candidate FM/AFM directories, with inherited validity and selection flags |
| `provenance/candidate_audit_en.csv` | English-header copy of the 156-row magnetic/convergence audit |
| `provenance/original_audit/selected_energy_and_sites.csv` | Original selected-record table, preserved unchanged |
| `provenance/original_audit/候选磁态审核.csv` | Original candidate audit, preserved unchanged |
| `provenance/original_audit/构型选择结果.csv` | Original 78-group selection table, preserved unchanged |
| `provenance/source_locations.csv` | Original local paths and their bundled equivalents |
| `provenance/audit_reason_strings.json` | Exact exclusion-reason strings present in the inherited audit |

Energies and magnetic moments are retained only to explain historical selection and traceability. The counting scripts read neither the energy columns nor the provenance tables when constructing geometry.

## 4. Why 75 configurations?

The inherited audit covers 156 spin calculations belonging to 78 groups. The recorded screening checked completed OUTCARs, ionic convergence, final Cr local moment magnitudes of 2.5–3.5 μB, and the intended FM/AFM sign pattern. Each retained group selected the lower-energy valid branch.

Three groups were excluded because neither branch was valid: `4Cr/group11`, `4Cr/group13`, and `10Cr/group06`. This leaves 13, 17, 15, 16, and 14 configurations at the five cell Cr counts.

These statements describe the inherited audit, not a new review of raw electronic-structure outputs. They explain the occupation list's provenance; they do not affect the distance calculations. The 75 structures are a selected dataset, not an exhaustive list of all possible occupations.

## 5. Input and output schema

### Input occupations

`nCr_cell` is the integer cell Cr count. `group` is a source identifier. `Cr_sites` is a semicolon-separated list of new-bulk-compatible labels, optionally prefixed by `Cr_`.

### Global outputs

| English filename | Meaning |
|---|---|
| `concentration_summary.csv` | Counts, unions, and ranges of per-configuration type counts |
| `configuration_summary.csv` | 75 individual configurations, family counts, and occupied bulk Ga indices |
| `cross_concentration_type_counts.csv` | 24 single-bond classes and 51 observed path classes with counts summed by concentration |
| `all_bonds.csv` | 11,400 individual bonds, with configuration identifiers |
| `all_MOM_paths.csv` | 17,100 individual oxygen-centered paths |
| `bulk_site_map.csv` | New bulk Ga index, original POSCAR global index, and label |
| `summary.json` | Cutoffs, tolerance-related results, input hash, verified totals, and multi-image pairs |

### Per-configuration outputs

Each `results/en/{N}Cr/{group}/` contains:

- `POSCAR_bulk_doped`: generated fixed-bulk occupation.
- `bond_types_and_counts.csv`: 24 shared categories, including absent categories.
- `bonds.csv`: actual bond lengths, element-local indices, original Ga-site indices, and image shifts.
- `all_MOM_combinations_including_zero.csv`: all 300 theoretical combinations.
- `observed_MOM_types_and_counts.csv`: only combinations with positive counts.
- `MOM_paths.csv`: actual path lengths, angles, endpoints, and oxygen indices.

The Chinese mirror uses translated filenames and headers. [results/column_dictionary.csv](../../results/column_dictionary.csv) maps every result column between languages. Numerical values and row order are preserved; CSV files use UTF-8 with BOM for common spreadsheet software.

## 6. Index conventions and units

- `bulk_Ga_index_1based`: Ga index 1–24 in the **new original bulk**, not the old bulk.
- `POSCAR_global_index_1based`: original new-bulk atom index 1–64; Ga atoms occupy 3–26.
- `element_local_index_1based`: index within a species in the generated structure. Ga and Cr are renumbered after species grouping.
- `oxygen_index_1based`: O index 1–38; O ordering is retained.
- `periodic_image_shift`: integer translation applied to the metal fractional position relative to the O when finding the shortest vector.
- `_A`: length in ångströms. `_deg`: angle in degrees.
- `_count`: occurrence count, except columns explicitly named `type_count` or `union_count`, which count distinct classes.

The two sides of a path retain their own elements and lengths. Do not mix the new-bulk Ga index with the generated Cr element-local index.

## 7. Reproducibility records

`validation/verification.json` records table/provenance and bilingual checks. `validation/reproduction_log.txt` records the packaged workflow run. `validation/accepted_result_comparison.json` records comparison with the previously accepted counting outputs.

`SHA256SUMS.csv` lists the packaged files and hashes, excluding itself. It describes a snapshot: regenerated files may change formatting or floating-point rounding on another numerical environment even when the geometric result remains equivalent. Structural invariants and the verifier are the primary numerical checks.

The preserved local and HPC paths document provenance; they are not portable execution dependencies. Reproduction uses the relative files already included in this repository.
