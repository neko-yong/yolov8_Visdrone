"""Convert VisDrone2019-DET annotations to Ultralytics YOLO format."""

from __future__ import annotations

import argparse
import shutil
from collections import Counter
from pathlib import Path

from PIL import Image


IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}


def convert_split(source_root: Path, output_root: Path, split: str) -> Counter:
    #定义路径
    source_images = source_root / f"VisDrone2019-DET-{split}" / "images"
    source_annotations = source_root / f"VisDrone2019-DET-{split}" / "annotations"
    output_images = output_root / "images" / split
    output_labels = output_root / "labels" / split
    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    #读取所有文件并统计
    image_paths = sorted(
        path for path in source_images.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )
    stats = Counter(images=len(image_paths))

    for image_path in image_paths:
        #找到对应标注文件
        annotation_path = source_annotations / f"{image_path.stem}.txt"
        label_path = output_labels / f"{image_path.stem}.txt"

        #读取图片尺寸
        with Image.open(image_path) as image:
            image_width, image_height = image.size

        #读取标注并转换为YOLO格式
        labels = []
        if annotation_path.exists():
            for line_number, raw_line in enumerate(
                annotation_path.read_text(encoding="utf-8-sig").splitlines(), start=1
            ):
                line = raw_line.strip().rstrip(",") #去掉空格和末尾逗号
                if not line:
                    continue

                fields = [field.strip() for field in line.split(",")] #切分字段
                if len(fields) < 8: #检查格式是否合法，不够8个字段说明标注损坏
                    stats["malformed"] += 1
                    print(f"Warning: skipping malformed row {annotation_path}:{line_number}")
                    continue

                #转数字
                try:
                    left, top, width, height, score, category = map(float, fields[:6])
                except ValueError:
                    stats["malformed"] += 1
                    print(f"Warning: skipping non-numeric row {annotation_path}:{line_number}")
                    continue

                category_id = int(category)
                if category_id == 0: #忽略区域
                    stats["ignored_region"] += 1
                    continue
                if score == 0: #官方认为无效实例
                    stats["score_zero"] += 1
                    continue
                if width <= 0 or height <= 0: #宽高非法
                    stats["invalid_size"] += 1
                    continue
                if not 1 <= category_id <= 10: #类别非法
                    stats["invalid_category"] += 1
                    continue

                #边界裁剪，确保坐标在图片范围内
                x1 = max(0.0, min(left, float(image_width)))
                y1 = max(0.0, min(top, float(image_height)))
                x2 = max(0.0, min(left + width, float(image_width)))
                y2 = max(0.0, min(top + height, float(image_height)))
                clipped_width = x2 - x1
                clipped_height = y2 - y1
                if clipped_width <= 0 or clipped_height <= 0:
                    stats["invalid_after_clip"] += 1
                    continue

                #归一化
                x_center = ((x1 + x2) / 2.0) / image_width
                y_center = ((y1 + y2) / 2.0) / image_height
                normalized_width = clipped_width / image_width
                normalized_height = clipped_height / image_height
                #保存标签，YOLO类别ID从0开始，因此减1
                labels.append(
                    f"{category_id - 1} {x_center:.6f} {y_center:.6f} "
                    f"{normalized_width:.6f} {normalized_height:.6f}"
                )
                stats[f"class_{category_id - 1}"] += 1
                stats["instances"] += 1
        else:
            stats["missing_annotations"] += 1
            print(f"Warning: annotation not found for {image_path.name}")

        #复制图片并写入标签文件
        shutil.copy2(image_path, output_images / image_path.name)
        label_path.write_text("\n".join(labels) + ("\n" if labels else ""), encoding="utf-8")
        if not labels:
            stats["empty_labels"] += 1

    return stats

#读取命令行参数，定义默认路径
def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=project_root / "datasets" / "VisDrone",
        help="Directory containing the original VisDrone2019-DET split folders.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "datasets" / "VisDrone_YOLO",
        help="YOLO dataset output directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    for split in ("train", "val"):
        stats = convert_split(args.source.resolve(), args.output.resolve(), split)
        print(f"{split}: " + ", ".join(f"{key}={value}" for key, value in sorted(stats.items())))


if __name__ == "__main__":
    main()
