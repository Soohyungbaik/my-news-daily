import datetime
import os
import re
import requests
from bs4 import BeautifulSoup

today = datetime.date.today().strftime('%Y-%m-%d')
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 키워드 리스트
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

news_items = []

def clean_title(raw):
    clean = re.split(r'[|｜\-–—:\[\]]', raw)[0].strip()
    return clean[:20] + "..." if len(clean) > 20 else clean

def collect_news_from(sites, region, selector="a[href]"):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    print(f"🟡 [{region}] 수집 시작")
    for url in sites:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                res.encoding = res.apparent_encoding
                soup = BeautifulSoup(res.text, "html.parser")
                links = soup.select(selector)

                matched = 0
                for link in links:
                    raw_title = link.get_text(strip=True)
                    title = clean_title(raw_title)
                    href = link.get("href", "")
                    if not href.startswith("http") or not title:
                        continue
                    if any(k.lower() in title.lower() for k in keywords):
                        news_items.append({"title": title, "url": href})
                        matched += 1
                    else:
                        print(f"[{region}] 미매칭: {title}")
                print(f"✅ [{region}] {url} - 매칭 {matched}건")
            else:
                print(f"❌ [{region}] {url} - 응답 코드 {res.status_code}")
        except Exception as e:
            print(f"❌ [{region}] {url} - 예외 발생: {e}")

# ✅ 한국/일본/중국 사이트 목록
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

# 🔎 수집 실행
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

