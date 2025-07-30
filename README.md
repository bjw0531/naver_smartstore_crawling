# 네이버 스마트스토어 이미지/텍스트 추출기

## 개요
네이버 스마트스토어 상품 페이지에서 이미지를 자동으로 크롤링하고, 이미지 내 텍스트를 추출하는 GUI 기반 크롤러입니다. PyQt5로 제작된 직관적인 인터페이스와 멀티프로세싱을 활용한 빠른 처리, PaddleOCR 기반의 강력한 텍스트 인식 기능을 제공합니다.

## 주요 기능
- 네이버 스마트스토어 상품 URL에서 이미지 자동 다운로드
- 이미지 내 텍스트 자동 추출 (OCR)
- GUI 기반 사용법 (PyQt5)
- 멀티프로세싱으로 빠른 처리
- 결과 자동 폴더 저장 및 로그 출력

## 설치 방법
1. Python 3.8 이상 설치
2. 필수 패키지 설치:
   ```bash
   pip install -r requirements.txt
   ```

## 사용법
1. `main.py` 실행:
   ```bash
   python main.py
   ```
2. GUI에서 `URL 파일 불러오기` 버튼 클릭 후, 크롤링할 URL 목록이 담긴 `url.txt` 선택
3. `이미지 추출` 버튼 클릭 → 자동으로 이미지 다운로드 및 텍스트 추출
4. 결과는 `save/` 폴더 하위에 URL별로 저장됨

### URL 파일 예시 (url.txt)
```
https://brand.naver.com/브랜드명/products/상품ID
...
```

## 폴더/파일 구조
```
main.py                # GUI 실행 진입점
ui.py                  # PyQt5 기반 GUI
extract_manager.py     # 멀티프로세싱 관리
processor.py           # 이미지/텍스트 처리 로직
webdriver.py           # Selenium 크롬 드라이버 래퍼
signal_manager.py      # PyQt5 시그널 관리
stylesheet.py          # GUI 스타일
vars.py                # 상수/메시지 정의
requirements.txt       # 의존성 목록
url.txt                # 크롤링 대상 URL 목록
save/                  # 결과 저장 폴더
output/, dist/, build/ # 빌드/출력 폴더
.idea/, .venv/, __pycache__/ # 개발 환경/캐시
```

## 주요 의존성
- opencv-python
- paddleocr, paddlepaddle
- pillow
- PyQt5
- selenium, webdriver-manager
- requests

## 결과물 예시
- `save/브랜드명_상품ID/` 폴더에 이미지와 `result.txt`(추출 텍스트) 저장

## 라이선스
MIT

## 문의
이슈 또는 PR로 문의 바랍니다.