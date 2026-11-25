# -*- coding: utf-8 -*-
"""轨迹校验：只读 JSON，不碰浏览器。

分工：
· 本文件判「数据合不合法」——不合法的一条都别执行
· 执行中「有没有生效」交给执行器的快照比对
· 执行后「产物对不对」交给 verify.py
"""
import json
from pathlib import Path

from config import ACTIONS, ROOT


def json_loads(data):
    with open(data, "r", encoding="utf-8") as f:
        return json.load(f)


def check_screen(screen_w_h):
    screen_w = int(screen_w_h["width"])
    screen_h = int(screen_w_h["height"])
    return screen_w, screen_h


def _resolve(value):
    """相对路径按项目根目录解析，绝对路径原样用。"""
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


_line_counts = {}


def _line_count(p):
    """数文件有多少条线（只数行，不解析 JSON），按路径缓存。"""
    if p not in _line_counts:
        with open(p, encoding="utf-8") as f:
            _line_counts[p] = sum(1 for line in f if line.strip())
    return _line_counts[p]


def _is_int(value):
    """真整数。布尔值不算（Python 里 True 也是 int）。"""
    return isinstance(value, int) and not isinstance(value, bool)


def _only(expect, allowed, no, action, errors):
    """不认识的预期键一律报错。"""
    for key in expect:
        if key not in allowed:
            errors.append(f"第 {no} 步：{action} 不支持预期 {key!r}，只能写 {sorted(allowed)}")


def _str_ok(value, no, key, errors):
    """非空字符串。"""
    if not isinstance(value, str):
        errors.append(f"第 {no} 步：expect.{key} 应为 str，实际是 {type(value).__name__}")
    elif not value.strip():
        errors.append(f"第 {no} 步：expect.{key} 不能是空字符串")


def _pair_ok(value, no, key, errors):
    """两个正整数（宽、高）。"""
    if not isinstance(value, list):
        errors.append(f"第 {no} 步：expect.{key} 应为 list，实际是 {type(value).__name__}")
    elif not (len(value) == 2 and all(_is_int(v) and v > 0 for v in value)):
        errors.append(f"第 {no} 步：expect.{key} 应为两个正整数")


def check_expect(step, no, action, args, errors):
    """校验 expect：每种动作只认它自己会造成的变化（一一对应）。"""
    expect = step.get("expect")
    if expect is None:
        return
    if not isinstance(expect, dict):
        errors.append(f"第 {no} 步：expect 应为对象，实际是 {type(expect).__name__}")
        return

    if action == "click_menu":
        allowed = {"dialog"}                       # 点菜单只该弹窗
        if args.get("item") == "export":
            allowed.add("file")                    # 导出那项还会落盘
        _only(expect, allowed, no, action, errors)
        if "dialog" in expect:
            _str_ok(expect["dialog"], no, "dialog", errors)
        if "file" in expect:
            _str_ok(expect["file"], no, "file", errors)

    elif action == "fill_size":
        _only(expect, {"fields"}, no, action, errors)        # 只填输入框
        if "fields" in expect:
            _pair_ok(expect["fields"], no, "fields", errors)

    elif action == "click_ok":
        _only(expect, {"canvas"}, no, action, errors)        # 只改画布
        if "canvas" in expect:
            _pair_ok(expect["canvas"], no, "canvas", errors)

    elif action == "activate_tool":
        _only(expect, {"tool"}, no, action, errors)
        if "tool" in expect:
            _str_ok(expect["tool"], no, "tool", errors)

    elif action == "draw_line":
        _only(expect, {"dirty"}, no, action, errors)
        if "dirty" in expect and not isinstance(expect["dirty"], bool):
            errors.append(f"第 {no} 步：expect.dirty 应为 bool，"
                          f"实际是 {type(expect['dirty']).__name__}")

    elif action == "export_png":
        _only(expect, {"file"}, no, action, errors)
        if "file" in expect:
            _str_ok(expect["file"], no, "file", errors)


def steps_check(steps, screen_w_h=None):
    errors = []

    if not isinstance(steps, list):
        return [f"steps 应为列表，实际是 {type(steps).__name__}"]

    for i, step in enumerate(steps):
        no = i + 1

        if not isinstance(step, dict):
            errors.append(f"第 {no} 步：本步应为对象，实际是 {type(step).__name__}")
            continue

        action = step.get("action")
        if action not in ACTIONS:
            errors.append(f"第 {no} 步：未知动作 {action!r}")
            continue

        args = step.get("args")
        if not isinstance(args, dict):
            errors.append(f"第 {no} 步：缺少 args 或不是对象")
            continue

        if action == "click_menu":
            try:
                menu, item = args["menu"], args["item"]
            except KeyError as e:
                errors.append(f"第 {no} 步：{e} 缺失")
                continue
            menus = ACTIONS["click_menu"]
            if menu not in menus:
                errors.append(f"第 {no} 步：未知菜单 {menu!r}，可选 {sorted(menus)}")
            elif not menus[menu]:
                errors.append(f"第 {no} 步：菜单 {menu!r} 还没接入条目")
            elif item not in menus[menu]:
                errors.append(f"第 {no} 步：{menu} 下没有 {item!r}，可选 {menus[menu]}")

        elif action == "fill_size":
            for name in ("width", "height"):
                try:
                    value = args[name]
                except KeyError:
                    errors.append(f"第 {no} 步：{name} 缺失")
                    continue
                if not _is_int(value):
                    errors.append(f"第 {no} 步：{name} 应为整数，"
                                  f"实际是 {type(value).__name__}")
                elif not 1 <= value <= 10000:
                    errors.append(f"第 {no} 步：{name}={value} 超出 1~10000")

        elif action == "click_ok":
            if args:
                errors.append(f"第 {no} 步：click_ok 不需要参数，多了 {sorted(args)}")

        elif action == "activate_tool":
            try:
                tool = args["tool"]
            except KeyError:
                errors.append(f"第 {no} 步：tool 缺失")
                continue
            if not isinstance(tool, str):
                errors.append(f"第 {no} 步：tool 应为字符串，"
                              f"实际是 {type(tool).__name__}")
            elif tool not in ACTIONS["activate_tool"]:
                errors.append(f"第 {no} 步：未知工具 {tool!r}，"
                              f"可选 {ACTIONS['activate_tool']}")

        elif action == "draw_line":
            try:
                path = args["path"]
            except KeyError:
                errors.append(f"第 {no} 步：path 缺失")
                continue
            if not isinstance(path, str) or not path.strip():
                errors.append(f"第 {no} 步：path 应为非空字符串")
            else:
                p = _resolve(path)
                if p.suffix.lower() != ".jsonl":
                    errors.append(f"第 {no} 步：path 应为 .jsonl，实际 {p.suffix!r}")
                if not p.exists():
                    errors.append(f"第 {no} 步：path 不存在 {p}")
            index = args.get("index")
            if index is not None and (not _is_int(index) or index < 0):
                errors.append(f"第 {no} 步：index 应为 >=0 的整数，实际 {index!r}")
            elif index is not None and p.exists():
                total = _line_count(p)
                if index >= total:
                    errors.append(f"第 {no} 步：index={index} 越界，{p.name} 只有 {total} 行")

        elif action == "export_png":
            try:
                name, path = args["filename"], args["path"]
            except KeyError as e:
                errors.append(f"第 {no} 步：{e} 缺失")
                continue
            if not isinstance(name, str) or not name.strip():
                errors.append(f"第 {no} 步：name 应为非空字符串")
            elif any(c in name for c in '\\/:*?"<>|'):
                errors.append(f"第 {no} 步：name 不能含路径分隔符或非法字符")
            if not isinstance(path, str) or not path.strip():
                errors.append(f"第 {no} 步：path 应为非空字符串")
            else:
                p = _resolve(path)
                if p.suffix.lower() != ".png":
                    errors.append(f"第 {no} 步：path 应以 .png 结尾，实际 {p.suffix!r}")
                if not p.parent.exists():
                    errors.append(f"第 {no} 步：导出目录不存在 {p.parent}")

        check_expect(step, no, action, args, errors)

    return errors

if __name__ == "__main__":
    with open(ROOT / "data" / "test_errors.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    errors = steps_check(data["steps"])
    print(f"共 {len(errors)} 条错误" if errors else "通过，没有错误")
    for e in errors:
        print("  " + e)
