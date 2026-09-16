# Jupyter 环境配置（小白版 · 3 分钟上手）

> Jupyter 是一个「可以边写边运行」的笔记本（文件后缀 `.ipynb`）。
> 本课程用它来写网页并直接预览——**你不需要学它**，会用下面三步即可。

---

## 第一步：双击 `setup_env.bat`

1. 双击项目文件夹里的 `setup_env.bat`
2. 没装 Python？它会**自动打开下载页** → 安装时**务必勾选 Add to PATH** → 装完再双击一次
3. 等它自动装好并自检，看到 **必需项全部 ✅**
4. 它问「启动 JupyterLab 吗？」→ **直接回车**，浏览器会自动打开
5. 在浏览器里点开 `AI_Coding_Workshop_Student.ipynb`，开课

学习新增水果分类模块时，改为打开 **`KNN_Workshop_Student.ipynb`**。使用 Python 3.10 或更新版本，保留完整的 `modules/knn/` 文件夹，并在项目根目录启动 Jupyter。无需再安装机器学习库。原自检脚本检查共用 Jupyter 环境与主页课程；KNN 课前请额外从头运行新 Notebook。若报 `No module named modules` 或找不到 CSV，请检查启动目录和文件是否完整。

> 提示：新项目里没有 `index.html` 是正常的，课堂上 Part 1 会生成。

---

## 第二步：上课只需要一个键

| 操作 | 怎么按 |
|---|---|
| 运行当前格 | **Shift + Enter**（全程唯一必须记的） |
| 卡住了 | 点工具栏 ⏹ 停止，再重启内核 |

格子只有两种：**文字格**（MarkDown说明，看看就行）和**代码格**（按 Shift + Enter 运行）。

---

## 第三步：卡住就看这里（5 条）

1. 提示「python 不是内部或外部命令」→ 重装 Python 时勾 **Add to PATH**
2. 自检 ❌ 提示缺 `ipykernel` / `jupyterlab` → 重新双击 `setup_env.bat`
3. `preview()` 提示「找不到文件」→ 先运行上面的 `%%writefile` 格子
4. 格子一直 `In [*]` 不结束 → 点 ⏹ 停止，重启内核
5. 粘贴 AI 返回的代码时，**不要带开头的 ```html 和结尾的 ```**

---

## 附录

- **用 VS Code 上课**：装 Python + Jupyter 两个扩展 → 直接双击 `.ipynb` → 右上角选 Python 内核，点格子左侧 ▶ 运行
- **课前批量检查电脑**（只检查、不安装）：命令行运行 `python setup_env.py --check`
- **脚本失败时的手动方式**：命令行 `pip install jupyterlab`，然后在项目文件夹里 `jupyter lab`
