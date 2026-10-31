# 工单助手 CLI

面向小团队的学习项目，使用模拟工单数据。当前支持创建、查看和JSON文件保存；建议是固定文字，尚未接入模型或文档查询。

## 首次运行（Windows / PowerShell）

在项目目录中执行：

```powershell
python -m venv .venv
```

首次运行前需要初始化数据文件。下面的命令仅在文件不存在时复制空列表示例，已有工单不会被覆盖：

```powershell
if (-not (Test-Path -LiteralPath tickets.json)) { Copy-Item -LiteralPath tickets.example.json -Destination tickets.json }
.\.venv\Scripts\python.exe main.py
```

没有第三方依赖。已在Python 3.13验证，其他版本尚未核验。上面的命令应在项目目录运行；程序的数据文件固定在main.py旁，避免从其他目录启动时读错文件。PyCharm解释器选择项目.venv。

## 使用

- 输入普通问题：创建工单（id、text、status），状态为open，并立即保存到tickets.json。
- 输入“查看”：逐条显示已有工单；没有记录时显示“暂无工单”。查看不创建工单、不写文件。
- 输入“退出”：结束程序。
- 空白输入被拒绝；首尾空白会先移除。“查看”和“退出”是保留命令。
- ID使用已有最大ID加1，空列表从1开始；退出重启后可继续读取和新增。

例如在空工单文件上运行：

```text
请输入问题投影仪无法启动
投影仪无法启动
固定建议
请输入问题查看
{'id': 1, 'text': '投影仪无法启动', 'status': 'open'}
请输入问题退出
再见
```

建议仅为固定示例，不根据输入诊断原因。

## 文件与边界

- main.py：输入循环、命令分派、工单创建与ID生成。
- storage.py：load_tickets(path)读取并返回列表，save_tickets(tickets, path)写入列表；文本读写明确使用UTF-8。
- tickets.example.json：空列表示例；tickets.json是本地运行数据，不提交。
- assessment.py：独立于主入口的筛选练习，不是自动化测试套件。
- tests/test_cli.py：基于标准库unittest的回归检查，由AI辅助编写。
学习进度与技能记录保留在本地docs/，不随当前版本发布。

## 回归检查

在项目目录执行：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

6项检查覆盖中文保存读取、退出重启与非连续ID、空白和空列表、创建后查看、查看不改文件，以及导入入口不会自动读取或提问。使用临时项目与模拟文件，不覆盖本地tickets.json。

## 学习与AI辅助说明

这是正在迭代的学习项目。核心CLI与持久化由学习者在提示和局部示例帮助下实现；首次上传整理中的入口封装、数据路径、少量注释修正、文档和回归测试由AI辅助完成，保留学习者原有主体代码与变量命名。项目成果与个人独立能力分开记录，详细学习记录保留在本地。当前版本是CLI源码仓库，尚未部署为网络服务。

## 当前限制

尚未处理缺失文件、损坏JSON、写入失败及并发修改；使用前需初始化文件。文件保存使用覆盖写入，不具备原子写入保障。尚未提供查询建议、真实模型调用或公网部署。
