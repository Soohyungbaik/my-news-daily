import datetime
import os
import re
import requests
from bs4 import BeautifulSoup

today = datetime.date.today().strftime('%Y-%m-%d')
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

keywords = [
    # 한국어
    "서브컬처", "수집형", "미소녀", "게임쇼", "굿스마일", "부스", "콜라보", "런칭", "업계 동향", "시장 보고서",
    "니케", "블루아카이브", "원신", "젠레스 존 제로", "스타레일", "붕괴",
    # 일본어
    "崩壊：スターレイル", "ブルーアーカイブ", "ゼンレスゾーンゼロ", "ホヨバース", "ゲームショウ", "二次創作", "ガチャ", "美少女",
    # 중국어
    "米哈游", "崩坏", "蓝档案", "原神", "少女收集", "二次元", "集换式", "合作", "发售", "虚拟主播",
    # 영어
    "Zenless Zone Zero", "Blue Archive", "Nikke"
]

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
    except Exception as e:
        print(f"⚠️ 제목 추출 실패: {url} - {e}")
    return None

def collect_news_from(sites, region, selector="a[href]"):
    print(f"🟡 [{region}] 수집 시작")
    match_count = 0
    for url in sites:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 403:
                print(f"❌ [{region}] {url} - 응답 코드 403")
                continue
            elif res.status_code != 200:
                print(f"❌ [{region}] {url} - 응답 코드 {res.status_code}")
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            links = soup.select(selector)
            for link in links:
                raw_text = link.get_text(strip=True)
                href = link.get("href", "")
                if not href.startswith("http"):
                    continue

                # 키워드 포함 여부 확인 (텍스트나 URL 기준)
                matched = any(k.lower() in raw_text.lower() or k.lower() in href.lower() for k in keywords)
                if matched:
                    title = get_article_title(href)
                    if title:
                        news_items.append({"title": title, "url": href})
                        match_count += 1
                    else:
                        print(f"[{region}] 미매칭(제목 추출 실패): {raw_text}")
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
