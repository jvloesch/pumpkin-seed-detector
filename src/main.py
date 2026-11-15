import cv2
from pathlib import Path
from src.image_processing.segmentation import segment_image
from src.labeling.labeling_methods import find_seeds, highlight_seeds

project_root = Path(__file__).resolve().parents[1]
image_path = project_root / "data" / "images" / "pumpkin_0080.jpg"

image = cv2.imread(image_path, cv2.IMREAD_COLOR)
if image is None:
        raise FileNotFoundError(f"Não foi possível abrir: {image}")

mask = segment_image(image)
seeds_4 = find_seeds(mask, 0)
seeds_8 = find_seeds(mask, 1)
areas_4 = highlight_seeds(image, seeds_4)
areas_8 = highlight_seeds(image, seeds_8)

print(f"Sementes encontradas: {len(seeds_4)}")
print(f"Sementes encontradas: {len(seeds_8)}")


cv2.namedWindow("Original", cv2.WINDOW_NORMAL)
cv2.imshow("Original", image)
cv2.namedWindow("Mascara", cv2.WINDOW_NORMAL)
cv2.imshow("Mascara", mask)
cv2.namedWindow("Areas 4", cv2.WINDOW_NORMAL)
cv2.imshow("Areas 4", areas_4)
cv2.namedWindow("Areas 8", cv2.WINDOW_NORMAL)
cv2.imshow("Areas 8", areas_8)
cv2.waitKey(0)
cv2.destroyAllWindows()