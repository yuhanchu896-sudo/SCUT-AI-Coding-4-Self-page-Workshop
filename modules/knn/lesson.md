# 模块二：用 KNN 给水果分类

**30 分钟｜零基础｜AI Coding × 数据实践**

今天交付一个模型：输入重量、直径，输出苹果 / 橙子 / 梨，并解释它参考了哪些邻居。

路径：**规划 → 收集 → 清洗 → 划分 → 建模 → 检查 → 迭代**。AI 帮你写程序，你负责判断数据与结果。

从项目根目录启动 Jupyter，使用 Python 3.10+。按顺序选中单元格，按 **Shift + Enter**。请保留完整项目文件夹，本课需要 `modules/knn/`。无需额外安装机器学习库，也不需要 API Key。

## 0–3 分钟：先定义问题

一行代表**一颗独立水果**。`weight_g`、`diameter_cm` 是特征（输入），`label` 是标签（正确答案），`fruit_id` 只是追踪编号，不参与预测。

KNN 的做法：把新水果和训练样本比较，找距离最近的 K 个邻居，再按票数判断类别。K 是邻居数，不是类别数。训练主要保存样本和缩放参数，预测时才计算距离。

三分类时，即使 K 是奇数也可能平票。本课票数并列时先比较该类别邻居的总距离，再按标签字母顺序决定；距离完全相同的邻居按编号排序，以保证复现。

先猜猜：165 g、6.8 cm 的水果可能是什么？只凭这两个数字不一定分得清，这正是需要验证的原因。

```python
from pathlib import Path
from collections import Counter
from html import escape
from IPython.display import HTML, display
from modules.knn.data import LABELS, read_csv, clean_rows, stratified_split
from modules.knn.model import KNNClassifier, select_k, evaluate, majority_baseline

DATA = Path("modules/knn/data/fruits_raw.csv")
names = {"apple": "苹果", "orange": "橙子", "pear": "梨"}
print("环境就绪。当前目录：", Path.cwd())
print("课堂数据存在：", DATA.exists())
```

## 3–8 分钟：规划与采集

真实采集使用 `modules/knn/data/collection_template.csv`，另存一个副本填写。每类目标至少 20 颗不同水果，覆盖不同大小与批次；课前采集，课堂用模拟数据也能完成。

| 字段 | 怎么记录 | 例子 |
|---|---|---|
| fruit_id | 唯一编号，同一颗复测沿用编号 | G1-001 |
| weight_g | 秤归零后的重量，单位 g | 180 |
| diameter_cm | 最宽横截面的直径，单位 cm；不是周长或高度 | 7.2 |
| label | 实物核对后填 apple / orange / pear | apple |

另记日期、器具、商店/批次和标签核对人。只测同一箱水果会限制代表性；同一颗称十次，不能当十颗。

完成真实采集后，将上方 `DATA` 改为你另存的 CSV 路径，再从头运行。只填表头的空模板不能训练；每类至少需要 5 条合格记录。本轮先使用模拟数据。

**Prompt 01 · 复制给 AI（不是运行代码）**

> 我要用重量和直径区分苹果、橙子、梨。请设计零基础小组能执行的采集方案，包含每行含义、编号、单位、测量方法、标签核对、样本覆盖和重复采集的处理。CSV 列名为 fruit_id,weight_g,diameter_cm,label。先列出方案，不急着写代码。指出方案的代表性限制。

验收 AI：是否把标签或编号当成了特征？是否明确直径的测法？

```python
raw = read_csv(DATA)
print("原始记录数：", len(raw))
print("注意：这是教学模拟数据，包含故意加入的问题记录。")
for record in raw[:3] + raw[-10:]:
    print("CSV 行", record.line, record.values)
```

## 8–14 分钟：清洗要留下理由

先观察最后几行。找出缺失、非有限数、错单位、错误标签与重复编号。

本练习预先限定重量 **50–500 g**、直径 **3–15 cm**。超范围先隔离、回查，不代表世界上不存在这样的水果。明确标注 kg / mm 才换算；未知单位不能猜。标签去首尾空格并统一小写。缺失值不擅自填，冲突编号全部隔离，一致重复保留一份。原始 CSV 不改写。

**Prompt 02**

> 阅读原始 CSV 和 modules/knn/data.py。请列出数据问题、原行号、原因和处理动作。仅按本课预定规则清洗，保留原始文件，不根据准确率删样本，不猜缺失的标签。解释实际审计中的一条修正和一条隔离。

```python
cleaned = clean_rows(raw)
print(f"原始 {len(raw)} 条 → 保留 {len(cleaned.rows)} 颗 → 减少 {len(raw)-len(cleaned.rows)} 条")
print("类别数量：", Counter(row.label for row in cleaned.rows))
print("审计事件数：", len(cleaned.audit), "（一行可能对应多个事件）")
for event in cleaned.audit:
    print(f"第 {event.line} 行 | {event.fruit_id} | {event.code} | {event.message}")
```

**暂停回答**：哪一行被换算？哪一行应回查？为什么不能把模型猜的类别当作新标签？

## 14–19 分钟：数据各司其职

训练集约 60%：提供邻居并计算标准化参数；验证集约 20%：选 K；测试集约 20%：最终考试。每个类别分别划分，四舍五入/整数分配会影响实际比例。

先按实体去重，再划分。固定随机种子 42，是为了复现，不是为了反复挑选高分。每类至少 5 个干净样本才能运行本示例；实际采集应该更多。来自同一批次的真实样本可能相互关联，跨店泛化要按商店或批次整体留出测试数据。

```python
split = stratified_split(cleaned.rows, seed=42)
for title, rows in [("训练", split.train), ("验证", split.validation), ("测试", split.test)]:
    print(title, len(rows), dict(Counter(row.label for row in rows)))
train_ids = {row.fruit_id for row in split.train}
validation_ids = {row.fruit_id for row in split.validation}
test_ids = {row.fruit_id for row in split.test}
assert not (train_ids & validation_ids or train_ids & test_ids or validation_ids & test_ids)
print("检查通过：同一颗水果没有跨集合。")
```

重量相差 30 g，直径相差 0.5 cm：若直接计算距离，数值跨度大的特征可能占主导。

**标准化值 =（原值 − 训练集均值）÷ 训练集标准差**。

这把尺子只用训练数据制作。验证、测试、新水果沿用同一把尺子。零方差特征的缩放因子设为 1。预先固定的格式修正、单位换算可以在划分前做；从数据估计的填补值或缩放参数不能提前使用验证/测试数据。

```python
demo_model = KNNClassifier.fit(split.train, k=3)
print("训练集均值（g, cm）：", demo_model.scaler.mean)
print("缩放因子：", demo_model.scaler.scale)
print("165 g、6.8 cm 标准化后：", demo_model.scaler.transform(165, 6.8))
```

## 19–25 分钟：选择 K，然后做一次最终评估

**Prompt 03**

> 阅读 modules/knn/model.py，解释 KNN 的输入、距离与投票。检查缩放参数是否仅来自训练集。在验证集比较 K=1、3、5，并列选较小 K。确定方案后，才报告测试集准确率、混淆矩阵和多数类基线。不要使用编号或标签作为输入特征。

```python
selection = select_k(split.train, split.validation, candidates=(1, 3, 5))
for score in selection.scores:
    print(f"K={score.k}，验证准确率={score.accuracy:.1%}")
print("验证集选出 K =", selection.k)
classifier = KNNClassifier.fit(split.train, k=selection.k)
```

下一格是最终考试。流程和 K 确定后再运行。重复运行原封不动的实验可以复现；根据测试结果改参数后，就不能再称原测试集为独立最终考试，应准备新的留出数据。

```python
result = evaluate(classifier, split.test)
correct = sum(row.label == prediction for row, prediction in zip(split.test, result.predictions))
print(f"测试：{correct}/{len(split.test)} 颗正确，准确率 {result.accuracy:.1%}")
print(f"始终猜训练集最多类别的基线：{majority_baseline(split.train, split.test):.1%}")
print("混淆矩阵：行=真实类别，列=预测类别")
print("       ", "  ".join(names[label] for label in result.labels))
for label, counts in zip(result.labels, result.confusion):
    print(names[label], "  ", "     ".join(str(count) for count in counts))
```

**检查**：比基线好吗？哪里出错最多？测试样本有多少？这是模拟数据上的结果，不能证明真实识别能力。

修改下方两个数字，看模型参考了哪些邻居。预测输入应是这三类水果、符合本练习范围；香蕉也可能被硬猜成三类之一。票数占比不是经过校准的概率。

```python
new_weight_g = 165.0
new_diameter_cm = 6.8
prediction = classifier.predict(new_weight_g, new_diameter_cm)
neighbors = classifier.neighbors(new_weight_g, new_diameter_cm)
print("预测：", names[prediction])
for neighbor in neighbors:
    print(neighbor.fruit_id, names[neighbor.label], f"标准化距离={neighbor.distance:.3f}")
```

图中只画**训练样本**，黑色十字是新水果，黑圈是被选中的邻居。横纵轴是原始测量值，便于理解；模型算的是**标准化距离**，不能直接按屏幕上的像素距离判断邻居。

```python
colors = {"apple": "#c94b36", "orange": "#a56800", "pear": "#24744e"}
neighbor_ids = {neighbor.fruit_id for neighbor in neighbors}
points = list(split.train)
x_min = min([row.weight_g for row in points] + [new_weight_g]) - 15
x_max = max([row.weight_g for row in points] + [new_weight_g]) + 15
y_min = min([row.diameter_cm for row in points] + [new_diameter_cm]) - 0.5
y_max = max([row.diameter_cm for row in points] + [new_diameter_cm]) + 0.5
svg = ['<svg viewBox="0 0 720 400" role="img" aria-label="训练水果与新水果的散点图" style="max-width:800px;background:#fff;border:1px solid #ddd">', '<path d="M60 25V340H690" fill="none" stroke="#555"/>']
for row in points:
    x = 60 + (row.weight_g-x_min)/(x_max-x_min)*610
    y = 340 - (row.diameter_cm-y_min)/(y_max-y_min)*290
    outline = "#111" if row.fruit_id in neighbor_ids else "white"
    svg.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{colors[row.label]}" stroke="{outline}" stroke-width="2"><title>{escape(row.fruit_id)} {names[row.label]} {row.weight_g}g {row.diameter_cm}cm</title></circle>')
x = 60 + (new_weight_g-x_min)/(x_max-x_min)*610
y = 340 - (new_diameter_cm-y_min)/(y_max-y_min)*290
svg.append(f'<path d="M{x-9} {y}h18 M{x} {y-9}v18" stroke="#111" stroke-width="3"/>')
svg.append(f'<text x="70" y="365" font-size="14">{x_min:.0f} g</text><text x="605" y="365" font-size="14">{x_max:.0f} g</text><text x="10" y="330" font-size="12">{y_min:.1f}</text><text x="10" y="50" font-size="12">{y_max:.1f}</text>')
svg.append('<text x="290" y="388" font-size="16">重量（g）</text><text x="12" y="18" font-size="14">直径（cm）</text></svg>')
display(HTML("".join(svg)))
print("图例：红=苹果，棕黄=橙子，绿=梨；黑圈=邻居，黑十字=新水果。悬停看样本。")
```

## 25–30 分钟：让 AI 修改一处，自己验证

选择一种挑战：

1. **入门**：请 AI 将清洗统计和分类报告中的英文标签显示成中文，内部 label 保持不变。运行前后核对保留数量、K、预测和准确率是否一致。
2. **进阶**：在训练/验证集比较更多合法 K，并解释变化。不要使用测试集挑参数，也不要把已经看过的测试集继续当作新方案的独立最终成绩。

**Prompt 04**

> 请在现有代码基础上完成【我的修改】，保留采集、清洗和数据划分规则。先解释会改哪里，再给出替换代码。给出验证方法，我会实际运行检查；报错时根据完整报错修复，不跳过检查。

遇到报错：复制代码、完整报错、实际结果、预期结果给 AI。修改后重新运行相关单元。若变量未定义，从最上面的导入开始顺序运行；若找不到 modules，回到项目根目录启动 Jupyter；若 CSV 表头错误，对照采集模板。

## 交付：数据决策比高分更重要

- 目标、特征、标签与每行含义。
- 两条清洗记录及理由；三份数据规模。
- 验证集选择的 K、最终测试正确数/总数、准确率与基线。
- 一个新水果的邻居解释及一个使用限制。
- 一次 AI 修改的提示词和验证证据。

[完整采集指南与教师参考](modules/knn/README.md) · [教师讲稿](KNN_Workshop_Teacher.html) · [返回个人主页 Notebook](AI_Coding_Workshop_Student.ipynb)

概念参考：[最近邻方法](https://scikit-learn.org/stable/modules/neighbors.html)、[数据泄漏](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)。课堂代码使用标准库，后续可迁移到 scikit-learn。
