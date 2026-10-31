from pathlib import Path

from storage import load_tickets, save_tickets


#把启动流程放进函数，导入这个文件时不会自动运行
def main():
    #读取本地的工单文件
    #固定为main.py同目录下的数据文件，避免终端位置影响读写
    path = Path(__file__).resolve().parent / "tickets.json"
    tickets = load_tickets(path)

    #读取用户问题,并写入本地工单,只有在退出后才结束
    #要求防止空白输入,查看已有工单,退出的功能
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

            # 查找最大id，再加1，避免已有id不连续时生成重复id。
            max_id = 0
            for ticket in tickets:
                if ticket["id"] > max_id:
                    max_id = ticket["id"]
            next_id = max_id + 1

            #先把新工单加入内存中的列表
            tickets.append({"id":next_id,"text":promber,"status":"open"})
            #再把更新后的列表写入本地文件
            save_tickets(tickets, path)


#只有直接运行main.py时才启动程序
if __name__ == "__main__":
    main()
