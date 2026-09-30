# 动手复现教程

[English](../en/tutorial.md) · [首页](../../README.zh-CN.md)

## 1. 运行前先看输入

打开[新 bulk 原文件](../../data/bulk_input_original.vasp)。缩放因子为 1.0，正式元素行为 `Sr Ga O`，数量行为 `2 24 38`，坐标类型为 `Cartesian`。之后有 64 行原子坐标，其中 24 行 Ga 坐标末尾带有位点标签。

第一行只是描述性标题，不是正式元素定义。其 Ba/Fe 字样已经过确认，实际按 Sr/Ga/O 处理。不要仅凭文件名悄悄推断元素。

再打开 [configuration_sites.csv](../../data/configuration_sites.csv)。每行表示一个给定占位，字段是 `nCr_cell`、`group`、`Cr_sites`。`group` 用来标识原计算，不能直接决定坐标。

## 2. 准备简单的 Python 环境

建议使用与本次验证相同的 Python 3.12，仅需 NumPy。

Linux/macOS：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell 可以直接调用虚拟环境解释器，不必先激活：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_workflow.py --output .reproduction
.\.venv\Scripts\python.exe scripts/verify_results.py --results .reproduction
```

Linux/macOS 或已激活的环境：

```bash
python scripts/run_workflow.py --output .reproduction
python scripts/verify_results.py --results .reproduction
```

从仓库根目录执行。路径含空格时加引号。脚本根据自身位置确定默认输入目录，因此复现不依赖作者电脑上的绝对路径。

## 3. 了解程序依次做什么

`run_workflow.py` 先调用 `count_doped.py`，再调用 `export_english.py`。

计数程序依次：

1. 读取新 bulk，建立 Ga 位点标签映射。
2. 重新计算最短金属–氧距离和成键阈值。
3. 建立统一的 Sr–O/Ga–O/Cr–O 类别。
4. 应用每个占位并输出 POSCAR。
5. 验证几何，并从生成结构独立重算成键。
6. 枚举路径、建立统一路径类别、输出表格。

英文导出器只转换文件名和表头，保持行顺序及数值字符串。中英文结构文件的字节内容完全相同。`verify_results.py` 检查两套语言结果的数值对应。

检查试运行后，如需更新仓库内正式结果，去掉 `--output .reproduction`。程序更新所选输出位置中的文件，不删除其他结果目录。

## 4. 跟着一个具体构型阅读

以 `2Cr/group10_2a_layer16__2b_layer12` 为例：

- 替换新 bulk 中 Ga 编号 10 和 14。
- 生成组成为 Sr₂Ga₂₂Cr₂O₃₈。
- [POSCAR](../../results/zh/2Cr/group10_2a_layer16__2b_layer12/POSCAR_bulk_doped) 保持新 bulk 的位点位置，只按元素重新分组。
- [单键类别表](../../results/zh/2Cr/group10_2a_layer16__2b_layer12/单键种类与数量.csv) 列出统一的 24 类，包括该构型中未出现的类别。
- [实际路径类别表](../../results/zh/2Cr/group10_2a_layer16__2b_layer12/实际M-O-M种类与数量.csv) 已排除零计数组合。

下面的 Python 示例使用英文镜像表，便于直接复制运行。从仓库根目录执行：

```python
import csv
from pathlib import Path

case = Path('results/en/2Cr/group10_2a_layer16__2b_layer12')
def rows(name):
    with (case / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))

bonds = rows('bond_types_and_counts.csv')
paths = rows('observed_MOM_types_and_counts.csv')
print(sum(int(r['count']) for r in bonds))  # 152 条单键
print(sum(int(r['count']) for r in paths))  # 228 条路径
for r in paths[:3]:
    print(r['path_family'], r['left_representative_distance_A'],
          r['right_representative_distance_A'], r['count'])
```

若要读取刚刚试运行的结果，将路径前缀换成 `.reproduction/en/...`。

## 5. 分清代表长度与逐条实际长度

`单键种类与数量.csv` 给出统一类别的代表平均长度与分类区间；`单键明细.csv` 给出每个具体原子对的实际长度。

同样，`实际M-O-M种类与数量.csv` 给出两侧代表长度及平均角度；`M-O-M路径明细.csv` 给出每条路径的真实两侧长度和角度。距离单位均为 Å，角度单位均为度。

不要将类别边界当作实际观测键长，也不要先将距离四舍五入后再分类。电子表格显示的小数位可能少于 CSV 实际保存的位数。

## 6. 不要只看一个总数

完成验证后，应得到 75 个构型、11,400 条单键、17,100 条路径，并通过中英文一致性检查。需要同时看“种类数”和“条数”：某个类别可以消失，但单键总数仍保持不变。

复现失败时，先检查 bulk 哈希、正式元素、坐标模式、位点标签唯一性，以及是否去掉 `Cr_` 前缀。类别数变化可能来自容差或参考几何变化，不一定是少了原子。

## 7. 如何学习并迁移流程

底层解析器支持正的 POSCAR 缩放因子、Direct/Cartesian 坐标，以及 Selective Dynamics 标记。本输入使用正的单一缩放因子。它不是所有 POSCAR 变体的完整实现，例如负值体积缩放会被拒绝。

本参考晶胞流程有意检查 24 个带标签 Ga 位点、75 个构型，以及该数据集已验证的单键和路径总数。换体系时，应明确检查这些假设。如果改变阈值或镜像口径，需要记录变化并重建所有类别，不能把新旧类别编号直接当作同一含义。

将参考几何、占位列表、脚本版本、容差和输入哈希一起保存，才能让数键结果可复现。
