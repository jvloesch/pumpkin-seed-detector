import json
import sys
import time
from pathlib import Path

import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.image_processing.segmentation import segment_image
from src.labeling.labeling_methods import find_seeds, seeds_statistics
from src.reporting.results_sheet import print_console_report

#Input e Output
IMAGES_DIR = PROJECT_ROOT / "data" / "images"
OUTPUT_FILE = PROJECT_ROOT / "data" / "annotations" / "seed_statistics.json"


def image_files(directory: Path):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in allowed_extensions
    )


def seed_metrics_for_image(image_path: Path, connectivity: int, pipeline: int = 0):
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Não foi possível abrir a imagem: {image_path}")

    mask = segment_image(image, pipeline=pipeline)
    seeds = find_seeds(mask, connectivity)
    statistics = seeds_statistics(seeds)

    entries = []
    for (height, width), area, aspect_ratio in statistics:
        entries.append(
            {
                "height": height,
                "width": width,
                "area": area,
                "aspect_ratio": aspect_ratio,
            }
        )

    return {
        "file_name": image_path.name,
        "total_seeds": len(seeds),
        "statistics": entries,
    }


def main():
    if not IMAGES_DIR.exists():
        raise FileNotFoundError(f"Diretório de imagens não encontrado: {IMAGES_DIR}")

    files = image_files(IMAGES_DIR)
    if not files:
        raise FileNotFoundError(f"Nenhuma imagem encontrada em: {IMAGES_DIR}")

    start_time = time.perf_counter()
    dataset = {
        "source_directory": str(IMAGES_DIR.relative_to(PROJECT_ROOT)),
        "images": [],
    }

    for image_path in files:
        image_result = {
            "file_name": image_path.name,
            "pipeline_a_connectivity_4": seed_metrics_for_image(image_path, 0, pipeline=0),
            "pipeline_a_connectivity_8": seed_metrics_for_image(image_path, 1, pipeline=0),
            "pipeline_b_connectivity_4": seed_metrics_for_image(image_path, 0, pipeline=1),
            "pipeline_b_connectivity_8": seed_metrics_for_image(image_path, 1, pipeline=1),
        }
        dataset["images"].append(image_result)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    elapsed = time.perf_counter() - start_time
    print(f"Processadas {len(files)} imagens.")
    print(f"Estatísticas salvas em: {OUTPUT_FILE}")
    print("\nComparação dos pipelines: A (kernel 15x15) vs B (kernel 11x11)")
    print_console_report(dataset, elapsed_testing=elapsed)


if __name__ == "__main__":
    main()
