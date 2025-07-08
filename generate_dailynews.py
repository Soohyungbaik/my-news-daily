import os
import json
import datetime
from googletrans import Translator

# 날짜 설정
today = datetime.date.today().strftime('%Y-%m-%d')
json_path = f"dailynews/{today}.json"
output_path = f"dailynews/{today}.html"
os.makedirs("dailynews", exist_ok=True)

# 뉴스 데이터 불러오기
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        news_items = json.load(f)
else:
    news_items = []

# 번역기 초기화
translator = Translator()

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

# 뉴스 본문 작성
if not news_items:
    html += "<li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공됩니다.</i></li>"
else:
    for item in news_items:
        title = item["title"]
        url = item["url"]
        try:
            translated = translator.translate(title, dest='ko').text
        except Exception:
            translated = title  # 번역 실패 시 원문 유지

        html += f"<li class='item'><a href='{url}'>{translated}</a></li>"

html += "</ul></body></html>"

# 저장
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML 생성 완료: {output_path}")


