from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import os

ocr_model = PaddleOCR(lang='korean', cpu_threads=8)

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

def ocr():
    img_paths = [
        os.path.join('./', 'test.png'),
    ]

    for img_path in img_paths:
        print(f"\n===== {os.path.basename(img_path)} 결과 =====")
        slices = split_image_with_overlap(img_path, max_height=1000, overlap=50)

        for idx, slice_img in enumerate(slices):
            np_img = np.array(slice_img)
            result = ocr_model.ocr(np_img)[0]

            print(f"--- {idx+1}번째 조각 결과 ---")
            for res in result:
                print(res[1][0])

ocr()
os.system('pause')
