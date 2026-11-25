# Appendix F. DFT Configuration Dataset

[简体中文](README.zh-CN.md)

This dataset contains the 88 Cr/Ga occupations used to train the SCGO energy models. Each row represents one 64-atom reference cell with composition Sr₂Ga₂₄₋ₙCrₙO₃₈. The training set contains 15, 18, 18, 21, and 16 configurations at 2, 4, 6, 8, and 10 Cr atoms per cell, respectively.

The FM- and AFM-initialized calculations for each occupation were screened as a pair. Both had to converge and every final Cr local moment in each calculation had to satisfy 2.9 ≤ |mCr| ≤ 3.1 μB, including the endpoints. The training target is the lower of the two VASP `energy(sigma->0)` values, in eV per 64-atom cell. FM and AFM identify the initial spin branches. The signed final moments follow the Cr order within each archived output.

The training set combines 82 configurations retained from the earlier 109-pair DFT archive and six retained from 18 candidates in two additional DFT batches. The [screening and provenance notes](../../docs/en/data_and_provenance.md) give the counts by composition and identify the six additional groups.

| File | Contents |
| --- | --- |
| [configurations.csv](configurations.csv) | Occupied sites, per-family counts, both spin-branch energies and moments, selected energy, and structure paths. |
| [configuration_provenance.csv](configuration_provenance.csv) | Source cohort, batch, and archived project-relative directories for both spin branches. |
| [filtered88.npz](filtered88.npz) | Original training arrays in their original order. Load with NumPy using `allow_pickle=False`. |
| [mom51_counts.csv](mom51_counts.csv) | The 88 × 51 path-count matrix. Each row sums to 228. |
| [mom51_feature_catalog.csv](mom51_feature_catalog.csv) | Feature order and identifiers, both reference metal–O bond lengths in Å, and training-set count ranges. |
| [site_mapping.csv](site_mapping.csv) | Parent-Ga indices, reference atom numbers, site labels, and site families. |
| [reference_Sr2Ga24O38.vasp](reference_Sr2Ga24O38.vasp) | Fixed parent structure used to compute the descriptors. |
| [structures/](structures/) | Indexed initial and relaxed VASP files for each selected spin branch. Original coordinate order is preserved. The header lines were standardized and the velocity records omitted. |
| [SHA256SUMS.txt](SHA256SUMS.txt) | Data and structure checksums. |

## Column and array conventions

- `row_1based` matches the structure filename prefix. `configuration_id` matches the training archive. The `occupation_key` consists of the Cr count and the sorted zero-based parent-Ga indices.
- Fields ending in `_json` contain JSON arrays inside CSV cells. The index and label lists correspond element by element.
- `n_Cr_<family>` gives the Cr count for that site family. The five family counts sum to `n_Cr`.
- Energy fields give the AFM and FM energies, the signed difference `E_FM - E_AFM`, and the selected minimum. The suffix `_eV_per_cell` refers to the 64-atom cell.
- In the NPZ file, `x` contains the path counts, `y` the selected energies, `ns` the Cr counts, `ids` the configuration IDs, `groups` the occupation keys, and `names` the ordered feature labels.

This release covers the screened training set. It includes both branch energies and moments and a structure pair for each selected branch. The archived inputs for the 176 branches list `GGA=PE`, `METAGGA=R2SCAN`, and `IVDW=11`. These entries record input tags. The VASP execution output determines the active settings.

The SHA-256 of the original training archive is `46d9469faa1fe0b17bccf4a492efc96a3af930954a5b1336f4496ee158e6eda5`.
