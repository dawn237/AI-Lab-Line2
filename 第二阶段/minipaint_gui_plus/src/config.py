"""全局配置：路径、端口、窗口、超时。

为什么集中：这些值要写进 README，
换机器、换分辨率时只改这里。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # 项目根目录

# miniPaint 静态文件（解压后的目录）
MINIPAINT_DIR = ROOT / "env" / "miniPaint-master"

PORT = 8123
BASE_URL = f"http://127.0.0.1:{PORT}"

# 固定窗口：截图和坐标都按这个尺寸
VIEWPORT = {"width": 1400, "height": 1600}

# 超时（毫秒）：所有等待都必须有上限
TIMEOUT_MS = 15_000

# 输出目录
OUTPUT_DIR = ROOT / "output"

# 轨迹：动作 → 合法取值 / 必填字段
ACTIONS = {
    # click_menu：菜单 → 该菜单下允许的条目（空列表 = 还没接入，校验一律拒绝）
    # 条目名取自 env/miniPaint-master/src/js/config-menu.js
    "click_menu": {
        "file":    ["new", "open", "export"],
        "edit":    [],
        "view":    [],
        "image":   [],
        "layer":   [],
        "effects": [],
        "tools":   [],
        "help":    [],
    },
    "fill_size": ["width", "height"],
    "click_ok": [],
    "activate_tool": ["brush", "rectangle", "text", "fill", "crop"],
    "draw_line": ["path"],
    "export_png": ["filename", "path"],
}

# ── 预期(expect)规范备忘 ───────────────────────────────────────────
# 校验逻辑写在 trace_check.py 里（每个动作一段 if），这里只是对照表，
# 方便加动作/改动作时一眼看到“这个动作能写哪些预期”，不用翻代码。
#
#   动作              允许的预期键        含义
#   ------------------------------------------------------------------
#   click_menu        dialog            做完应弹出某个对话框
#                     file              仅 item=export 时：应落盘一个文件
#   fill_size         fields            两个输入框里应是 [宽, 高]
#   click_ok          canvas            画布应变成 [宽, 高]
#   activate_tool     tool              该工具应处于选中态
#   draw_line         dirty             画布内容应变成“已修改”
#   export_png        file              磁盘上应出现这个文件
#
# 约定：一个键只表达一种含义；改这里的说明时，记得同步 trace_check.py。
# ──────────────────────────────────────────────────────────────────