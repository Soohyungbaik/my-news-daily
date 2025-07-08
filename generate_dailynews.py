import datetime
import os
import re
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

today = datetime.date.today().strftime('%Y-%m-%d')
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 키워드 리스트
keywords = []
if os.path.exists('keywords.txt'):
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = [line.strip().lower() for line in f if line.strip()]

# 매체 리스트
media_list = []
if os.path.exists('media_list.txt'):
    with open('media_list.txt', 'r', encoding='utf-8') as f:
        media_list = [line.strip().lower() for line in f if line.strip()]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

news_items = []

def get_article_title(url):
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                return og_title["content"].strip()
        else:
            print(f"⚠️ 헤드라인 응답코드 {res.status_code}: {url}")
    except Exception as e:
        print(f"⚠️ 제목 추출 실패: {url} - {e}")
    return None

def collect_news_from(sites, region, selector="a[href]"):
    print(f"🟡 [{region}] 수집 시작")
    match_count = 0
    for url in sites:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200:
                print(f"⚠️ [{region}] {url} - 응답 코드 {res.status_code} (계속 진행)")
            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select(selector)
            for link in links:
                raw_text = link.get_text(strip=True)
                href = link.get("href", "")
                if not href.startswith("http"):
                    continue

                title = get_article_title(href)
                lower_title = (title or raw_text).lower()
                lower_href = href.lower()

                keyword_match = any(k in lower_title for k in keywords)
                media_match = any(m in lower_href for m in media_list)

                if keyword_match or media_match:
                    final_title = title if title else raw_text
                    news_items.append({"title": final_title, "url": href})
                    match_count += 1
                else:
                    print(f"[{region}] 미매칭: {raw_text}")
        except Exception as e:
            print(f"❌ [{region}] {url} - 예외 발생: {e}")
    print(f"✅ [{region}] {url} - 매칭 {match_count}건")

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

# 실행
collect_news_from(korea_sites, "한국")
collect_news_from(japan_sites, "일본")
collect_news_from(china_sites, "중국")

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
    html += "<li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공됩니다.</i></li>"
    for kw in keywords:
        html += f"<li>- {kw}</li>"
else:
    for item in news_items:
        html += f"<li class='item'><a href='{item['url']}'>{item['title']}</a></li>"

html += "</ul></body></html>"

with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")

