import cv2
import numpy as np

def segment_image(image_path):

    #Carrega a imagem convertendo para HSV
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if image is None:
        raise FileNotFoundError(f"Não foi possível abrir: {image_path}")

    #Aplica median blur para retirar os arranhados do fundo
    image = cv2.medianBlur(image,7)

    #Transforma em imagem binária definindo um valor mínimo para H e V
    low_limit = np.array([18, 0, 100])
    high_limit = np.array([255, 255, 255])
    image = cv2.inRange(image, low_limit, high_limit)
    
    #Aplica mais um median blur para reduzir os ruídos restantes
    image = cv2.medianBlur(image,7)
    return image