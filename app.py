from fastapi import FastAPI

from pydantic import BaseModel

from fastapi import HTTPException

from pathlib import Path

import db

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

#返回
@app.get("/health")
def health():
    return {"status": "ok"}
