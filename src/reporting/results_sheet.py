import json
import statistics
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ANNOTATIONS_DIR = PROJECT_ROOT / "data" / "annotations"
ACTUAL_RESULTS_FILE = ANNOTATIONS_DIR / "seed_statistics.json"


def load_expected_counts(annotation_dir: Path):
    expected_counts = {}

    for json_path in sorted(annotation_dir.glob("*.json")):
        if json_path.name in {"seed_statistics.json", "results_sheet_summary.json"}:
            continue

        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        images_by_id = {}
        for image in data.get("images", []):
            image_id = image.get("id")
            file_name = image.get("file_name")
            if image_id is not None and file_name is not None:
                images_by_id[image_id] = file_name

        counts_by_image = {}
        for annotation in data.get("annotations", []):
            image_id = annotation.get("image_id")
            if image_id is None:
                continue
            file_name = images_by_id.get(image_id)
            if file_name is None:
                continue
            counts_by_image[file_name] = counts_by_image.get(file_name, 0) + 1

        expected_counts.update(counts_by_image)

    return expected_counts


def load_actual_counts(results_object):
    actual_counts = {}

    if isinstance(results_object, Path):
        if not results_object.exists():
            return {}
        data = json.loads(results_object.read_text(encoding="utf-8"))
    else:
        data = results_object

    for image_result in data.get("images", []):
        file_name = image_result.get("file_name")
        if file_name is None:
            continue

        if "pipeline_a_connectivity_4" in image_result:
            actual_counts[file_name] = {
                "pipeline_a_connectivity_4": image_result.get("pipeline_a_connectivity_4", {}).get("total_seeds", 0),
                "pipeline_a_connectivity_8": image_result.get("pipeline_a_connectivity_8", {}).get("total_seeds", 0),
                "pipeline_b_connectivity_4": image_result.get("pipeline_b_connectivity_4", {}).get("total_seeds", 0),
                "pipeline_b_connectivity_8": image_result.get("pipeline_b_connectivity_8", {}).get("total_seeds", 0),
            }
        else:
            connectivity_4 = image_result.get("connectivity_4", {}).get("total_seeds", 0)
            connectivity_8 = image_result.get("connectivity_8", {}).get("total_seeds", 0)
            actual_counts[file_name] = {
                "connectivity_4": connectivity_4,
                "connectivity_8": connectivity_8,
            }

    return actual_counts


def build_rows(actual_data):
    expected_counts = load_expected_counts(ANNOTATIONS_DIR)
    actual_counts = load_actual_counts(actual_data)

    common_files = sorted(set(expected_counts) & set(actual_counts))
    rows = []
    abs_error_a_4 = []
    abs_error_a_8 = []
    abs_error_b_4 = []
    abs_error_b_8 = []

    for image_name in common_files:
        expected = expected_counts.get(image_name, 0)
        actual = actual_counts.get(image_name, {})

        if "pipeline_a_connectivity_4" in actual:
            detected_a_4 = actual.get("pipeline_a_connectivity_4", 0)
            detected_a_8 = actual.get("pipeline_a_connectivity_8", 0)
            detected_b_4 = actual.get("pipeline_b_connectivity_4", 0)
            detected_b_8 = actual.get("pipeline_b_connectivity_8", 0)
            diff_a_4 = detected_a_4 - expected
            diff_a_8 = detected_a_8 - expected
            diff_b_4 = detected_b_4 - expected
            diff_b_8 = detected_b_8 - expected
            abs_error_a_4.append(abs(diff_a_4))
            abs_error_a_8.append(abs(diff_a_8))
            abs_error_b_4.append(abs(diff_b_4))
            abs_error_b_8.append(abs(diff_b_8))

            rows.append({
                "imagem": image_name,
                "esperado": expected,
                "detectado_a_4": detected_a_4,
                "diff_a_4": diff_a_4,
                "detectado_a_8": detected_a_8,
                "diff_a_8": diff_a_8,
                "detectado_b_4": detected_b_4,
                "diff_b_4": diff_b_4,
                "detectado_b_8": detected_b_8,
                "diff_b_8": diff_b_8,
                "abs_error_a_4": abs(diff_a_4),
                "abs_error_a_8": abs(diff_a_8),
                "abs_error_b_4": abs(diff_b_4),
                "abs_error_b_8": abs(diff_b_8),
            })
        else:
            detected_4 = actual.get("connectivity_4", 0)
            detected_8 = actual.get("connectivity_8", 0)
            diff_4 = detected_4 - expected
            diff_8 = detected_8 - expected
            abs_error_4_value = abs(diff_4)
            abs_error_8_value = abs(diff_8)

            abs_error_a_4.append(abs_error_4_value)
            abs_error_a_8.append(abs_error_8_value)
            abs_error_b_4.append(abs_error_4_value)
            abs_error_b_8.append(abs_error_8_value)

            rows.append({
                "imagem": image_name,
                "esperado": expected,
                "detectado_a_4": detected_4,
                "diff_a_4": diff_4,
                "detectado_a_8": detected_8,
                "diff_a_8": diff_8,
                "detectado_b_4": detected_4,
                "diff_b_4": diff_4,
                "detectado_b_8": detected_8,
                "diff_b_8": diff_8,
                "abs_error_a_4": abs_error_4_value,
                "abs_error_a_8": abs_error_8_value,
                "abs_error_b_4": abs_error_4_value,
                "abs_error_b_8": abs_error_8_value,
            })

    return rows, abs_error_a_4, abs_error_a_8, abs_error_b_4, abs_error_b_8


def format_table(rows):
    headers = [
        "imagem",
        "esperado",
        "A_4",
        "A_diff_4",
        "B_4",
        "B_diff_4",
        "A_8",
        "A_diff_8",
        "B_8",
        "B_diff_8",
    ]

    widths = [len(header) for header in headers]
    for row in rows:
        values = [
            row["imagem"],
            str(row["esperado"]),
            str(row["detectado_a_4"]),
            str(row["diff_a_4"]),
            str(row["detectado_b_4"]),
            str(row["diff_b_4"]),
            str(row["detectado_a_8"]),
            str(row["diff_a_8"]),
            str(row["detectado_b_8"]),
            str(row["diff_b_8"]),
        ]
        for index, value in enumerate(values):
            widths[index] = max(widths[index], len(value))

    line = "  ".join(header.ljust(widths[idx]) for idx, header in enumerate(headers))
    separator = "  ".join("-" * widths[idx] for idx in range(len(headers)))

    lines = [line, separator]
    for row in rows:
        values = [
            row["imagem"],
            str(row["esperado"]),
            str(row["detectado_a_4"]),
            str(row["diff_a_4"]),
            str(row["detectado_b_4"]),
            str(row["diff_b_4"]),
            str(row["detectado_a_8"]),
            str(row["diff_a_8"]),
            str(row["detectado_b_8"]),
            str(row["diff_b_8"]),
        ]
        lines.append("  ".join(value.ljust(widths[idx]) for idx, value in enumerate(values)))

    return "\n".join(lines)


def print_console_report(actual_data, elapsed_testing=None, title="=== Relatório de avaliação estatística ==="):
    rows, abs_error_a_4, abs_error_a_8, abs_error_b_4, abs_error_b_8 = build_rows(actual_data)

    total_expected = sum(row["esperado"] for row in rows)
    total_detected_a_4 = sum(row["detectado_a_4"] for row in rows)
    total_detected_a_8 = sum(row["detectado_a_8"] for row in rows)
    total_detected_b_4 = sum(row["detectado_b_4"] for row in rows)
    total_detected_b_8 = sum(row["detectado_b_8"] for row in rows)

    summary = {
        "tempo_execucao_script_testes_seconds": round(elapsed_testing, 6) if elapsed_testing is not None else None,
        "total_imagens_avaliadas": len(rows),
        "total_esperado": total_expected,
        "total_detectado_pipeline_a_connectivity_4": total_detected_a_4,
        "total_detectado_pipeline_a_connectivity_8": total_detected_a_8,
        "total_detectado_pipeline_b_connectivity_4": total_detected_b_4,
        "total_detectado_pipeline_b_connectivity_8": total_detected_b_8,
        "mae_pipeline_a_connectivity_4": round(statistics.mean(abs_error_a_4), 6) if abs_error_a_4 else 0.0,
        "mae_pipeline_a_connectivity_8": round(statistics.mean(abs_error_a_8), 6) if abs_error_a_8 else 0.0,
        "mae_pipeline_b_connectivity_4": round(statistics.mean(abs_error_b_4), 6) if abs_error_b_4 else 0.0,
        "mae_pipeline_b_connectivity_8": round(statistics.mean(abs_error_b_8), 6) if abs_error_b_8 else 0.0,
    }

    print(f"\n{title}")
    if elapsed_testing is not None:
        print(f"Tempo de execução do script de teste: {elapsed_testing:.6f} s")
    print(f"Total de imagens avaliadas: {len(rows)}")
    print(f"Total esperado: {total_expected}")
    print(f"Pipeline A total detectado (4): {total_detected_a_4}")
    print(f"Pipeline A total detectado (8): {total_detected_a_8}")
    print(f"Pipeline B total detectado (4): {total_detected_b_4}")
    print(f"Pipeline B total detectado (8): {total_detected_b_8}")
    print(f"MAE pipeline A conectividade 4: {summary['mae_pipeline_a_connectivity_4']:.6f}")
    print(f"MAE pipeline A conectividade 8: {summary['mae_pipeline_a_connectivity_8']:.6f}")
    print(f"MAE pipeline B conectividade 4: {summary['mae_pipeline_b_connectivity_4']:.6f}")
    print(f"MAE pipeline B conectividade 8: {summary['mae_pipeline_b_connectivity_8']:.6f}")
    print("\nTabela comparativa: ")
    print(format_table(rows))

    return summary


def main():
    actual_data = json.loads(ACTUAL_RESULTS_FILE.read_text(encoding="utf-8")) if ACTUAL_RESULTS_FILE.exists() else {"images": []}
    print_console_report(actual_data, elapsed_testing=None)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
