import datetime
import os
import requests
from bs4 import BeautifulSoup

today = '2025-07-04'
output_dir = "dailynews"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 키워드 리스트 (대소문자 구분 없음)
keywords = [
    # 한국어
    "서브컬처", "수집형", "미소녀", "게임쇼", "굿스마일", "코스프레", "부스", "콜라보", "런칭", "업계 동향", "시장 보고서",
    "니케", "블루아카이브", "원신", "젠레스 존 제로", "스타레일", "붕괴",
    # 일본어
    "崩壊：スターレイル", "ブルーアーカイブ", "ゼンレスゾーンゼロ", "ホヨバース", "ゲームショウ", "二次創作", "ガチャ", "美少女",
    # 중국어
    "米哈游", "崩坏", "蓝档案", "原神", "少女收集", "二次元", "集换式", "合作", "发售", "虚拟主播"
    # 영어
    "Zenless Zone Zero", "Blue Archive", "Nikke"
]

news_items = []

# ✅ 한국 사이트 (대부분 RSS 없이 BeautifulSoup 기반 처리 필요)
korea_sites = [
    "https://www.inven.co.kr/webzine/news/",
    "https://www.thisisgame.com/webzine/news/nboard/263/?category=2",
    "https://www.ezyeconomy.com/news/articleList.html?sc_sub_section_code=S2N71&view_type=sm"
]

# ✅ 일본 사이트
japan_sites = [
    "https://gamebiz.jp/news",
    "https://www.4gamer.net/",
    "https://www.gamer.ne.jp/",
    "https://gnn.gamer.com.tw/index.php?k=4"
]

# ✅ 중국 사이트
china_sites = [
    "https://www.17173.com/",
    "https://www.youxituoluo.com/",
    "https://www.163.com/dy/media/T1439279320876.html",
    "https://news.qq.com/"
]

# 🔎 한국 뉴스 수집
for url in korea_sites:
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for link in soup.select("a[href]"):
                title = link.get_text(strip=True)
                href = link['href']
                if title and href.startswith("http") and any(k.lower() in title.lower() for k in keywords):
                    news_items.append({"title": title, "url": href})
    except Exception as e:
        print(f"[한국 수집 오류] {url} - {e}")

# 🔎 일본 뉴스 수집
for url in japan_sites:
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for link in soup.select("a[href]"):
                title = link.get_text(strip=True)
                href = link['href']
                if title and href.startswith("http") and any(k.lower() in title.lower() for k in keywords):
                    news_items.append({"title": title, "url": href})
    except Exception as e:
        print(f"[일본 수집 오류] {url} - {e}")

# 🔎 중국 뉴스 수집
for url in china_sites:
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for link in soup.select("a[href]"):
                title = link.get_text(strip=True)
                href = link['href']
                if title and href.startswith("http") and any(k.lower() in title.lower() for k in keywords):
                    news_items.append({"title": title, "url": href})
    except Exception as e:
        print(f"[중국 수집 오류] {url} - {e}")

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
