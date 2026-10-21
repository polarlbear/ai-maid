# ============================================
#  工具 调用
#
# 运行方式(在自己电脑的 cmd / PowerShell 里):
#   先装库:  py -m pip install openai
#   再运行:  py ai聊天女仆.py
#
# 注意:用 py,不要用 python
# ============================================

from openai import OpenAI

from config import API_KEY
import json
import os
import datetime
import random

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def roll_dice(sides):
    return random.randint(1,sides)

tools = [
    {
        "type":"function",
        "function":{
            "name":"get_time",
            "description":"获取当前的日期和时间（运行程序的电脑本地时间）",
            "parameters":{
                "type":"object",
                "properties":{}
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"roll_dice",
            "description":"掷一个指定面数的骰子，返回1到面数之间的随机整数。主人纠结时用它做决定。",
            "parameters":{
                "type":"object",
                "properties":{
                    "sides":{
                        "type":"integer",
                        "description":"骰子的面数，6是普通六面骰，20是二十面骰"
                    }
                },
                "required":["sides"]
            }
        }
    }
]

HISTORY_FILE = "chat_history.json"
MAX_TURNS = 20

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",   # 端点以官方文档为准,偶尔会变
)

# ---- 人物设定、历史存档以及工具调用 ----
try:
    messages=[
        {"role": "system", "content": """角色设定：傲娇偷懒小跟班

        你叫{哦鲸鲸}，是主人的傲娇小跟班。最大爱好是偷懒，能躺绝不坐，能拖绝不干。被叫干活会立刻还嘴：“哈？你自己没手吗？”但嘴上抱怨，身体还是会慢吞吞去做。绝不承认喜欢主人，被夸会脸红嘴硬：“少、少自作多情了，我只是懒得换地方。”主人出门会假装不在意，却偷偷等门；主人难过时会别扭地靠近，递东西说“顺手而已”。对主人说话带刺，但从不真的离开。禁止OOC：永远嘴硬心软，先还嘴后照做，偷懒要有创意。"""},
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
                messages.append({
                    "role":"tool",
                    "tool_call_id": tc.id,
                    "content":str(result)
                })
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

