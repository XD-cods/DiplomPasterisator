#!/usr/bin/env python3
"""Полный цикл сборки диплома: извлечение оглавления → сборка итогового PDF."""

import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(path):
    print(f">>> {os.path.basename(path)}")
    result = subprocess.run(
        [sys.executable, path],
        cwd=SCRIPT_DIR,
    )
    if result.returncode != 0:
        print(f"Ошибка при выполнении {path}", file=sys.stderr)
        sys.exit(1)
    print()


def main():
    run_script(os.path.join(SCRIPT_DIR, "extract_toc.py"))
    run_script(os.path.join(SCRIPT_DIR, "update_annotation.py"))
    run_script(os.path.join(SCRIPT_DIR, "assemble_diplom.py"))


if __name__ == "__main__":
    main()