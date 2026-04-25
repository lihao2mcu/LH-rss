import os
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime

# 从 GitHub Secrets 获取密钥
API_KEY = os.getenv('SERPER_API_KEY')

def fetch_data(query):
    url = "https://google.serper.dev/search"
    # tbs:qdr:d 表示搜索过去 24 小时
    payload = {"q": query, "tbs": "qdr:d"}
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, headers=headers, json=payload)
        return response.json().get('organic', [])
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def generate_rss(items, filename, feed_title):
    fg = FeedGenerator()
    fg.title(feed_title)
    fg.link(href='https://github.com/lihao2mcu/LH-rss', rel='alternate')
    fg.description(f'Automated Monitor for {feed_title}')

    if not items:
        # 如果没有结果，创建一个占位条目，防止 RSS 报错
        fe = fg.add_entry()
        fe.title("今日暂无更新")
        fe.link(href="https://github.com")
        fe.description("过去一段时间内未搜索到相关高价值信息")
    else:
        for item in items:
            fe = fg.add_entry()
            fe.title(item.get('title', '无标题'))
            fe.link(href=item.get('link', '#'))
            fe.description(item.get('snippet', ''))

    os.makedirs('output', exist_ok=True)
    fg.rss_file(f'output/{filename}')
    print(f"已生成文件: output/{filename}")

if __name__ == "__main__":
    # 获取今天是本年的第几天，用于判断“两天一更”
    day_of_year = datetime.now().timetuple().tm_yday
    
    # 任务清单配置
    # 频率说明：'daily' 每次运行都执行，'bi-daily' 只有在奇数天执行
    tasks = [
        {"name": "BTC Monitor", "query": "BTC filetype:pdf", "file": "btc.xml", "freq": "daily"},
        {"name": "Bitcoin News", "query": "比特币 深度分析", "file": "bitcoin.xml", "freq": "daily"},
        {"name": "Duan Yongping Monitor", "query": "段永平 投资观点 OR 问答", "file": "dyp.xml", "freq": "bi-daily"},
        {"name": "Buffett Monitor", "query": "Warren Buffett research report filetype:pdf", "file": "buffett.xml", "freq": "bi-daily"}
    ]

    for task in tasks:
        # 如果是两天一更的任务，且今天是偶数天，则跳过（实现隔天更新）
        if task["freq"] == "bi-daily" and day_of_year % 2 == 0:
            print(f"任务 {task['name']} 今日休息，隔日再战")
            continue
        
        print(f"正在执行任务: {task['name']}")
        results = fetch_data(task["query"])
        generate_rss(results, task["file"], task["name"])
