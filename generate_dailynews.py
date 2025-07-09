import datetime
import os
import re
import requests
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning
import warnings

# XML 경고 무시
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

today = datetime.date.today().strftime('%Y-%m-%d')
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 키워드
keywords = [
    # 한국어
    "서브컬처", "수집형", "미소녀", "게임쇼", "굿스마일", "코스프레", "부스", "콜라보", "런칭", "업계 동향", "시장 보고서",
    "니케", "블루아카이브", "원신", "젠레스 존 제로", "스타레일", "붕괴",
    # 일본어
    "崩壊：スターレイル", "ブルーアーカイブ", "ゼンレスゾーンゼロ", "ホヨバース", "ゲームショウ", "二次創作", "ガチャ", "美少女",
    # 중국어
    "米哈游", "崩坏", "蓝档案", "原神", "少女收集", "二次元", "集换式", "合作", "发售", "虚拟主播",
    # 영어
    "Zenless Zone Zero", "Blue Archive", "Nikke"
]

# media_list 필터
media_list = []
if os.path.exists('media_list.txt'):
    with open('media_list.txt', 'r', encoding='utf-8') as f:
        media_list = [line.strip().lower() for line in f if line.strip()]

news_items = []

# 🔍 기사 제목 추출 함수
def get_article_title(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        if res.status_code == 200:
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'html.parser')

            # ✅ 17173 특화 처리
            if "17173.com" in url:
                h1 = soup.find("h1")
                if h1 and h1.text.strip():
                    return h1.text.strip()
                title_tag = soup.find("title")
                if title_tag:
                    return title_tag.text.strip()

            # ✅ 일반적인 og:title 처리
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                return og_title["content"].strip()
    except Exception as e:
        print(f"⚠️ 제목 추출 실패: {url} - {e}")
    return None

# 🔍 뉴스 수집 함수
def collect_news_from(sites, region, selector="a[href]", max_links=30):
    print(f"🟡 [{region}] 수집 시작")
    match_count = 0
    for url in sites:
        try:
            res = requests.get(url, headers=HEADERS, timeout=5)
            if res.status_code != 200:
                print(f"❌ [{region}] {url} - 응답 코드 {res.status_code} (계속 진행)")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select(selector)
            checked = 0

            for link in links:
                if checked >= max_links:
                    break
                raw_text = link.get_text(strip=True)
                href = link.get("href", "").strip()
                if not href.startswith("http"):
                    continue
                checked += 1

                # 키워드 또는 매체 기준 필터링
                matched = any(k.lower() in raw_text.lower() or k.lower() in href.lower() for k in keywords) or \
                          any(m in href.lower() for m in media_list)
                if matched:
                    title = get_article_title(href)
                    if title:
                        news_items.append({"title": title, "url": href})
                        match_count += 1
                    else:
                        print(f"[{region}] 제목 추출 실패로 제외: {href}")
        except Exception as e:
            print(f"❌ [{region}] {url} - 예외 발생: {e}")
    print(f"✅ [{region}] 수집 완료 - 매칭 {match_count}건")

# ✅ 수집 대상 사이트
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

# ✅ 뉴스 수집 실행
collect_news_from(korea_sites, "한국")
collect_news_from(japan_sites, "일본")
collect_news_from(china_sites, "중국")

# ✅ HTML 생성
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
