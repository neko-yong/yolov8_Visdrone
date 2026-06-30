"""PIoU loss for YOLOv8-style xyxy bounding boxes."""

from __future__ import annotations

import torch
from torch import Tensor, nn


class PIoULoss(nn.Module):
    """Penalty IoU loss with center, corner, and small-object terms."""

    def __init__(
        self,
        center_weight: float = 0.5,
        corner_weight: float = 0.25,
        small_object_gain: float = 0.5,
        eps: float = 1e-7,
    ) -> None:
        super().__init__()
        self.center_weight = center_weight
        self.corner_weight = corner_weight
        self.small_object_gain = small_object_gain
        self.eps = eps

    def forward(self, pred: Tensor, target: Tensor, xywh: bool = False) -> Tensor:
        pred_xyxy = _to_xyxy(pred, xywh)
        target_xyxy = _to_xyxy(target, xywh)
        loss, _ = _piou_loss_components(
            pred_xyxy,
            target_xyxy,
            center_weight=self.center_weight,
            corner_weight=self.corner_weight,
            small_object_gain=self.small_object_gain,
            eps=self.eps,
        )
        return loss


def piou_bbox_iou(
    box1: Tensor,
    box2: Tensor,
    xywh: bool = True,
    GIoU: bool = False,
    DIoU: bool = False,
    CIoU: bool = False,
    eps: float = 1e-7,
) -> Tensor:
    """Ultralytics-compatible bbox_iou replacement.

    YOLOv8 BboxLoss calls ``1 - bbox_iou(..., CIoU=True)``. Returning
    ``1 - PIoU_loss`` lets the existing loss wrapper use PIoU without changing
    its public interface or Detect head.
    """
    pred_xyxy = _to_xyxy(box1, xywh)
    target_xyxy = _to_xyxy(box2, xywh)
    loss, iou = _piou_loss_components(pred_xyxy, target_xyxy, eps=eps)
    if CIoU:
        return 1.0 - loss
    if DIoU or GIoU:
        return iou
    return iou


def _to_xyxy(box: Tensor, xywh: bool) -> Tensor:
    if not xywh:
        return box
    x, y, w, h = box.chunk(4, dim=-1)
    half_w, half_h = w / 2, h / 2
    return torch.cat((x - half_w, y - half_h, x + half_w, y + half_h), dim=-1)


def _piou_loss_components(
    pred: Tensor,
    target: Tensor,
    center_weight: float = 0.5,
    corner_weight: float = 0.25,
    small_object_gain: float = 0.5,
    eps: float = 1e-7,
) -> tuple[Tensor, Tensor]:
    p_x1, p_y1, p_x2, p_y2 = pred.chunk(4, dim=-1)
    t_x1, t_y1, t_x2, t_y2 = target.chunk(4, dim=-1)

    p_w = (p_x2 - p_x1).clamp_min(eps)
    p_h = (p_y2 - p_y1).clamp_min(eps)
    t_w = (t_x2 - t_x1).clamp_min(eps)
    t_h = (t_y2 - t_y1).clamp_min(eps)

    inter_w = (p_x2.minimum(t_x2) - p_x1.maximum(t_x1)).clamp_min(0)
    inter_h = (p_y2.minimum(t_y2) - p_y1.maximum(t_y1)).clamp_min(0)
    inter = inter_w * inter_h
    union = p_w * p_h + t_w * t_h - inter + eps
    iou = inter / union

    c_x1 = p_x1.minimum(t_x1)
    c_y1 = p_y1.minimum(t_y1)
    c_x2 = p_x2.maximum(t_x2)
    c_y2 = p_y2.maximum(t_y2)
    c_w = (c_x2 - c_x1).clamp_min(eps)
    c_h = (c_y2 - c_y1).clamp_min(eps)
    c_diag = c_w.square() + c_h.square() + eps

    p_cx = (p_x1 + p_x2) * 0.5
    p_cy = (p_y1 + p_y2) * 0.5
    t_cx = (t_x1 + t_x2) * 0.5
    t_cy = (t_y1 + t_y2) * 0.5
    center_penalty = ((p_cx - t_cx).square() + (p_cy - t_cy).square()) / c_diag

    corner_distance = (
        (p_x1 - t_x1).square()
        + (p_y1 - t_y1).square()
        + (p_x2 - t_x2).square()
        + (p_y2 - t_y2).square()
    )
    corner_penalty = corner_distance / (2.0 * c_diag)

    target_area = (t_w * t_h).clamp_min(eps)
    enclosing_area = (c_w * c_h).clamp_min(eps)
    small_weight = 1.0 + small_object_gain * (1.0 - (target_area / enclosing_area).clamp(0, 1))

    base_loss = 1.0 - iou
    penalty = center_weight * center_penalty + corner_weight * corner_penalty
    loss = (base_loss + penalty) * small_weight
    return loss.clamp_min(0), iou
