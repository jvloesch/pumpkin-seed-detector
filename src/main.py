import cv2
from pathlib import Path
from src.image_processing.segmentation import segment_image

project_root = Path(__file__).resolve().parents[1]
image_path = project_root / "data" / "images" / "pumpkin_0076.jpg"
result = segment_image(image_path)

cv2.namedWindow("Resultado", cv2.WINDOW_NORMAL)
cv2.imshow("Resultado", result)
cv2.waitKey(0)
cv2.destroyAllWindows()