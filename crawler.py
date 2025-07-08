import os
import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

# 오늘 날짜
today = datetime.today().strftime('%Y-%m-%d')

# 키워드 불러오기
if os.path.exists("keywords.txt"):
    with open("keywords.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip().lower() for line in f if line.strip()]
else:
    keywords = []

# 매체 리스트 불러오기
if os.path.exists("media_list.txt"):
    with open("media_list.txt", "r", encoding="utf-8") as f:
        media_list = [line.strip().lower() for line in f if line.strip()]
else:
    media_list = []

# dailynews JSON 경로
json_path = f"dailynews/{today}.json"

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

filtered = []

if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        news_items = json.load(f)

    for item in news_items:
        title = item["title"].strip()
        url = item["url"].strip()
        full_text = f"{title} {url}".lower()

        keyword_match = any(k in full_text for k in keywords)
        media_match = any(m in url.lower() for m in media_list)

        if keyword_match or media_match:
            filtered.append((title, url))

    if filtered:
        for title, url in filtered:
            html += f"<li class='item'><a href='{url}'>{title}</a></li>"
    else:
        html += "<li class='item'><i>조건에 맞는 뉴스가 없습니다.</i></li>"
        if keywords:
            html += "<li><strong>📌 오늘의 키워드 목록:</strong></li>"
            for k in keywords:
                html += f"<li>- {k}</li>"
else:
    html += "<li class='item'><i>금일 뉴스 데이터가 존재하지 않습니다.</i></li>"
    if keywords:
        html += "<li><strong>📌 오늘의 키워드 목록:</strong></li>"
        for k in keywords:
            html += f"<li>- {k}</li>"

html += "</ul></body></html>"

# 저장 경로
output_dir = "daily_html"
os.makedirs(output_dir, exist_ok=True)
output_path = f"{output_dir}/{today}.html"

# 저장
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

# 이메일 발송
msg = MIMEText(html, "html")
msg["Subject"] = f"[뉴스레터] {today}"
msg["From"] = os.getenv("EMAIL_FROM")
msg["To"] = os.getenv("EMAIL_TO")

try:
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
    server.send_message(msg)
    server.quit()
    print("✅ 이메일 전송 완료")
except Exception as e:
    print("❌ 이메일 전송 실패:", e)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")


