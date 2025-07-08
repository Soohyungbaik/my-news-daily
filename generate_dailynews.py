import datetime
import os
import re
import requests
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings

# 경고 무시
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

today = datetime.date.today().strftime('%Y-%m-%d')
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 키워드 불러오기
keywords = []
if os.path.exists("keywords.txt"):
    with open("keywords.txt", "r", encoding="utf-8") as f:
        keywords = [line.strip().lower() for line in f if line.strip()]

# 매체 필터
media_list = []
if os.path.exists("media_list.txt"):
    with open("media_list.txt", "r", encoding="utf-8") as f:
        media_list = [line.strip().lower() for line in f if line.strip()]

news_items = []

# 요청 헤더
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ko,en;q=0.9",
    "Referer": "https://www.google.com"
}

# 제목 추출 함수
def get_article_title(url):
    try:
        with requests.Session() as s:
            res = s.get(url, headers=headers, timeout=7)
            res.encoding = res.apparent_encoding
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    return og_title["content"].strip()
                elif soup.title and soup.title.string:
                    return soup.title.string.strip()
    except Exception as e:
        print(f"⚠️ 제목 추출 실패: {url} - {e}")
    return None

# 뉴스 수집 함수
def collect_news_from(sites, region, selector="a[href]"):
    print(f"🟡 [{region}] 수집 시작")
    match_count = 0
    for url in sites:
        try:
            with requests.Session() as s:
                res = s.get(url, headers=headers, timeout=7)
                if res.status_code >= 400:
                    print(f"⚠️ [{region}] {url} - 응답 코드 {res.status_code} (계속 진행)")
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, "html.parser")
                links = soup.select(selector)
                for link in links:
                    text = link.get_text(strip=True)
                    href = link.get("href", "")
                    if not href.startswith("http"):
                        continue

                    lower_text = text.lower()
                    lower_url = href.lower()

                    keyword_match = any(k in lower_text or k in lower_url for k in keywords)
                    media_match = any(m in lower_url for m in media_list)

                    if keyword_match or media_match:
                        title = get_article_title(href)
                        if title and len(title) > 5:
                            news_items.append({"title": title, "url": href})
                            match_count += 1
                        else:
                            print(f"[{region}] 제목 누락/짧음: {href}")
        except Exception as e:
            print(f"❌ [{region}] {url} - 예외 발생: {e}")
    print(f"✅ [{region}] 수집 완료 - 매칭 {match_count}건")

# 사이트 목록
korea_sites = [
    "https://www.inven.co.kr/webzine/news/",
    "https://www.thisisgame.com/webzine/news/nboard/263/?category=2",
    "https://www.ezyeconomy.com/news/articleList.html?sc_sub_section_code=S2N71&view_type=sm"
]

japan_sites = [
    "https://gamebiz.jp/news",
    "https://www.4gamer.net/",
    "https://www.gamer.ne.jp/",
    "https://gnn.gamer.com.tw/index.php?k=4"
]

china_sites = [
    "https://www.17173.com/",
    "https://www.youxituoluo.com/",
    "https://www.163.com/dy/media/T1439279320876.html",
    "https://news.qq.com/"
]

# 수집 실행
collect_news_from(korea_sites, "한국")
collect_news_from(japan_sites, "일본")
collect_news_from(china_sites, "중국")

# HTML 출력
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
    for kw in keywords:
        html += f"<li>- {kw}</li>"
else:
    for item in news_items:
        html += f"<li class='item'><a href='{item['url']}'>{item['title']}</a></li>"

html += "</ul></body></html>"

# 저장
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")


