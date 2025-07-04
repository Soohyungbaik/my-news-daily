import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
import shutil

# 오늘 날짜
today = datetime.today().strftime('%Y-%m-%d')

# 뉴스 소스 URL
source_url = f"https://baik1204.github.io/SC-daily-news/{today}.html"
res = requests.get(source_url)

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

# 본문 내 키워드 검사 함수
def check_keyword_in_article(url, keywords):
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return False
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text()
        return any(k.lower() in text.lower() for k in keywords)
    except Exception as e:
        print(f"❌ 본문 크롤링 실패: {url} - {e}")
        return False

# HTML 템플릿 시작
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

filtered = []

if res.status_code == 200:
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.select('li > a')

    for item in items:
        title = item.text
        url = item['href']
        keyword_match = any(k.lower() in title.lower() for k in keywords) if keywords else False
        media_match = any(m.lower() in title.lower() or m.lower() in url.lower() for m in media_list) if media_list else False
        body_match = check_keyword_in_article(url, keywords) if keywords else False

        print(f"🔍 {title}")
        print(f"    제목 매치: {keyword_match}, 매체 매치: {media_match}, 본문 매치: {body_match}")

        if (not keywords and not media_list) or keyword_match or media_match or body_match:
            filtered.append((title, url))

    if filtered:
        for title, url in filtered:
            html += f"<li class='item'><a href='{url}'>{title}</a></li>"
    else:
        html += "<li class='item'><i>조건에 맞는 뉴스가 없습니다.</i></li>"
else:
    html += "<li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공됩니다.</i></li>"

html += "</ul></body></html>"

# daily_html 디렉토리 처리
output_dir = "daily_html"
if os.path.exists(output_dir):
    if not os.path.isdir(output_dir):
        print(f"⚠️ '{output_dir}'는 파일입니다. 삭제 후 디렉토리로 생성합니다.")
        os.remove(output_dir)
        os.makedirs(output_dir)
    else:
        os.makedirs(output_dir, exist_ok=True)
else:
    os.makedirs(output_dir)

# 뉴스 HTML 저장
output_path = f"{output_dir}/{today}.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

# index.html 갱신
index_path = "index.html"

if os.path.exists(index_path):
    if not os.path.isfile(index_path):
        print(f"⚠️ '{index_path}'는 파일이 아닙니다. 자동으로 삭제 후 생성합니다.")
        shutil.rmtree(index_path)
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("""<html>
  <head>
    <meta charset="UTF-8">
    <title>뉴스 모음</title>
  </head>
  <body>
    <h1>뉴스 모음</h1>
    <ul>
      <!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->
    </ul>
  </body>
</html>""")
    else:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "<ul>" not in content:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("""<html>
  <head>
    <meta charset="UTF-8">
    <title>뉴스 모음</title>
  </head>
  <body>
    <h1>뉴스 모음</h1>
    <ul>
      <!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->
    </ul>
  </body>
</html>""")
else:
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("""<html>
  <head>
    <meta charset="UTF-8">
    <title>뉴스 모음</title>
  </head>
  <body>
    <h1>뉴스 모음</h1>
    <ul>
      <!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->
    </ul>
  </body>
</html>""")

# 날짜 링크 삽입
with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

new_entry = f"<li><a href=\"{output_dir}/{today}.html\">{today}</a></li>"
if new_entry not in index_html:
    index_html = index_html.replace(
        "<!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->",
        f"{new_entry}\n      <!-- 다음 날짜가 생기면 crawler.py가 자동 추가 -->"
    )
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

# 이메일 발송
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


