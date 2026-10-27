from pathlib import Path
from collections import Counter
import csv
import sys

"""所有图片格式"""
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
SIZE=["B","KB","MB","GB","TB"]

def word_scan(path):
    list=[]
    for p in path.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        list.append({"路径":p,"类型":p.suffix.lower(),"大小":human_size(p.stat().st_size)})
    return list

def human_size(size):
    size = float(size)
    for unit in SIZE:
        if size < 1024 or unit == "GB":
            return f"{size:.2f} {unit}"
        size /= 1024

def count_words(list):
    count=Counter()
    for item in list:
        count[item["类型"]]+=1
    return count

def summary_words(list):
    print(f"图片总数量:{len(list)}")
    print(f"各种图片数量:")
    for key,value in count_words(list).items():
        print(f"{key}:{value}个")

def write_csv(path,path_,word_scan_output):
    path_.parent.mkdir(parents=True,exist_ok=True)
    with open(path_, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f,fieldnames=["路径","类型","大小"])
        writer.writeheader()
        writer.writerows(word_scan_output)
    print(f"已写入{path_}")

def choice(road,root):
    print(f"是否更改{road}路径(Y/N)")
    answer = input().strip().upper()
    if answer == "Y":
        print("请输入绝对路径")
        root=Path(input())
        return root
    elif answer == "N":
        print("使用默认路径")
        return root
    else:
        print("无效输入!")
        return choice(road,root)

if __name__ == "__main__":
    print("默认路径传入:../input 传出:../output/summary.csv")
    root=choice("传入",Path("../input"))
    root_=choice("传出", Path("../output/summary.csv"))

    if not root.exists():
        print(f"路径不存在:{root}")
        sys.exit(1)

    try:
        word_scan_output = word_scan(root)
    except OSError as exc:
        print(f"扫描失败:{root}，原因:{exc}")
        sys.exit(1)

    if not word_scan_output:
        print(f"这个目录里没有图片:{root}")
        sys.exit(0)

    summary_words(word_scan_output)

    try:
        write_csv(root,root_,word_scan_output)
    except OSError as e:
        print(f"写入失败:{root_}，原因:{e}")