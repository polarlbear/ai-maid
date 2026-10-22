import json
import random
import datetime
from ddgs import DDGS

LAST_IMAGES = []

def get_time():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")

def roll_dice(sides):
    return random.randint(1,sides)

def web_search(query):
    results = DDGS(timeout=30,proxy="http://127.0.0.1:7897").text(query,region="cn-zh",max_results=5)
    lines = []
    for r in results:
        title = r.get("title","无标题")
        url = r.get("href","")
        snippet = r.get("body","")
        lines.append(f"{title}\n{url}\n{snippet}\n")
    return "\n".join(lines)

def search_images(query):
    global LAST_IMAGES
    LAST_IMAGES.clear()
    results = DDGS(timeout=30,proxy="http://127.0.0.1:7897").images(query,region="cn-zh",max_results=3)
    lines = []
    for r in results:
        title = r.get("title","无标题")
        img = r.get("image","")
        page = r.get("url","")
        LAST_IMAGES.append(img)
        lines.append(f"{title}\n图片链接:{img}\n来源网页:{page}")
    return "\n".join(lines)

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
    },
    {
        "type":"function",
        "function":{
            "name":"web_search",
            "description":"当主人问到实时信息、新闻、或者你不确定答案的问题时，用这个工具去网上搜索。",
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description":"要搜索的关键词"
                    }
                },
                "required":["query"]
            }
        }

    },
    {
        "type":"function",
        "function":{
            "name":"search_images",
            "description":"当主人想找图片、表情包、壁纸、照片参考时，用这个工具搜图，返回图片链接。",
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description":"要搜索的关键词"
                    }
                },
                "required":["query"]
            }
        }
    }
]
