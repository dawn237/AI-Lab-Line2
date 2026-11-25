# -*- coding: utf-8 -*-
"""主流程：读轨迹 → 校验 → 逐条执行。"""
import json
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from actions import click_menu, fill_size, click_ok, activate_tool, export_png, draw_line
from browser import start_browser
from config import OUTPUT_DIR, ROOT
from report import build_markdown, write_markdown, write_log
from server import start_server, stop_server
from trace_check import steps_check
from verify import verify_trace



def main():
    log = []

    # 每次运行一个独立目录：产物、检测报告、运行日志都放这里，互不覆盖
    run_dir = OUTPUT_DIR / f"run_{datetime.now():%Y%m%d%H%M%S}"
    run_dir.mkdir(parents=True, exist_ok=True)

    with open(ROOT / "data" / "trace" / "trace.json", "r", encoding="utf-8") as f:
        file = json.load(f)

    steps = file["steps"]                # 这个必须有，没有就该崩
    task_id = file.get("task_id")        # 没有就是 None，报告里不填
    screen = file.get("screen")

    # 轨迹不合法就一条都不执行
    errors = steps_check(steps)

    # 无论有没有错误都写报告，留一份“校验跑过”的证据
    write_markdown(run_dir / "check" / "check_report.md",
                   build_markdown(task_id, screen, errors))

    if errors:
        print(f"轨迹不合法，拒绝执行（{len(errors)} 条）：")
        for e in errors:
            print("  " + e)
        write_log(run_dir / "log" / "run_log.jsonl", log)
        return log
    print("校验完毕, 无异常 !")

    server = start_server()
    try:
        with sync_playwright() as p:
            browser, page = start_browser(p)

            for step in steps:
                if step["action"] == "click_menu":
                    args = step["args"]
                    verify_trace(click_menu(page, args["menu"], args["item"]), page, log)
                elif step["action"] == "click_ok":
                    verify_trace(click_ok(page), page, log)
                elif step["action"] == "fill_size":
                    args = step["args"]
                    verify_trace(fill_size(page, args["width"], args["height"]), page, log)
                elif step["action"] == "activate_tool":
                    args = step["args"]
                    verify_trace(activate_tool(page, args["tool"]), page, log)
                elif step["action"] == "export_png":
                    args = step["args"]
                    verify_trace(
                        export_png(page, args["filename"], run_dir / Path(args["path"]).name),
                        page, log)
                elif step["action"] == "draw_line":
                    args = step["args"]
                    with open(ROOT / args["path"], "r", encoding="utf-8") as f:
                        lines = [json.loads(l) for l in f if l.strip()]

                    # index 越界已在 steps_check 里拦下
                    raw = lines[args["index"]]
                    box = page.locator("#canvas_minipaint").bounding_box()
                    pts = [[box["x"] + x / 1000 * box["width"],
                            box["y"] + y / 1000 * box["height"]]
                           for x, y in raw["points"]]

                    # width 由 draw_line 内部处理（粗线多画几遍）
                    rec = draw_line(page, pts, raw["width"])
                    verify_trace(rec, page, log)
                    print(f"已执行完 {args["index"]}条!")

            run_errors = [r for r in log if r["level"] == "ERROR"]
            run_warns = [r for r in log if r["level"] == "WARNING"]

            if run_errors:
                print(f"执行期发现 {len(run_errors)} 个错误：")
                for rec in run_errors:
                    print(f"  {rec['ts']} {rec['action']}：{rec['message']}")
            else:
                print("执行期无错误")

            if run_warns:
                print(f"另有 {len(run_warns)} 条警告：")
                for rec in run_warns:
                    print(f"  {rec['ts']} {rec['action']}：{rec['message']}")
    finally:
        stop_server(server)
        print("已退出!")
        write_log(run_dir / "log" / "run_log.jsonl", log)
    return log


if __name__ == "__main__":
    main()
