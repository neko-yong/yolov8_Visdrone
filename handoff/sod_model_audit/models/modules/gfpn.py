"""GFPN-lite neck module for YOLOv8-style P3/P4/P5 feature fusion."""

from __future__ import annotations

from typing import Sequence

import torch
from torch import Tensor, nn
import torch.nn.functional as F


class ConvBNAct(nn.Module):
    """Lightweight Conv-BN-SiLU block."""

    def __init__(self, c1: int, c2: int, k: int = 1, s: int = 1) -> None:
        super().__init__()
        padding = k // 2
        self.block = nn.Sequential(
            nn.Conv2d(c1, c2, k, s, padding, bias=False),
            nn.BatchNorm2d(c2),
            nn.SiLU(inplace=True),
        )

    def forward(self, x: Tensor) -> Tensor:
        return self.block(x)


class FusionBlock(nn.Module):
    """Concat fusion followed by 1x1 and 3x3 lightweight conv fusion."""

    def __init__(self, c1: int, c2: int) -> None:
        super().__init__()
        self.fuse = nn.Sequential(
            ConvBNAct(c1, c2, k=1, s=1),
            ConvBNAct(c2, c2, k=3, s=1),
        )

    def forward(self, features: Sequence[Tensor]) -> Tensor:
        return self.fuse(torch.cat(tuple(features), dim=1))


class GFPNLite(nn.Module):
    """Simplified GFPN neck with bidirectional concat fusion and skip connections.

    Inputs:
        P3, P4, P5 feature maps from a YOLOv8 backbone.

    Outputs:
        P3, P4, P5 fused feature maps with the same strides as the original
        YOLOv8 Detect head expects.
    """

    def __init__(
        self,
        channels: tuple[int, int, int] = (128, 256, 512),
        out_channels: tuple[int, int, int] | None = None,
    ) -> None:
        super().__init__()
        c3, c4, c5 = channels
        o3, o4, o5 = out_channels or channels

        self.p5_reduce = ConvBNAct(c5, o4, k=1, s=1)
        self.p4_top_down = FusionBlock(o4 + c4, o4)
        self.p4_reduce = ConvBNAct(o4, o3, k=1, s=1)
        self.p3_out = FusionBlock(o3 + c3, o3)

        self.p3_down = ConvBNAct(o3, o3, k=3, s=2)
        self.p4_out = FusionBlock(o3 + o4 + c4, o4)
        self.p4_down = ConvBNAct(o4, o4, k=3, s=2)
        self.p5_out = FusionBlock(o4 + o4 + c5, o5)

    def forward(self, features: Sequence[Tensor]) -> list[Tensor]:
        if len(features) != 3:
            raise ValueError(f"GFPNLite expects 3 feature maps P3/P4/P5, got {len(features)}")

        p3, p4, p5 = features

        p5_lat = self.p5_reduce(p5)
        p5_up = F.interpolate(p5_lat, size=p4.shape[-2:], mode="nearest")
        p4_td = self.p4_top_down((p5_up, p4))

        p4_lat = self.p4_reduce(p4_td)
        p4_up = F.interpolate(p4_lat, size=p3.shape[-2:], mode="nearest")
        p3_out = self.p3_out((p4_up, p3))

        p3_down = self.p3_down(p3_out)
        p4_out = self.p4_out((p3_down, p4_td, p4))

        p4_down = self.p4_down(p4_out)
        p5_out = self.p5_out((p4_down, p5_lat, p5))

        return [p3_out, p4_out, p5_out]
