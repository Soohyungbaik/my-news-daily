import datetime
import os

# 오늘 날짜
today = datetime.date.today().strftime('%Y-%m-%d')

# 저장 경로
output_dir = "dailynews"  # 크롤러가 참조하는 폴더
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 예시 뉴스 항목 (운영 시 외부에서 주입)
news_items = [
    # {"title": "젠레스 존 제로 출시", "url": "https://example.com/news1"},
    # {"title": "HoYoverse 신작 공개", "url": "https://example.com/news2"},
]

# HTML 시작
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
        title = item["title"].strip()
        url = item["url"].strip()
        html += f"<li class='item'><a href='{url}'>{title}</a></li>"

html += "</ul></body></html>"

# 저장
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")
