#!/usr/bin/env python3
"""VELMARA — a travel poster for a place that does not exist.

Draws a 1024x1024 poster with PIL only (no network, no downloaded images).
Deterministic: fixed geometry, fixed palette, no randomness, no timestamps.
Writes /output/entry.png (falls back to ./output/entry.png when /output
is not writable, e.g. during local testing).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = "/output/entry.png"

# Palette: dusk indigo sky, amber horizon, cream type, teal sea of cloud.
INK_TOP = (18, 22, 66)
INK_MID = (58, 48, 110)
DUSK = (150, 84, 130)
AMBER = (247, 178, 102)
GOLD = (255, 205, 120)
CREAM = (250, 238, 210)
CLOUD = (244, 222, 196)
CLOUD_SHADOW = (214, 178, 168)
ROCK = (74, 52, 84)
ROCK_DARK = (52, 36, 64)
GREEN = (46, 110, 78)
GREEN_DARK = (30, 80, 58)
WATER = (170, 214, 228)
TOWER = (246, 236, 214)
TOWER_SHADE = (214, 196, 168)


def font(path_candidates, size):
    for p in path_candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default(size)


SERIF = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf",
]
SANS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vertical_gradient(img, top, mid, bottom, y_mid):
    """Three-stop vertical gradient painted row by row (deterministic)."""
    d = ImageDraw.Draw(img)
    for y in range(H):
        if y < y_mid:
            c = lerp(top, mid, y / max(1, y_mid))
        else:
            c = lerp(mid, bottom, (y - y_mid) / max(1, H - y_mid))
        d.line([(0, y), (W, y)], fill=c)


def ellipse(draw, cx, cy, rx, ry, fill):
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=fill)


def cloud(draw, cx, cy, scale, tint):
    """A soft flat cloud made of overlapping ellipses, with a warm
    under-shadow so it sits in the sky instead of floating flat."""
    # warm under-shadow, slightly lower and wider than the body
    puffs = [(-46, 6, 52, 26), (-14, -12, 46, 30), (22, -4, 48, 26),
             (52, 8, 40, 20), (-72, 12, 34, 16)]
    for dx, dy, rx, ry in puffs:
        ellipse(draw, cx + int(dx * scale), cy + int((dy + 14) * scale),
                int(rx * scale), int(ry * scale * 0.8), CLOUD_SHADOW)
    for dx, dy, rx, ry in puffs:
        ellipse(draw, cx + int(dx * scale), cy + int(dy * scale),
                int(rx * scale), int(ry * scale), tint)


def draw_tracked(draw, cx, y, text, fnt, fill, tracking):
    """Draw text centered, with extra tracking between letters."""
    widths = []
    total = 0
    for ch in text:
        w = draw.textlength(ch, font=fnt)
        widths.append(w)
        total += w + tracking
    total -= tracking
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += w + tracking


def island(draw, cx, top_y, half_w, depth, flip=False):
    """A floating island: green plateau on top, rock tapering to a point."""
    # plateau
    draw.ellipse([cx - half_w, top_y - 14, cx + half_w, top_y + 22], fill=GREEN)
    draw.rectangle([cx - half_w, top_y, cx + half_w, top_y + 12], fill=GREEN)
    # rock underside tapering to a point, with terraced facets
    tip_x, tip_y = cx - 6, top_y + depth + 26
    draw.polygon([
        (cx - half_w + 8, top_y + 10),
        (cx + half_w - 8, top_y + 10),
        (cx + 18, top_y + depth),
        (tip_x, tip_y),
    ], fill=ROCK)
    # rock shading facet
    draw.polygon([
        (cx - half_w + 8, top_y + 10),
        (cx - 30, top_y + 10),
        (tip_x, tip_y),
    ], fill=ROCK_DARK)
    # terraces: muted ledges stepping down the rock face (close in tone
    # to the rock so they read as strata, not stripes)
    for i, (ty, tw) in enumerate([(0.30, 0.72), (0.55, 0.50), (0.78, 0.28)]):
        y = top_y + 10 + int((depth + 16) * ty)
        hw = int(half_w * tw)
        ledge = (88, 64, 96) if i % 2 == 0 else (80, 58, 90)
        draw.polygon([(cx - hw, y), (cx + hw, y),
                      (cx + int(hw * 0.55), y + 12),
                      (cx - int(hw * 0.55), y + 12)], fill=ledge)
    # small crystal shard at the tip
    draw.polygon([(tip_x - 7, tip_y - 6), (tip_x + 7, tip_y - 6),
                  (tip_x, tip_y + 18)], fill=(170, 214, 228))
    # grass fringe
    for dx in range(-half_w + 16, half_w - 8, 26):
        draw.polygon([(cx + dx, top_y + 8), (cx + dx + 8, top_y + 8),
                      (cx + dx + 4, top_y + 20)], fill=GREEN_DARK)


def tree(draw, x, y, s):
    draw.rectangle([x - 2 * s, y, x + 2 * s, y + 12 * s], fill=(58, 40, 52))
    draw.polygon([(x - 11 * s, y), (x + 11 * s, y), (x, y - 22 * s)], fill=GREEN_DARK)
    draw.polygon([(x - 8 * s, y - 12 * s), (x + 8 * s, y - 12 * s),
                  (x, y - 30 * s)], fill=GREEN)


def upward_fall(draw, x, y0, y1, bend=34):
    """A waterfall that falls upward: a tapering arc of water.

    Quadratic arc that sweeps outward as it rises, wide where it leaves
    the island and narrowing as it climbs, with a pale highlight thread
    and a spray of droplets — so it reads as water, not a stick.
    """
    # control point: arc bows outward (away from the island centre)
    cx = x + bend
    cy = (y0 + y1) // 2
    steps = 40
    pts = []
    for i in range(steps + 1):
        t = i / steps
        bx = (1 - t) ** 2 * x + 2 * (1 - t) * t * cx + t * t * (x + bend * 2.2)
        by = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1
        pts.append((int(bx), int(by)))
    # tapered body: consecutive segments with shrinking width, so the
    # stream reads as one continuous ribbon, not a chain of beads
    for i in range(steps):
        t = i / steps
        w = max(2, int(11 - 7 * t))
        draw.line([pts[i], pts[i + 1]], fill=WATER, width=w)
    # pale highlight thread running along the sun side of the stream
    hl = [(px + 3, py) for px, py in pts]
    draw.line(hl, fill=(226, 242, 248), width=2)
    # spray where the water leaves the island
    bx, by = pts[0]
    for dx, dy, r in [(-10, 4, 6), (10, 6, 5), (0, 10, 6), (-4, 12, 4)]:
        ellipse(draw, bx + dx, by + dy, r, int(r * 0.7), (226, 240, 244))
    # mist blooming at the top of the arc
    top_x, top_y = pts[-1]
    for dx, dy, r in [(-22, -4, 11), (-6, -16, 14), (14, -10, 11),
                      (24, 2, 9), (2, 2, 9), (-14, 6, 8)]:
        ellipse(draw, top_x + dx, top_y + dy, r, int(r * 0.65),
                (226, 240, 244))


def main():
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- sky ---
    vertical_gradient(img, INK_TOP, DUSK, AMBER, 560)

    # --- stars in the upper sky (a few with a sparkle cross) ---
    stars = [(80, 60), (170, 130), (300, 50), (430, 100), (560, 55),
             (700, 120), (830, 60), (920, 140), (950, 260), (60, 220),
             (250, 190), (640, 200), (880, 210)]
    for sx, sy in stars:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(235, 225, 200))
    for sx, sy, s in [(300, 50, 7), (700, 120, 6), (880, 210, 6)]:
        draw.line([(sx - s, sy), (sx + s, sy)], fill=(235, 225, 200), width=2)
        draw.line([(sx, sy - s), (sx, sy + s)], fill=(235, 225, 200), width=2)

    # --- low sun with a smooth glow (many fine steps, no banding) ---
    sun_cx, sun_cy, sun_r = 712, 480, 88
    glow_steps = 48
    for i in range(glow_steps, 0, -1):
        t = i / glow_steps
        r = int(sun_r + (232 - sun_r) * t)
        a = int(2 + 34 * (1 - t) ** 2)
        draw.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r],
                     fill=(255, 196, 110, a))
    ellipse(draw, sun_cx, sun_cy, sun_r, sun_r, GOLD)
    # thin warm halo ring right at the disc edge
    draw.ellipse([sun_cx - sun_r - 3, sun_cy - sun_r - 3,
                  sun_cx + sun_r + 3, sun_cy + sun_r + 3],
                 outline=(255, 226, 160), width=2)

    # --- distant thin clouds ---
    cloud(draw, 180, 400, 0.8, (226, 170, 160))
    cloud(draw, 850, 330, 0.7, (226, 170, 160))

    # --- birds: a loose V in open sky, clear of the title ---
    for bx, by, s in [(215, 330, 13), (258, 312, 10), (300, 330, 12),
                      (838, 268, 11), (882, 246, 8)]:
        draw.line([(bx - s, by), (bx, by - s // 2), (bx + s, by)],
                  fill=CREAM, width=3)

    # --- small floating islets (right) ---
    island(draw, 845, 520, 78, 120)
    tree(draw, 845, 500, 1)
    island(draw, 905, 640, 52, 84)
    tree(draw, 895, 622, 1)

    # --- small floating islet (left) ---
    island(draw, 150, 600, 64, 100)
    tree(draw, 140, 582, 1)
    tree(draw, 168, 586, 1)

    # --- the main island: Velmara's tower rock ---
    island(draw, 480, 560, 210, 185)
    # warm rim light: a thin muted line along the sun-side rock edge
    draw.line([(690, 570), (474, 771)], fill=(196, 128, 116), width=3)
    tree(draw, 330, 540, 2)
    tree(draw, 360, 548, 1)
    tree(draw, 620, 542, 2)
    tree(draw, 648, 550, 1)
    # bushes on the plateau
    for bx, by, br in [(400, 552, 12), (560, 550, 10), (590, 554, 8)]:
        ellipse(draw, bx, by, br, int(br * 0.7), GREEN_DARK)

    # landmark: the white tower with a gold dome
    tx = 480
    draw.rectangle([tx - 30, 380, tx + 30, 560], fill=TOWER)
    draw.rectangle([tx + 10, 380, tx + 30, 560], fill=TOWER_SHADE)
    # gold band under the roof
    draw.rectangle([tx - 34, 372, tx + 34, 380], fill=GOLD)
    draw.polygon([(tx - 38, 372), (tx + 38, 372), (tx, 314)], fill=GOLD)
    draw.ellipse([tx - 8, 298, tx + 8, 314], fill=GOLD)
    # arched tower windows, lit warm
    for wy in (404, 446, 488):
        draw.rectangle([tx - 8, wy, tx + 8, wy + 18], fill=(255, 196, 110))
        draw.ellipse([tx - 8, wy - 8, tx + 8, wy + 4], fill=(255, 196, 110))
    # arched door at the base
    draw.rectangle([tx - 9, 528, tx + 9, 560], fill=(58, 40, 52))
    draw.ellipse([tx - 9, 519, tx + 9, 535], fill=(58, 40, 52))
    # flag, flying free of any cloud
    draw.line([(tx, 298), (tx, 270)], fill=CREAM, width=3)
    draw.polygon([(tx, 270), (tx + 30, 277), (tx, 286)], fill=GOLD)

    # --- upward waterfalls arcing off the main island ---
    upward_fall(draw, 296, 566, 340, bend=40)
    upward_fall(draw, 664, 562, 316, bend=-36)

    # --- haze band to separate sky from the cloud sea ---
    for y in range(800, 862):
        a = int(34 * (y - 800) / 62)
        draw.line([(0, y), (W, y)], fill=(250, 214, 170, a))

    # --- sea of cloud at the bottom ---
    for cx, cy, sc in [(120, 900, 1.6), (420, 940, 1.9), (760, 905, 1.7),
                       (980, 950, 1.4), (250, 985, 1.5), (600, 990, 1.6)]:
        cloud(draw, cx, cy, sc, CLOUD)
    for cx, cy, sc in [(200, 860, 1.1), (560, 880, 1.2), (880, 865, 1.0)]:
        cloud(draw, cx, cy, sc, CLOUD_SHADOW)

    # --- frame ---
    draw.rectangle([26, 26, W - 26, H - 26], outline=CREAM, width=4)
    draw.rectangle([38, 38, W - 38, H - 38], outline=CREAM, width=1)

    # --- type ---
    title_font = font(SERIF, 116)
    sub_font = font(SANS, 34)
    foot_font = font(SANS, 26)

    # title shadow then title (tighter tracking so the word holds together)
    draw_tracked(draw, W // 2 + 4, 78, "VELMARA", title_font, (20, 16, 52), 10)
    draw_tracked(draw, W // 2, 74, "VELMARA", title_font, CREAM, 10)
    # thin rule under the title with a gold diamond at its centre
    draw.line([(W // 2 - 190, 232), (W // 2 + 190, 232)], fill=GOLD, width=3)
    draw.polygon([(W // 2, 222), (W // 2 + 10, 232), (W // 2, 242),
                  (W // 2 - 10, 232)], fill=GOLD)
    draw_tracked(draw, W // 2, 248, "WHERE THE SEA FALLS UPWARD",
                 sub_font, CREAM, 8)

    # footer line on a deep indigo band (matches the sky, not grey)
    # with gold hairlines so it reads as part of the poster, not pasted on
    draw.rectangle([60, 926, W - 60, 976], fill=(24, 20, 60, 205))
    draw.line([(60, 926), (W - 60, 926)], fill=GOLD, width=2)
    draw.line([(60, 976), (W - 60, 976)], fill=GOLD, width=2)
    draw_tracked(draw, W // 2, 938, "THE ISLES ABOVE THE CLOUDS",
                 foot_font, (250, 238, 210), 6)

    # --- write output ---
    out_dir = os.path.dirname(OUT)
    try:
        os.makedirs(out_dir, exist_ok=True)
        img.save(OUT, format="PNG", optimize=True)
        path = OUT
    except OSError:
        local = os.path.join(os.getcwd(), "output", "entry.png")
        os.makedirs(os.path.dirname(local), exist_ok=True)
        img.save(local, format="PNG", optimize=True)
        path = local
    print("wrote", path, img.size)


if __name__ == "__main__":
    sys.exit(main())
