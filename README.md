# AI Coding 入门 Workshop

45 分钟做出你的第一个个人主页；新增独立的 **30 分钟 KNN 水果分类模块**，学习数据收集、清洗、规划与建模。两部分可分别授课，连上共约 75 分钟。

这不是一节 HTML 课。学生要带走的是工作流：

**Describe → Generate → Run → Inspect → Iterate → Debug → Personalize**

## 文件

- 发给学生：`AI_Coding_Workshop_Student.ipynb`
- 教师投影讲稿：`AI_Coding_Workshop_Teacher.html`（用浏览器打开，当 PPT 用）
- KNN 学生实操：[KNN_Workshop_Student.ipynb](KNN_Workshop_Student.ipynb)
- KNN 教师投影：[KNN_Workshop_Teacher.html](KNN_Workshop_Teacher.html)
- KNN 采集指南、课时安排、验收标准：[模块说明](modules/knn/README.md)
- 环境配置指南：`JUPYTER_SETUP.md`（纯文本，没装 Jupyter 也能看）
- 一键配置脚本：`setup_env.bat`（双击自动完成安装 + 自检，最省事）
- 只做自检（不安装）：命令行运行 `python setup_env.py --check`
- 备用成品：`assets/backup/`（`demo` / `v0` / `v1` / `v2` / `final`）
- Skill 示例：`examples/skill/`（课后进阶）
- Harness 示例：`examples/harness/`（课后进阶）

学生课堂运行后会在本目录生成 `index.html`、`versions/`、`debug_demo.html`。

## 新模块：KNN 水果分类

用重量和直径区分苹果、橙子、梨，从“每行数据代表什么”开始，完成采集方案、脏数据审计、训练/验证/测试划分、标准化、选 K、最终评估和新水果预测。每个阶段配有 AI 提示词和检查问题。

从项目根目录启动 Jupyter 后打开 `KNN_Workshop_Student.ipynb`。使用 Python 3.10+，沿用现有 Jupyter 环境，模型无需额外依赖。必须分发完整项目目录：Notebook 会读取 `modules/knn/` 中的代码和 CSV。模拟数据已提供，真实数据可课前用 [采集表](modules/knn/data/collection_template.csv) 收集。

教师打开 `KNN_Workshop_Teacher.html` 放映，操作与原讲稿一致。详细课堂安排见 [模块说明](modules/knn/README.md)。以下原有时间节点和单文件网页约束仍针对个人主页课。

维护新模块：编辑 `modules/knn/lesson.md`，再运行 `python -m modules.knn.build_notebook` 重新生成学生 Notebook。开发验证使用 `python -m pytest tests/test_knn.py`（pytest 仅供开发者，学生不需要）。

## 讲稿怎么用

用浏览器打开 `AI_Coding_Workshop_Teacher.html`，当 PPT 放映：

- 点击页面 / `F5`：全屏开始
- `→` / 空格 / 点击右半边：下一页
- `←` / 点击左半边：上一页
- `Esc`：退出全屏
- `N`：显示 / 隐藏教师备注

Demo 和成品页已嵌在讲稿里。学生卡住时，打开 `assets/backup/` 对应文件，让他们把代码贴进 Notebook。

## 课前准备

1. 安装 Python 3 与 Jupyter（Notebook 或 JupyterLab 均可；最简单：双击 `setup_env.bat` 自动完成）。
2. **在本文件夹里启动 Jupyter**，保证 Notebook 和生成的 `index.html` 在同一目录。

```text
jupyter notebook
```

或：

```text
jupyter lab
```

3. 用浏览器打开 `AI_Coding_Workshop_Teacher.html`，点一下进入全屏放映，用方向键翻页。
4. 确认讲稿里的 Demo / final 预览能显示，中文正常，按钮可点。
5. 用学生版走一遍 Part 1：能写出 `index.html`，且 `preview()` 显示 Hello 页。
6. 确认学生能使用 ChatGPT 或其他 AI。课程不调用 API，不需要 Key。
7. 学生卡住时，把对应备用页发给他贴进 Notebook，不要现场改 HTML。

## 课堂硬约束

- 单文件 `index.html`，不使用 CDN / npm / React / 多文件项目
- 15 分钟：每个人必须看到自己的网页；否则直接 Backup V0
- 33 分钟：每个人至少有一个可点击交互
- 37 分钟以后：停止统一讲授，进入自由开发

## 课堂三原则

1. 学生问代码什么意思：除非挡住任务，不要讲完整语法。
2. 学生问功能怎么写：先让他把效果告诉 AI。
3. 不要追求全班统一结果。同一个起点、完全不同作品，才算成功。

## 环境说明

- 标准环境：本地 Jupyter Notebook / JupyterLab（Windows 可用）
- VS Code / Cursor 的 Jupyter 一般也能预览
- 不要用 Google Colab 作为主路径（本地 HTML 预览方式不同）

## 课后继续探索 / Where to go next

以下是可选的课后进阶内容，课堂只需理解概念，不要求配置或完成示例。

### 1. Build reusable Skills

把经常重复的任务经验沉淀下来，回答“这类事情通常怎么做好”。从 [Skill 接入说明](examples/skill/README.md) 和 [个人主页 Skill 示例](examples/skill/personal-homepage/SKILL.md) 开始。

### 2. Build your AI Coding workflow

让 Agent 按 **Read → Edit → Run → Check → Fix → Verify** 完整执行并验证任务。参考 [Harness 接入说明](examples/harness/README.md) 和 [个人主页工作流示例](examples/harness/personal-homepage-workflow.md)，为自己的任务明确目标、检查方法和完成条件。

### 3. Learn your tool

不同 AI Coding 工具对 Skills、rules、instructions、tools 和 workflow 的支持方式不同。使用 Codex、Claude Code、Cursor 或 GitHub Copilot 时，优先查对应工具的官方文档，确认真实配置与加载方式。这里的 Markdown 是教学示例，不代表所有工具都能直接加载或执行。
