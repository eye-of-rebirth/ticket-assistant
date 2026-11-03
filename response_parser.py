import json

def parse_response(raw_text):
    try:
        data = json.loads(raw_text)

    except json.JSONDecodeError:
        raise ValueError("模型返回的不是有效JSON")

    if not isinstance(data, dict) :
        raise ValueError("模型返回的必须是JSON对象")

    if "category" not in data:
        raise ValueError("缺少category")

    if "summary" not in data:
        raise ValueError("缺少summary")

    if "suggestion" not in data:
        raise ValueError("缺少suggestion")

    #进行一次洗净字典数据操作
    for field in ("category", "summary", "suggestion"):
        value = data[field]
        if not isinstance(value, str):
            raise ValueError(f"{field}必须是字符串")
        else:
            value = value.strip()
        if value == "":
            raise ValueError(f"{field}不能为空")
        data[field] = value

    return data

if __name__ == "__main__":
    res = parse_response('{"category": "设备故障", "summary": "投影仪无法启动", "suggestion": "检查电源连接"}')
    print(res)