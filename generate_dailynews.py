### ✅ generate_dailynews.py (RSS 기반 자동 뉴스 수집)
import datetime
import os
import feedparser

# 오늘 날짜
today = datetime.date.today().strftime('%Y-%m-%d')

# 저장 경로
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# RSS 피드 (예: 4Gamer 최신 뉴스)
rss_url = "https://www.4gamer.net/rss/viewer/4gamer_latest.xml"
feed = feedparser.parse(rss_url)

# 뉴스 항목 추출
news_items = []
for entry in feed.entries[:10]:
    news_items.append({"title": entry.title, "url": entry.link})

# HTML 생성
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
    html += "<li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공합니다.</i></li>"
else:
    for item in news_items:
        html += f"<li class='item'><a href='{item['url']}'>{item['title']}</a></li>"

html += "</ul></body></html>"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 자동 뉴스 HTML 생성 완료: {output_path}")

