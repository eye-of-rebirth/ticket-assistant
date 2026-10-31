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

没有第三方依赖。程序使用相对文件路径，请从项目目录运行；PyCharm的工作目录也应设置为项目目录，解释器选择项目.venv。

## 使用

- 输入普通问题：创建工单（id、text、status），状态为open，并立即保存到tickets.json。
- 输入“查看”：逐条显示已有工单；没有记录时显示“暂无工单”。查看不创建工单、不写文件。
- 输入“退出”：结束程序。
- 空白输入被拒绝；首尾空白会先移除。“查看”和“退出”是保留命令。
- ID使用已有最大ID加1，空列表从1开始；退出重启后可继续读取和新增。

例如输入“投影仪无法启动”，再输入“查看”，会看到新记录及固定建议。当前输出为简单文本或字典形式。

## 文件与边界

- main.py：输入循环、命令分派、工单创建与ID生成。
- storage.py：load_tickets(path)读取并返回列表，save_tickets(tickets, path)写入列表；文本读写明确使用UTF-8。
- tickets.example.json：空列表示例；tickets.json是本地运行数据，不提交。
- assessment.py：独立于主入口的筛选练习，不是自动化测试套件。
- docs/：学习进度与技能证据，由Sol维护。

已通过助手在临时数据上的实际运行检查：中文读写、退出重启保留、非连续ID下新增不重复、空白不入库、逐条查看及空列表提示、查看不改文件。用户实现与AI帮助程度见docs/progress.md，不能据运行成功认定全部能力独立通过。

尚未处理缺失文件、损坏JSON、写入失败及并发修改；使用前需初始化文件。文件保存使用覆盖写入，不具备原子写入保障。尚未提供查询建议、真实模型调用或公网部署。
