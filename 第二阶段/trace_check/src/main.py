import check
import report
import sys
from pathlib import Path

def main():
    data=Path(input())
    path=Path("../output/reports.md")
    out=report.write_markdown(path,report.build_markdown(data))
    print(f"已导入{out}")

if __name__ == "__main__":
    main()