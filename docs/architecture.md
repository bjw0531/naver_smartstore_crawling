# 아키텍처 및 구조 (Architecture)

## 전체 구조
- PyQt5 기반 GUI (`ui.py`)
- 멀티프로세싱 기반 크롤링/처리 (`extract_manager.py`, `processor.py`)
- Selenium WebDriver를 통한 크롤링 (`webdriver.py`)
- PaddleOCR 기반 이미지 내 텍스트 추출
- 실시간 로그 및 시그널 처리 (`signal_manager.py`)

## 주요 모듈 설명
- **main.py**: 프로그램 진입점, GUI 실행
- **ui.py**: 사용자 인터페이스, 버튼/로그/파일선택 등
- **extract_manager.py**: 멀티프로세싱 관리, 작업 분배/수집
- **processor.py**: 이미지 다운로드, OCR 텍스트 추출, 결과 저장
- **webdriver.py**: 크롬 드라이버 래퍼, 페이지 이동/스크롤/요소 탐색
- **signal_manager.py**: PyQt5 시그널 정의 및 연결
- **stylesheet.py**: UI 스타일
- **vars.py**: 상수/메시지 정의

## 데이터 흐름
1. 사용자가 URL 파일을 선택하고 '이미지 추출' 클릭
2. ExtractManager가 멀티프로세싱으로 URL별 작업 분배
3. 각 프로세스에서 Selenium으로 이미지 크롤링, PaddleOCR로 텍스트 추출
4. 결과를 `save/` 폴더에 저장, 로그/상태는 시그널로 GUI에 전달

## 멀티프로세싱 구조
- `ExtractManager`가 작업 큐/메시지 큐/이벤트로 프로세스 관리
- `TaskProducer`가 작업 투입, `TaskConsumer`가 실제 크롤링/처리
- 프로세스 종료/정리/중단 신호 처리

## 시그널 구조
- `SignalManager`에서 PyQt5 시그널 정의
- 이미지/텍스트 완료, 로그, 사용자 중단 등 다양한 이벤트를 GUI에 전달

## 폴더 구조 예시
```
naver_smartstore_crawling/
├── main.py
├── ui.py
├── extract_manager.py
├── processor.py
├── webdriver.py
├── signal_manager.py
├── stylesheet.py
├── vars.py
├── requirements.txt
├── url.txt
├── save/
├── docs/
│   ├── usage.md
│   └── architecture.md
...
```