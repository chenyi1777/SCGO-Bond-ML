# SCGO DFT configuration dataset and M–O–M descriptors

[English](README.md) | [简体中文](README.zh-CN.md)

This repository provides the **88 screened Cr/Ga configurations** used to train the SCGO energy models. Each configuration is a 64-atom Sr₂Ga₂₄₋ₙCrₙO₃₈ cell with 2, 4, 6, 8, or 10 Cr atoms.

| Cr per cell | From the earlier DFT archive | From additional DFT batches | Training configurations |
| ---: | ---: | ---: | ---: |
| 2 | 15 | 0 | 15 |
| 4 | 14 | 4 | 18 |
| 6 | 16 | 2 | 18 |
| 8 | 21 | 0 | 21 |
| 10 | 16 | 0 | 16 |
| **Total** | **82** | **6** | **88** |

The earlier DFT archive contained 109 candidate pairs after a 2.8–3.2 μB prescreen. Rescreening retained 82, and two subsequent DFT batches contributed another 6 of 18 candidates. For each retained occupation, **both the FM- and AFM-initialized calculations had to converge**, and every final Cr local moment in both branches had to satisfy **2.9 ≤ |mCr| ≤ 3.1 μB**. The training label is the lower of their VASP `energy(sigma->0)` values, in eV per cell. See the [screening history and DFT provenance](docs/en/data_and_provenance.md).

## Download the current dataset

- [Appendix F data dictionary](appendices/appendix-f/README.md)
- [Configuration table with both spin branches](appendices/appendix-f/configurations.csv)
- [Per-configuration DFT provenance](appendices/appendix-f/configuration_provenance.csv)
- [Original training arrays](appendices/appendix-f/filtered88.npz) and [MOM51 counts](appendices/appendix-f/mom51_counts.csv)
- [Fixed parent structure](appendices/appendix-f/reference_Sr2Ga24O38.vasp) and [initial and relaxed structures for the selected branches](appendices/appendix-f/structures/)

The descriptor workflow relabels occupied sites on a fixed Sr₂Ga₂₄O₃₈ parent structure. Each configuration gives 228 oxygen-centered M–O–M paths across a catalog of 51 path types. The DFT energy labels and relaxed structures come from the corresponding electronic-structure calculations.

## Verify the dataset

```bash
python -m pip install -r requirements.txt
python scripts/verify_training_dataset.py
```

The script checks file hashes, the occupation and provenance joins, both archived moment sets, and the selected energies. It independently recomputes all 88 × 51 path counts from the parent structure.

## Historical 75-configuration example

The original 75-configuration bond-counting tutorial and outputs remain available as a historical example. Its inputs and outputs are under `data/`, `results/`, `provenance/`, and `validation/`. The archive’s `SHA256SUMS.csv` describes the earlier packaged snapshot. See the [historical workflow](docs/en/workflow.md), [tutorial](docs/en/tutorial.md), and [historical data reference](docs/en/legacy_data_and_provenance.md).
