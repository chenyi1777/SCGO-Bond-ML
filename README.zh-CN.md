# SCGO DFT 构型数据集与 M–O–M 描述符

[English](README.md) | [简体中文](README.zh-CN.md)

本仓库提供训练 SCGO 能量模型所用的 **88 个通过筛选的 Cr/Ga 占位构型**。每个构型对应一个 64 原子的 Sr₂Ga₂₄₋ₙCrₙO₃₈ 晶胞，每晶胞含 2、4、6、8 或 10 个 Cr。

| 每晶胞 Cr 数 | 来自早期 DFT 归档 | 来自补充 DFT 批次 | 最终训练构型 |
| ---: | ---: | ---: | ---: |
| 2 | 15 | 0 | 15 |
| 4 | 14 | 4 | 18 |
| 6 | 16 | 2 | 18 |
| 8 | 21 | 0 | 21 |
| 10 | 16 | 0 | 16 |
| **合计** | **82** | **6** | **88** |

早期 DFT 归档中的 109 对候选已通过 2.8–3.2 μB 的初筛，按最终规则复筛后保留 82 个。后续两批补充计算的 18 个候选中又保留 6 个。同一占位构型的 **FM 和 AFM 两次计算都要收敛**，且两次计算中每个 Cr 的最终局域磁矩都须满足 **2.9 ≤ |mCr| ≤ 3.1 μB**。训练能量取两次 VASP `energy(sigma->0)` 中的较小值，单位为 eV/晶胞。详见[筛选过程与 DFT 来源](docs/zh/data_and_provenance.md)。

## 下载当前数据集

- [附录 F 数据字典](appendices/appendix-f/README.zh-CN.md)
- [包含 FM 和 AFM 两分支的构型表](appendices/appendix-f/configurations.csv)
- [逐构型 DFT 来源表](appendices/appendix-f/configuration_provenance.csv)
- [原始训练数组](appendices/appendix-f/filtered88.npz)及 [MOM51 计数](appendices/appendix-f/mom51_counts.csv)
- [固定母相结构](appendices/appendix-f/reference_Sr2Ga24O38.vasp)及[所选磁态分支的初始和弛豫后结构](appendices/appendix-f/structures/)

MOM51 以固定的 Sr₂Ga₂₄O₃₈ 母相结构为基准，按各构型的占位重新标记 Cr 和 Ga。每个构型有 228 条以氧为中心的 M–O–M 路径，按 51 类特征计数。DFT 能量标签和弛豫结构来自各自的电子结构计算。

## 验证数据集

```bash
python -m pip install -r requirements.txt
python scripts/verify_training_dataset.py
```

脚本验证文件校验值、占位和来源对应关系、两分支的归档磁矩及所选能量，并从固定母相结构重新计算全部 88 × 51 个路径计数。

## 历史 75 构型示例

原有 75 构型的键长统计教程与结果以历史示例保留。其输入输出位于 `data/`、`results/`、`provenance/` 和 `validation/`。根目录的 `SHA256SUMS.csv` 对应早期打包快照。详见[历史流程](docs/zh/workflow.md)、[历史教程](docs/zh/tutorial.md)和[历史数据说明](docs/zh/legacy_data_and_provenance.md)。
