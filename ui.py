import threading
import time

from PyQt5.QtGui import QFontMetrics
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
)
from extract_manager import ExtractManager
from signal_manager import SignalManager
import stylesheet
from vars import *


class CrawlerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.signal_manager = SignalManager()
        self.extract_manager = ExtractManager()
        self.extract_manager.start_multiprocess()

        # signal manager connection
        self.signal_manager.image_done_signal.connect(self.on_image_extraction_done)
        self.signal_manager.text_done_signal.connect(self.on_text_extraction_done)
        self.signal_manager.log_message_signal.connect(self.on_log_message_received)
        self.signal_manager.user_stop_signal.connect(self.on_user_stop_requested)

        self.setWindowTitle("네이버 스마트 스토어 추출기")
        self.resize(600, 400)

        self.load_button = QPushButton("URL 파일 불러오기")
        self.load_button.clicked.connect(self.load_url_file)
        self.file_path_label = QLabel("선택된 파일 없음")
        self.file_path_label.setStyleSheet("border: 1px solid gray; padding: 5px;")

        load_hbox = QHBoxLayout()
        load_hbox.addWidget(self.load_button)
        load_hbox.addWidget(self.file_path_label)

        # 2. 이미지 추출, 텍스트 추출 버튼 부분 (HBox)
        self.extract_image_button = QPushButton("이미지 추출")
        self.extract_image_button.clicked.connect(self.extract_images)

        extract_hbox = QHBoxLayout()
        extract_hbox.addWidget(self.extract_image_button)

        # 정지 버튼 추가
        self.stop_button = QPushButton("정지")
        self.stop_button.clicked.connect(self.stop_extraction)

        # 3. 로그 텍스트 필드 (Multiline TextEdit)
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setPlaceholderText("여기에 로그가 출력됩니다.")

        # 전체 배치 (VBox)
        main_layout = QVBoxLayout()
        main_layout.addLayout(load_hbox)
        main_layout.addLayout(extract_hbox)
        main_layout.addWidget(self.stop_button)
        main_layout.addWidget(self.log_text_edit)

        self.setLayout(main_layout)
        self.setStyleSheet(stylesheet.STYLE_SHEET)

    def start_thread(self):
        print("watcher 스레드 시작")
        self.watcher = threading.Thread(target=self.watch_message_queue,
                                        args=(self.extract_manager.message_queue, self.signal_manager))
        self.watcher.daemon = True  # 프로그램 종료 시 함께 종료
        self.watcher.start()

    def watch_message_queue(self, queue, signal_manager):
        while True:
            try:
                message = queue.get()
                if message == IMAGE_DONE_MESSAGE:
                    signal_manager.image_done_signal.emit()
                elif message == TEXT_DONE_MESSAGE:
                    signal_manager.text_done_signal.emit()
                elif message == STOP_MESSAGE:
                    signal_manager.user_stop_signal.emit()
                else:
                    signal_manager.log_message_signal.emit(message)
                time.sleep(0.1)
            except EOFError:
                print("[Watcher] 연결이 끊어졌습니다. 감시 스레드를 종료합니다.")
                break  # ★ 에러 발생하면 while True 탈출해서 스레드 자연 종료
            except Exception as e:
                print(f"[Watcher] 예외 발생: {e}")
                break

    def on_log_message_received(self, message):
        self.log_text_edit.append(message)
        self.log_text_edit.verticalScrollBar().setValue(
            self.log_text_edit.verticalScrollBar().maximum()
        )

    def on_user_stop_requested(self):
        self.enable_extract_buttons()

    def stop_extraction(self):
        self.extract_manager.shutdown()
        self.signal_manager.log_message_signal.emit("[CrawlerApp] 정지 요청: 프로세스 종료 대기 중...")

    def update_file_path_label(self, path):
        # QLabel 가로 길이 기준으로 텍스트 생략
        metrics = QFontMetrics(self.file_path_label.font())
        elided_text = metrics.elidedText(path, Qt.ElideMiddle, self.file_path_label.width())
        self.file_path_label.setText(elided_text)

    def load_url_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "URL 파일 선택", "", "텍스트 파일 (*.txt)")
        if file_path:
            self.update_file_path_label(f"선택된 파일: {file_path}")
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.urls = [line.strip() for line in file.readlines()]
                self.signal_manager.log_message_signal.emit(f"성공 : {len(self.urls)}개의 URL을 불러왔습니다!")
            except Exception as e:
                self.signal_manager.log_message_signal(f"오류 : 파일을 읽는 중 오류 발생: {e}")

    def extract_images(self):
        if not self.urls:
            QMessageBox.critical(self, "오류", "URL 파일을 먼저 선택하세요!")
            return
        self.disable_extract_buttons()
        self.extract_manager.start_extract(self.urls, "image")

    def disable_extract_buttons(self):
        self.extract_image_button.setEnabled(False)

    def enable_extract_buttons(self):
        self.extract_image_button.setEnabled(True)

    def on_image_extraction_done(self):
        self.enable_extract_buttons()
        self.signal_manager.log_message_signal.emit("이미지 추출이 완료되었습니다!")

    def on_text_extraction_done(self):
        self.enable_extract_buttons()
        self.signal_manager.log_message_signal.emit("텍스트 추출이 완료되었습니다!")
