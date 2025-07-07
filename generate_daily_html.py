import datetime
import os

# 오늘 날짜
today = datetime.date.today().strftime('%Y-%m-%d')

# 저장 경로
output_dir = "dailynews"  # ← 크롤러가 참조하는 폴더
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{today}.html")

# 외부에서 수집된 뉴스 리스트 (예: 크롤링, API, 수동 입력 등)
# 구조: [{"title": "...", "url": "..."}, ...]
news_items = []  # ← 운영 시 외부에서 동적으로 주입

# 예외 처리: 뉴스가 없는 경우 안내만 포함
if not news_items:
    html = f"""<html><head><meta charset='UTF-8'></head><body>
<h2>[뉴스레터] {today}</h2>
<ul>
  <li class='item'><i>금일 뉴스 소스가 없어 키워드만 제공됩니다.</i></li>
</ul></body></html>"""
else:
    # 뉴스 항목 HTML 생성
    html = f"<html><head><meta charset='UTF-8'></head><body>\n"
    html += f"<h2>[뉴스레터] {today}</h2>\n<ul>\n"
    for item in news_items:
        title = item["title"].strip()
        url = item["url"].strip()
        html += f"  <li><a href=\"{url}\">{title}</a></li>\n"
    html += "</ul>\n</body></html>"

# 파일 저장
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ 뉴스 HTML 생성 완료: {output_path}")

