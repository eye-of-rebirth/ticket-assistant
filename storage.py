"""工单列表的JSON文件读写。"""

import json


# 需要执行一个判断JSON文件是否存在的操作
def load_tickets(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_tickets(tickets, path):
    """覆盖保存工单列表；调用者负责提供有效数据。"""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(tickets, file, ensure_ascii=False, indent=2)
        file.write("\n")
