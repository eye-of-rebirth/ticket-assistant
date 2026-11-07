import os

from pathlib import Path

from dotenv import load_dotenv

from response_parser import parse_response

#导入openai模块
from openai import OpenAI

from openai import APITimeoutError


#把.env中的apikey保存到环境变量
load_dotenv(Path(__file__).resolve().parent / ".env")


def generate_suggestion(text):
    #读取环境变量中的apikey
    api_key = os.environ.get("DEEPSEEK_API_KEY")

    #如果apikey为空结束函数
    if not api_key:
        raise ValueError("未配置DEEPSEEK_API_KEY")

    # ai的客户端,起到一个接入的作用
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
        timeout=30.0,
        max_retries=0,
    )

    def send_request():
        response = client.chat.completions.create(
            model="deepseek-flash",
            messages=[
                {"role":"system", "content":(
                "你是工单助手，根据问题生成分类、简短摘要和安全的初步排查建议。"
                "只返回JSON对象，必须包含category、summary、suggestion三个字段，"
                "值均为非空字符串。不要Markdown代码围栏或额外说明。"
                "summary最多80字符"
            ),},
                {"role": "user", "content": f"{text}请给出两条安全的初步排查建议。"},
            ],
            stream=False,
        )
        return parse_response(response.choices[0].message.content)
    try:
        response = send_request()
    except APITimeoutError as e:
        response = send_request()

    return response

if __name__ == "__main__":
    response = generate_suggestion("投影仪打不开")
    print(response)
