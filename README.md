# CNI Lab 홈페이지 시안 (정적 사이트)

기존 사이트(https://ibrain.kaist.ac.kr)의 내용을 그대로 옮겨 만든 리뉴얼 시안입니다.
서버 이전 없이 디자인·구성·내용만 바꾸는 것을 전제로 했습니다.

## 실행 방법

- 가장 간단: `index.html`을 브라우저에서 열기 (더블클릭)
- 로컬 서버로 보기(권장):
  ```bash
  cd cni-lab-site
  python3 -m http.server 8000
  # 브라우저에서 http://localhost:8000
  ```

## 파일 구조

```
index.html          Home (히어로 · 소개 · Dual goals · Research themes · News · Join us)
research.html       Research (큰 주제 3개 + 기존 5개 세부 분야 원문)
professor.html      Professor (약력 전체)
members.html        Members (Post Doc / Ph.D / Master / 학부연구생 / Staff)
alumni.html         Alumni (사진 없음, 이름·학위·소속·이메일 표)
publications.html   Publications (International / Domestic / Books / Conference)
news.html           Lab News (기존 사이트 게시물 10건)
contact.html        Contact
assets/css/style.css   디자인 전체 (색·폰트·레이아웃·반응형)
assets/js/site.js      모바일 메뉴, 논문 카테고리 전환, 뉴스 필터
```

## 디자인 토큰

`assets/css/style.css` 맨 위 `:root` 에 색과 폰트가 모여 있습니다.

| 변수 | 값 | 용도 |
|---|---|---|
| `--navy` | #101B43 | 히어로·배너·푸터 (로고 네이비) |
| `--cerulean` | #0C84C0 | 강조선·그래픽 (로고 세룰리안) |
| `--sky` | #37B8EB | 네이비 위 강조 (기존 사이트 포인트색) |
| `--link` | #0A6FA3 | 흰 배경 위 링크 (명도대비 AA) |

폰트: 제목 Newsreader(600), 본문 IBM Plex Sans / IBM Plex Sans KR, 라벨·연도 IBM Plex Mono.
Google Fonts에서 불러오므로 인터넷 연결이 필요합니다.

## 로고

- 헤더(CNI 로고): `assets/img/cni-logo.png` (기존 로고를 배경 투명하게 다듬은 파일).
  혹시 이 파일이 없으면 기존 사이트 주소를 불러오고, 그것도 실패하면 글자 로고가 대신 보입니다.
- 푸터(KAIST 로고): `assets/img/kaist-logo.png` (전달받은 공식 파일). 어두운 배경용 흰색 버전은
  `assets/img/kaist-logo-white.png` 입니다.

## Home 히어로 — 키워드 네트워크

기존 사이트 워드클라우드의 키워드 32개를 뇌 모양 네트워크의 노드로 배치하고 edge로 이었습니다.
단어에 마우스를 올리면 그 단어가 커지면서 이어진 edge와 이웃 단어가 함께 밝아집니다.
오른쪽 아래의 큰 원은 세포 수준(동물 실험) 네트워크로, 뇌 네트워크(사람 영상)와 같은 비중으로 보이도록
크게 두고 그 안에도 키워드 노드를 넣었습니다.

- 키워드 목록: `data/keywords.csv` 한 파일만 고치면 됩니다. 각 줄은 `단어,글자크기,위치`이고
  위치는 `macro`(뇌 네트워크) 또는 `micro`(세포 확대 원)입니다. 랩원 의견을 받아 이 파일을 고친 뒤
  `python3 gen_kwnet.py && python3 build_site.py` 를 실행하면 겹치지 않게 다시 배치됩니다.
- 배치 결과: `kwnet.json` → `index.html` 안에 SVG와 `<span class="kw">`로 들어갑니다.
- 글자 크기는 컨테이너 너비 기준(`cqw`)이라 화면이 좁아지면 작은 키워드부터 자동으로 숨습니다.
- 호버 동작: `assets/js/site.js` 상단의 keyword network 블록.

## 알려진 제약

- 이 시안을 Claude 아티팩트 링크로 볼 때는 보안 정책 때문에 외부 이미지(연구실 서버의
  로고)가 차단되어 텍스트 로고로 보입니다. 로컬에서 열거나 실제 서버에 올리면 정상 표시됩니다.
- 논문 목록은 기존 사이트의 International / Domestic / Books / Conference 항목을 그대로
  옮긴 것이며, DOI가 적힌 논문에는 DOI 버튼이 자동으로 붙습니다.

## 기존 서버에 올릴 때

- 지금 구조 그대로 웹 루트에 복사하면 동작합니다 (빌드 과정 없음).
- Hugo로 옮길 경우: `assets/` 를 `static/` 으로 두고, 각 페이지의 본문을 레이아웃
  템플릿(`layouts/`)으로 옮기면 됩니다. 색·폰트는 `style.css` 하나만 가져가면 유지됩니다.
