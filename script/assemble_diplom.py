#!/usr/bin/env python3
"""Сборка полного диплома из отдельных PDF-файлов."""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PDFS = [
    os.path.join(BASE_DIR, "../title", "title.pdf"),
    os.path.join(BASE_DIR, "../annotation", "annotation.pdf"),
    os.path.join(BASE_DIR, "../summary", "main.pdf"),
    os.path.join(BASE_DIR, "../diplom", "main.pdf"),
]

OUTPUT = os.path.join(BASE_DIR, "diplom_full.pdf")


def main():
    for p in PDFS:
        if not os.path.exists(p):
            print(f"Ошибка: файл не найден: {p}", file=sys.stderr)
            sys.exit(1)

    result = subprocess.run(
        ["pdfunite"] + PDFS + [OUTPUT],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Ошибка: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"Собрано: {OUTPUT}")


if __name__ == "__main__":
    main()
