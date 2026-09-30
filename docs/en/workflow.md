# Workflow and reasoning

[中文](../zh/workflow.md) · [Home](../../README.md)

## 1. What question does this workflow answer?

For a prescribed Ga/Cr occupation on a fixed reference crystal, we ask:

1. Which metal–oxygen pairs satisfy a documented distance cutoff?
2. How many distinct element-and-length bond classes occur, and how many bonds belong to each class?
3. Which pairs of bonds meet at the same O atom, forming an M–O–M path?
4. How many distinct path classes and individual paths occur in each configuration and concentration group?

Here M means Sr, Ga, or Cr. Thus Sr–O–Ga and Ga–O–Cr are included along with Cr–O–Cr. A path is an oxygen-centered connection between two different metal atoms; a bond class is not a path class.

## 2. How the final procedure was established

The following sequence summarizes the technical decisions, rather than reproducing chat messages.

1. The original counting task required automatic length categories and exhaustive combinations, replacing a small hand-written list of length windows. Closely spaced but distinct lengths had to remain distinguishable.
2. For comparing occupations, the agreed geometry convention was one fixed bulk, with only Ga/Cr species changed. Categories must remain identical across configurations.
3. A new bulk file was supplied. Its filename/title suggested Ba/Fe, while its species line specified Sr/Ga/O. The user explicitly confirmed the species line.
4. The new bulk was first counted without Cr: 13 bond classes and 16 observed path classes. This was a baseline, not the completed doped study.
5. The scope was clarified: apply the previous 2/4/6/8/10 Cr occupation labels to the **new** bulk and repeat the analysis. The old bulk must not provide replacement coordinates.
6. All 75 occupations were mapped by their coordinate-line labels, generated, counted, and checked. The user confirmed this result. This is the authoritative calculation reproduced here.

The old bulk itself and superseded tables are omitted to avoid mixing reference geometries. The earlier source archive is identified in the provenance documentation.

## 3. Separate geometry, occupation, and provenance

These are three different inputs:

- **Geometry:** the exact bytes of `data/bulk_input_original.vasp`, a Sr₂Ga₂₄O₃₈ cell with Cartesian coordinates.
- **Occupation:** `data/configuration_sites.csv`, containing Cr count, configuration name, and selected site labels.
- **Historical provenance:** the recorded `Compare_Energy` directories and inherited screening tables. Their energies and magnetic labels do not enter the counting code.

The cell has two formula units. A cell containing N Cr atoms has composition Sr₂Ga₂₄₋NCrNO₃₈; in SrCrₓGa₁₂₋ₓO₁₉, x=N/2. Thus cell Cr counts 2–10 correspond to x=1–5.

The new file has 24 unique Ga labels: 12×12k, 4×4f1, 4×4f2, 2×2a, and 2×2b. These strings are inherited site identifiers, not a fresh crystallographic symmetry classification performed by this code.

## 4. Map labels, then generate occupations

Some source labels start with `Cr_`; normalize this prefix before looking them up. Do not transfer an old atom index directly: the new file can order its Ga atoms differently.

For example, the new Ga index 10 is `2a_layer16` and index 14 is `2b_layer12`. The configuration `2Cr/group10_2a_layer16__2b_layer12` replaces precisely these two Ga sites. It contains Sr₂Ga₂₂Cr₂O₃₈.

The generated POSCAR is written in Sr/Ga/Cr/O groups. This reorders atom records, but does not move their sites. Coordinates are converted to fractional form with 16 decimal places. Every generated lattice and coordinate block is compared to the corresponding new-bulk block. The observed maximum Cartesian difference is about 1.3×10⁻¹⁵ Å.

## 5. Periodic-distance convention

For each cell-indexed metal i and oxygen j, calculate

```text
v(i,j,t) = (f_metal(i) - f_O(j) + t) @ lattice
d(i,j)   = min_t ||v(i,j,t)||
```

where t ranges over {-1,0,1}³ and lattice vectors are rows. Keep one minimizing vector. For this structure, expanding the search to {-2,-1,0,1,2}³ gives identical shortest distances.

**This is an index-pair convention, not enumeration of every periodic neighbor.** The following six Sr/O pairs have two images inside the cutoff:

| Sr index | O index |
|---:|---:|
| 1 | 2 |
| 1 | 16 |
| 1 | 35 |
| 2 | 10 |
| 2 | 23 |
| 2 | 37 |

Only one image per pair is kept, following the accepted earlier convention. Tied or near-tied images can have different directions. Therefore both coordination counts and the geometry of paths must be interpreted under this convention. Full periodic-neighbor counting would require a separately specified image-aware algorithm and new results.

This image range is verified for the supplied cell; it is not a proof for arbitrarily skewed cells or arbitrary coordinate representations.

## 6. Find new cutoffs from the new geometry

Sort the shortest distances inside an element-specific search window, find the largest adjacent gap, and use its midpoint as the cutoff. Accept a bond if `distance < cutoff`.

| Pair | Gap-search window (Å) | Lower gap endpoint (Å) | Upper endpoint (Å) | Cutoff (Å) |
|---|---|---:|---:|---:|
| Sr–O | 0.5 < d < 5.0 | 2.958098043228469 | 4.101205487029025 | 3.5296517651287473 |
| Ga/Cr–O | 0.5 < d < 4.0 | 2.2779384420000004 | 3.2893487629771907 | 2.7836436024885955 |

The 0.5 Å value limits gap searching; it is not an additional lower cutoff on accepted bonds. This is a heuristic geometric rule retained for consistency, not a universal chemical bonding criterion.

Because Ga and Cr occupy the same fixed sites here, they share the framework cutoff. No separate relaxed Cr–O distances are introduced.

## 7. Define global bond classes once

Within each element, sort the accepted distances and group values only while `new_value - group_minimum <= 1e-5 Å`. Comparing to the group minimum avoids a chain of small gaps merging a wide interval.

For adjacent groups A and B, use `(max(A)+min(B))/2` as a class boundary. Classification intervals are left-inclusive and right-exclusive. Their bounds are assignment rules, not the observed minimum and maximum distances. A representative distance is the mean of the group's observed values.

For example, lengths near 1.908436 and 1.909127 Å remain different classes. Rounding both values before classification would risk changing the result; full precision is used.

Compute categories from the new undoped framework once, then give its Ga–O categories corresponding Cr–O names. Ga–O and Cr–O retain separate identities even when their numerical lengths coincide. Do not re-cluster independently inside each configuration, since the meaning of a class ID would then change.

## 8. Construct and classify M–O–M paths

Collect all accepted metal–O bonds by oxygen index. For an oxygen with k retained metal neighbors, enumerate `k*(k-1)/2` unordered pairs of different metal neighbors. A reverse path is the same path; paths through different O atoms remain separate.

The initial key is:

```text
(ordered endpoint elements, left bond-length class, right bond-length class)
```

Order endpoints first by Sr/Ga/Cr element order, then by class and atom index. Always move the attached bond length with its endpoint. For a Ga–O–Cr path, “short Ga–O + long Cr–O” and “long Ga–O + short Cr–O” can be different classes; reversing the written direction of one path does not create a new path.

Calculate the angle at O from the two retained O→metal vectors:

```text
theta = arccos(clip(dot(v1,v2)/(d1*d2), -1, 1))
```

Only inside an otherwise identical element/length key, split angle groups if needed at a 0.01° tolerance. Define these subtypes globally over the 75 configurations. There are no additional angle subtypes in this dataset, but actual angles are retained for every path.

## 9. Theoretical classes versus observed classes

With 24 bond categories, the number of unordered category pairs with repetition is `24*25/2=300`. This includes hypothetical combinations that share no oxygen in the structure. Every configuration's complete table includes those combinations with zero counts.

The union of observed path types is 51. The corresponding per-concentration unions are 43, 48, 48, 50, and 49. Never sum these union sizes to obtain the global union: categories overlap.

The total number of paths in a configuration is 228, which is distinct from the number of path types. Aggregate occurrence counts across a concentration group sum over its available configurations; the groups have different sample counts, so these sums are not normalized populations or thermodynamic probabilities.

## 10. Checks and limits

The workflow asserts occupation cardinality and uniqueness, element counts, preserved lattice/coordinates, and agreement between mapped new-bulk distances and distances independently recomputed from every generated POSCAR. It also checks the larger image range, path uniqueness, and per-O combinatorial count identity.

The packaging verifier checks class sums, nonzero subsets, 75 occupation/provenance matches, input hash, and numerical identity of the English/Chinese outputs.

This is a documented workflow for this 64-atom cell and these 75 prescribed occupations. It does not enumerate all possible occupations at each concentration. Reusing it for another cell requires reviewing labels, element counts, cutoffs, image handling, and dataset-specific assertions, rather than assuming that 152 bonds or 228 paths are universal.
