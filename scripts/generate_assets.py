#!/usr/bin/env python3
"""Generate Akinator's brand assets.

Codex plugin validation **requires** `interface.composerIcon` and
`interface.logo`, and requires both to reference square images that really exist
inside the plugin. This script draws them.

They are generated rather than committed as opaque binaries for the same reason
everything else here is: a binary nobody can regenerate is a fact with no
provenance. The mark is defined in code, so it can be changed, reviewed as a
diff, and re-rendered at any size.

No third-party dependencies - the PNG encoder and the rasterizer are both here,
in about 150 lines. Rendering is analytic: each pixel's coverage comes from a
signed distance field rather than from supersampling, which is both faster and
sharper.

Deterministic: pure math, fixed compression level, no clock. Same source, same
bytes - which is what makes the drift check meaningful.

Usage:
    python scripts/generate_assets.py            # dry run
    python scripts/generate_assets.py --write    # render the assets
    python scripts/generate_assets.py --check    # exit 1 if drifted
"""

from __future__ import annotations

import argparse
import math
import struct
import sys
import zlib
from pathlib import Path

GENERATOR = "scripts/generate_assets.py"
SIZE = 512

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
# Deep navy ground, warm amber mark. Amber rather than another blue so the icon
# is legible at 16px against the blue-on-blue field most tool UIs present.

NAVY_TOP = (0x12, 0x24, 0x4A)
NAVY_BOTTOM = (0x07, 0x0F, 0x22)
AMBER = (0xF2, 0xB3, 0x3D)


# --------------------------------------------------------------------------
# Signed distance fields
# --------------------------------------------------------------------------
# Every shape returns a signed distance in normalized units, where the canvas
# spans [-1, 1] on both axes and y points up. Negative is inside.

def sd_rounded_box(px: float, py: float, half: float, radius: float) -> float:
    qx = abs(px) - half + radius
    qy = abs(py) - half + radius
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    inside = min(max(qx, qy), 0.0)
    return outside + inside - radius


def sd_circle(px: float, py: float, cx: float, cy: float, r: float) -> float:
    return math.hypot(px - cx, py - cy) - r


def sd_capsule(px: float, py: float, ax: float, ay: float,
               bx: float, by: float, r: float) -> float:
    pax, pay = px - ax, py - ay
    bax, bay = bx - ax, by - ay
    denom = bax * bax + bay * bay
    h = 0.0 if denom == 0 else max(0.0, min(1.0, (pax * bax + pay * bay) / denom))
    return math.hypot(pax - bax * h, pay - bay * h) - r


def sd_arc(px: float, py: float, cx: float, cy: float, radius: float,
           half_width: float, a0: float, a1: float) -> float:
    """Distance to a stroked arc from angle a0 to a1, with rounded caps.

    Angles are radians, counter-clockwise, and a1 > a0. A pixel whose angle
    falls outside the span is measured against the nearer end cap, which is what
    gives the stroke rounded ends instead of a hard chord.
    """
    vx, vy = px - cx, py - cy
    angle = math.atan2(vy, vx)
    while angle < a0:
        angle += 2.0 * math.pi

    if angle <= a1:
        return abs(math.hypot(vx, vy) - radius) - half_width

    cap = float("inf")
    for a in (a0, a1):
        cap = min(cap, sd_circle(px, py, cx + radius * math.cos(a),
                                 cy + radius * math.sin(a), half_width))
    return cap


# --------------------------------------------------------------------------
# The mark
# --------------------------------------------------------------------------

def question_mark(px: float, py: float, scale: float) -> float:
    """The Akinator mark: a question mark. Ask everything.

    Built from three primitives so it stays crisp at any size: the hook is a
    stroked arc, the stem a capsule tangent to where the arc ends, and the dot a
    circle. Coordinates are divided by `scale` so the whole mark grows and
    shrinks about the origin.
    """
    px /= scale
    py /= scale

    width = 0.105

    # Hook: from -60 degrees, counter-clockwise over the top, to 190 degrees.
    # That span covers the right shoulder, the crown and the left shoulder.
    hook = sd_arc(px, py, 0.0, 0.34, 0.30, width,
                  math.radians(-60.0), math.radians(190.0))

    # Stem: starts where the arc ends and falls to just above the dot.
    end_x = 0.30 * math.cos(math.radians(-60.0))
    end_y = 0.34 + 0.30 * math.sin(math.radians(-60.0))
    stem = sd_capsule(px, py, end_x, end_y, 0.0, -0.20, width)

    dot = sd_circle(px, py, 0.0, -0.50, 0.125)

    return min(hook, stem, dot) * scale


# --------------------------------------------------------------------------
# Rasterizer
# --------------------------------------------------------------------------

def _mix(a: tuple[int, int, int], b: tuple[int, int, int],
         t: float) -> tuple[float, float, float]:
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def _coverage(distance: float, pixel: float) -> float:
    """Analytic antialiasing: convert a signed distance to pixel coverage."""
    return max(0.0, min(1.0, 0.5 - distance / pixel))


def render(size: int, mark_scale: float, corner_radius: float) -> bytes:
    """Render one asset to raw RGBA rows."""
    pixel = 2.0 / size
    out = bytearray()

    for row in range(size):
        py = 1.0 - (row + 0.5) * pixel          # y points up
        out.append(0)                            # PNG filter: none
        for col in range(size):
            px = -1.0 + (col + 0.5) * pixel

            ground = _coverage(
                sd_rounded_box(px, py, 1.0, corner_radius), pixel
            )
            if ground <= 0.0:
                out.extend((0, 0, 0, 0))
                continue

            # Vertical gradient, lighter at the top.
            r, g, b = _mix(NAVY_BOTTOM, NAVY_TOP, (py + 1.0) * 0.5)

            ink = _coverage(question_mark(px, py, mark_scale), pixel)
            if ink > 0.0:
                r += (AMBER[0] - r) * ink
                g += (AMBER[1] - g) * ink
                b += (AMBER[2] - b) * ink

            out.extend((
                int(r + 0.5), int(g + 0.5), int(b + 0.5),
                int(ground * 255.0 + 0.5),
            ))

    return bytes(out)


# --------------------------------------------------------------------------
# PNG encoder
# --------------------------------------------------------------------------

def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (struct.pack(">I", len(payload)) + kind + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF))


def encode_png(size: int, raw: bytes) -> bytes:
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8-bit RGBA
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


# --------------------------------------------------------------------------
# Assets
# --------------------------------------------------------------------------
# Both are square, as Codex requires. The icon carries a larger mark because it
# is displayed small; the logo has more breathing room.

ASSETS = {
    "assets/akinator-icon.png": {"mark_scale": 1.00, "corner_radius": 0.42},
    "assets/akinator-logo.png": {"mark_scale": 0.84, "corner_radius": 0.30},
}


def plan(repo: Path) -> dict[str, bytes]:
    return {
        rel: encode_png(SIZE, render(SIZE, **params))
        for rel, params in sorted(ASSETS.items())
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="generate_assets")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    repo = Path(args.root).resolve()
    if not (repo / ".codex-plugin").is_dir():
        print(f"no .codex-plugin/ under {repo}", file=sys.stderr)
        return 2

    desired = plan(repo)
    drifted: list[str] = []

    for rel, content in desired.items():
        path = repo / rel
        current = path.read_bytes() if path.is_file() else None
        if current == content:
            continue
        drifted.append(rel)
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            print(f"wrote   {rel} ({len(content):,} bytes, {SIZE}x{SIZE})")

    if args.write:
        if not drifted:
            print("assets already up to date")
        return 0

    for rel in drifted:
        print(f"drifted {rel}")
    if drifted:
        print(f"\nFix with: python {GENERATOR} --write")
        return 1

    print("assets match the generator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
