"""Validate a YOLO detection dataset and render random annotated samples."""

from __future__ import annotations

import argparse
import random
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


CLASS_NAMES = [
    "pedestrian",
    "people",
    "bicycle",
    "car",
    "van",
    "truck",
    "tricycle",
    "awning-tricycle",
    "bus",
    "motor",
]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp"}
COLORS = [
    "#ff3b30",
    "#ff9500",
    "#ffcc00",
    "#34c759",
    "#00c7be",
    "#32ade6",
    "#007aff",
    "#5856d6",
    "#af52de",
    "#ff2d55",
]


def read_labels(label_path: Path) -> list[tuple[int, float, float, float, float]]:
    labels = []
    for line_number, line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"Expected 5 fields at {label_path}:{line_number}")
        class_id = int(fields[0])
        coordinates = tuple(map(float, fields[1:]))
        if not 0 <= class_id < len(CLASS_NAMES):
            raise ValueError(f"Invalid class id at {label_path}:{line_number}: {class_id}")
        if any(value < 0.0 or value > 1.0 for value in coordinates):
            raise ValueError(f"Coordinate outside [0, 1] at {label_path}:{line_number}")
        labels.append((class_id, *coordinates))
    return labels


def inspect_split(dataset_root: Path, split: str) -> tuple[dict[str, int], list[Path]]:
    image_dir = dataset_root / "images" / split
    label_dir = dataset_root / "labels" / split
    image_paths = sorted(
        path for path in image_dir.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES
    )
    label_paths = sorted(label_dir.glob("*.txt"))
    label_stems = {path.stem for path in label_paths}
    image_stems = {path.stem for path in image_paths}
    class_counts = Counter()
    empty_labels = 0

    for label_path in label_paths:
        labels = read_labels(label_path)
        if not labels:
            empty_labels += 1
        class_counts.update(label[0] for label in labels)

    result = {
        "images": len(image_paths),
        "labels": len(label_paths),
        "empty_labels": empty_labels,
        "images_without_labels": len(image_stems - label_stems),
        "labels_without_images": len(label_stems - image_stems),
        **{f"class_{class_id}": class_counts[class_id] for class_id in range(len(CLASS_NAMES))},
    }
    return result, image_paths


def render_sample(image_path: Path, label_path: Path, output_path: Path) -> None:
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    image_width, image_height = image.size

    for class_id, x_center, y_center, width, height in read_labels(label_path):
        x1 = (x_center - width / 2.0) * image_width
        y1 = (y_center - height / 2.0) * image_height
        x2 = (x_center + width / 2.0) * image_width
        y2 = (y_center + height / 2.0) * image_height
        color = COLORS[class_id]
        draw.rectangle((x1, y1, x2, y2), outline=color, width=2)
        text = f"{class_id} {CLASS_NAMES[class_id]}"
        text_box = draw.textbbox((x1, y1), text, font=font, stroke_width=1)
        text_height = text_box[3] - text_box[1]
        text_y = max(0, y1 - text_height - 4)
        draw.rectangle((x1, text_y, x1 + text_box[2] - text_box[0] + 4, text_y + text_height + 4), fill=color)
        draw.text((x1 + 2, text_y + 2), text, fill="white", font=font, stroke_width=1, stroke_fill="black")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, quality=95)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=project_root / "datasets" / "VisDrone_YOLO")
    parser.add_argument("--output", type=Path, default=project_root / "runs" / "dataset_check")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    all_images = []
    for split in ("train", "val"):
        stats, image_paths = inspect_split(args.dataset.resolve(), split)
        all_images.extend((split, path) for path in image_paths)
        print(f"[{split}] images={stats['images']}, labels={stats['labels']}, empty_labels={stats['empty_labels']}")
        print(
            f"[{split}] images_without_labels={stats['images_without_labels']}, "
            f"labels_without_images={stats['labels_without_images']}"
        )
        for class_id, class_name in enumerate(CLASS_NAMES):
            print(f"[{split}] class {class_id} {class_name}: {stats[f'class_{class_id}']}")

    random_generator = random.Random(args.seed)
    sample_count = min(args.samples, len(all_images))
    for index, (split, image_path) in enumerate(random_generator.sample(all_images, sample_count), start=1):
        label_path = args.dataset.resolve() / "labels" / split / f"{image_path.stem}.txt"
        output_path = args.output.resolve() / f"sample_{index}_{split}_{image_path.name}"
        render_sample(image_path, label_path, output_path)
        print(f"Saved visualization: {output_path}")


if __name__ == "__main__":
    main()
