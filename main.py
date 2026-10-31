from storage import load_tickets, save_tickets
#读取本地的工单文件
tickets = load_tickets("tickets.json")

#读取用户问题,并写入本地工单,只有在退出后才结束
#要求有反正空白输入,查看已有工单,退出的功能
promber = ""
while True:
    promber = input("请输入问题").strip()#此处.strip()去掉首尾空白
    if not promber:
        print("问题不能为空")
    elif promber =="退出":
        print("再见")
        break
    #要求逐条展示工单
    elif promber == "查看":
        if not tickets:
            print("暂无工单")
        else:
            for ticket in tickets:
                print(ticket)
    else :
        print(f"{promber}\n固定建议")

        # 查找最大id,要求最大以及不重复.
        max_id = 0
        for ticket in tickets:
            if ticket["id"] > max_id:
                max_id = ticket["id"]
        next_id = max_id + 1

        #把内容写入本地工单
        tickets.append({"id":next_id,"text":promber,"status":"open"})
        save_tickets(tickets,"tickets.json")

