# ============================================
#  工具 调用
#
# 运行方式(在自己电脑的 cmd / PowerShell 里):
#   先装库:  py -m pip install openai ddgs
#   再运行:  py maid.py
#
# 注意:用 py,不要用 python
# ============================================

from openai import OpenAI
from config import API_KEY
import json
import os
from persona import SYSTEM_PROMPT
from tools import get_time,roll_dice,search_images,web_search,tools,LAST_IMAGES

HISTORY_FILE = "chat_history.json"
LAST_IMAGES = []
MAX_TURNS = 20

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",   # 端点以官方文档为准,偶尔会变
)

# ---- 人物设定、历史存档以及工具调用 ----
try:
    messages=[
        {"role":"system","content":SYSTEM_PROMPT}
    ]
    
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE,"r",encoding="utf-8") as f:
            history = json.load(f)
        messages.extend(history)

    while True:
        user_text = input("master：")
        if user_text in ("exit", "quit", "再见", "退出"):  #输出这些即结束
            break

        messages.append({"role": "user", "content": user_text})
        r = client.chat.completions.create(
            temperature=1.2,
            model="deepseek-flash",
            messages=messages,
            tools=tools
        )
        msg = r.choices[0].message

        if msg.tool_calls:
            tc_list = []         
            for tc in msg.tool_calls:
                tc_list.append({
                    "id": tc.id,
                    "type":"function",
                    "function":{
                        "name":tc.function.name,
                        "arguments":tc.function.arguments
                    }
                })
            messages.append({
                "role":"assistant",
                "content":msg.content,
                "tool_calls":tc_list
            })

            for tc in msg.tool_calls:
                if tc.function.name == "get_time":
                    result = get_time()
                elif tc.function.name == "roll_dice":
                    args = json.loads(tc.function.arguments)
                    result = roll_dice(args["sides"])
                elif tc.function.name == "web_search":
                    args = json.loads(tc.function.arguments)
                    result = web_search(args["query"])
                elif tc.function.name == "search_images":
                    args = json.loads(tc.function.arguments)
                    result = search_images(args["query"])
                messages.append({
                    "role":"tool",
                    "tool_call_id": tc.id,
                    "content":str(result)
                })
                if LAST_IMAGES:
                    messages.append({
                        "role":"user",
                        "content":[
                            {"type":"text","text":"顺便用你的人设点评一下第一张图里是什么内容。"},
                            {"type":"image_url","image_url":{"url":LAST_IMAGES[0]}}
                        ]
                    })
                    LAST_IMAGES.clear()
            r = client.chat.completions.create(
                temperature=1.2,
                model="deepseek-flash",
                messages=messages
            )
            msg = r.choices[0].message

        reply = msg.content
        print("哦鲸鲸:",reply)    
        messages.append({"role": "assistant", "content": reply})
        # ---- 附:这次花了多少 token(就是钱) ----
        print("输入 token:", r.usage.prompt_tokens)
        print("输出 token:", r.usage.completion_tokens)
        print("合计 token:", r.usage.total_tokens)


    recent=messages[1:][-MAX_TURNS*2:]
    while recent and recent[0]["role"] == "tool":
        recent.pop(0)
    with open(HISTORY_FILE,"w",encoding="utf-8")as f:
        json.dump(recent,f,ensure_ascii=False,indent=2)

except Exception as e:
    print("错误类型",type(e).__name__)
    print("调用出错了:",e)

