import multiprocessing
import time
import atexit
from processor import ImageProcessor, TextProcessor
from vars import *


class ExtractManager:
    def __init__(self):
        self.task_queue = multiprocessing.JoinableQueue()
        self.shutdown_event = multiprocessing.Event()
        self.message_queue = multiprocessing.Queue()

        self.image_processor = ImageProcessor(self.message_queue)
        self.text_processor = TextProcessor(self.message_queue)
        self.extract_process = None
        self.task_producer = None

        # ★ 프로그램 종료 시점에 cleanup 함수 등록
        atexit.register(self.cleanup)

    def start_multiprocess(self):
        print("[ExtractManager] 멀티프로세스 시작")
        self.extract_process = multiprocessing.Process(
            target=ExtractManager._start_consumer,
            args=(self.task_queue, self.shutdown_event, self.message_queue, self.image_processor, self.text_processor)
        )
        self.extract_process.daemon = True
        self.extract_process.start()
        self.task_producer = TaskProducer(self.task_queue, self.shutdown_event, self.message_queue)

    @staticmethod
    def _start_consumer(task_queue, shutdown_event, message_queue, image_processor, text_processor):
        consumer = TaskConsumer(task_queue, shutdown_event, message_queue, image_processor, text_processor)
        consumer.run()

    def start_extract(self, urls, mode):
        if mode == "image":
            self.message_queue.put("이미지 추출 모드")

        self.task_producer.put_task(urls, mode)

    def shutdown(self):
        self.shutdown_event.set()

    def cleanup(self):
        self.message_queue.put("[ExtractManager] 프로그램 종료: 멀티프로세스 정리 시작")
        if self.extract_process.is_alive():
            self.extract_process.terminate()
            self.extract_process.join()
            self.message_queue.put("[ExtractManager] 멀티프로세스 정상 종료 완료")


class TaskProducer:
    def __init__(self, task_queue, shutdown_event, message_queue):
        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.message_queue = message_queue

    def put_task(self, tasks, mode):
        for url in tasks:
            self.task_queue.put({mode: url})
        self.task_queue.put({mode: TASK_DONE_MESSAGE})


class TaskConsumer:
    def __init__(self, task_queue, shutdown_event, message_queue, image_processor, text_processor):
        self.task_queue = task_queue
        self.shutdown_event = shutdown_event
        self.message_queue = message_queue
        self.image_processor = image_processor
        self.text_processor = text_processor

    def run(self):
        while True:
            if self.shutdown_event.is_set():
                self.message_queue.put("[TaskConsumer] 강제 셧다운 감지됨: 큐 비우기 시작")
                while not self.task_queue.empty():
                    try:
                        self.task_queue.get_nowait()
                        self.task_queue.task_done()
                    except:
                        break
                self.message_queue.put("[TaskConsumer] 작업 큐 비우기 완료.")
                self.message_queue.put(STOP_MESSAGE)
                self.shutdown_event.clear()
                continue

            try:
                # task get하기
                task = self.task_queue.get(timeout=0.5)
            except:
                time.sleep(0.1)
                continue

            # task가 "EXIT"인 경우
            if task == EXIT_MESSAGE:
                self.message_queue.put("[TaskConsumer] EXIT 명령 수신: 프로세스 종료")
                break

            # task가 dict인 경우
            if isinstance(task, dict):
                if "image" in task:
                    url = task["image"]
                    if url == TASK_DONE_MESSAGE:
                        self.message_queue.put("[TaskConsumer] 모든 이미지 작업 완료")
                        self.message_queue.put(IMAGE_DONE_MESSAGE)
                        continue

                    # 이미지 프로세싱 실행
                    self.message_queue.put(f"[TaskConsumer] 작업 시작: {url}")
                    arr = self.image_processor.crawl(url)
                    if arr:
                        self.text_processor.process(arr)
                        self.message_queue.put(f"[TaskConsumer] 작업 완료: {url}")
                    else:
                        self.message_queue.put(f"[TaskConsumer] 작업 실패: {url}")

                else:
                    self.message_queue.put(f"[TaskConsumer] 알 수 없는 작업 형식: {task}")

                self.task_queue.task_done()
            else:
                self.message_queue.put(f"[TaskConsumer] 잘못된 작업 데이터: {task}")
                self.task_queue.task_done()
