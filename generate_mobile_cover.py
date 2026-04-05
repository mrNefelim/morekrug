#!/usr/bin/env python3
"""Generate mobile cover image 1080x1350 for Boomstarter/social media."""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

WIDTH, HEIGHT = 1080, 1350
CENTER_X, CENTER_Y = WIDTH // 2, int(HEIGHT * 0.42)

BG_DARK = (10, 22, 40)
BG_TEAL = (13, 32, 32)
GLOW_COLOR = (30, 180, 180)
RING_COLOR = (60, 110, 110, 50)
BADGE_BG = (180, 240, 230)
BADGE_GLOW = (60, 200, 200, 100)
ICON_COLOR = (30, 70, 70)

RING_RADII = [100, 170, 260, 350, 440]

ICONS = [
    {"symbol": "\u2709", "angle": 180, "orbit": 4, "label": "email"},
    {"symbol": "\u{1F4C5}", "angle": 135, "orbit": 4, "label": "calendar"},
    {"symbol": "\u{1F4AC}", "angle": 55, "orbit": 3, "label": "chat"},
    {"symbol": "\u{1F514}", "angle": 30, "orbit": 4, "label": "bell"},
    {"symbol": "\u{1F3A5}", "angle": -15, "orbit": 4, "label": "video"},
    {"symbol": "\u{1F4DD}", "angle": 200, "orbit": 2, "label": "notes"},
    {"symbol": "\u260E", "angle": 230, "orbit": 3, "label": "phone"},
    {"symbol": "\u{1F4CD}", "angle": 290, "orbit": 3, "label": "location"},
]


def make_radial_gradient(width, height, cx, cy, inner_color, outer_color, radius):
    img = Image.new("RGB", (width, height), outer_color)
    draw = ImageDraw.Draw(img)
    steps = 200
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(radius * t)
        color = tuple(
            int(outer_color[c] + (inner_color[c] - outer_color[c]) * (1 - t) ** 1.5)
            for c in range(3)
        )
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=color,
        )
    return img


def draw_glow_circle(base, cx, cy, radius, color, alpha=60, blur=30):
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for i in range(10, 0, -1):
        t = i / 10
        r = int(radius * (1 + 0.3 * t))
        a = int(alpha * (1 - t))
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(*color[:3], a),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base.convert("RGBA"), glow)


def draw_icon_badge(img, x, y, badge_radius=28):
    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    for i in range(8, 0, -1):
        t = i / 8
        r = int(badge_radius * (1 + 0.8 * t))
        a = int(35 * (1 - t))
        glow_draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=(100, 230, 220, a),
        )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
    result = Image.alpha_composite(img, glow_layer)

    draw = ImageDraw.Draw(result)
    draw.ellipse(
        [x - badge_radius, y - badge_radius, x + badge_radius, y + badge_radius],
        fill=(190, 245, 235, 230),
    )

    inner_r = badge_radius - 2
    draw.ellipse(
        [x - inner_r, y - inner_r, x + inner_r, y + inner_r],
        fill=(175, 235, 225, 240),
    )

    return result


def draw_simple_icon(draw, icon_type, cx, cy, size=14, color=(30, 70, 70, 255)):
    s = size

    if icon_type == "email":
        pts = [cx - s, cy - s * 0.6, cx + s, cy + s * 0.6]
        draw.rectangle(pts, outline=color, width=2)
        draw.line([(cx - s, cy - s * 0.6), (cx, cy + s * 0.1), (cx + s, cy - s * 0.6)], fill=color, width=2)

    elif icon_type == "calendar":
        draw.rectangle([cx - s, cy - s * 0.5, cx + s, cy + s], outline=color, width=2)
        draw.line([(cx - s, cy - s * 0.1), (cx + s, cy - s * 0.1)], fill=color, width=2)
        draw.line([(cx - s * 0.5, cy - s * 0.5), (cx - s * 0.5, cy - s * 0.8)], fill=color, width=2)
        draw.line([(cx + s * 0.5, cy - s * 0.5), (cx + s * 0.5, cy - s * 0.8)], fill=color, width=2)
        for row in range(2):
            for col in range(3):
                dx = cx - s * 0.6 + col * s * 0.6
                dy = cy + s * 0.15 + row * s * 0.35
                draw.rectangle([dx, dy, dx + s * 0.3, dy + s * 0.2], fill=color)

    elif icon_type == "chat":
        draw.ellipse([cx - s, cy - s * 0.8, cx + s, cy + s * 0.5], outline=color, width=2)
        draw.polygon([(cx - s * 0.2, cy + s * 0.5), (cx - s * 0.6, cy + s), (cx + s * 0.2, cy + s * 0.4)], fill=color)
        for i, dx in enumerate([-s * 0.5, 0, s * 0.5]):
            draw.ellipse([cx + dx - 2, cy - 2, cx + dx + 2, cy + 2], fill=color)

    elif icon_type == "bell":
        draw.arc([cx - s * 0.8, cy - s, cx + s * 0.8, cy + s * 0.6], 180, 0, fill=color, width=2)
        draw.line([(cx - s * 0.8, cy + s * 0.3), (cx + s * 0.8, cy + s * 0.3)], fill=color, width=2)
        draw.line([(cx, cy - s), (cx, cy - s * 1.3)], fill=color, width=2)
        draw.arc([cx - s * 0.25, cy + s * 0.2, cx + s * 0.25, cy + s * 0.7], 0, 180, fill=color, width=2)

    elif icon_type == "video":
        draw.rectangle([cx - s, cy - s * 0.6, cx + s * 0.3, cy + s * 0.6], outline=color, width=2, fill=None)
        draw.polygon([(cx + s * 0.4, cy - s * 0.35), (cx + s, cy), (cx + s * 0.4, cy + s * 0.35)], fill=color)

    elif icon_type == "notes":
        draw.rectangle([cx - s * 0.7, cy - s, cx + s * 0.7, cy + s], outline=color, width=2)
        for i, frac in enumerate([-0.4, 0, 0.4]):
            lw = s * (1.0 if i < 2 else 0.6)
            draw.line([(cx - lw * 0.5, cy + s * frac), (cx + lw * 0.5, cy + s * frac)], fill=color, width=2)

    elif icon_type == "phone":
        draw.arc([cx - s, cy - s, cx + s, cy + s], 200, 340, fill=color, width=3)
        r2 = s * 0.6
        draw.arc([cx - r2, cy - r2, cx + r2, cy + r2], 200, 340, fill=color, width=3)
        draw.ellipse([cx - 3, cy + s * 0.1, cx + 3, cy + s * 0.1 + 6], fill=color)

    elif icon_type == "location":
        draw.ellipse([cx - s * 0.7, cy - s, cx + s * 0.7, cy + s * 0.2], outline=color, width=2)
        draw.polygon([(cx - s * 0.3, cy + s * 0.1), (cx, cy + s * 1.1), (cx + s * 0.3, cy + s * 0.1)], fill=color)
        draw.ellipse([cx - s * 0.25, cy - s * 0.55, cx + s * 0.25, cy - s * 0.1], fill=color)


def main():
    bg = make_radial_gradient(WIDTH, HEIGHT, CENTER_X, CENTER_Y, (20, 50, 50), BG_DARK, 700)
    img = bg.convert("RGBA")

    img = draw_glow_circle(img, CENTER_X, CENTER_Y, 200, GLOW_COLOR, alpha=30, blur=60)
    img = draw_glow_circle(img, CENTER_X, CENTER_Y, 100, GLOW_COLOR, alpha=20, blur=40)

    draw = ImageDraw.Draw(img)
    for r in RING_RADII:
        for t_offset in [0]:
            draw.ellipse(
                [CENTER_X - r, CENTER_Y - r, CENTER_X + r, CENTER_Y + r],
                outline=(80, 130, 130, 45),
                width=1,
            )

    icon_map = {
        "email": 180,
        "calendar": 135,
        "chat": 60,
        "bell": 25,
        "video": -20,
        "notes": 155,
        "phone": 225,
        "location": 280,
    }
    icon_orbits = {
        "email": 4,
        "calendar": 3,
        "chat": 3,
        "bell": 4,
        "video": 4,
        "notes": 2,
        "phone": 3,
        "location": 3,
    }

    for icon_type, angle_deg in icon_map.items():
        orbit_idx = icon_orbits[icon_type]
        radius = RING_RADII[orbit_idx]
        angle_rad = math.radians(angle_deg)
        ix = CENTER_X + int(radius * math.cos(angle_rad))
        iy = CENTER_Y - int(radius * math.sin(angle_rad))

        img = draw_icon_badge(img, ix, iy, badge_radius=28)
        draw = ImageDraw.Draw(img)
        draw_simple_icon(draw, icon_type, ix, iy, size=13, color=(35, 75, 75, 240))

    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    max_dist = math.sqrt((WIDTH / 2) ** 2 + (HEIGHT / 2) ** 2)
    for y_pos in range(0, HEIGHT, 4):
        for x_pos in range(0, WIDTH, 4):
            dist = math.sqrt((x_pos - WIDTH / 2) ** 2 + (y_pos - HEIGHT / 2) ** 2)
            alpha = int(min(60, 60 * (dist / max_dist) ** 2))
            if alpha > 5:
                vdraw.rectangle(
                    [x_pos, y_pos, x_pos + 3, y_pos + 3],
                    fill=(0, 0, 10, alpha),
                )

    img = Image.alpha_composite(img, vignette)

    final = img.convert("RGB")
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "boomstarter-cover-mobile.png")
    final.save(out_path, "PNG", optimize=True)
    print(f"Saved: {out_path} ({final.size[0]}x{final.size[1]})")


if __name__ == "__main__":
    main()
