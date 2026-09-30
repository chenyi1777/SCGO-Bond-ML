# 一种适用于金属氧化物的键长和构型的统计方法

[English](README.md) | [简体中文](README.zh-CN.md)

示例体系为 **Sr₂Ga₂₄O₃₈**，在 64 原子晶胞内按给定的 75 个构型，将 2、4、6、8、10 个 Ga 位点分别替换为 Cr。

**本次提供的新 bulk 是晶格和坐标的唯一来源。**历史超算计算只提供占位标签和来源记录，其弛豫坐标不参与此次几何统计。本项目只整理数键及数路径的流程，不包含训练模型或预测结果。

## 推荐阅读顺序

1. [流程与思路](docs/zh/workflow.md)：研究问题、决策过程、公式和计数口径。
2. [动手复现教程](docs/zh/tutorial.md)：环境、运行命令及一个具体构型的阅读方法。
3. [数据、字段与超算来源](docs/zh/data_and_provenance.md)：文件用途、原子编号和历史超算路径。
4. [English documentation](README.md)。

## 主要结果

| 晶胞内 Cr 数 | 构型数 | 单键种类并集 | 实际 M–O–M 种类并集 |
|---:|---:|---:|---:|
| 2 | 13 | 24 | 43 |
| 4 | 17 | 24 | 48 |
| 6 | 15 | 24 | 48 |
| 8 | 16 | 24 | 50 |
| 10 | 14 | 24 | 49 |
| **总体去重** | **75** | **24** | **51** |

在本项目约定下，每个构型有 **152 条单键、228 条 M–O–M 路径**。种类并集是多个构型中出现类别的去重集合，不表示每个构型都有这么多类。

24 类单键包括 Sr–O 2 类、Ga–O 11 类、Cr–O 11 类。24 类单键共有 300 种理论无序搭配，其中包含数量为零的组合。在 0.01° 容差下，没有额外角度子类。

## 快速复现

已在 Python 3.12、NumPy 2.3.5 上运行验证。安装 NumPy 后，无需 VASP、超算账号或网络连接。

```bash
python -m pip install -r requirements.txt
python scripts/run_workflow.py
python scripts/verify_results.py
```

默认命令更新 `results/zh/` 与 `results/en/`。如果想保留打包时的结果不变，使用另一个输出目录：

```bash
python scripts/run_workflow.py --output .reproduction
python scripts/verify_results.py --results .reproduction
```

## 阅读结果前需要知道

- 原文件名是 `BaFeO (1).vasp`，首行标题为 `Ba2 Fe24 O38`，但正式元素行是 `Sr Ga O`。**用户明确确认使用 Sr/Ga/O。**[data/bulk_input_original.vasp](data/bulk_input_original.vasp) 保存的是未经修改的原文件。这是由于Jiamao所建立的原文档是以BaFe12O19为对象研究，以此为POSCAR。
- 所有距离、成键阈值和类别边界均由新 bulk 重新计算，没有沿用旧 bulk 的阈值或类别。但是整体思路一致。
- 目前按**每个晶胞内金属/O 编号对只保留一个最短周期镜像**计数。存在 6 组 Sr/O 编号对，其多个镜像都在成键范围内，因此当前数量不等同于完整周期邻居配位数。详见[周期性约定与限制](docs/zh/workflow.md#5-周期距离约定)。
- 这里的类别是明确规则下的几何分类，不等同于已经独立证明的化学键或交换常数。

## 目录结构

```text
data/          新 bulk 原文件、占位表、输入哈希、未掺杂结构摘要
scripts/       计数、英文导出、复现和验证代码
results/en/    英文表头结果与 75 个生成的 POSCAR
results/zh/    对应中文表头结果及相同的 75 个 POSCAR
provenance/    超算目录、来源位置与继承的审核记录
docs/en/       英文流程、教程和数据说明
docs/zh/       与英文对应的中文文档
validation/   复现与验证记录
SHA256SUMS.csv 压缩包快照的文件清单和校验值
```

常用文件：[逐构型统计汇总](results/zh/逐构型统计汇总.csv)、[跨浓度各类别计数](results/zh/跨浓度各类别计数.csv)、[75 个所选超算来源目录](provenance/hpc_selected_paths_zh.csv)。

这是可供检查后上传的项目快照，不包含 `.git` 目录，也没有向任何远程账号发布内容。
