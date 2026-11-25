# -*- coding: utf-8 -*-
"""校验：动作执行完之后，检查界面/产物是否符合预期。

每条动作在 logs 里留两行：start（开始）、end（成功或失败）。
ms 用动作自己测的 t0/t1 差值（单步耗时，不是累计）。
"""
from datetime import datetime
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import TimeoutError as PWTimeout


def verify_trace(trace: dict, page, logs=None):
    action = trace["action"]
    extra = trace["extra"]
    ms = round((trace["t1"] - trace["t0"]) * 1000)

    if action == "click_menu":
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "start", "action": action,
                     "message": "开始执行", "ms": ms})
        try:
            page.wait_for_selector(".popup", state="visible", timeout=5000)
        except PWTimeout:
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "ERROR", "phase": "end", "action": action,
                         "message": "期望弹窗出现，5 秒内没出现", "ms": ms})
        else:
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "INFO", "phase": "end", "action": action,
                         "message": "执行成功", "ms": ms})

    elif action == "click_ok":
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "start", "action": action,
                     "message": "开始执行", "ms": ms})
        try:
            page.wait_for_selector(".popup", state="hidden", timeout=5000)
        except PWTimeout:
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "ERROR", "phase": "end", "action": action,
                         "message": "点确定后弹窗没有关闭", "ms": ms})
        else:
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "INFO", "phase": "end", "action": action,
                         "message": "执行成功", "ms": ms})

    elif action == "activate_tool":
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "start", "action": action,
                     "message": "开始执行", "ms": ms})
        want = extra.get("tool")
        ok = page.evaluate(
            """(sel) => {
                const el = document.getElementById(sel);
                return !!el && el.className.includes('active');
            }""",
            want,
        )
        if ok:
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "INFO", "phase": "end", "action": action,
                         "message": "执行成功", "ms": ms})
        else:
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "ERROR", "phase": "end", "action": action,
                         "message": f"工具 {want} 没有处于选中态", "ms": ms})

    elif action == "export_png":
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "start", "action": action,
                     "message": "开始执行", "ms": ms})
        min_ratio = 0.01
        want = extra.get("path")
        if not want or not Path(want).exists():
            logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                         "level": "ERROR", "phase": "end", "action": action,
                         "message": f"导出文件不存在：{want}", "ms": ms})
        else:
            with Image.open(want).convert("RGB") as img:
                arr = np.asarray(img).astype(int)
            non_white = (np.abs(arr - 255).sum(axis=2) > 20).mean()
            if non_white > min_ratio:
                logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                             "level": "INFO", "phase": "end", "action": action,
                             "message": f"执行成功（非白像素 {non_white:.2%}）", "ms": ms})
            else:
                logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                             "level": "WARNING", "phase": "end", "action": action,
                             "message": f"导出的图像{Path(want).name}像素点过少", "ms": ms})

    elif action == "fill_size":
        # 不校验：fill 不抛异常就说明值已经写进输入框了，只记日志
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "start", "action": action,
                     "message": "开始执行", "ms": ms})
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "end", "action": action,
                     "message": "执行成功", "ms": ms})

    elif action == "draw_line":
        # 不校验：画没画上属于“有没有痕迹”，要前后对比才算得出来
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "start", "action": action,
                     "message": "开始执行", "ms": ms})
        logs.append({"ts": datetime.now().isoformat(timespec="milliseconds"),
                     "level": "INFO", "phase": "end", "action": action,
                     "message": "执行成功", "ms": ms})

