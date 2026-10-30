promber = ""
while True:
    promber = input("请输入问题").strip()
    if not promber:
        print("问题不能为空")
    elif promber =="退出":
        print("再见")
        break
    else :
        print(f"{promber}\n固定建议")
