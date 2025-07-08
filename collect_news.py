import datetime
import requests
from bs4 import BeautifulSoup
import re
import json
import os

today = datetime.date.today().strftime('%Y-%m-%d')
output_path = f"news_items_{today}.json"

# 🔍 키워드 리스트 (소문자 변환 기준)
keywords = [
 # 한국어
    "서브컬처", "수집형", "미소녀", "게임쇼", "굿스마일", "코스프레", "부스", "콜라보", "런칭", "업계 동향", "시장 보고서",
    "니케", "블루아카이브", "원신", "젠레스 존 제로", "스타레일", "붕괴",
    # 일본어
    "崩壊：スターレイル", "ブルーアーカイブ", "ゼンレスゾーンゼロ", "ホヨバース", "ゲームショウ", "二次創作", "ガチャ", "美少女",
    # 중국어
    "米哈游", "崩坏", "蓝档案", "原神", "少女收集", "二次元", "集换式", "合作", "发售", "虚拟主播"
]

keywords = [k.lower() for k in keywords]

# 🔍 사이트별 HTML 구조별 분기 처리
news_items = []

# ✅ 한국 매체 (일반 구조)
korean_sites = [
    "https://www.inven.co.kr/webzine/news/",
    "https://www.thisisgame.com/webzine/news/nboard/263/?category=2",
    "https://www.ezyeconomy.com/news/articleList.html?sc_sub_section_code=S2N71&view_type=sm"
]

for url in korean_sites:
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.select("a[href]"):
                title = a.get_text(strip=True)
                href = a["href"]
                if title and href.startswith("http") and any(k in title.lower() for k in keywords):
                    news_items.append({"title": title, "url": href})
    except Exception as e:
        print(f"[한국 매체 오류] {url} - {e}")

# ✅ 일본 매체 구조 처리
japan_sites = [
    "https://gamebiz.jp/news",        # Gamebiz
    "https://www.4gamer.net/",        # 4Gamer
    "https://www.gamer.ne.jp/"        # Gamer.ne.jp
]

for url in japan_sites:
    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.select("a[href]"):
                title = a.get_text(strip=True)
                href = a["href"]
                full_url = href if href.startswith("http") else requests.compat.urljoin(url, href)
                if title and any(k in title.lower() for k in keywords):
                    news_items.append({"title": title, "url": full_url})
    except Exception as e:
        print(f"[일본 매체 오류] {url} - {e}")

# ✅ 중국 매체 구조 처리
china_sites = [
    "https://www.youxituoluo.com/",
    "http://news.17173.com/quanqiu/",
    "https://www.163.com/dy/media/T1439279320876.html",
    "https://gnn.gamer.com.tw/index.php?k=4",
    "https://news.qq.com/"
]

for url in china_sites:
    try:
        res = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            for a in soup.select("a[href]"):
                title = a.get_text(strip=True)
                href = a["href"]
                full_url = href if href.startswith("http") else requests.compat.urljoin(url, href)
                if title and any(k in title.lower() for k in keywords):
                    news_items.append({"title": title, "url": full_url})
    except Exception as e:
        print(f"[중국 매체 오류] {url} - {e}")

# ✅ 중복 제거
unique_items = {item["url"]: item for item in news_items}
news_items = list(unique_items.values())

# ✅ 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(news_items, f, ensure_ascii=False, indent=2)

print(f"✅ 뉴스 수집 완료: {len(news_items)}건 → {output_path}")
