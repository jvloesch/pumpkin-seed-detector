import cv2
import numpy as np

def segment_image(image):
    #Converte para HSV
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #Aplica median blur para retirar os arranhados do fundo
    image = cv2.medianBlur(image,7)

    #Transforma em imagem binária definindo um valor mínimo para H e V
    low_limit = np.array([18, 0, 100])
    high_limit = np.array([255, 255, 255])
    image = cv2.inRange(image, low_limit, high_limit)
    
    #Aplica morfologia para reduzir os ruídos restantes
    image = cv2.morphologyEx(image,cv2.MORPH_OPEN, np.ones((15, 15), dtype=np.uint8))
    return image