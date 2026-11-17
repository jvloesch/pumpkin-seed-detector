import cv2
import numpy as np


def segment_image(image, pipeline: int = 0):
    """
    pipeline=0 -> kernel 15x15 (pipeline A)
    pipeline=1 -> kernel 11x11 (pipeline B)
    """
    #Converte para HSV
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #Aplica median blur para retirar os arranhados do fundo
    image = cv2.medianBlur(image, 7)

    #Transforma em imagem binária definindo um valor mínimo para H e V
    low_limit = np.array([18, 0, 100])
    high_limit = np.array([255, 255, 255])
    image = cv2.inRange(image, low_limit, high_limit)

    if pipeline == 0:
        kernel_size = (15, 15)
    elif pipeline == 1:
        kernel_size = (11, 11)
    else:
        raise ValueError("pipeline deve ser 0 (pipeline A) ou 1 (pipeline B)")

    #Aplica morfologia para reduzir os ruídos restantes
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, np.ones(kernel_size, dtype=np.uint8))
    return image