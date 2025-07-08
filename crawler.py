import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# 날짜 지정
today = datetime.today().strftime('%Y-%m-%d')
source_url = f"https://soohyungbaik.github.io/my-news-daily/dailynews/{today}.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# HTML 로드 (원격 우선, 실패 시 로컬 대체)
try:
    res = requests.get(source_url, headers=HEADERS)
    res.raise_for_status()
    res.encoding = res.apparent_encoding
    html_text = res.text
    print(f"✅ 원격 뉴스 파일 요청 성공: {source_url}")
except Exception:
    local_path = f"dailynews/{today}.html"
    if os.path.exists(local_path):
        print(f"⚠️ 원격 요청 실패, 로컬 파일로 대체: {local_path}")
        with open(local_path, 'r', encoding='utf-8') as f:
            html_text = f.read()
    else:
        print("❌ 원격 뉴스 요청 실패 및 로컬 파일도 없음")
        html_text = None

# 키워드 및 매체 리스트 불러오기
keywords, media_list = [], []
if os.path.exists('keywords.txt'):
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = [line.strip().lower() for line in f if line.strip()]
if os.path.exists('media_list.txt'):
    with open('media_list.txt', 'r', encoding='utf-8') as f:
        media_list = [line.strip().lower() for line in f if line.strip()]

# HTML 템플릿 시작
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
matching_urls = []

def extract_og_title(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')
            og = soup.find("meta", property="og:title")
            if og and og.get("content"):
                return og["content"].strip()
    except Exception as e:
        print(f"⚠️ 제목 추출 실패: {url} - {e}")
    return None

if html_text:
    soup = BeautifulSoup(html_text, 'html.parser')
    items = soup.select('li > a')

    for item in items:
        raw_title = item.text.strip()
        url = item['href'].strip()
        lower_url = url.lower()

        # URL로 본문 접근 및 키워드 필터링
        try:
            article_res = requests.get(url, headers=HEADERS, timeout=5)
            article_res.encoding = article_res.apparent_encoding
            article_text = article_res.text.lower() if article_res.status_code == 200 else ''
        except:
            article_text = ''

        og_title = extract_og_title(url)
        effective_title = og_title if og_title else raw_title
        lower_title = effective_title.lower()

        keyword_match = any(k in lower_title or k in article_text for k in keywords)
        media_match = any(m in lower_url for m in media_list)

        if keyword_match or media_match:
            filtered.append((effective_title, url))
            matching_urls.append(url)

    if filtered:
        for title, url in filtered:
            html += f"<li class='item'><a href='{url}'>{title}</a></li>"
    else:
        html += "<li class='item'><i>조건에 맞는 뉴스가 없습니다.</i></li>"
        if matching_urls:
            html += "<li><strong>📌 매칭된 URL 목록:</strong></li>"
            for u in matching_urls:
                html += f"<li><a href='{u}'>{u}</a></li>"
        elif keywords:
            html += "<li><strong>📌 오늘의 키워드 목록:</strong></li>"
            for kw in keywords:
                html += f"<li>- {kw}</li>"
else:
    html += "<li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공합니다.</i></li>"
    for kw in keywords:
        html += f"<li>- {kw}</li>"

html += "</ul></body></html>"

# 저장
output_dir = "daily_html"
os.makedirs(output_dir, exist_ok=True)
output_path = f"{output_dir}/{today}.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"✅ 뉴스 HTML 생성 완료: {output_path}")

# index.html 갱신
index_path = "index.html"
if not os.path.exists(index_path):
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><meta charset='UTF-8'><title>뉴스 모음</title></head><body><h1>뉴스 모음</h1><ul>\n<!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->\n</ul></body></html>")

with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

new_entry = f"<li><a href=\"{output_dir}/{today}.html\">{today}</a></li>"
if new_entry not in index_html:
    index_html = index_html.replace("<!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->", f"{new_entry}\n<!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

# 이메일 전송
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

