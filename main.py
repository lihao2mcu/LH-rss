import os
import requests
from feedgen.feed import FeedGenerator

# 这里配置你的 Google Hack 指令
# 示例：搜索过去24小时内关于“量子计算”的PDF文档，排除特定站点
QUERY = 'intitle:"量子计算" filetype:pdf -site:youtube.com'
API_KEY = os.getenv('SERPER_API_KEY') # 从 GitHub Secrets 获取密钥

def fetch_data():
    url = "https://google.serper.dev/search"
    payload = {"q": QUERY, "tbs": "qdr:d"} # qdr:d 表示最近24小时
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get('organic', [])

def generate_rss(items):
    fg = FeedGenerator()
    fg.title('My Google Hacks Monitor')
    fg.link(href='https://github.com', rel='alternate')
    fg.description('Automated Search Results')
    
    for item in items:
        fe = fg.add_entry()
        fe.title(item['title'])
        fe.link(href=item['link'])
        fe.description(item.get('snippet', ''))
    
    os.makedirs('output', exist_ok=True)
    fg.rss_file('output/feed.xml')

if __name__ == "__main__":
    results = fetch_data()
    generate_rss(results)
