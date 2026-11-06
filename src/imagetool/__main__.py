"""命令行入口：python -m imagetool 时执行 main()。"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
