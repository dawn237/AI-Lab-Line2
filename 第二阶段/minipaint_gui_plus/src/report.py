# -*- coding: utf-8 -*-
"""把轨迹校验结果渲染成 Markdown 报告。"""
import json
from pathlib import Path


def build_markdown(task_id, screen, errors):
    """task_id / screen 缺失时（None）对应的行就不写。"""
    lines = ["# GUI 轨迹检测", "", "## 错误", "| # | 原因 |", "| :---: | :---: |"]

    if errors:
        for i, e in enumerate(errors, 1):
            lines.append(f"| {i} | {e} |")
    else:
        lines.append("| - | 无错误 |")

    lines.append("")
    if task_id:
        lines.append(f"task_id: `{task_id}`  ")
    if screen:
        lines.append(f"screen: {screen.get('width')} × {screen.get('height')}  ")
    lines.append(f"总计 {len(errors)} 条错误")
    return "\n".join(lines)


def write_markdown(path, text):
    """把 Markdown 写入文件，自动创建父目录。"""
    target = Path(path)
    if target.parent and not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    return target


def write_log(path, records):
    """把运行日志写成 JSONL：一行一个记录，方便 grep / 统计。"""
    target = Path(path)
    if target.parent and not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return target
