#!/usr/bin/env python3
"""
Alumni 페이지 갱신 스크립트
---------------------------
data/CNI_Alumni.xlsx 의 '시트1'을 읽어 alumni.html 의 표를 통째로 다시 만듭니다.

엑셀 열 구성 (첫 줄은 머리글, 둘째 줄부터 데이터):
    A Category | B Name | C Year | D Current position | E Affiliation | F Link

  · Category 는 아래 네 가지 중 하나로 적습니다. 그 외의 값은 무시됩니다.
        Ph.D.  /  M.S.  /  Post Doc & Research Prof.  /  Visiting Prof.
  · Name 이 비어 있는 줄은 건너뜁니다. 분류 사이 빈 줄을 넣어도 됩니다.
  · 사이트에 나오는 순서는 엑셀에 적힌 순서 그대로입니다.
  · Current position / Affiliation / Link 가 비어 있으면 사이트에 '-' 로 나옵니다.

사용법 (homepage 폴더에서):
    python tools/update_alumni.py

실행 후 GitHub Desktop에서 Commit & Push 해야 사이트에 반영됩니다.
필요한 것: Python 3 + openpyxl  (설치: pip install openpyxl)
"""
import html
import re
import sys
from pathlib import Path

try:
    import openpyxl
except ImportError:
    sys.exit("openpyxl이 필요합니다.  pip install openpyxl  을 먼저 실행하세요.")

ROOT = Path(__file__).resolve().parent.parent
XLSX = ROOT / "data" / "CNI_Alumni.xlsx"
PAGE = ROOT / "alumni.html"
SHEET = "시트1"

GROUPS = [
    ("Ph.D.", "Ph.D. Alumni"),
    ("M.S.", "M.S. Alumni"),
    ("Post Doc & Research Prof.", "Post Doc &amp; Research Prof."),
    ("Visiting Prof.", "Visiting Prof."),
]
ARROW = ('<svg aria-hidden="true" viewBox="0 0 14 14">'
         '<path d="M4 10 10 4M5.2 4H10v4.8"/></svg>')
DASH = '<span class="dash">-</span>'


def esc(s):
    return html.escape(s, quote=False)


def read_rows():
    if not XLSX.exists():
        sys.exit(f"엑셀 파일을 찾을 수 없습니다: {XLSX}")
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    if SHEET not in wb.sheetnames:
        sys.exit(f"'{SHEET}' 시트가 없습니다. 현재 시트: {wb.sheetnames}")
    ws = wb[SHEET]
    rows = []
    for raw in ws.iter_rows(min_row=2, max_col=6, values_only=True):
        cat, name, year, pos, aff, link = [
            ("" if v is None else str(v).strip()) for v in raw
        ]
        if not name:
            continue
        rows.append(dict(cat=cat, name=name, year=year, pos=pos, aff=aff, link=link))
    return rows


def row_html(r):
    pos, aff = r["pos"], r["aff"]
    if pos and aff:
        mid = "%s &middot; %s" % (esc(pos), esc(aff))
    elif aff:
        mid = esc(aff)
    elif pos:
        mid = esc(pos)
    else:
        mid = DASH
    if r["link"]:
        link = ('<a class="link-arrow" href="%s" target="_blank" rel="noopener">Profile%s</a>'
                % (html.escape(r["link"], quote=True), ARROW))
    else:
        link = DASH
    return ('<div class="al-row"><span class="nm">%s</span><span class="dg">%s</span>\n'
            '<span>%s</span>%s</div>' % (esc(r["name"]), esc(r["year"]), mid, link))


def main():
    rows = read_rows()
    known = {c for c, _ in GROUPS}
    unknown = sorted({r["cat"] for r in rows if r["cat"] not in known})
    if unknown:
        print("경고: 알 수 없는 Category 라서 제외합니다 ->", ", ".join(unknown))

    blocks, total = [], 0
    for i, (cat, title) in enumerate(GROUPS):
        group = [r for r in rows if r["cat"] == cat]
        if not group:
            print(f"  (건너뜀) {title}: 해당하는 줄이 없습니다")
            continue
        style = "" if not blocks else ' style="margin-top:44px"'
        blocks.append('<div class="group"%s>\n<div class="group-head"><h2>%s</h2></div>\n'
                      '<div>%s</div>\n</div>'
                      % (style, title, "".join(row_html(r) for r in group)))
        total += len(group)
        print(f"  {title}: {len(group)}명")

    if not blocks:
        sys.exit("표에 넣을 줄이 하나도 없습니다. Category 값을 확인하세요.")

    page = PAGE.read_text(encoding="utf-8")
    try:
        start = page.index('<div class="group"')
        end = page.index("</section>", start)
    except ValueError:
        sys.exit("alumni.html에서 표 영역을 찾지 못했습니다. 수동으로 확인하세요.")
    page = page[:start] + "\n".join(blocks) + "\n</div>\n" + page[end:]

    if page.count("<div") != page.count("</div>"):
        sys.exit("태그 짝이 맞지 않아 저장하지 않았습니다. 엑셀 내용을 확인하세요.")

    PAGE.write_text(page, encoding="utf-8")
    print(f"\n완료: 모두 {total}명이 alumni.html 에 들어갔습니다.")
    print("GitHub Desktop에서 Commit & Push 하면 반영됩니다.")


if __name__ == "__main__":
    main()
