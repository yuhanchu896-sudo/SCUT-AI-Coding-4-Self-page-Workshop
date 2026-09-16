# -*- coding: utf-8 -*-
"""Generate the student Jupyter notebook for the AI Coding Workshop."""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent


STUDENT_HELPER = '''from pathlib import Path
from IPython.display import HTML, display
import html as html_lib
import shutil
import warnings


def preview(path="index.html", height=600):
    file_path = Path(path)
    if not file_path.exists():
        print(f"找不到文件：{path}")
        print("请先运行上面的 %%writefile Cell。")
        return
    raw = file_path.read_text(encoding="utf-8")
    escaped = html_lib.escape(raw, quote=True)
    iframe = (
        '<iframe srcdoc="' + escaped + '" '
        f'style="width:100%; height:{height}px; border:1px solid #d0d0d0; '
        'border-radius:8px; background:#ffffff;"></iframe>'
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        display(HTML(iframe))


def save_version(tag):
    versions = Path("versions")
    versions.mkdir(exist_ok=True)
    dest = versions / f"{tag}.html"
    src = Path("index.html")
    if not src.exists():
        print("找不到 index.html，无法保存版本。")
        return
    shutil.copy(src, dest)
    print(f"已保存 {dest.as_posix()}")


preview("index.html", height=400)
'''


TEACHER_HELPER = '''from pathlib import Path
from IPython.display import HTML, display
import html as html_lib
import shutil
import warnings


def preview(path="index.html", height=600):
    file_path = Path(path)
    if not file_path.exists():
        print(f"找不到文件：{path}")
        print("请先运行上面的 %%writefile Cell。")
        return
    raw = file_path.read_text(encoding="utf-8")
    escaped = html_lib.escape(raw, quote=True)
    iframe = (
        '<iframe srcdoc="' + escaped + '" '
        f'style="width:100%; height:{height}px; border:1px solid #d0d0d0; '
        'border-radius:8px; background:#ffffff;"></iframe>'
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)
        display(HTML(iframe))


def save_version(tag):
    versions = Path("versions")
    versions.mkdir(exist_ok=True)
    dest = versions / f"{tag}.html"
    src = Path("index.html")
    if not src.exists():
        print("找不到 index.html，无法保存版本。")
        return
    shutil.copy(src, dest)
    print(f"已保存 {dest.as_posix()}")


def restore(tag, height=650):
    src = Path("assets/backup") / f"{tag}.html"
    if not src.exists():
        print(f"找不到备用文件：{src.as_posix()}")
        print("可用标签：demo / v0 / v1 / v2 / final")
        return
    Path("index.html").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"已恢复 {src.as_posix()} → index.html")
    preview("index.html", height=height)
'''


HELLO_HTML = '''%%writefile index.html

<!DOCTYPE html>

<html>

<head>
    <meta charset="UTF-8">
    <title>My First Website</title>
</head>

<body>

    <h1>Hello!</h1>

    <p>This is my first website.</p>

</body>

</html>
'''


DEBUG_HTML = '''%%writefile debug_demo.html

<!DOCTYPE html>

<html>

<head>
    <meta charset="UTF-8">

    <style>

        body {
            font-family: Arial;
            padding: 50px;
        }

        .dark {
            background: #111;
            color: white;
        }

    </style>

</head>

<body>

    <h1>Theme Demo</h1>

    <button onclick="toggleTheme()">
        Switch Theme
    </button>

    <script>

        function switchTheme() {
            document.body.classList.toggle("dark");
        }

    </script>

</body>

</html>
'''


STEPS = ["Run", "Generate", "Iterate", "Design", "Interaction", "Debug", "Create"]


def progress(part_num: int, active_idx: int) -> str:
    bits = []
    for i, name in enumerate(STEPS):
        if active_idx >= len(STEPS) or i < active_idx:
            bits.append(f"✅ {name}")
        elif i == active_idx:
            bits.append(f"➡️ {name}")
        else:
            bits.append(f"⬜ {name}")
    return f"**Progress  Part {part_num} / 8**\n\n" + "  ".join(bits)


def md(text: str):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text: str):
    cell = nbf.v4.new_code_cell(text.strip("\n") + "\n")
    cell["outputs"] = []
    cell["execution_count"] = None
    return cell


def writefile_cell(filename: str = "index.html"):
    cell = nbf.v4.new_code_cell(f"%%writefile {filename}\n")
    cell["outputs"] = []
    cell["execution_count"] = None
    return cell


def new_notebook(cells):
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }
    return nb


def student_cells():
    return [
        md("""\
# AI Coding 入门 Workshop

## 45 分钟做出你的第一个个人主页

今天你不需要系统学习：

- HTML
- CSS
- JavaScript
- Web 开发

今天需要学习的是：

# 如何和 AI 一起做软件
"""),
        md("""\
## 今天的挑战

45 分钟之后，每个人都需要拥有一个：

# 属于自己的个人主页

它至少应该包含：

- 你的名字
- About Me
- Interests / Skills
- Projects
- Contact
- 至少一个可以点击的交互功能

并且：

> 每个人最终的网页应该是不一样的。
"""),
        md(f"""\
# Part 1：让第一个网页跑起来

{progress(1, 0)}

今天唯一必须记住的 Jupyter 操作：

## Shift + Enter

运行当前 Cell。
"""),
        code('print("Hello AI Coding!")'),
        md("""\
接下来我们不写 Python。

我们要直接创建一个真正的网页。

下面的：

`%%writefile index.html`

意思是：

> 把这个 Cell 中的内容保存成 index.html
"""),
        code(HELLO_HTML),
        code(STUDENT_HELPER),
        md("""\
# 你已经运行了一个真正的网页。

注意：

今天我们并不需要知道：

- `<h1>` 是什么
- `<p>` 是什么
- HTML 为什么这样写

接下来：

# 让 AI 来帮我们写。
"""),
        md(f"""\
# Part 2：告诉 AI 你是谁

{progress(2, 1)}

首先填写下面的信息。

不想公开的信息可以虚构。

姓名：

身份：

一句话介绍：

我的三个兴趣：

1.
2.
3.

我想展示的一个项目 / 经历：

联系方式：
"""),
        md("""\
# Prompt 01

把下面内容复制给 AI：

---

请帮我制作一个个人主页。

我的信息：

姓名：【填写】

身份：【填写】

一句话介绍：【填写】

兴趣：

- 【填写】
- 【填写】
- 【填写】

我的项目 / 经历：

【填写】

联系方式：

【填写】

要求：

1. 使用 HTML、CSS 和 JavaScript。
2. 所有内容必须放在一个 index.html 文件中。
3. 不使用任何第三方框架。
4. 页面包含：
   - Hero
   - About Me
   - Interests
   - Projects
   - Contact
5. 页面需要适配电脑和手机。
6. 现在先做一个简单但可以正常使用的版本。
7. 请直接输出完整 index.html 代码。

---

**非常重要：**

AI 返回代码以后，只复制 **代码本身**。

不要复制开头的 `` ```html ``，也不要复制结尾单独一行的 `` ``` ``。

把完整 HTML 粘贴到下一格 `%%writefile index.html` 的下面，然后 Shift + Enter。
"""),
        writefile_cell("index.html"),
        code("""\
preview("index.html", height=650)
save_version("v0")
"""),
        md(f"""\
# Part 3：第一次迭代

{progress(3, 2)}

现在观察你的网页。

问自己：

1. 页面有没有介绍清楚“我是谁”？
2. Projects 是否足够清楚？
3. 页面结构是否合理？
4. 有没有缺少你想展示的信息？

不要直接修改代码。

# 告诉 AI 你想改什么。
"""),
        md("""\
# Prompt 02：修改已有程序

把你当前完整的 index.html 代码发送给 AI，然后说：

---

这是我现在的个人主页代码。

请不要重新设计整个网站。

请在现有代码基础上修改。

我希望：

1. Hero 区域更加突出我的名字和身份。
2. About Me 增加一段个人介绍。
3. Projects 使用卡片展示。
4. 每个 Project 包含：
   - 项目名称
   - 简短介绍
   - 使用的技术 / 关键词
5. 增加 Contact 区域。
6. 保留已有内容和已有功能。
7. 仍然只使用一个 index.html。
8. 不引入任何第三方库。

请输出修改后的完整 index.html。

---

今天要记住的原则：

> **不要永远说“重新帮我写一个”。**

而应该说：

> **“在现有代码基础上修改，并保留已有功能。”**
"""),
        writefile_cell("index.html"),
        code("""\
preview("index.html", height=650)
save_version("v1")
"""),
        md(f"""\
# Part 4：它现在好看吗？

{progress(4, 3)}

假设你对 AI 说：

> 帮我改得好看一点。

AI 可以修改。

但是：

# “好看”到底是什么意思？

## Prompt A

```text
帮我改得好看一些。
```

## Prompt B

```text
请把页面重新设计为：

- 简洁现代
- 大面积留白
- Hero 区域占首屏主要位置
- 标题层级明显
- Project 使用圆角卡片
- 卡片具有轻微 Hover 动画
- 页面整体使用统一的圆角和间距
- 不使用复杂动画
- 保持专业学生个人主页风格
```

问自己：

> 哪个 Prompt 更容易得到你真正想要的结果？
"""),
        md("""\
# 选择你的主页风格

## A — Minimal

简洁、留白、专业。

## B — Dark Tech

深色背景、科技感、强调项目。

## C — Colorful

更加年轻、丰富、活泼。

## D — Academic

偏学术主页，突出经历与项目。

也可以完全自己描述。

---

# Prompt 03

这是我当前的完整 index.html：

【代码】

请保留所有内容和功能，只修改视觉设计。

我希望整体风格是：

【描述你的风格】

具体要求：

- 页面层次清楚
- Hero 更突出
- Projects 使用卡片布局
- 卡片增加轻微 Hover 效果
- 保证文字容易阅读
- 手机端可以正常显示
- 不引入任何第三方库
- 不删除已有内容

请输出完整修改后的 index.html。
"""),
        writefile_cell("index.html"),
        code("""\
preview("index.html", height=650)
save_version("v2")
"""),
        md(f"""\
# Part 5：让网页真正“动起来”

{progress(5, 4)}

现在我们的网页主要是静态内容。

接下来加入一个：

# Dark / Light Theme Toggle

点击按钮：

Light → Dark

再次点击：

Dark → Light

运行下一格之后，请 **真的点一下按钮**。
"""),
        md("""\
# Prompt 04

这是我当前的个人主页代码：

【完整代码】

请在现有网页基础上增加：

“深色 / 浅色模式切换”

要求：

1. 页面右上角增加一个主题切换按钮。
2. 点击以后可以在 Light Mode 和 Dark Mode 之间切换。
3. 使用原生 JavaScript。
4. 使用 CSS Variables 管理主题颜色。
5. 不使用任何第三方库。
6. 不删除已有内容。
7. 不改变我的页面结构。
8. 保证手机端正常显示。

请输出完整的 index.html。
"""),
        writefile_cell("index.html"),
        code("""\
preview("index.html", height=650)
print("请点击页面右上角的主题按钮，确认 Light / Dark 真的会切换。")
"""),
        md(f"""\
# Part 6：AI 写的代码一定正确吗？

{progress(6, 5)}

答案：

# 不一定。

现在我们故意制造一个 Bug。

这一页是独立的调试练习，**不会覆盖你自己的个人主页**。
"""),
        code(DEBUG_HTML),
        code("""\
preview("debug_demo.html", height=350)
print("点击 Switch Theme。如果没有反应，这就是我们要修的 Bug。")
"""),
        md("""\
# 不要直接问：

“为什么不行？”

给 AI 足够的信息。

建议发送：

1. 完整代码
2. 发生了什么
3. 你预期发生什么
4. 如果有报错，也一起提供

模拟报错：

```text
Uncaught ReferenceError:
toggleTheme is not defined
```

# Debug Prompt

下面的网页存在一个 Bug。

现象：

点击 “Switch Theme” 按钮以后没有任何反应。

浏览器报错：

Uncaught ReferenceError:
toggleTheme is not defined

下面是完整代码：

【代码】

请：

1. 解释 Bug 的原因；
2. 指出具体哪里有问题；
3. 给出修改后的代码；
4. 不改变其他功能。

请先解释，再给代码。

---

# Debug 的基本流程

Bug

↓

描述现象

↓

提供代码

↓

提供报错

↓

AI 分析

↓

AI 修改

↓

重新运行

↓

自己验证

> **AI 说“已经修复”没有意义。**
>
> **只有重新运行并验证以后才算修复。**
"""),
        md(f"""\
# Part 7：现在你是产品经理

{progress(7, 6)}

接下来老师不再告诉你应该加什么功能。

你需要回答：

# “我希望我的主页还可以做什么？”
"""),
        md("""\
# Feature Challenge

## Level 1

- 返回顶部按钮
- 当前时间
- 点击头像显示一句话
- Project 卡片 Hover 动画
- 导航栏平滑滚动

## Level 2

- Skills 进度条
- 打字机效果
- Project 分类筛选
- 页面滚动时导航栏高亮
- Theme 设置记忆

## Level 3

- Project 搜索
- 简单留言 UI
- Project 弹窗详情
- 页面访问计数器（本地）
- 多语言切换

## Open Challenge

你可以增加：

# 任何你认为自己的主页应该拥有的功能。
"""),
        md("""\
# 自由开发 Prompt 模板

这是我当前的完整代码：

【粘贴代码】

我希望新增：

【描述功能】

用户操作：

【用户如何使用这个功能】

预期效果：

【点击以后应该发生什么】

要求：

- 保留已有功能
- 尽量少修改无关代码
- 不引入第三方库
- 保证 Jupyter 中可以正常运行
- 保持单个 index.html 文件

请先简单说明你的修改思路，
然后给出完整代码。
"""),
        writefile_cell("index.html"),
        code("""\
preview("index.html", height=650)
"""),
        md(f"""\
# 今天真正学习的是什么？

{progress(8, 7)}

不是 HTML。

不是 CSS。

也不是 JavaScript。

---

# AI Coding Workflow

## 1. Describe

把需求描述清楚。

↓

## 2. Generate

让 AI 实现。

↓

## 3. Run

真正运行。

↓

## 4. Inspect

看看是不是你想要的。

↓

## 5. Iterate

继续修改。

↓

## 6. Debug

发生问题就：

代码 + 现象 + 报错 → AI

↓

## 7. Verify

最后由你判断结果是否正确。
"""),
        md("""\
# AI Coding ≠ AI 替你思考

AI 可以：

- 写代码
- 修改代码
- 找 Bug
- 解释代码

但是你仍然需要决定：

- 我要做什么？
- 什么才算完成？
- 结果是不是正确？
- 下一步应该修改什么？

# AI Coding 改变的是“如何写程序”。

# 而不是“是否需要思考”。
"""),
        md("""\
# 继续实践：KNN 水果分类（独立 30 分钟模块）

用重量和直径判断水果种类，学习数据采集、清洗、规划和模型验证。

- [打开 KNN 学生 Notebook](KNN_Workshop_Student.ipynb)
- [采集指南与模块说明](modules/knn/README.md)

沿用当前 Jupyter 环境，Python 3.10+，保留完整项目文件夹。
"""),
    ]



def main():
    student = new_notebook(student_cells())
    student_path = ROOT / "AI_Coding_Workshop_Student.ipynb"
    nbf.write(student, student_path)
    print(f"student cells: {len(student.cells)} -> {student_path}")
    print("teacher slides: AI_Coding_Workshop_Teacher.html")


if __name__ == "__main__":
    main()
