from pathlib import Path

from openai import APIError

from openai import APITimeoutError

from storage import load_tickets, save_tickets

from service import create_ticket

from llm_client import generate_suggestion

import json

#把启动流程放进函数，导入这个文件时不会自动运行
def main():
    #读取本地的工单文件
    #固定为main.py同目录下的数据文件，避免终端位置影响读写
    path = Path(__file__).resolve().parent / "tickets.json"
    #使用try,except语句来判断json有没有出错,出错后结束进程
    try:
        tickets = load_tickets(path)
    #如果json文件损害
    except json.JSONDecodeError:
        print("工单文件格式损坏,请检查tickets.json")
        return
    #如果没有读取权限
    except PermissionError:
        print("没有权限读取工单文件")
        return


    #读取用户问题,并写入本地工单,只有在退出后才结束
    #要求防止空白输入,查看已有工单,退出的功能
    user_input = ""
    while True:
        user_input = input("请输入问题").strip()#此处.strip()去掉首尾空白
        #防空白内容
        if not user_input:
            print("问题不能为空")
        #退出功能
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
            #写一个错误处理来处理空白无效工单
            try:
            #接入service中的新建工单函数
                new_ticket = create_ticket(tickets, user_input)
            except ValueError as e:
                print(e)
            # 只要未报错,数据有效就把更新后的列表写入本地文件
            else:
                save_tickets(tickets, path)
                try:
                    llm_client = generate_suggestion(user_input)
                except APITimeoutError:
                    print("工单已保存，建议生成超时")
                except APIError :
                    print("工单已保存，建议生成失败，请稍后再试")
                except ValueError :
                    print("工单已保存，但模型返回格式无效，请稍后再试")
                else:
                    print(f"分类:{llm_client["category"]}")
                    print(f"摘要:{llm_client["summary"]}")
                    print(f"建议:{llm_client["suggestion"]}")


#只有直接运行main.py时才启动程序
if __name__ == "__main__":
    main()
