# 数据说明与超算来源

[English](../en/data_and_provenance.md) · [首页](../../README.zh-CN.md)

## 1. 权威结构与来源标识

原始提供位置：

```text
C:/Users/yuany/Downloads/BaFeO (1).vasp
```

原样保存为 `data/bulk_input_original.vasp`，SHA-256 为：

```text
73bfd6939e1f1996e2938504004307aeb6ef55716ae53223f229fd8cc8c0305a
```

正式组成为 Sr₂Ga₂₄O₃₈。首行仍写 `Ba2 Fe24 O38`，是因为有意保留原文件字节内容。新 bulk 的晶格和全部 64 个原子坐标均在文件中。24 个 Ga 标签及新编号导出在 `results/zh/新bulk位点映射.csv`。

`data/undoped_reference_summary.json` 保存未掺杂支持性统计：Sr–O 2 类、18 条；Ga–O 11 类、134 条；Sr–O–Ga 4 类、54 条；Ga–O–Ga 12 类、174 条。它是基准记录，不能替代 75 个掺 Cr 构型结果。

## 2. 原计算在超算上的目录

继承的来源记录仅使用以下根目录内的 `Compare_Energy` 计算：

```text
/ix/gwang/yiy219/SrCrGaO/{N}/Compare_Energy/{group}/{spin}/
```

`N` 为 2、4、6、8、10，`spin` 为 FM 或 AFM。不同浓度的 group 命名不同，上述花括号是占位符，完整字符串见清单。

一个实际记录的所选目录为：

```text
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM
```

相应的常规文件路径为：

```text
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM/OUTCAR
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM/INCAR
/ix/gwang/yiy219/SrCrGaO/2/Compare_Energy/group10_2a_layer16__2b_layer12/AFM/POSCAR
```

**证据范围：**目录来自继承 CSV 的记录；三个文件路径是按常规文件名拼接的。本次整理没有连接超算，也没有确认文件目前是否存在。尚未提供主机名、SSH 别名、登录账号或凭据；不能仅根据路径中的用户目录名推断登录方式。

包内**不包含**超算原始 OUTCAR、INCAR、POSCAR。生成的本地 `POSCAR_bulk_doped` 使用新固定 bulk，不能将它们称为原超算结构的副本。

## 3. 包含哪些来源表？

| 文件 | 内容 |
|---|---|
| `provenance/hpc_selected_paths_en.csv` | 75 个所选构型的占位、记录目录、推导文件路径及对应新 bulk 结构 |
| `provenance/hpc_selected_paths_zh.csv` | 对应中文表 |
| `provenance/all_156_hpc_directories.csv` | 156 次候选 FM/AFM 目录及继承的有效性、选择标记 |
| `provenance/candidate_audit_en.csv` | 156 行磁态与收敛审核的英文表头副本 |
| `provenance/original_audit/selected_energy_and_sites.csv` | 原所选记录表，未经修改 |
| `provenance/original_audit/候选磁态审核.csv` | 原候选审核表，未经修改 |
| `provenance/original_audit/构型选择结果.csv` | 原 78 组选择记录，未经修改 |
| `provenance/source_locations.csv` | 原本地路径与包内对应位置 |
| `provenance/audit_reason_strings.json` | 原审核出现的排除原因字符串 |

保留能量与磁矩只是为了说明历史筛选和可追溯性。构造几何时，计数脚本不读取能量列，也不读取这些来源表。

## 4. 为什么是 75 个构型？

继承审核覆盖 78 组、156 次磁态计算。记录的筛选检查了 OUTCAR 是否完成、离子是否收敛、Cr 最终局域磁矩绝对值是否在 2.5–3.5 μB，以及 FM/AFM 的预期磁矩符号模式。每个保留组从有效分支中选择能量较低的一支。

`4Cr/group11`、`4Cr/group13`、`10Cr/group06` 三组因没有有效分支而排除。最终五个晶胞 Cr 数分别保留 13、17、15、16、14 个构型。

这是对继承审核的说明，不是本次重新审核原始电子结构输出。它解释占位表的来源，不影响距离计算。75 个结构是所选数据集，不是所有可能占位的完整枚举。

## 5. 输入与输出字段

### 占位输入

`nCr_cell` 为晶胞 Cr 整数数量；`group` 为来源标识；`Cr_sites` 为分号分隔的位点标签，可带 `Cr_` 前缀，标签必须能在新 bulk 中找到。

### 总体输出

| 中文文件名 | 含义 |
|---|---|
| `各浓度统计汇总.csv` | 各浓度数量、种类并集与单构型种类范围 |
| `逐构型统计汇总.csv` | 75 个构型分别统计的类别、家族数量与 Cr 占据的原 Ga 编号 |
| `跨浓度各类别计数.csv` | 24 类单键、51 类实际路径及按浓度累计的数量 |
| `全部构型单键明细.csv` | 11,400 条具体单键，含构型标识 |
| `全部构型M-O-M路径明细.csv` | 17,100 条具体共氧路径 |
| `新bulk位点映射.csv` | 新 Ga 编号、原始 POSCAR 全局编号及标签 |
| `summary.json` | 阈值、容差相关结果、输入哈希、总数验证及多镜像原子对 |

### 每个构型的输出

`results/zh/{N}Cr/{group}/` 下包含：

- `POSCAR_bulk_doped`：生成的固定 bulk 占位结构。
- `单键种类与数量.csv`：24 类共享类别，包含未出现的类别。
- `单键明细.csv`：实际键长、元素内编号、原 Ga 位点编号及镜像平移。
- `全部M-O-M组合_含零.csv`：全部 300 种理论组合。
- `实际M-O-M种类与数量.csv`：仅正计数组合。
- `M-O-M路径明细.csv`：实际两侧键长、角度、端点和氧编号。

英文镜像提供对应文件名和表头。[results/column_dictionary.csv](../../results/column_dictionary.csv) 列出全部结果字段的中英对应。数值和行顺序保持一致；CSV 使用 UTF-8 BOM，方便常见电子表格软件识别中文。

## 6. 原子编号与单位

- `新bulk_Ga编号`：**新原始 bulk** 中 Ga 的 1–24 编号，不是旧 bulk 编号。
- `POSCAR全局编号`：新原始 bulk 的 1–64 原子编号，其中 Ga 为 3–26。
- `元素内编号`：生成结构中该元素内部的编号；按元素分组后 Ga 与 Cr 分别重新编号。
- `O编号`：O 的 1–38 编号，氧顺序保持不变。
- `周期镜像`：寻找最短向量时，相对于该 O，施加在金属分数坐标上的整数平移。
- `_A`：距离单位 Å；`_度`：角度单位度。
- 数量是出现条数；明确写“种类数”“并集”的列才是不同类别数。

路径两端各自保留自己的元素和键长。不要混淆新 bulk 的 Ga 编号与生成结构中 Cr 的元素内编号。

## 7. 复现记录

`validation/verification.json` 记录表格、来源和中英一致性检查；`validation/reproduction_log.txt` 保存打包代码的运行日志；`validation/accepted_result_comparison.json` 记录与此前已确认计数结果的比较。

`SHA256SUMS.csv` 列出除清单自身以外的包内文件及校验值。它描述的是一个快照；在不同数值环境中重新生成后，格式或浮点末位可能变化，但几何结果仍可能等价。结构不变量与验证脚本是主要数值检查依据。

保留的本地和超算路径用于说明来源，不是跨电脑执行依赖。复现使用仓库内已有的相对路径文件即可。
