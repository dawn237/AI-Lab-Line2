# -*- coding: utf-8 -*-
"""动作：点菜单、填参数、拖拽、导出、画线。

原则：一个函数只做一件事，返回可记录的结果。

返回约定（所有动作统一）：
    {"action": 动作名, "t0": 开始, "t1": 结束, "extra": 该动作自身的信息}

- 通用字段人人都有，字段名固定；
- extra 里只放“这个动作真的有”的东西，没有就留空 {}；
- 不知道“自己是第几个”，序号由调用方补。
"""
import time
from pathlib import Path

import locator as L

# 粗线的每一遍比上一遍偏移多少像素（模拟笔宽）
OFF = 0.8


def click_menu(page, menu: str, item: str) -> dict:
    """点一级菜单，再点二级菜单项。

    为什么要 sleep 一下：
    菜单展开有动画/异步渲染，点太快会点空。
    更好的是 wait_for_selector(visible)，这里用短 sleep 保持简单。
    """
    t0 = time.perf_counter()
    page.click(L.MENU[menu])
    page.wait_for_timeout(300)
    page.click(L.MENU_ITEM[menu][item])
    page.wait_for_timeout(500)
    t1 = time.perf_counter()
    return {"action": "click_menu", "t0": t0, "t1": t1,
            "extra": {"menu": menu, "item": item}}


def fill_size(page, width: int, height: int) -> dict:
    """在 New 对话框里填宽高。

    fill 会先清空再输入，比 type 稳定。
    """
    t0 = time.perf_counter()
    page.fill(L.NEW_WIDTH, str(width))
    page.fill(L.NEW_HEIGHT, str(height))
    t1 = time.perf_counter()
    return {"action": "fill_size", "t0": t0, "t1": t1,
            "extra": {"width": width, "height": height}}


def click_ok(page) -> dict:
    """点对话框的 Ok。"""
    t0 = time.perf_counter()
    page.click(L.POPUP_OK)
    page.wait_for_timeout(800)
    t1 = time.perf_counter()
    return {"action": "click_ok", "t0": t0, "t1": t1, "extra": {}}


def activate_tool(page, name: str) -> dict:
    """激活左侧工具。

    注意：矩形/椭圆等形状工具在折叠分组里，
    默认 display:none，Playwright 的 click 会报“元素不可见”。
    这里用 JS 直接触发 click，效果和用户点开分组选工具一样。
    """
    t0 = time.perf_counter()
    selector = L.TOOL[name]
    page.evaluate(
        "(sel) => document.querySelector(sel).click()",
        selector,
    )
    page.wait_for_timeout(300)
    t1 = time.perf_counter()
    return {"action": "activate_tool", "t0": t0, "t1": t1,
            "extra": {"tool": name}}


def export_png(page, name: str, save_path) -> dict:
    """导出 PNG 并保存。

    expect_download 必须包住“触发下载的那次点击”，
    否则下载事件接不住，文件会丢。
    """
    t0 = time.perf_counter()
    click_menu(page, "file", "export")

    page.fill(L.EXPORT_NAME, name)
    page.check(L.EXPORT_TYPE_PNG)

    with page.expect_download(timeout=30_000) as dl_info:
        page.click(L.POPUP_OK)

    download = dl_info.value
    download.save_as(str(save_path))
    page.wait_for_timeout(500)
    t1 = time.perf_counter()

    saved = Path(save_path)
    return {"action": "export_png", "t0": t0, "t1": t1,
            "extra": {"name": name,
                      "path": str(save_path),
                      "bytes": saved.stat().st_size if saved.exists() else None}}


def draw_line(page, line: list, width: int = 1):
    """画一条线。width=3 表示粗线：内部用平行偏移画多遍来模拟。

    为什么偏移放这里而不放主循环：
    怎么把一条线画粗是绘图的实现细节，主循环只该说“画这条线，粗 3”。
    """
    t0 = time.perf_counter()
    pts = line
    for _ in range(width):
        page.mouse.move(*pts[0])
        page.mouse.down()
        for p in pts[1:]:
            page.mouse.move(*p, steps=1)
        page.mouse.up()
        pts = [[x + OFF, y + OFF] for x, y in pts]
    t1 = time.perf_counter()
    return {"action": "draw_line", "t0": t0, "t1": t1,
            "extra": {"points": len(line), "width": width}}
