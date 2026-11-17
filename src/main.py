import cv2
import random
from pathlib import Path
from src.image_processing.segmentation import segment_image
from src.labeling.labeling_methods import find_seeds, highlight_seeds, seeds_statistics

#Importa imagem aleatória da pasta data
project_root = Path(__file__).resolve().parents[1]
images_dir = project_root / "data" / "images"
image_paths = [
        path
        for path in images_dir.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
]
if not image_paths:
        raise FileNotFoundError(f"Nenhuma imagem encontrada em: {images_dir}")

image_path = random.choice(image_paths)

image = cv2.imread(image_path, cv2.IMREAD_COLOR)
if image is None:
        raise FileNotFoundError(f"Não foi possível abrir: {image_path}")

#Gera a máscara, identificação e desenho das sementes com conectividade 4 e conectividade 8
mask = segment_image(image, 0) #0 PARA PIPELINE A E 1 PARA PIPELINE B
seeds_4 = find_seeds(mask, 0)
seeds_8 = find_seeds(mask, 1)
areas_4 = highlight_seeds(image, seeds_4)
areas_8 = highlight_seeds(image, seeds_8)

#Imprime a quantidade de sementes encontradas com conectividade 4 e conectividade 8 e suas estatísticas
print(f"Sementes encontradas (conectividade 4): {len(seeds_4)}")
print(f"Sementes encontradas (conectividade 8): {len(seeds_8)}")
print(f"Estatísticas (conectividade 4): {seeds_statistics(seeds_4)}")
print(f"Estatísticas (conectividade 8): {seeds_statistics(seeds_8)}")


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