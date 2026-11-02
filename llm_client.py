import os

from pathlib import Path

from dotenv import load_dotenv

#导入openai模块
from openai import OpenAI

load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.environ.get("DEEPSEEK_API_KEY")


#ai的客户端,起到一个接入的作用
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
    timeout=30.0,
    max_retries=0,
)

def generate_suggestion(text):
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "user", "content": f"{text}请给出两条安全的初步排查建议。"},
        ],
        stream=False,
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("已读取密钥" if api_key else "未配置密钥")
    response = generate_suggestion("投影仪打不开")
    print(response)
