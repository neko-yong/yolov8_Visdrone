"""Custom model modules for the SOD-YOLO VisDrone reproduction project."""

from .block import C2fEMA
from .ema import EMAAttention
from .gfpn import GFPNLite


def register_yolo_modules(enable_piou: bool = False) -> None:
    """Register project modules for Ultralytics YAML parsing."""
    import ultralytics.nn.tasks as yolo_tasks

    yolo_tasks.C2fEMA = C2fEMA
    if enable_piou:
        import ultralytics.utils.loss as yolo_loss

        from models.loss import piou_bbox_iou

        yolo_loss.bbox_iou = piou_bbox_iou


__all__ = ["C2fEMA", "EMAAttention", "GFPNLite", "register_yolo_modules"]
