from pathlib import Path

from storage import load_tickets, save_tickets

from service import create_ticket

#把启动流程放进函数，导入这个文件时不会自动运行
def main():
    #读取本地的工单文件
    #固定为main.py同目录下的数据文件，避免终端位置影响读写
    path = Path(__file__).resolve().parent / "tickets.json"
    tickets = load_tickets(path)

    #读取用户问题,并写入本地工单,只有在退出后才结束
    #要求防止空白输入,查看已有工单,退出的功能
    user_input = ""
    while True:
        user_input = input("请输入问题").strip()#此处.strip()去掉首尾空白
        if not user_input:
            print("问题不能为空")
        elif user_input =="退出":
            print("再见")
            break
        #要求逐条展示工单
        elif user_input == "查看":
            if not tickets:
                print("暂无工单")
            else:
                for ticket in tickets:
                    print(ticket)
        else :
            print(f"{user_input}\n固定建议")
            #写一个错误处理来处理空白无效工单
            try:
            #接入service中的新建工单函数
                new_ticket = create_ticket(tickets, user_input)
            except ValueError as e:
                print(e)
            # 只要未报错,数据有效就把更新后的列表写入本地文件
            else:
                save_tickets(tickets, path)



#只有直接运行main.py时才启动程序
if __name__ == "__main__":
    main()
