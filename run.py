import os
import sys
import pytest

def main():
    # 切换工作目录到项目根目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # 构造 pytest 参数列表
    pytest_args = [
        "-vs",
        "--alluredir=allure-results",
        "--clean-alluredir",
        "tests",
    ]
    # pytest_args.append("--env=dev")

    # 运行 pytest
    exit_code = pytest.main(pytest_args)

    # 让 run.py 的退出码和 pytest 一致
    sys.exit(exit_code)

if __name__ == "__main__":
    main()