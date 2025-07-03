import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# 오늘 날짜
today = datetime.today().strftime('%Y-%m-%d')

# 실제 뉴스 소스 URL (SC-daily-news 기준)
source_url = f"https://baik1204.github.io/SC-daily-news/{today}.html"
res = requests.get(source_url)

# 소스가 없으면 종료
if res.status_code == 404:
    print("⛔ 뉴스 소스 없음:", source_url)
    exit()

# 뉴스 파싱
soup = BeautifulSoup(res.text, 'html.parser')
items = soup.select('li > a')

# 키워드 불러오기
if os.path.exists('keywords.txt'):
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
else:
    keywords = []

# 매체 리스트 불러오기
if os.path.exists('media_list.txt'):
    with open('media_list.txt', 'r', encoding='utf-8') as f:
        media_list = [line.strip() for line in f if line.strip()]
else:
    media_list = []

# 뉴스 필터링
filtered = []
for item in items:
    title = item.text
    url = item['href']
    keyword_match = any(k in title for k in keywords) if keywords else False
    media_match = any(m in title or m in url for m in media_list) if media_list else False

    if (not keywords and not media_list) or keyword_match or media_match:
        filtered.append((title, url))

# HTML 생성
html = f"""
<html><head><meta charset='UTF-8'>
<style>
  body {{ font-family: sans-serif; }}
  .item {{ margin-bottom: 10px; }}
</style></head>
<body>
<h2>[뉴스레터] {today}</h2>
<ul>
"""

for title, url in filtered:
    html += f"<li class='item'><a href='{url}'>{title}</a></li>"

html += "</ul></body></html>"

# 결과 저장
os.makedirs("docs/daily_html", exist_ok=True)
output_path = f"docs/daily_html/{today}.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 📌 index.html 갱신 (docs/index.html)
index_path = "docs/index.html"
if not os.path.exists(index_path):
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><meta charset='UTF-8'></head><body><h1>뉴스 모음</h1><ul></ul></body></html>")

with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

new_entry = f"<li><a href='daily_html/{today}.html'>{today}</a></li>"
if new_entry not in index_html:
    index_html = index_html.replace("</ul>", f"{new_entry}\n</ul>")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

# ✅ 이메일 발송
msg = MIMEText(html, 'html')
msg['Subject'] = f"[뉴스레터] {today}"
msg['From'] = os.getenv("EMAIL_FROM")
msg['To'] = os.getenv("EMAIL_TO")

try:
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
    server.send_message(msg)
    server.quit()
    print("✅ 이메일 전송 완료")
except Exception as e:
    print("❌ 이메일 전송 실패:", e)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")

