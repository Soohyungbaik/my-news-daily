import datetime
import os
import requests
from bs4 import BeautifulSoup

today = datetime.date.today().strftime('%Y-%m-%d')
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
]

news_items = []

# ✅ 일본 사이트 예시
japan_sites = [
    https://gamebiz.jp/news,
    https://www.4gamer.net/
]

# ✅ 중국 사이트 예시
china_sites = [
    https://www.youxituoluo.com/,
    https://www.17173.com/
]

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
