"""Print the runtime environment used by the YOLOv8 project."""

from __future__ import annotations

import importlib.metadata
import platform
import sys

import cv2
import numpy
import torch
import torchvision
import ultralytics


def package_version(distribution: str, fallback: str = "Not installed") -> str:
    """Return an installed distribution version without invoking pip."""
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return fallback


def main() -> None:
    cuda_version = torch.version.cuda or "Not available"
    gpu_name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Not available"

    information = [
        ("Python", platform.python_version()),
        ("Operating system", platform.platform()),
        ("CUDA (PyTorch build)", cuda_version),
        ("CUDA available", str(torch.cuda.is_available())),
        ("GPU", gpu_name),
        ("torch", torch.__version__),
        ("torchvision", torchvision.__version__),
        ("ultralytics", ultralytics.__version__),
        ("numpy", numpy.__version__),
        ("opencv-python", package_version("opencv-python", cv2.__version__)),
        ("Python executable", sys.executable),
    ]

    print("YOLOv8 Environment Information")
    print("=" * 31)
    width = max(len(label) for label, _ in information)
    for label, value in information:
        print(f"{label:<{width}} : {value}")


if __name__ == "__main__":
    main()
