#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="云帆系统自动化测试运行脚本")
    parser.add_argument(
        "--env", choices=["pre", "test"], default="pre",
        help="目标环境: pre(预发布) 或 test(测试环境)，默认 pre",
    )
    parser.add_argument(
        "--case", default=None,
        help="指定测试文件，如 test_brand 或 cases/test_brand.py",
    )
    parser.add_argument(
        "--no-headed", action="store_true",
        help="无头模式运行（默认有头）",
    )
    parser.add_argument(
        "--allure", action="store_true",
        help="生成并打开 allure 报告（需要安装 Java + allure CLI）",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    root = os.path.dirname(os.path.abspath(__file__))

    if args.case:
        case_path = args.case if os.path.exists(args.case) else f"cases/{args.case}.py"
    else:
        case_path = "cases/"

    cmd = [
        sys.executable, "-m", "pytest", case_path,
        f"--env={args.env}",
        "--alluredir=allure-results",
        "--html=report.html",
        "--self-contained-html",
        "-v",
    ]
    if args.no_headed:
        cmd.append("--no-headed")

    env_label = "预发布(pre)" if args.env == "pre" else "测试环境(test)"
    print("=" * 60)
    print("  云帆系统自动化测试")
    print(f"  环境: {env_label}")
    print(f"  目标: {case_path}")
    print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"执行命令: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, cwd=root)

    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("  测试结果: 全部通过")
    else:
        print(f"  测试结果: 存在失败用例 (exit code: {result.returncode})")
    print(f"  HTML 报告: {os.path.join(root, 'report.html')}")
    print(f"  Allure 结果: {os.path.join(root, 'allure-results')}")
    print("=" * 60)

    if args.allure:
        allure_cmd = shutil.which("allure")
        if allure_cmd:
            print("\n正在生成 Allure 报告...")
            subprocess.run(
                [allure_cmd, "generate", "allure-results", "-o", "allure-report", "--clean"],
                cwd=root,
            )
            subprocess.Popen([allure_cmd, "open", "allure-report"], cwd=root)
            print(f"  Allure 报告: {os.path.join(root, 'allure-report', 'index.html')}")
        else:
            print("\n未找到 allure 命令，跳过 Allure 报告生成。")
            print("安装方式: npm install -g allure-commandline（还需安装 Java）")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
