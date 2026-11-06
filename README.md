# Image Tool —— 图片信息查看与简单编辑工具

一个用 Python 编写的命令行小程序：读取图片的基础信息，并对图片做缩放、裁剪、旋转、翻转、灰度化和格式转换。

所有编辑结果都会另存为新文件，**不会覆盖原图**。

## 1. 项目介绍

- **程序做什么**：查看一张图片的文件名、格式、宽高、颜色模式和文件大小；对图片做常见的简单编辑并保存。
- **程序形式**：命令行（CLI）。在终端里输入命令使用，不需要图形界面。
- **适合谁用**：需要批量或快速处理图片、又不想打开大型修图软件的人；也适合作为 Python 图片处理的学习示例。

### 功能一览

| 命令 | 功能 | 说明 |
| --- | --- | --- |
| `info` | 查看图片信息 | 文件名、格式、宽高、颜色模式、文件大小 |
| `resize` | 缩放 | 指定宽高；只给宽或高时按原比例缩放 |
| `crop` | 裁剪 | 指定左、上、右、下坐标，越界会给出提示 |
| `rotate` | 旋转 | 支持顺时针 90、180、270 度 |
| `flip` | 翻转 | 水平翻转（左右镜像）、垂直翻转（上下镜像） |
| `gray` | 灰度化 | 彩色图转灰度图 |
| `convert` | 格式转换 | PNG、JPG 等格式互转，自动处理透明通道 |

## 2. 环境配置

- **Python 版本**：3.10 及以上（开发与测试使用 Python 3.12）
- **依赖**：Pillow 10.0 及以上（图像处理库）

### 方式一：使用 uv（推荐）

项目使用 `pyproject.toml` 管理依赖。安装 [uv](https://docs.astral.sh/uv/) 后，在仓库根目录执行：

```bash
uv sync
```

首次执行会创建 `.venv` 虚拟环境，并按 `uv.lock` 中锁定的版本安装依赖；`uv.lock` 已随仓库提供，可保证不同机器安装到相同的依赖版本。

### 方式二：使用 pip

```bash
python -m pip install "pillow>=10.0"
```

如果想安装成系统命令（之后可以直接用 `imagetool`），在仓库根目录执行：

```bash
python -m pip install -e .
```

### 方式三：不安装，直接运行

只要求已经装好 Pillow，然后用仓库根目录的 `run.py` 启动：

```bash
python run.py --help
```

`run.py` 会自动把 `src` 加入模块搜索路径，适合临时试用。

> 国内网络安装依赖较慢时，可以加镜像源，例如：
> `python -m pip install "pillow>=10.0" -i https://pypi.tuna.tsinghua.edu.cn/simple`

## 3. 运行方式

以下命令都在**仓库根目录**执行。三种启动方式效果相同，任选一种：

| 启动方式 | 命令前缀 | 前提 |
| --- | --- | --- |
| 免安装脚本 | `python run.py` | 已安装 Pillow |
| uv | `uv run imagetool` | 已执行 `uv sync` |
| pip 安装 | `imagetool` | 已执行 `pip install -e .` |

如果 `uv run imagetool` 无法启动（个别电脑会拦截新生成的程序），可改用 `uv run python -m imagetool`，参数完全相同。

下文示例统一使用 `python run.py`。仓库自带两张示例图片：

- `samples/demo.jpg`：640 × 480 的彩色图
- `samples/logo.png`：320 × 320，带透明通道

### 3.1 查看图片信息

```bash
python run.py info samples/demo.jpg
```

预期输出（`文件路径` 会显示为绝对路径）：

```text
图片信息
--------------------------------
文件名    demo.jpg
图片格式  JPEG
尺寸      640 × 480 像素
颜色模式  RGB（彩色）
文件大小  20.61 KB
文件路径  ...\image-tool\samples\demo.jpg
```

### 3.2 缩放

只给宽度，高度按比例自动计算：

```bash
python run.py resize samples/demo.jpg --width 320
```

```text
已保存：samples\demo_320x240.jpg
尺寸：320 × 240 像素（原图未修改）
```

只给高度时，默认文件名同样带上计算后的尺寸，例如 `demo_160x120.jpg`，连续缩放不同尺寸不会互相覆盖。

只给高度：

```bash
python run.py resize samples/demo.jpg --height 120
```

同时给宽高（会改变宽高比）：

```bash
python run.py resize samples/demo.jpg --width 200 --height 300
```

指定输出文件：

```bash
python run.py resize samples/demo.jpg --width 320 -o samples/output/demo_320.jpg
```

### 3.3 裁剪

参数是左、上、右、下四个坐标（单位：像素），右边界和下边界**不包含**在结果内：

```bash
python run.py crop samples/demo.jpg -l 40 -t 40 -r 600 -b 440
```

```text
已保存：samples\demo_cropped_40_40_600_440.jpg
尺寸：560 × 400 像素（原图未修改）
```

如果坐标超出图片范围，程序会提示而不是崩溃：

```text
错误：裁剪区域超出图片范围：图片尺寸为 640 × 480 像素，
坐标需满足 0 ≤ left < right ≤ 640、0 ≤ top < bottom ≤ 480。
```

### 3.4 旋转

按顺时针方向旋转，支持 90、180、270 度：

```bash
python run.py rotate samples/demo.jpg --angle 90
```

```text
已保存：samples\demo_rotated_90.jpg
尺寸：480 × 640 像素（原图未修改）
```

### 3.5 翻转

```bash
python run.py flip samples/demo.jpg --direction horizontal   # 左右镜像，输出 demo_flipped_horizontal.jpg
python run.py flip samples/demo.jpg --direction vertical     # 上下镜像，输出 demo_flipped_vertical.jpg
```

### 3.6 灰度化

结果统一保存为 PNG，避免 JPEG 压缩影响灰度值：

```bash
python run.py gray samples/demo.jpg
```

```text
已保存：samples\demo_gray.png
尺寸：640 × 480 像素（原图未修改）
```

### 3.7 格式转换

PNG 转 JPG（带透明通道的图片会用白色背景填充，不会报错）：

```bash
python run.py convert samples/logo.png --format jpg
```

```text
提示：原图包含透明通道，已用白色背景填充后保存为 JPG。
已保存：samples\logo.jpg
尺寸：320 × 320 像素（原图未修改）
```

JPG 转 PNG：

```bash
python run.py convert samples/demo.jpg --format png
```

### 3.8 通用参数

| 参数 | 作用 |
| --- | --- |
| `-o` / `--output` | 指定输出文件路径；不指定时保存在原图旁边，文件名包含操作与参数，例如 `demo_320x240.jpg`、`demo_rotated_90.jpg`、`demo_cropped_40_40_600_440.jpg` |
| `--force` | 输出文件已存在时覆盖；不加该参数会提示并退出，防止误覆盖 |
| `-h` / `--help` | 查看帮助，例如 `python run.py crop --help` |

各命令的缩写参数：`-w`/`--width`、`-H`/`--height`、`-l`/`--left`、`-t`/`--top`、`-r`/`--right`、`-b`/`--bottom`、`-a`/`--angle`、`-d`/`--direction`、`-f`/`--format`。

完整帮助：

```bash
python run.py --help
```

## 4. 项目结构

```text
image-tool/
├── pyproject.toml          # 项目元数据与依赖
├── run.py                  # 免安装启动脚本
├── README.md               # 本说明文件
├── .gitignore
├── samples/                # 示例图片
│   ├── demo.jpg
│   └── logo.png
├── src/imagetool/          # 程序源码
│   ├── __init__.py
│   ├── __main__.py         # python -m imagetool 入口
│   ├── cli.py              # 命令行参数解析与流程编排
│   ├── editor.py           # 缩放、裁剪、旋转、翻转、灰度化
│   ├── info.py             # 图片信息读取与展示
│   ├── loader.py           # 读取图片、校验文件、处理 EXIF 方向
│   ├── saver.py            # 保存图片、格式判断、透明通道处理
│   ├── errors.py           # 自定义异常
│   └── utils.py            # 中文宽度对齐等小工具
└── tests/                  # 单元测试
    ├── test_cli.py
    ├── test_editor.py
    ├── test_info.py
    └── test_saver.py
```

## 5. 错误处理与退出码

程序会捕获可预期的错误，打印中文提示，不会抛出堆栈：

| 场景 | 提示示例 |
| --- | --- |
| 文件不存在 | `错误：文件不存在：samples/not-exist.jpg` |
| 不是有效图片 | `错误：不是有效的图片文件：notes.txt` |
| 宽高不合法 | `错误：宽度必须是大于 0 的整数，当前为 0。` |
| 裁剪越界 | `错误：裁剪区域超出图片范围：图片尺寸为 640 × 480 像素……` |
| 试图覆盖原图 | `错误：输出路径与原图相同；程序不会覆盖原图，请指定其他输出文件名。` |
| 输出文件已存在 | `错误：输出文件已存在：...；如需覆盖请加 --force。` |

退出码：`0` 成功；`1` 业务错误；`2` 命令行参数错误（argparse 报错）。

## 6. 测试

在仓库根目录执行：

```bash
python -m unittest discover -s tests -t . -v
```

共有 49 个测试用例，覆盖信息读取、缩放比例、裁剪边界、旋转方向、翻转、灰度化、透明通道转 JPG、EXIF 方向、防覆盖和命令行提示。

如果使用 uv：

```bash
uv run python -m unittest discover -s tests -t . -v
```

## 7. 常见问题

**Q：提示 `ModuleNotFoundError: No module named 'PIL'`？**
A：还没有安装 Pillow，执行 `python -m pip install "pillow>=10.0"`。

**Q：Windows 上 `python` 命令不存在？**
A：尝试 `py -3 run.py --help` 或 `python3 run.py --help`，或使用 uv 的 `uv run`。

**Q：输出文件已存在，但我想覆盖？**
A：加 `--force`，例如 `python run.py resize samples/demo.jpg -w 320 --force`。

**Q：处理手机照片时方向不对？**
A：程序会读取 EXIF 方向信息并自动摆正；`info` 命令会额外显示 `EXIF 方向` 一行。

**Q：会修改原图吗？**
A：不会。结果一律写入新文件，并且当 `-o` 指向原图时会直接拒绝。

## 8. Git 分支说明

- `main`：稳定分支，只保留可运行的代码。
- `dev`：开发分支，功能开发与提交都在这里完成，最后合并回 `main`。

提交信息采用 `feat:`、`test:`、`docs:`、`chore:` 等前缀，说明本次改动内容。
