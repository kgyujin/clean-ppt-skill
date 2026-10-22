# 보조 제작 도구

저장소 루트에서 실행합니다. Node.js와 Python 3를 준비하고, 필요한 패키지는 작업용 환경에 설치합니다. 아래 명령은 프로젝트 잠금 파일을 만들지 않습니다.

```bash
npm install --no-save --package-lock=false pptxgenjs
python3 -m venv .venv
.venv/bin/python -m pip install reportlab Pillow PyMuPDF
```

macOS/Linux 예시입니다. Windows에서는 가상환경의 `Scripts/python.exe`를 사용합니다.

## PPTX 생성과 구조 검사

```bash
mkdir -p output
PYTHON=.venv/bin/python node scripts/build_deck.cjs examples/business-blue/scene.json output/deck.pptx
.venv/bin/python scripts/audit_deck.py examples/business-blue/scene.json output/deck.pptx
```

`assets/example-deck.json`은 기본 도형·표·차트용 최소 예제입니다. 실제 발표 배치는 `examples/`의 장면 파일을 참고합니다. 폰트는 PPTX에 내장되지 않습니다.

## PDF와 이미지 미리보기

Pretendard TTF 파일의 경로를 지정합니다.

```bash
.venv/bin/python scripts/preview_scene.py examples/business-blue/scene.json output/deck.pdf \
  --font-regular /path/to/Pretendard-Regular.ttf \
  --font-bold /path/to/Pretendard-Bold.ttf
```

PDF 옆에 페이지별 1920×1080 이미지와 전체 축소판을 생성합니다. 이는 별도의 ReportLab 렌더이며, 실제 PPTX 내보내기 결과와 다를 수 있습니다.

## 지원 범위

텍스트, 사각형, 타원, 직각 연결선, PNG/JPEG, 단순 표와 막대 차트를 지원합니다. 지원하지 않는 요소는 별도 제작기로 만들고 실제 출력에서 확인합니다. 복잡한 차트의 축·범례 표현은 보조 PDF와 같지 않을 수 있습니다.

[장면 JSON 형식](../references/scene-format.md)에서 좌표와 단위를 확인할 수 있습니다.
