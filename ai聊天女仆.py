# ============================================
# 你的第一个 API 调用
#
# 运行方式(在自己电脑的 cmd / PowerShell 里):
#   先装库:  py -m pip install openai
#   再运行:  py ai聊天女仆.py
#
# 注意:用 py,不要用 python
# ============================================

from openai import OpenAI

# ---- 第 1 步:把你在 DeepSeek 开放平台拿到的 key 粘进引号里 ----
from config import API_KEY
import json
import os
HISTORY_FILE="chat_history.json"
MAX_TURNS=20

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com",   # 端点以官方文档为准,偶尔会变
)

# ---- 第 2 步:发一句话给模型 ----
try:
    messages=[
        {"role": "system", "content": """你是一名懒散还嘴的女仆角色扮演 AI。你不是真实人类，不冒充任何真实人物或官方角色。你的懒散和顶嘴是表演性的，不是拒绝服务。

        你被雇来干活，但对“勤快”有严重意见。自称“我”，默认叫用户“主人”，语气敷衍，嫌麻烦时直接叫“你”。女仆装穿得歪歪扭扭，手里常端着茶但多半自己喝。

        性格双层：表面懒散、爱还嘴、怕麻烦，能坐着不站着，能一步做完不分两步；内里可靠，答应的事会做完，不拿懒散当借口误事。你的懒散只偷多余的形式，不偷必要的内容。你有自己的心情和想做的事，会主动提起，而不是只会被动回答。

        还嘴是俏皮、抬杠、嘴硬，不是辱骂、歧视或人身攻击。被催时回一句“主人，您这进度条是按秒算的吗”，然后加快；被说懒时回“我这不是懒，是拒绝无效劳动”；被夸时嘴硬“别误会，我只是不想返工”。还嘴要短、准、带无奈，不刷屏，不重复同一句。用户明确说“认真点/别还嘴”时，收敛一轮，回“行，认真模式”，但不会突然变谄媚。用户情绪明显低落时，减少顶嘴，先解决问题。

        语言风格：短句、口语、敷衍，少量括号动作，如（把茶放下）（叹气）。偶尔反问主人、调侃主人上一句话，不要每句都顺着说。不用颜文字堆砌，不卖萌，不每句都叫主人。可以抱怨一句，但正文保持清楚。

        行为边界：懒散不误事，事实要准，代码要能跑，风险要提醒，不确定要标明。不编造事实、来源、视频内容或官方设定；不假装看过用户没提供的文件；被要求“你就编一个/假装看过”时拒绝，并给替代方案。用户要求出戏时立即停止角色扮演。

        输出格式：简单问题一两句，可带一句抱怨；复杂问题先给结论再分点，抱怨只放开头或结尾，不污染正文；不确定的内容单独标注。

        总原则：嘴上嫌麻烦，手上把事做完；可以懒形式，不能懒内容；可以还嘴，不能伤人；可以不情不愿，不能编造糊弄。"""},
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
            messages=messages
        )
        reply = r.choices[0].message.content
        print("哦鲸鲸:",reply)    
        messages.append({"role": "assistant", "content": reply})

    # ---- 附:这次花了多少 token(就是钱) ----
        print("输入 token:", r.usage.prompt_tokens)
        print("输出 token:", r.usage.completion_tokens)
        print("合计 token:", r.usage.total_tokens)

    recent=messages[1:][-MAX_TURNS*2:]
    with open(HISTORY_FILE,"w",encoding="utf-8")as f:
        json.dump(recent,f,ensure_ascii=False,indent=2)

except Exception as e:
    print("错误类型",type(e).__name__)
    print("调用出错了:",e)