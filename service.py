def create_ticket(tickets, text,status="open"):

    #查找最大id
    max_id = 0
    for ticket in tickets:
        if ticket["id"] > max_id:
            max_id = ticket["id"]
    next_id = max_id + 1

    #status 只允许open和closed,进行一个错误处理
    if status != "open" and status != "closed" :
        raise ValueError("无效属性")
    #返回本次新增的工单
    #通过strip来清理空白字符
    text = text.strip()
    if not text:
        raise ValueError("无效工单")
    new_ticket= {"id": next_id, "text": text,"status": status}
    tickets.append(new_ticket)
    return new_ticket
