#!/usr/bin/env python3
"""
Lab life 슬라이드쇼 갱신 스크립트
---------------------------------
assets/img/lab/ 폴더에 사진을 넣고 이 파일을 실행하면
  1) 새 사진을 웹용 크기(가로 1800px, JPEG)로 변환해 lab-NN.jpg 로 저장하고
  2) 원본은 assets/img/lab/_originals/ 로 옮기고
  3) index.html 의 슬라이드와 아래 점(dot) 개수를 자동으로 맞춥니다.

실행 후에는 GitHub Desktop에서 Commit & Push 해야 사이트에 반영됩니다.

사용법 (homepage 폴더에서):
    python tools/update_lab_photos.py
필요한 것: Python 3 + Pillow  (설치: pip install pillow)
"""
import os, re, sys, shutil
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow이 필요합니다.  pip install pillow  를 먼저 실행하세요.")

ROOT = Path(__file__).resolve().parent.parent
LAB  = ROOT / "assets" / "img" / "lab"
ORIG = LAB / "_originals"
INDEX = ROOT / "index.html"
MAXW = 1800
QUALITY = 82
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".bmp", ".tif", ".tiff"}
PATTERN = re.compile(r"^lab-(\d{2})\.jpg$")

def next_number(existing):
    used = {int(m.group(1)) for f in existing if (m := PATTERN.match(f.name))}
    n = 1
    while n in used:
        n += 1
    return n

def main():
    if not LAB.is_dir():
        sys.exit(f"폴더를 찾을 수 없습니다: {LAB}")
    ORIG.mkdir(exist_ok=True)
    gi = ORIG / ".gitignore"
    if not gi.exists():
        gi.write_text("*\n!.gitignore\n", encoding="utf-8")

    existing = [f for f in LAB.iterdir() if f.is_file() and PATTERN.match(f.name)]
    sources  = [f for f in LAB.iterdir()
                if f.is_file() and f.suffix.lower() in EXTS and not PATTERN.match(f.name)]
    sources.sort(key=lambda f: f.stat().st_mtime)

    added = []
    for src in sources:
        try:
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        except Exception as e:
            print(f"  건너뜀 (열 수 없음): {src.name}  [{e}]")
            continue
        im.thumbnail((MAXW, MAXW), Image.LANCZOS)
        n = next_number(existing + added)
        out = LAB / f"lab-{n:02d}.jpg"
        im.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        added.append(out)
        shutil.move(str(src), str(ORIG / src.name))
        print(f"  추가: {src.name}  ->  {out.name}  ({im.width}x{im.height}, "
              f"{out.stat().st_size // 1024} KB)")

    photos = sorted([f for f in LAB.iterdir() if f.is_file() and PATTERN.match(f.name)],
                    key=lambda f: f.name, reverse=True)      # 번호가 큰(최신) 사진이 먼저
    if not photos:
        sys.exit("lab-NN.jpg 사진이 하나도 없습니다.")

    html = INDEX.read_text(encoding="utf-8")
    slides = "".join(
        f'<figure class="slide{" is-on" if i == 0 else ""}">'
        f'<img src="assets/img/lab/{p.name}" alt="Lab life photo" loading="lazy"></figure>'
        for i, p in enumerate(photos))
    dots = "".join(
        f'<button type="button" class="{"is-on" if i == 0 else ""}" '
        f'aria-label="Photo {i + 1}"></button>' for i in range(len(photos)))

    try:
        i = html.index('<div class="slides">')
        j = html.index("</div>", html.rindex("</figure>", i))
        html = html[:i] + '<div class="slides">' + slides + html[j:]
        i = html.index('<div class="sl-dots">')
        j = html.index("</div>", i)
        html = html[:i] + '<div class="sl-dots">' + dots + html[j:]
    except ValueError:
        sys.exit("index.html에서 슬라이드쇼 영역을 찾지 못했습니다. 수동으로 확인하세요.")

    INDEX.write_text(html, encoding="utf-8")
    print(f"\n완료: 사진 {len(photos)}장이 슬라이드쇼에 들어갔습니다"
          f" (새로 추가 {len(added)}장).")
    print("원본은 assets/img/lab/_originals/ 에 보관했습니다 (사이트에는 올라가지 않습니다).")
    print("GitHub Desktop에서 Commit & Push 하면 반영됩니다.")

if __name__ == "__main__":
    main()
