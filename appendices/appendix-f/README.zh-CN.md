# 附录 F　DFT 构型数据集

[English](README.md)

本数据集包含训练 SCGO 能量模型所用的 88 个 Cr/Ga 占位构型。每行对应一个 64 原子参考晶胞，化学组成为 Sr₂Ga₂₄₋ₙCrₙO₃₈。每晶胞含 2、4、6、8、10 个 Cr 时，依次有 15、18、18、21、16 个构型。

同一占位构型的 FM 和 AFM 初始磁态计算成对筛选。两次计算均需收敛，且两者的每个最终 Cr 局域磁矩绝对值均需处于闭区间 2.9–3.1 μB。训练能量标签取两次 VASP `energy(sigma->0)` 的较小值，单位为每 64 原子晶胞的 eV。FM 和 AFM 表示初始磁态分支。最终磁矩保留正负号及各自归档输出中的 Cr 顺序。

最终训练集包含早期 109 对 DFT 候选经复筛后保留的 82 个构型，以及后续两批 18 个 DFT 候选中保留的 6 个构型。[筛选与来源说明](../../docs/zh/data_and_provenance.md)列出了各浓度的数量和 6 个补充构型的组号。

| 文件 | 内容 |
| --- | --- |
| [configurations.csv](configurations.csv) | 占据位点、各位点族计数、两种磁态的能量和磁矩、所选能量及结构文件路径。 |
| [configuration_provenance.csv](configuration_provenance.csv) | 来源批次、分组及两种磁态各自的归档运行目录，目录以原项目根目录为基准。 |
| [filtered88.npz](filtered88.npz) | 原始训练数组，保留原顺序，可用 NumPy 的 `allow_pickle=False` 读取。 |
| [mom51_counts.csv](mom51_counts.csv) | 88 × 51 路径计数矩阵，每行的计数之和为 228。 |
| [mom51_feature_catalog.csv](mom51_feature_catalog.csv) | 特征顺序、名称、两段参考金属–氧键长及各特征的训练集计数范围。键长以 Å 为单位。 |
| [site_mapping.csv](site_mapping.csv) | 母相 Ga 索引、参考原子编号、位点标签和位点族。 |
| [reference_Sr2Ga24O38.vasp](reference_Sr2Ga24O38.vasp) | 计算路径特征所用的固定母相结构。 |
| [structures/](structures/) | 各构型所选磁态的初始和弛豫后 VASP 文件。原子坐标保留归档顺序，统一了首行说明并省略速度记录。 |
| [SHA256SUMS.txt](SHA256SUMS.txt) | 数据和结构文件校验值。 |

## 列及数组说明

- `row_1based` 对应结构文件名前缀。`configuration_id` 与训练归档一致。`occupation_key` 由 Cr 数量和升序排列的母相 Ga 零基索引组成。
- 以 `_json` 结尾的列在 CSV 单元格中存储 JSON 数组。位点索引和标签逐项对应。
- `n_Cr_<family>` 为该位点族的 Cr 计数。五个位点族计数之和等于 `n_Cr`。
- 能量列给出两个磁态能量、带符号的 `E_FM - E_AFM` 及所选较小值。`_eV_per_cell` 后缀表示每 64 原子晶胞的 eV。
- NPZ 文件中的 `x` 为路径计数，`y` 为所选能量，`ns` 为 Cr 数量，`ids` 为构型编号，`groups` 为占位键，`names` 为有序特征名称。

本次发布涵盖筛选后的训练集，包括两种磁态的能量和磁矩，以及所选磁态的两份结构。176 个分支的归档输入均列有 `GGA=PE`、`METAGGA=R2SCAN` 和 `IVDW=11`。这些值记录的是输入标签，实际启用的设置以 VASP 运行输出为准。

原始训练压缩文件的 SHA-256 为 `46d9469faa1fe0b17bccf4a492efc96a3af930954a5b1336f4496ee158e6eda5`。
