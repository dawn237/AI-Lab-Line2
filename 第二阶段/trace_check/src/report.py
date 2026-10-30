import check
from pathlib import Path

def build_markdown(data):
    reports=[]
    # 标题
    reports.append("# GUI轨迹检测")
    reports.append("\n")
    # errors表头
    reports.append("## 错误step数据")
    reports.append("| # | 原因 |")
    reports.append("| :---: | :---: |")
    # errors内容
    json_load=check.json_loads(data)
    i=0
    j=0
    for item in json_load["steps"]:
        errors, check_errors = check.check_step(item, json_load["screen"])
        for error in errors:
            i+=1
            reports.append(f"| {i} | {error} |")
    reports.append("\n")
    # check_errors表头
    reports.append("## 无法解析的step数据")
    reports.append("| # | 原因 |")
    reports.append("| :---: | :---: |")
    # check_errors内容
    for item in json_load["steps"]:
        errors, check_errors = check.check_step(item, json_load["screen"])
        for check_error in check_errors:
            j+=1
            reports.append(f"| {j} | {check_error} |")
    # 其他
    reports.append(f"task_id:`{json_load.get("task_id","暂无")}`  ")
    reports.append(f"task:`{json_load.get("task","暂无")}`  ")
    reports.append(f"screen: width:`{json_load["screen"]["width"]}`height:`{json_load["screen"]["height"]}`  ")
    reports.append(f"created_at:`{json_load.get("created_at","暂无")}`  ")
    reports.append(f"总计`{i}`条已解析错误,`{j}`条无法解析 ")

    return "\n".join(reports)

def write_markdown(path, text):
    """把 Markdown 写入文件，自动创建父目录。"""
    target=Path(path)
    if target.parent and not target.parent.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(text)
    return target



