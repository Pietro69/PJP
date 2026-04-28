from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GRAMMAR = ROOT / "PJP.g4"
ANTLR_JAR = ROOT / "antlr-4.13.2-complete.jar"


def main() -> int:
    command = [
        "java",
        "-jar",
        str(ANTLR_JAR),
        "-Dlanguage=Python3",
        "-visitor",
        "-no-listener",
        "-o",
        str(ROOT),
        str(GRAMMAR),
    ]
    subprocess.run(command, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
