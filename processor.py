import multiprocessing
import threading
import time

import numpy as np
import requests
from paddleocr import PaddleOCR
from selenium.webdriver.common.by import By
import base64

from webdriver import WebDriver
from vars import *
import os
from urllib.parse import urlparse
from PIL import Image

class Processor:
    save_folder_name = "save"

    def __init__(self, message_queue):
        self.message_queue = message_queue

    def make_folder(self, folder_name):
        # 현재 작업 디렉토리 확인
        current_dir = os.getcwd()
        # 폴더 경로 생성
        folder_path = os.path.join(current_dir, Processor.save_folder_name, folder_name)

        # 폴더가 존재하지 않으면 생성
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.message_queue.put(f"[Processor] '{folder_name}'이 {folder_path}에 생성되었습니다.")
        else:
            self.message_queue.put(f"[Processor] '{folder_name}'이 {folder_path}에 이미 존재합니다.")

        return folder_path

    def make_folder_name(self, url):
        # URL 구조: https://brand.naver.com/브랜드명/products/상품ID
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        folder_name = path_parts[0] + '_' + path_parts[-1]
        self.message_queue.put(f"[Processor] 폴더 이름 : '{folder_name}'")

        return folder_name

    def save_result_to_file(self, result, save_path):
        """
        결과를 파일로 저장
        result : 처리된 결과 리스트
        save_path : 저장할 경로
        """
        try:
            path = os.path.join(save_path, 'result.txt')
            with open(path, 'w', encoding='utf-8') as f:
                for item in result:
                    f.write(item + '\n')
            self.message_queue.put(f"[Processor] 결과 저장 완료: {path}")
            return True
        except Exception as e:
            self.message_queue.put(f"[Processor] 결과 저장 실패: {e}")
            return False


class ImageProcessor(Processor):
    """이미지 다운로드 및 처리 클래스"""

    SHARE_BTN_XPATH = "//*[contains(@class, '_spi_release_cont') and contains(@class, '_spi_release') and contains(@class, '_spi_release_btn') and contains(@class, 'spi_btn_more')]"
    DETAIL_BTN_XPATH = '//button[text()="상세정보 펼쳐보기"]'
    IMAGE_FIELD_XPATH = '//*[@id="INTRODUCE"]/div/div[contains(@class, "G87ogwKGfR")]/div[1]'
    IMAGE_FIELD_ELEMS_XPATH = IMAGE_FIELD_XPATH + '//strong' + ' | ' + IMAGE_FIELD_XPATH + '//span' + ' | ' + IMAGE_FIELD_XPATH + '//img'

    def __init__(self, message_queue):
        super().__init__(message_queue)
        self.driver = None

    def ensure_driver(self):
        if self.driver is None:
            self.driver = WebDriver()
            self.message_queue.put("[ImageProcessor] 드라이버 생성 완료")

    def crawl(self, url):
        """
        네이버 스마트 스토어에서 이미지 다운로드
        url : 스마트 스토어 링크
        결과 : 이미지 저장 위치
        """
        try:
            self.ensure_driver()
            self.message_queue.put(f"[ImageProcessor] {url} 크롤링 시작")

            # URL에서 폴더 이름 생성
            save_path = self.make_folder(self.make_folder_name(url))

            # URL에서 이미지와 텍스트 추출
            self.driver.get(url)
            self.driver.wait_page_load(self.SHARE_BTN_XPATH)
            time.sleep(1)

            self.driver.scroll_down()
            time.sleep(1)

            self.driver.find_element(By.XPATH, self.DETAIL_BTN_XPATH).click()
            time.sleep(1)
            self.driver.scroll_down(1e10)
            time.sleep(1)

            img_idx = 0
            crawled_arr = [{'url': url, 'save_path': save_path}, []]
            for elem in self.driver.find_elements(By.XPATH, self.IMAGE_FIELD_ELEMS_XPATH):
                # 이미지 필드에서 이미지 요소 찾기
                if elem.tag_name == 'img':
                    src = elem.get_attribute('data-src')
                    if not src:
                        self.message_queue.put(f"[ImageProcessor] 이미지 URL 없음: {elem}")
                        continue

                    img_path = self.img_download(src, save_path, img_idx)
                    if img_path:
                        crawled_arr[1].append({'img': img_path})
                        img_idx += 1
                    continue

                # 텍스트 필드에서 텍스트 요소 찾기
                text = elem.text.strip()
                if text == '':
                    continue

                crawled_arr[1].append({'text': text})

            self.message_queue.put("[ImageProcessor] 크롤링 완료")
            return crawled_arr
        except Exception as e:
            self.message_queue.put(f"[ImageProcessor] {url} 크롤링 실패: {e}")
            self.message_queue.put(STOP_MESSAGE)
            return False


    def img_download(self, img_url, folder_path, idx):
        """
        이미지 다운로드
        img_url : 이미지 URL 또는 Base64 데이터
        folder_path : 저장할 폴더 경로
        """
        try:
            if img_url.startswith("data:image/"):  # Base64 데이터 처리
                header, encoded = img_url.split(",", 1)
                img_data = base64.b64decode(encoded)
                ext = header.split(";")[0].split("/")[1]  # 확장자 추출 (예: png, jpg)
                filename = os.path.join(folder_path, f'image_{idx}.{ext}')
            else:  # 일반 URL 처리
                img_data = requests.get(img_url).content
                filename = os.path.join(folder_path, f'image_{idx}.jpg')

            with open(filename, 'wb') as f:
                f.write(img_data)
            self.message_queue.put(f"[ImageProcessor] 이미지 다운로드 완료: {filename}")
            return filename
        except Exception as e:
            self.message_queue.put(f"[ImageProcessor] 이미지 다운로드 실패: {e}")
            return False

    @staticmethod
    def split_image_with_overlap(img_path, max_height=1000, overlap=50):
        img = Image.open(img_path)
        width, height = img.size
        slices = []

        y = 0
        while y < height:
            top = y
            bottom = min(y + max_height, height)
            box = (0, top, width, bottom)
            slice_img = img.crop(box)
            slices.append(slice_img)

            y += (max_height - overlap)

        return slices

class TextProcessor(Processor):
    def __init__(self, message_queue):
        super().__init__(message_queue)
        self.ocr_model = None

    def ensure_ocr_model(self):
        if self.ocr_model is None:
            self.ocr_model = PaddleOCR(lang='korean', cpu_threads=8, rec_batch_num=12)

    def process(self, crawled_arr):
        self.ensure_ocr_model()
        if not crawled_arr:
            self.message_queue.put(f"[TextProcessor] 크롤링 결과 없음: 오류")
            return False

        if not crawled_arr[1]:
            self.message_queue.put(f"[TextProcessor] 크롤링 결과 없음: {crawled_arr[0]['url']}")
            return False

        processed_arr = []
        for elem in crawled_arr[1]:
            (kind, item), = elem.items()

            if kind == 'text':
                processed_arr.append(item)
                self.message_queue.put(f"[TextProcessor] 텍스트 처리 완료: {item}")
            elif kind == 'img':
                # OCR 처리
                img_path = item
                slices = ImageProcessor.split_image_with_overlap(img_path, 1080, 50)

                # big_image_ocred_text = 단일 이미지에 대한 총 OCR 결과
                big_image_ocred_text = ""
                for idx, slice_img in enumerate(slices):
                    np_img = np.array(slice_img)
                    result = self.ocr_model.ocr(np_img)[0]

                    if result is None:
                        self.message_queue.put(f"[TextProcessor] OCR 결과 없음: {img_path}, {idx+1}번째")
                        continue

                    # sliced_image_ocred_text = 단일 이미지의 잘린 이미지에 대한 총 OCR 결과
                    sliced_image_ocred_text = ""
                    for res in result:
                        sliced_image_ocred_text += res[1][0] + " "

                    self.message_queue.put(f"[TextProcessor] OCR 결과: {sliced_image_ocred_text} ,({os.path.basename(img_path)}, {idx+1}번째)")
                    big_image_ocred_text += sliced_image_ocred_text + "\n"

                processed_arr.append(big_image_ocred_text)
        self.message_queue.put("[TextProcessor] 모든 이미지 처리 완료")

        if processed_arr:
            self.save_result_to_file(processed_arr, crawled_arr[0]['save_path'])
            return processed_arr
        return False


def watch_message_queue(queue):
    """
    메시지 큐를 감시하는 스레드
    :param queue: multiprocessing.Queue
    """
    while True:
        try:
            message = queue.get()
            print(f"[Watcher] 메시지 수신: {message}")
        except EOFError:
            print("[Watcher] 연결이 끊어졌습니다. 감시 스레드를 종료합니다.")
            break
        except Exception as e:
            print(f"[Watcher] 예외 발생: {e}")
            break

def test():
    # 테스트용 코드
    message_queue1 = multiprocessing.Queue()

    watcher = threading.Thread(target=watch_message_queue,
                               args=(message_queue1,))
    watcher.daemon = True
    watcher.start()

    image_processor = ImageProcessor(message_queue1)
    text_processor = TextProcessor(message_queue1)
    arr = image_processor.crawl(
        "https://brand.naver.com/vicxxo/products/6223000520?site_preference=device&NaPm=ct%3Dm9zqpfxu%7Cci%3Dshopn%7Ctr%3Dnshfum%7Chk%3D0b3285c89c36ad24ee6379d01d89751db1b30b74%7Ctrx%3Dundefined")
    text_processor.process(arr)
    print(arr)

if __name__ == "__main__":
   # test()
   pass