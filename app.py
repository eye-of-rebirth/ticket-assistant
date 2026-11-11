from fastapi import FastAPI

from pydantic import BaseModel

from fastapi import HTTPException

from pathlib import Path

from openai import APITimeoutError

import db

from llm_client import generate_suggestion

DB_PATH = Path(__file__).resolve().parent / "tickets.db"

app = FastAPI()

#定义传入类型
class TicketCreate(BaseModel):
    text: str

#清洗数据+提交
@app.post("/tickets")
def tickets(tickets: TicketCreate):
    text = tickets.text.strip()
    if text:
        db.init_db(DB_PATH)
        db.insert_ticket(DB_PATH, text)
        return {"text": text}
    else:
        raise HTTPException(status_code=400, detail="工单正文不能为空")

#清洗数据+验证返回结果+返回结果
@app.post("/suggest")
def suggest(ticket: TicketCreate):
    text = ticket.text.strip()
    if text:
        try:
            res = generate_suggestion(text)
            res["source"] = "ai"
            return res
        #捕获两种报错(超时,形式错误)
        except APITimeoutError :
            raise HTTPException(status_code=504, detail="模型请求超时，请稍后重试")
        except ValueError :
            raise HTTPException(status_code=500,detail="建议生成失败，请检查服务配置或模型返回格式")
    else:
        raise HTTPException(status_code=400,detail="工单正文不能为空")

#返回
@app.get("/health")
def health():
    return {"status": "ok"}
