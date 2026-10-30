import json

ACTIONS = {
    "click":  ["x", "y"],
    "type":   ["text"],
    "hotkey": ["keys"],
    "wait":   ["seconds"],
    "scroll": ["x", "y", "dy"],
}
BUTTONS = {"left", "right"}
KEYS = {"ctrl", "alt", "shift", "a", "c", "s", "v", "z", "enter", "esc"}

def json_loads(data):
    with open(data, "r",encoding="utf-8") as f:
        return json.load(f)

def check_screen(screen_w_h):
    screen_w=int(screen_w_h["width"])
    screen_h=int(screen_w_h["height"])
    return screen_w,screen_h

def check_step(step,screen_w_h):
    """返回错误列表；空列表表示通过。"""
    errors = []
    check_errors=[]
    try:
        no = step.get("step", "?")
        action = step.get("action")
    except AttributeError as e:
        check_errors.append(f"无法解析{e}")
        return [],check_errors

    screen_w,screen_h=check_screen(screen_w_h)

    if action not in ACTIONS:
        return [f"第 {no} 步：未知动作 {action!r}"],[]
    #!r如果action是None,将它变为'None',便于排查Bug

    for field in ACTIONS[action]:  #必需字段统一查
        if field not in step:
            errors.append(f'第 {no} 步 {action}：缺少必需字段 "{field}"')

    #坐标：类型 + 范围（一次循环处理 x 和 y）
    if action in ("click","scroll"):
        try:
            for axis,limit in(("x",screen_w),("y",screen_h)):
                value =step.get(axis)
                if value is None:
                    continue
                if type(value) is not int:
                    errors.append(f"第{no}中{axis}应为整数")
                elif not 0 <= value< limit:
                    errors.append(f"第{no}中{axis}超出0~{limit-1}")
        except Exception:
            check_errors.append(f"第{no}步{action}无法解析")

    #各个动做校验
    if action=="wait":
        try:
            seconds = step.get("seconds")
            if seconds is not None:
                if type(seconds) not in (int, float):
                    errors.append(f"第 {no} 步 wait：seconds 应为数字")
                elif not 0 < seconds <= 10:
                    errors.append(f"第 {no} 步 wait：seconds={seconds} 应在 (0, 10]")
        except Exception:
            check_errors.append(f"第{no}步{action}无法解析")

    if action=="click":
        try:
            button = step.get("button")
            if button is not None:
                if button not in BUTTONS:
                    errors.append(f"第 {no} 步 click: button 只能是 left/right")
        except Exception:
            check_errors.append(f"第{no}步{action}无法解析")

    if action == "type":
        try:
            text = step.get("text")
            if text is not None:
                if not isinstance(text, str):
                    errors.append(f"第 {no} 步 type：text 应为字符串")
                elif not text.strip():
                    errors.append(f"第 {no} 步 type：text 不能为空")
                elif len(text) > 200:
                    errors.append(f"第 {no} 步 type：text 超过 200 字符")
        except Exception:
            check_errors.append(f"第{no}步{action}无法解析")

    if action == "hotkey":
        try:
            keys=step.get("keys")
            if keys is not None:
                if not isinstance(keys, list) or not keys:
                    errors.append(f"第 {no} 步 hotkey：keys 应为非空列表")
                else:
                    for key in keys:
                        if key not in KEYS:
                            errors.append(f"第 {no} 步 hotkey: {key}参数不合规")
        except Exception:
            check_errors.append(f"第{no}步{action}无法解析")

    if action == "scroll":
        try:
            dy=step.get("dy")
            if not isinstance(dy, int):
                errors.append(f"第 {no} 步 scroll：dy 应为整数")
            elif not -10 <= dy <= 10:
                errors.append(f"第 {no} 步 scroll：dy 应为在 [-10, 10]")
        except Exception:
            check_errors.append(f"第{no}步{action}无法解析")

    return errors,check_errors