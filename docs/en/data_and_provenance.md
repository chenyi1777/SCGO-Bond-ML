# Provenance of the 88-configuration SCGO training set

[简体中文](../zh/data_and_provenance.md) | [Repository home](../../README.md) | [Appendix F](../../appendices/appendix-f/README.md)

## Screening and inclusion

The training set contains 88 distinct Cr/Ga occupations. The source records come from VASP calculations on concentration-optimized structures. The earlier archive had 109 occupations after a 2.8–3.2 μB moment prescreen. Applying the final rule retained 82 of those occupations, including 54 from the base calculations and 28 from the rebuilt batches. Two additional batches covered 18 candidates and contributed six retained occupations.

| Cr per cell | Earlier candidates | Earlier retained | Additional candidates | Additional retained | Final |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 16 | 15 | 0 | 0 | 15 |
| 4 | 17 | 14 | 10 | 4 | 18 |
| 6 | 23 | 16 | 8 | 2 | 18 |
| 8 | 28 | 21 | 0 | 0 | 21 |
| 10 | 25 | 16 | 0 | 0 | 16 |
| **Total** | **109** | **82** | **18** | **6** | **88** |

1. Match the FM- and AFM-initialized calculations by composition and occupied Ga sites.
2. Require convergence for both calculations. In each calculation, require every final Cr local moment magnitude to lie in the inclusive range 2.9–3.1 μB.
3. Use the smaller of the two VASP `energy(sigma->0)` values as the target in eV per 64-atom cell. This selects 57 AFM-initialized and 31 FM-initialized branches.

The first additional batch, `additional_4Cr6Cr_20261030` (array 3257252), contributed 4-Cr groups 01 and 02. The second, `additional_4Cr6Cr_20261031_add8` (array 3257302), contributed 4-Cr groups 07 and 09 and 6-Cr groups 05 and 08. The archived AFM entry for the 6-Cr group 08 uses its converged restart. The FM branch supplies that occupation’s training energy.

## Trace a configuration to its calculation

Use `configuration_id` or `occupation_key` to join the [DFT source table](../../appendices/appendix-f/configuration_provenance.csv) to the [configuration table](../../appendices/appendix-f/configurations.csv). The two source columns record the actual AFM and FM run directories relative to the original SCGO project root, including restart or retry directory names where applicable. `source_cohort` identifies the earlier base, earlier rebuilt, and additional calculations. The additional array ID identifies the original submission batch.

The published structure files contain the initial and relaxed structures for each selected branch. The configuration table records the energies and Cr moments of both branches. The [dataset verifier](../../scripts/verify_training_dataset.py) checks the published tables against the training archive and recomputes MOM51 from the fixed parent structure. Reproducing the DFT calculations requires the original run inputs and a VASP installation.
