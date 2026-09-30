# Counting metal–oxygen bonds and M–O–M paths on a fixed bulk structure

[English](README.md) | [简体中文](README.zh-CN.md)

A reproducible case study for readers learning how to turn a labeled VASP structure into consistent bond-length categories and oxygen-centered path counts. The example uses **Sr₂Ga₂₄O₃₈** and 75 prescribed Ga→Cr occupations with 2, 4, 6, 8, or 10 Cr atoms per 64-atom cell.

The supplied **new bulk structure is the only source of lattice vectors and coordinates**. Archived calculations supply the occupation labels and provenance. Their relaxed coordinates are not used for this geometry analysis. This repository covers counting only; it contains no trained models or prediction results.

## Start here

1. [Workflow and reasoning](docs/en/workflow.md): the problem, decisions, equations, and counting conventions.
2. [Hands-on tutorial](docs/en/tutorial.md): installation, reproduction, and reading one example.
3. [Data, output schema, and HPC provenance](docs/en/data_and_provenance.md): what each file means and where the original calculations were recorded.
4. [中文对应文档](README.zh-CN.md).

## Main results

| Cr atoms per cell | Configurations | Bond-type union | Observed M–O–M type union |
|---:|---:|---:|---:|
| 2 | 13 | 24 | 43 |
| 4 | 17 | 24 | 48 |
| 6 | 15 | 24 | 48 |
| 8 | 16 | 24 | 50 |
| 10 | 14 | 24 | 49 |
| **All, deduplicated** | **75** | **24** | **51** |

Each configuration contains **152 counted bonds and 228 counted M–O–M paths** under the stated convention. A type union is taken over several configurations; it is not the number of types in every individual configuration.

Bond categories comprise 2 Sr–O, 11 Ga–O, and 11 Cr–O length classes. There are 300 theoretical unordered combinations of the 24 bond classes, including zero-count combinations. No additional angle subtypes occur at the chosen 0.01° tolerance.

## Reproduce

Tested with Python 3.12 and NumPy 2.3.5. No VASP executable, HPC login, or network connection is needed after installing NumPy.

```bash
python -m pip install -r requirements.txt
python scripts/run_workflow.py
python scripts/verify_results.py
```

The default command updates `results/zh/` and `results/en/`. To keep the published outputs untouched during a trial:

```bash
python scripts/run_workflow.py --output .reproduction
python scripts/verify_results.py --results .reproduction
```

## Important interpretation

- The file originally named `BaFeO (1).vasp` has the title `Ba2 Fe24 O38`, but its formal species line is `Sr Ga O`. **The user explicitly confirmed Sr/Ga/O.** The original file is preserved unchanged at [data/bulk_input_original.vasp](data/bulk_input_original.vasp).
- Distances and cutoffs were recomputed from this new bulk. Old-bulk thresholds and categories were not reused.
- This workflow keeps **one shortest periodic image per cell-indexed metal/O pair**. Six Sr/O index pairs have multiple images within the cutoff. Consequently these counts are not full periodic-neighbor coordination counts. See the [precise convention and limitations](docs/en/workflow.md#5-periodic-distance-convention).
- These are operational geometric categories, not independently established chemical bonds or exchange constants.

## Repository layout

```text
data/          Original new bulk, occupations, input hash, undoped summary
scripts/       Counting code, English export, reproduction and verification
results/en/    English tables and all 75 generated POSCARs
results/zh/    Equivalent Chinese tables and the same 75 POSCARs
provenance/    Recorded HPC directories, source locations, inherited audits
docs/en/       English workflow, tutorial, and data reference
docs/zh/       Corresponding Chinese documentation
validation/   Reproduction and verification records
SHA256SUMS.csv File manifest for the packaged snapshot
```

Useful tables: [per-configuration summary](results/en/configuration_summary.csv), [cross-concentration class counts](results/en/cross_concentration_type_counts.csv), and [75 selected HPC source directories](provenance/hpc_selected_paths_en.csv).

The package is a repository snapshot ready to inspect and upload. It does not contain a `.git` directory or publish anything to a remote account.
