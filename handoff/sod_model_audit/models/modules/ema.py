"""Lightweight EMA-style channel attention for YOLO feature maps."""

from __future__ import annotations

import torch
from torch import Tensor, nn


class EMAAttention(nn.Module):
    """Efficient multi-scale channel attention.

    The module keeps the input shape unchanged. It combines global average
    pooling with coarse spatial pooling to produce lightweight channel
    reweighting for small-object feature enhancement.
    """

    def __init__(self, channels: int, reduction: int = 16) -> None:
        super().__init__()
        hidden = max(channels // reduction, 8)
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.scale_pool = nn.AdaptiveAvgPool2d(2)
        self.fc = nn.Sequential(
            nn.Conv2d(channels, hidden, 1, bias=True),
            nn.SiLU(inplace=True),
            nn.Conv2d(hidden, channels, 1, bias=True),
        )
        self.scale_fc = nn.Sequential(
            nn.Conv2d(channels, hidden, 1, bias=True),
            nn.SiLU(inplace=True),
            nn.Conv2d(hidden, channels, 1, bias=True),
        )
        self.act = nn.Sigmoid()

    def forward(self, x: Tensor) -> Tensor:
        global_weight = self.fc(self.global_pool(x))
        scale_context = self.scale_pool(x).mean(dim=(2, 3), keepdim=True)
        scale_weight = self.scale_fc(scale_context)
        weight = self.act(global_weight + scale_weight)
        return x * weight
