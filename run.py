"""免安装启动脚本：直接把 src 加入模块搜索路径后运行命令行程序。

用法：
    python run.py info samples/demo.jpg
    python run.py resize samples/demo.jpg --width 320
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from imagetool.cli import main  # noqa: E402  （必须先插入路径再导入）

if __name__ == "__main__":
    raise SystemExit(main())
