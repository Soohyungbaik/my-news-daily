import datetime
import os
import feedparser

# 오늘 날짜
today = datetime.date.today().strftime('%Y-%m-%d')

# 저장 경로
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 키워드 목록
keywords = [
    "hoyoverse", "블루아카이브", "원신", "nikke", "goddess of victory: nikke",
    "zenless zone zero", "젠레스 존 제로", "서브컬처", "수집형", "수집형 rpg", "rpg",
    "米哈游", "崩壊：スターレイル", "스타레일", "붕괴", "미소녀", "벽람항로", "azur lane", "니케",
    "vtuber", "굿스마일", "코스프레", "부스", "콜라보", "2차 창작", "업계 동향", "시장 보고서",
    "게임쇼", "런칭", "bluearchive"
]
keywords = [k.lower() for k in keywords]

# 참조할 RSS 피드 URL (서브컬처/게임 관련)
rss_urls = [
    "https://www.inven.co.kr/webzine/news/rss",             # 인벤
    "https://www.thisisgame.com/rss/news.xml",              # 디스이즈게임
    "https://www.4gamer.net/rss/index.xml",                 # 4gamer
    "https://gamebiz.jp/?mod=rss_feed",                     # 게임비즈
    "https://gamer.ne.jp/rss.xml"                           # 게이머
]

# 뉴스 수집
news_items = []
for url in rss_urls:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue
        text = f"{title} {link}".lower()
        if any(k in text for k in keywords):
            news_items.append({"title": title, "url": link})

# HTML 작성
html = f"""<html><head><meta charset='UTF-8'>
<style>
  body {{ font-family: sans-serif; }}
  .item {{ margin-bottom: 10px; }}
</style></head>
<body>
<h2>[뉴스레터] {today}</h2>
<ul>
"""

if not news_items:
    html += "<li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공됩니다.</i></li>"
else:
    for item in news_items:
        title = item["title"]
        url = item["url"]
        html += f"<li class='item'><a href='{url}'>{title}</a></li>"

html += "</ul></body></html>"

# 저장
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")

